Development
===========

MISLAND is free and open-source software, licensed under the `GNU 
General Public License, version 2.0 or later 
<https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html>`_.

There are a number of components to the MISLAND tool. The first is a 
QGIS plugin supporting calculation of indicators, access to raw data, 
reporting, and production of print maps . The code for the plugin, and further 
instructions on installing it if you want to modify the code, are in 
`MISLAND <https://github.com/LocateIT/trends.earth>`_ 
GitHub repository.

The MISLAND QGIS plugin is supported by a number of different Python 
scripts that allow calculation of the various indicators on Google Earth Engine 
(GEE). These scripts sit in the "gee" sub-folder of that GitHub repository. The 
GEE scripts are supported by the `landdegradation` Python module, which 
includes code for processing inputs and outputs for the plugin, as well as 
other common functions supporting calculation of NDVI integrals, statistical 
significance, and other shared code. The code for this module is available in 
the `landdegradation 
<https://github.com/ConservationInternational/landdegradation>`_ repository on 
GitHub.

Further details are below on how to contribute to MISLAND by working on 
the plugin code, by modifying the processing code, or by contributing to 
translating the website and plugin.

Modifying the QGIS Plugin code
______________________________


Downloading the MISLAND code
---------------------------------

The MISLAND code for both the plugin and the Google Earth Engine scripts 
that support it are located on GitHub in the `MISLAND
<https://github.com/LocateIT/trends.earth>`_ repository. Clone 
this repository to a convenient place on your machine in order to ensure you 
have the latest version of the code.

There are a number of different branches of the MISLAND repository that 
are under active development. While the plugin does not yet officially support 
QGIS3, however the majority of development is occurring on the "master" branch, 
which is aimed at QGIS3. The "qgis2" branch is the older version of the plugin, 
and supports QGIS2 version 2.18+.

The first time you download the MISLAND code, you will also need to clone 
the "schemas" submodule that is located within it, under "LDMP\\schemas". If 
you are using TortoiseGit on Windows, you can right-click anywhere within the 
MISLAND folder and choose "TortoiseGit" and then "Submodule Update...". 
Clicking ok in the window that comes up will checkout the schemas submodule. If 
you prefer, you can also do this from the command line by running the below two 
commands in shell::

   git submodule init
   git submodule update

Once you are done you should see files within the "LDMP\\schemas" folder within 
the MISLAND folder.

Installing dependencies
-----------------------

Python
~~~~~~

The plugin is coded in Python. In addition to being used to run the plugin 
through QGIS, Python is also used to support managing the plugin (changing the 
version, installing development versions, etc.). Though Python is included with 
QGIS, you will also need a local version of Python that you can setup with the 
software needed to manage the plugin. The easiest way to manage multiple 
versions of Python is through the `Anaconda distribution 
<https://www.anaconda.com>`_. For work developing the plugin, Python 
3 is required. To download Python 3.7 (recommended) though Anaconda,
`see this page <https://www.anaconda.com/distribution/#download-section>`_.

Python dependencies
~~~~~~~~~~~~~~~~~~~

In order to work with the MISLAND code, you need to have Invoke
installed on your machine, as well as a number of other packages that are used 
for managing the documentation, translations, etc. These packages are all 
listed in the "dev" requirements file for MISLAND, so they can be 
installed by navigating in a command prompt to the root of the MISLAND 
code folder and typing::

   pip install -r requirements-dev.txt

.. note::
   If you are using Anaconda, you will first want to activate a Python 3.7 
   virtual environment before running the above command (and any of the other 
   invoke commands listed on the page). One way to do this is by starting an 
   "Anaconda prompt", by `following the instructions on this Anaconda page
   <https://docs.anaconda.com/anaconda/user-guide/getting-started/#write-a-python-program-using-anaconda-prompt-or-terminal>`_.

PyQt
~~~~

PyQt5 is the graphics toolkit used by QGIS3. To compile the user interface for 
MISLAND for QGIS3 you need to install PyQt5. This package can be installed 
from pip using::

    pip install PyQt5

