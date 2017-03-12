from __future__ import absolute_import
from contextlib import contextmanager
import copy
import json
import logging
from os.path import dirname, exists, join, isdir
import os
import subprocess
import sys
from traits.api import (Any, Bool, DelegatesTo, Dict, Enum, HasTraits,
                        Instance, Int, List, Property, Str, Tuple)

from .project import Project, TagInfo, get_project_dir
from .directory import File, Directory
from .media import Media
from .processor import (FactoryBase, CommandFactory, Processor,
                        PythonFunctionFactory, TaggerFactory, Job)
from .ui_utils import askopenfilename, askdirectory, asksaveasfilename


logger = logging.getLogger(__name__)


class Vixen(HasTraits):

    projects = List(Project)

    save_file = Str

    def save(self):
        data = [dict(name=p.name, save_file=p.save_file)
                for p in self.projects]
        with open(self.save_file, 'w') as fp:
            json.dump(data, fp)

    def load(self):
        if exists(self.save_file):
            with open(self.save_file) as fp:
                data = json.load(fp)
            self.projects = [Project(name=x['name'], save_file=x['save_file'])
                             for x in data]
        if len(self.projects) == 0:
            # FIXME: This seems like a jigna issue. If the projects trait is an
            # empty list to start with, then the UI does not seem to update
            # correctly when a new project is added. Adding a hidden project
            # seems to solve the issue. So this is a temporary workaround
            # until a better fix is found.
            self.projects = [Project(name='__hidden__')]

    def remove(self, project):
        if exists(project.save_file):
            os.remove(project.save_file)
        self.projects.remove(project)
        self.save()

    def _save_file_default(self):
        return join(get_project_dir(), 'projects.json')


class ProjectEditor(HasTraits):

    project = Instance(Project, allow_none=True)

    name = Str
    description = Str
    path = Str
    tags = List(TagInfo)

    extensions = List(Str)

    processors = List(FactoryBase)

    available_exts = List(Str)

    valid_path = Bool
    tag_name = Str
    ext_name = Str
    processor_type = Str

    test_job = Dict(Int, Job)
    test_job_status = Dict(Int, Str)

    ui = Instance('VixenUI')

    def add_tag(self, name):
        logger.info('Added tags: %s', name)
        tags = [TagInfo(name=x.strip(), type="string")
                for x in name.split(',')]
        self.tags.extend(tags)
        self.tag_name = ''

    def remove_tag(self, index):
        logger.info('Removed tag: %s', self.tags[index].name)
        del self.tags[index]

    def add_extension(self, name):
        logger.info('Added extensions: %s', name)
        self.extensions.extend([x.strip().lower() for x in name.split(',')])
        self.ext_name = ''

    def remove_extension(self, index):
        logger.info('Removed extension: %s', self.extensions[index])
        del self.extensions[index]

    def add_processor(self, name):
        logger.info('Adding processor: %s', name)
        procs = {
            'command': CommandFactory,
            'python': PythonFunctionFactory,
            'tagger': TaggerFactory
        }
        self.processors.append(procs[name](dest=self.path))

    def remove_processor(self, index):
        logger.info('Removing processor: %s', self.processors[index].name)
        del self.processors[index]

    def select_path(self):
        initialdir = self.path if len(self.path) > 0 else None
        path = askdirectory(
            title='Select Project Directory', initialdir=initialdir
        )
        if len(path) > 0:
            self.path = path

    def select_destination_path(self, proc):
        initialdir = proc.dest if len(proc.dest) > 0 else None
        path = askdirectory(
            title='Select Destination Directory',
            initialdir=initialdir
        )
        if len(path) > 0:
            proc.dest = path

    def find_extensions(self):
        with self.ui.busy():
            path = self.path
            exts = set(
                os.path.splitext(x.lower())[1]
                for r, d, files in os.walk(path) for x in files
            )
            self.available_exts = sorted(exts)

    def apply(self):
        with self.ui.busy():
            cp = self.project
            if cp is not None and self.valid_path:
                logger.info('Applying changes for project: %s', self.name)
                cp.name = self.name
                cp.description = self.description
                cp.path = self.path
                cp.extensions = self.extensions
                cp.processors = self.processors
                cp.update_tags(self.tags)
                cp.scan()
                cp.save()
                if self.ui is not None:
                    self.ui.vixen.save()

    def check_processor(self, proc):
        with self.ui.busy():
            proj = self.project
            jobs = []
            for key in proj.keys():
                test_media = [key]
                jobs = proc.make_jobs(test_media, proj)
                if len(jobs) > 0:
                    break
            index = self.processors.index(proc)
            self.clear_test_info(index)
            if len(jobs) == 0:
                self.test_job_status[index] = 'Error'
            else:
                job = jobs[0]
                self.test_job[index] = job
                job.run()
                job.thread.join()
                proc.clear()

    def clear_test_info(self, index):
        if index in self.test_job:
            del self.test_job[index]
        if index in self.test_job_status:
            del self.test_job_status[index]

    def _project_changed(self, proj):
        with self.ui.busy():
            if proj is not None:
                if proj.number_of_files == 0:
                    proj.load()
                self.name = proj.name
                self.description = proj.description
                self.path = proj.path
                self.tags = copy.deepcopy(proj.tags)
                self.extensions = list(proj.extensions)
                self.processors = proj.processors
                self.available_exts = []
                self.test_job = {}
                self.test_job_status = {}

    def _path_changed(self, path):
        self.valid_path = isdir(path)


