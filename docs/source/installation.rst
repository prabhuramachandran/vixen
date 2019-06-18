.. _installation:

=================================
Installation and getting started
=================================

To install ViXeN, you first need to know the platform you will be running it
on. ViXeN binaries are available for Linux (64 bit), Mac (64 bit), and Windows
(32 and 64 bit). You can install ViXeN in a Python environment easily too but
this is not necessary if you do not use Python.

In order to use ViXeN you will need to have a working browser. See the
:ref:`dependencies` section for more information on the dependencies.
Installing ViXeN is relatively straight-forward. Please see the instructions
for installing ViXeN in the relevant sections below.

.. contents::
    :local:
    :depth: 1

.. _dependencies:

------------------
Dependencies
------------------

^^^^^^^^^^^^^^^^^^
Core dependencies
^^^^^^^^^^^^^^^^^^

Please make sure you have a recent, functional browser such as:
- Mozilla Firefox_ (any recent version)
- Google Chrome_ (any recent version)
- Internet Explorer (IE 9 and above)

ViXeN is tested to work best on Firefox_ and Chrome_.

.. _Firefox: https://www.mozilla.org/en-US/firefox/new/
.. _Chrome: https://www.google.com/chrome/


^^^^^^^^^^^^^^^^^^^^^^
Optional dependencies
^^^^^^^^^^^^^^^^^^^^^^

The optional dependencies are:

- ffmpeg_

.. _ffmpeg: http://ffmpeg.org


This is only needed if you wish to use ffmpeg_ to convert any of your video media.

-------------------------------
Installing ViXeN on GNU/Linux
-------------------------------

On GNU/Linux systems one may install the dependencies by following three very
simple steps:

- Download the Linux binary from the `ViXeN releases`_.
- Unpack the ``vixen*.tgz`` file.
- Run the application inside the unpacked directory.

More detailed instructions are given below.

.. _ViXeN releases: https://github.com/vixen-project/vixen/releases

.. _using-nautilus:

^^^^^^^^^^^^^^^^^^^
Using Nautilus
^^^^^^^^^^^^^^^^^^^

1. Download the ViXen binary file (say vixen-1.0-linux64.tgz) from
   `ViXeN releases`_ to your preferred directory.

2. Right click and select 'Extract Here' or 'Open With Archive Manager'. A
   ViXeN folder will appear in the directory you have selected (in this case
   the folder will be ``vixen-1.0``).

3. Open the directory and double click the ``ViXeN`` file (the file is
   ``ViXeN.desktop``). The ViXeN application will open on the browser.

4. If the above did not work you can try to run the ``vixen`` file. This will
   run **if** Nautilus supports running executables. If it does not, run the
   command shown in :ref:`using-cli`.

.. _using-cli:

^^^^^^^^^^^^^^^^^^^^^^^
Using the Command Line
^^^^^^^^^^^^^^^^^^^^^^^

After downloading and unpacking ViXen either :ref:`using-nautilus`, run the
following commands on the terminal::

	$ cd vixen-1.0

Where ``vixen-1.0`` is the extracted ViXeN binary. Suppose you downloaded and
unpacked the ``vixen-1.0-linux64.tgz`` file in a folder named ``Software`` in
your ``home`` directory, then this command will be::

	$ cd Software/vixen-1.0

Then run the application using::

	$ ./vixen


------------------------------
Installing ViXeN on Mac OS X
------------------------------

1. On OS X, download the ZIP file from the `ViXeN releases`_ page.
2. Unpack it.
3. Run the resulting ``ViXeN.dmg`` file by double clicking it.

You may move this dmg file anywhere you like or move it to your
``Applications`` folder if you wish to.

------------------------------
Installing ViXeN on Windows
------------------------------


1. On Windows, download the ZIP file for your platform from `ViXeN releases`_.
2. Unpack the ZIP file.
3. Inside the unpacked directory is a ``vixen.bat`` script or a ``vixen.lnk``
   shortcut that you can use to run the application.

The application will open in your default browser window.


-----------------------
Installing using `pip`
-----------------------

If you have no idea what `pip`_ is, then you should look above for suitable
instructions. If you are familiar with Python and wish to install ViXeN in
your own Python environment, you can simply run::

  $ pip install vixen

The requirements for ViXeN are fairly modest.

Otherwise, if you wish to install the development version, you can clone the
ViXeN git repository at https://github.com/vixen-project/vixen and then do the
following::

  $ cd vixen
  $ pip install -r requirements.txt
  $ python setup.py install

If you want to stay up-to-date and not have to re-install each time you update
the git repository, you could instead do::

  $ python setup.py develop

.. _pip: https://pip.pypa.io/en/stable/

Once installed you can start the application by::

  $ vixen

To see any command line options try this::

  $ vixen -h

That's about it.

.. _troubleshooting:

-----------------
Troubleshooting
-----------------

If the application fails to run or you have any problems, please look at the
log file ``vixen.log`` located inside the ``.vixen`` folder in your home
directory.

- On Linux this is typically in the directory ``/home/username/.vixen``.
- On OS X this is in ``/Users/username/.vixen``.
- On Windows this may be ``C:\Users\username\.vixen``.

The log file should also be accessible once the ViXeN UI launches, it is
available on the top bar next to the "Home" and "Help" links on the top left.

The log file is a text file and if you see any sensitive information there,
you can feel free to edit it before you send it.

You may e-mail your log file to the developers or the mailing list.

The ViXeN mailing list is available at https://groups.google.com/d/forum/vixen