.. note::
    PyQt4 is the graphics toolkit used by QGIS2. The best source for this 
    package on Windows is from the set of packages maintained by Christoph 
    Gohlke at UC Irvine. To download PyQt4, select `the appropriate package 
    from this page <https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyqt4>`_. 
    Choose the appropriate file for the version of Python you are using. For 
    example, if you are using Python 2.7, choose the version with "cp27" in the 
    filename. If you are using Python 3.7, choose the version with "cp37" in 
    the filename. Choose "amd64" for 64-bit python, and "win32" for 32-bit 
    python.

    After downloading from the above link, use ``pip`` to install it. For example, 
    for the 64-bit wheel for Python 3.7, you would run::

       pip install PyQt4-4.11.4-cp37-cp37m-win_amd64.whl

Changing the version of the plugin
----------------------------------

The convention for MISLAND is that version numbers ending in an odd number
(for example 0.65) are development versions, while versions ending in an even 
number (for example (0.66) are release versions. Development versions of the 
plugin are never released via the QGIS repository, so they are never seen by 
normal users of the plugin. Odd-numbered development versions are used by the 
MISLAND development team while testing new features prior to their public 
release.

If you wish to make changes to the code and have downloaded a public release of 
the plugin (one ending in an even number), the first step is to update the 
version of the plugin to the next sequential odd number. So, for example, if 
you downloaded version 0.66 of the plugin, you would need to update the version 
to be 0.67 before you started making your changes. There are several places in 
the code where the version is mentioned (as well as within every GEE script) so 
there is an invoke task to assist with changing the version. To change the 
version to be 0.67, you would run::

   invoke set-version -v 0.67

Running the above command will update the version number every place it is 
referenced in the code. To avoid confusion, never change the version to one 
that has already been released - always INCREASE the value of the version tag 
to the next odd number.

Testing changes to the plugin
-----------------------------

After making changes to the plugin code, you will need to test them to ensure 
the plugin behaves as expected, and to ensure no bugs or errors come up. The 
plugin should go through extensive testing before it is released to the QGIS 
repository (where it can be accessed by other users) to ensure that any changes
to the code do not break the plugin.

To test any changes that you have made to the plugin within QGIS, you will need 
to install it locally. There are invoke tasks that assist with this process. 
The first step prior to installing the plugin is ensuring that you have setup 
the plugin with all of the dependencies that it needs in order to run from 
within QGIS. To do this, run::

   invoke plugin-setup

The above task only needs to be run immediately after downloading the 
MISLAND code, or if any changes are made to the dependencies for the 
plugin. By default ``plugin-setup`` will re-use any cached files on your 
machine. To start from scratch, add the ``-c`` (clean) flag to the above 
command.

After running ``plugin-setup``, you are ready to install the plugin to the QGIS 
plugins folder on your machine. To do this, run::

  invoke plugin-install

After running the above command, you will need to either 1) restart QGIS, or 2) 
use the `plugin reloader <https://plugins.qgis.org/plugins/plugin_reloader/>`_ 
to reload the MISLAND plugin in order to see the effects of the changes 
you have made.

By default ``plugin-install`` will overwrite any existing plugin files on your 
machine, but leave in place any data (administrative boundaries, etc.) that the 
plugin might have downloaded. To start from scratch, add the ``-c`` (clean) 
flag to the above command. You may need to close QGIS in order to successfully 
perform a clean install of the plugin using the ``-c`` flag.

.. note::
   By default plugin-install assumes you want to install the plugin to be used 
   in QGIS3. To install the plugin for use in QGIS3, add the flag ``-v 2`` to 
   the ``plugin-install`` command. Remember the plugin may or may not be 
   entirely functional on QGIS3 - the plugin was originally designed for QGIS2 
   and is still being tested on QGIS3.

Syncing and deploying changes to the binaries
---------------------------------------------