class Pager(HasTraits):

    """A simple paginator for a large list of elements.
    """

    selected = Any

    limit = Int(20)

    index = Property(Int, depends_on='_index')

    rel_index = Property(Int, depends_on='_index')

    page = Property(Int, depends_on='_page')

    start = Property(Int, depends_on='_page')

    view = Property(List, depends_on=['page', 'data'])

    total = Property(Int, depends_on='data')

    total_pages = Property(Int, depends_on=['data', 'limit'])

    data = List
    _page = Int
    _index = Int

    def select(self, relindex=None):
        if relindex is None:
            index = self.index
        else:
            index = (self.page - 1)*self.limit + relindex
            self.index = index
        data = self.data
        if len(data) > 0:
            self.selected = data[index]
        else:
            self.selected = None

    def next(self):
        self.index += 1

    def prev(self):
        self.index -= 1

    def next_page(self):
        self.page += 1

    def prev_page(self):
        self.page -= 1

    def _data_changed(self, data):
        self.selected = None
        self._index = 0
        self._page = 1

    def _get_page(self):
        return self._page

    def _set_page(self, page):
        p = min(max(1, page), self.total_pages)
        limit = self.limit
        if p != self._page:
            self._page = p
            base_index = (p - 1)*limit
            if self.index < base_index or self.index > base_index + limit:
                self.index = base_index

    def _get_start(self):
        return (self.page - 1)*self.limit

    def _get_view(self):
        p = self.page - 1
        limit = self.limit
        return self.data[p*limit:(p+1)*limit]

    def _get_index(self):
        return self._index

    def _set_index(self, index):
        idx = min(max(0, index), self.total-1)
        if idx != self._index:
            self._index = idx
            desired_page = int(idx/self.limit) + 1
            if self.page != desired_page:
                self.page = desired_page

    def __index_default(self):
        return -1

    def _get_rel_index(self):
        return self.index - (self.page - 1)*self.limit

    def _get_total(self):
        return len(self.data)

    def _get_total_pages(self):
        size = len(self.data)
        n = size/self.limit if size > 0 else 1
        rem = size % self.limit
        if rem > 0:
            return n + 1
        else:
            return n


class ProjectViewer(HasTraits):

    project = Instance(Project, allow_none=True)

    name = Str

    ui = Instance('VixenUI')

    parent = Instance(Directory)

    current_dir = Instance(Directory)

    current_file = Instance(File)

    pager = Instance(Pager)

    media = Instance(Media)

    last_save_time = DelegatesTo('project')

    search = Str

    search_pager = Instance(Pager)

    active_pager = Property(Instance(Pager), depends_on="is_searching")

    is_searching = Property(Bool, depends_on="search")

    search_completed = Bool(False)

    type = Enum("unknown", "image", "video", "audio")

    def go_to_parent(self):
        if self.parent is not None and not self.is_searching:
            self.current_dir = self.parent

    def import_csv(self):
        csv = askopenfilename(title='Open CSV file')
        if len(csv) > 0:
            result = self.project.import_csv(csv)
            if result[0]:
                self.ui.success(result[1])
            else:
                self.ui.error(result[1])

    def export_csv(self):
        csv = asksaveasfilename(
            title='Enter CSV file to create',
            defaultextension='.csv'
        )
        if len(csv) > 0:
            self.project.export_csv(csv)
            self.ui.success('Data saved to %s' % csv)

    def view(self, path):
        if isinstance(path, Directory):
            self.current_dir = path
        else:
            self.current_file = path

    def view_search_media(self, media):
        if media is not None:
            fname, key = media
            self.media = self.project.get(key)
        else:
            self.media = media

    def clear_search(self):
        if self.is_searching:
            self.search = ''
            self.media = None
            self.search_pager.data = []
            self.current_file = None

    def do_search(self):
        with self.ui.busy():
            if self.is_searching:
                self.media = None
                result = list(self.project.search(self.search))
                self.search_pager.data = result
                self.search_completed = True

    def rescan(self):
        with self.ui.busy():
            proj = self.project
            if proj is not None:
                proj.refresh()
                self.current_dir = proj.root
                self._current_dir_changed(proj.root)

    def os_open(self, path):
        """Ask the OS to open the path with a suitable application.
        """
        if sys.platform.startswith('win'):
            os.startfile(path)
        elif sys.platform.startswith('linux'):
            subprocess.call(['xdg-open', path])
        elif sys.platform == 'darwin':
            subprocess.call(['open', path])

    def _project_changed(self, proj):
        with self.ui.busy():
            if proj is not None:
                if proj.number_of_files == 0:
                    proj.load()
                self.name = proj.name
                self.current_dir = proj.root
                self.current_file = None
                self.clear_search()

    def _current_dir_changed(self, d):
        self.parent = d.parent
        self.pager.data = d.directories + d.files

    def _current_file_changed(self, file):
        if file is not None:
            self.media = self.project.get(file.relpath)

    def _pager_default(self):
        p = Pager(limit=20)
        p.on_trait_change(self.view, 'selected')
        return p

    def _search_pager_default(self):
        p = Pager(limit=20)
        p.on_trait_change(self.view_search_media, 'selected')
        return p

    def _get_is_searching(self):
        return len(self.search) > 0

    def _search_changed(self, s):
        self.search_completed = False
        self.current_file = None

    def _get_active_pager(self):
        if self.is_searching:
            return self.search_pager
        else:
            return self.pager


