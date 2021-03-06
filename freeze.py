#!/usr/bin/env python

import datetime
import os
import shutil
import subprocess
import sys


def copy_python_on_osx():
    if hasattr(sys, 'base_prefix'):
        dest = os.path.join('dist', 'ViXeN.app', 'Contents', 'MacOS')
        python_lib = os.path.join(sys.base_prefix, 'Python')
        print("Copying %s -> %s" % (python_lib, dest))
        shutil.copy(python_lib, dest)


def get_platform_name():
    import platform
    name = ''
    if sys.platform == 'darwin':
        name = 'mac'
    elif sys.platform.startswith('linux'):
        name = 'linux'
    else:
        name = 'win'
    arch = platform.architecture()[0][:2]
    return name + arch


def get_package_dir():
    import vixen

    version = vixen.__version__
    if version.endswith('.dev0'):
        today = datetime.datetime.now().strftime('%Y%m%d')
        version += '-' + today

    plat = get_platform_name()
    return os.path.join(
        'dist', 'vixen-{version}-{plat}'.format(
            version=version, plat=plat
        )
    )


def make_bundle():
    package_dir = get_package_dir()
    os.makedirs(package_dir)

    if sys.platform.startswith('darwin'):
        shutil.move(os.path.join('dist', 'ViXeN.app'), package_dir)
    else:
        shutil.move(os.path.join('dist', 'vixen_app'), package_dir)

    if sys.platform.startswith('linux'):
        shutil.copy(os.path.join('installer', 'vixen'), package_dir)
        shutil.copy(os.path.join('installer', 'ViXeN.desktop'), package_dir)
        shutil.copy(os.path.join('installer', 'vixen.png'), package_dir)
        ssl_cert = os.path.join(sys.prefix, 'ssl', 'cert.pem')
        if os.path.exists(ssl_cert):
            d = os.path.join(package_dir, 'vixen_app', 'ssl')
            if not os.path.exists(d):
                os.makedirs(d)
            shutil.copy(ssl_cert, d)
    elif sys.platform.startswith('darwin'):
        ssl_cert = os.path.join(sys.prefix, 'ssl', 'cert.pem')
        if os.path.exists(ssl_cert):
            d = os.path.join(
                package_dir, 'ViXeN.app', 'Contents', 'Resources', 'ssl'
            )
            if not os.path.exists(d):
                os.makedirs(d)
            shutil.copy(ssl_cert, d)
            cwd = os.getcwd()
            os.chdir(
                os.path.join(package_dir, 'ViXeN.app', 'Contents', 'MacOS')
            )
            os.symlink('../Resources/ssl', 'ssl')
            os.chdir(cwd)

    elif sys.platform.startswith('win32'):
        shutil.copy(os.path.join('installer', 'vixen.bat'), package_dir)
        shutil.copy(os.path.join('installer', 'vixen.lnk'), package_dir)


def main():
    os.chdir('docs')
    make = 'make.bat' if sys.platform.startswith('win') else 'make'
    subprocess.call([make, 'html'])
    os.chdir('..')

    subprocess.call(['pyinstaller', 'vixen.spec'])

    if sys.platform == 'darwin':
        copy_python_on_osx()

    make_bundle()

if __name__ == '__main__':
    main()