To speed the computations in MISLAND, some of the tools allow making use 
of pre-compiled binaries that have been compiled using `numba 
<https://numba.pydata.org>`_. Numba is an open source compiler that can compile 
Python and NumPy code, making it faster than when it is run as ordinary Python. 
To avoid users of MISLAND needing to download Numba and all of its 
dependencies, the MISLAND team makes pre-compiled binaries available for 
download if users choose to install them.

To generate pre-compiled binaries for the OS, bitness (32/64 bit) and Python 
version you are running on your machine, use::

    invoke binaries-compile

.. note::
  You will need a C++ compiler for the above command to work. On
  Windows, see `this github page 
  <https://wiki.python.org/moin/WindowsCompilers#Which_Microsoft_Visual_C.2B-.2B-_compiler_to_use_with_a_specific_Python_version_.3F>`_ 
  for details on how to
  install the Microsoft Visual C++ compiler needed for you Python version. On
  MacOS, you will most likely need to install Xcode. On Linux, install the
  appropriate version of GCC.

To make binaries publicly available, they are distributed through an Amazon Web 
services S3 bucket. To upload the binaries generated with the above command to 
the bucket, run::

    invoke binaries-sync

.. note:: The above command will fail if you do not have keys allowing write 
   access to the ``MISLAND`` bucket on S3.

The above command will sync each individual binary file to S3. However, users 
of the toolbox download the binaries as a single zipfile tied to the version of 
the plugin that they are using. To generate that zipfile so that it can be 
accessed by MISLAND users, run::

    invoke binaries-deploy

.. note:: The above command will fail if you do not have keys allowing write 
   access to the ``MISLAND`` bucket on S3.


Building a plugin ZIP file
--------------------------

There are several invoke tasks to help with building a ZIP file to deploy the 
plugin to the QGIS repository, or to share the development version of the 
plugin with others. To package the plugin and all of its dependencies into a 
ZIP file that can be installed following, run:

   invoke zipfile-build

This command will create a folder named ``build`` at the root of the 
MISLAND code folder, and in that folder it will create a file called 
``LDMP.zip``. This file can be shared with others, who can use it to manually 
install MISLAND.

This can be useful if there is a need to share the latest features with someone 
before they are available in the publicly released version of the plugin.

Deploying the development version ZIP file
------------------------------------------

The MISLAND GitHub page gives a link a ZIP file that allows users who may 
not be developers to access the development version of MISLAND. To create 
a ZIP file and make it available on that page (the ZIP file is stored on S3), 
run::

   invoke zipfile-deploy


.. note:: The above command will fail if you do not have keys allowing write 
   access to the ``misland`` bucket on S3.

Modifying the Earth Engine processing code
__________________________________________


The Google Earth Engine (GEE) processing scripts used by MISLAND are all 
stored in the "gee" folder under the main MISLAND folder. For these script 
to be accessible to users of the MISLAND QGIS plugin, they have to be 
deployed to the api.trends.earth serviceThe below 
describes how to test and deploy GEE scripts to be used with MISLAND.

Setting up dependencies
-----------------------

trends.earth-CLI
~~~~~~~~~~~~~~~~

The "trends.earth-CLI" Python package is required in order to work with the 
api.trends.earth server. This package is located on GitHub in the 
`trends.earth-CLI <https://github.com/LocateIT/trends.earth-CLI>`_ 
repository.

The first step is to clone this repository onto your machine. We recommend that 
you clone the repository into the same folder where you the trends.earth code. 
For example, if you had a "Code" folder on your machine, clone both the 
`trends.earth
<https://github.com/LocateIT/trends.earth>`_ repository (the 
code for the QGIS plugin and associated GEE scripts) and also the 
`trends.earth-CLI <https://github.com/LocateIT/trends.earth-CLI>`_ repository 
into that same folder.