class VixenUI(HasTraits):

    vixen = Instance(Vixen)

    mode = Enum('edit', 'view')

    editor = Instance(ProjectEditor)

    viewer = Instance(ProjectViewer)

    processor = Instance(Processor)

    is_busy = Bool(False)

    docs = Property(Str)

    version = Str

    message = Tuple()

    # Private trait to generate message counts.
    _message_count = Int

    def get_context(self):
        return dict(
            ui=self, vixen=self.vixen, editor=self.editor, viewer=self.viewer
        )

    def home(self):
        self.mode = 'edit'

    def error(self, msg):
        mid = self._get_message_id()
        self.message = msg, "error", mid
        logger.info("ERROR: %s", msg)

    def info(self, msg):
        mid = self._get_message_id()
        self.message = msg, "info", mid
        logger.info("INFO: %s", msg)

    def success(self, msg):
        mid = self._get_message_id()
        self.message = msg, "success", mid
        logger.info("SUCCESS: %s", msg)

    def edit(self, project):
        logger.info('Edit project: %s', project.name)
        self.editor.project = project
        self.mode = 'edit'
        self.info('Remember to "Apply changes" if you change anything.')

    def view(self, project):
        logger.info('View project: %s', project.name)
        self.viewer.project = project
        self.mode = 'view'
        self.editor.project = None
        self.info('Remember to "Save" if you edit any tags.')

    def process(self, project):
        jobs = []
        for proc in project.processors:
            if self.viewer.is_searching:
                to_process = [x[1] for x in self.viewer.search_pager.data]
            else:
                to_process = project.keys()
            jobs.extend(proc.make_jobs(to_process, project))
        self.processor.jobs = jobs
        self.processor.process()
        self.info("Remember to save the project once processing completes.")

    def remove(self, project):
        logger.info('Removing project: %s', project.name)
        self.vixen.remove(project)
        self.editor.project = None

    def add_project(self):
        name = 'Project%d' % (len(self.vixen.projects))
        p = Project(name=name)
        self.vixen.projects.append(p)
        self.editor.project = p
        logger.info('Added project %s', name)

    def save(self):
        with self.busy():
            if self.mode == 'edit':
                if self.editor is not None and self.editor.project is not None:
                    self.editor.apply()
            elif self.mode == 'view':
                if self.viewer.project is not None:
                    self.viewer.project.save()

    def halt(self):
        """Shut down the webserver.
        """
        logger.info('**** Halting ViXeN ****')
        from tornado.ioloop import IOLoop
        ioloop = IOLoop.instance()
        ioloop.stop()

    @contextmanager
    def busy(self):
        self.is_busy = True
        try:
            yield
        finally:
            self.is_busy = False

    def _get_docs(self):
        mydir = dirname(__file__)
        build = join(dirname(mydir), 'docs', 'build', 'html', 'index.html')
        bundled = join(
            dirname(mydir), 'vixen_data', 'docs', 'html', 'index.html'
        )
        if exists(bundled):
            return bundled
        else:
            return build

    def _vixen_default(self):
        v = Vixen()
        v.load()
        return v

    def _editor_default(self):
        return ProjectEditor(ui=self)

    def _viewer_default(self):
        return ProjectViewer(ui=self)

    def _processor_default(self):
        return Processor()

    def _version_default(self):
        import vixen
        return vixen.__version__

    def _get_message_id(self):
        mc = self._message_count
        mc += 1
        if mc > 100:
            mc = 0
        self._message_count = mc
        return mc