When you setup your system as recommended above, trends.earth-CLI will work 
with the invoke tasks used to manage MISLAND without any modifications. 
If, however, you download trends.earth-CLI into a different folder, then you 
will need to add a file named "invoke.yaml" file into the root of the 
MISLAND repository, and in that file tell MISLAND where to locate the 
trends.earth-CLI code. This YAML file should look something like the below (if 
you downloaded the code on Windows into a folder called 
"C:/Users/grace/Code/trends.earth-CLI/tecli"):

.. code-block:: yaml

    gee:
        tecli: "C:/Users/grace/Code/trends.earth-CLI/tecli"

Again, you **do not** need to add this .yaml file if you setup your system as 
recommended above.

docker
~~~~~~

The trends.earth-CLI package requires `docker <http://www.docker.com>`_ in 
order to function. `Follow these instructions to install docker on Windows 
<https://docs.docker.com/docker-for-windows/install/>`_, and `these 
instructions to install docker on Mac OS 
<https://docs.docker.com/docker-for-mac/install/>`_. If you are running
Linux, `follow the instructions on this page
<https://docs.docker.com/install>`_ that are appropriate for the Linux 
distribution you are using.

Testing an Earth Engine script locally
--------------------------------------

After installing the trends.earth-CLI package, you will need to setup a 
.tecli.yml file with an access token to a GEE service account in order to test 
scripts on GEE. To setup the GEE service account for tecli, first obtain the 
key for your service account in JSON format (from the google cloud console), 
then and encode it in base64. Provide that base64 encoded key to tecli with the 
following command::

    invoke tecli-config set EE_SERVICE_ACCOUNT_JSON key

where "key" is the base64 encoded JSON format service account key.

While converting a script specifying code to be run on GEE from JavaScript to 
Python, or when making modifications to that code, it can be useful to test the 
script locally, without deploying it to the api.trends.earth server. To do 
this, use the ``run`` invoke task. For example, to test the "land_cover" 
script, go to the root directory of the code, and, in a command 
prompt, run::
   
   invoke tecli-run land_cover

This will use the trends.earth-CLI package to build and run a docker container 
that will attempt to run the "land_cover" script. If there are any syntax 
errors in the script, these will show up when the container is run. Before 
submitting a new script to api.trends.earth, always make sure that ``invoke 
tecli-run`` is able to run the script without any errors.

When using ``invoke tecli-run`` you may get an error saying:

.. code-block:: sh

   Invalid JWT: Token must be a short-lived token (60 minutes) and in a 
   reasonable timeframe. Check your iat and exp values and use a clock with 
   skew to account for clock differences between systems.
   
This error can be caused if the clock on the docker container gets out of sync 
with the system clock. Restarting docker should fix this error.

Deploying a GEE script to api.trends.earth
------------------------------------------

When you have finished testing a GEE script and would like it to be accessible 
using the QGIS plugin (and by other users of MISLAND), you can deploy it 
to the api.trends.earth server. The first step in the process is logging in to 
the api.trends.earth server. To login, run::
   
   invoke tecli-login

You will be asked for a username and password. These are the same as the 
username and password that you use to login to the MISLAND server from the 
QGIS plugin. **If you are not an administrator, you will be able to login, but 
the below command will fail**. To upload a script (for example, the 
"land_cover" script) to the server, run::
   
   invoke tecli-publish -s land_cover

If this script already exists on the server, you will be asked if you want to 
overwrite the existing script. Be very careful uploading scripts with 
even-numbered versions, as these are publicly available scripts, and any errors
that you make will affect anyone using the plugin. Whenever you are testing be 
sure to use development version numbers (odd version numbers).

After publishing a script to the server, you can use the `tecli-info` task to 
check the status of the script (to know whether it deployed successfully - 
though note building the script may take a few minutes). To check the status, 
of a deployed script, run::

   invoke tecli-publish -s land_cover

If you are making a new release of the plugin, and want to upload ALL of the 
GEE scripts at once (this is necessary whenever the plugin version number 
changes), run::
   
   invoke tecli-publish

Again - never run the above on a publicly released version of the plugin unless 
you are intending to overwrite all the publicly available scripts used by the 
plugin.