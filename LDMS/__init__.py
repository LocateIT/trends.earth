# -*- coding: utf-8 -*-
"""
/***************************************************************************
 LDMS - A QGIS plugin
 This plugin supports monitoring and reporting of land degradation to the UNCCD 
 and in support of the SDG Land Degradation Neutrality (LDN) target.
                              -------------------
        begin                : 2017-05-23
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Conservation International
        email                : trends.earth@conservation.org
 ***************************************************************************/
"""

__version__ = "1.0.2"

import sys
import os
import requests
import site
from tempfile import NamedTemporaryFile

from qgis.PyQt import QtCore

from qgis.core import QgsMessageLog
from qgis.utils import iface

# Ensure that the ext-libs for the plugin are near the front of the path
# (important on Linux)
dirpath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'ext-libs'))
sys.path, remainder = sys.path[:1], sys.path[1:]
site.addsitedir(dirpath)
sys.path.extend(remainder)

debug = QtCore.QSettings().value('LDMS/debug', True)


def log(message, level=0):
    if debug:
        QgsMessageLog.logMessage(message, tag="LDMS", level=level)

# noinspection PyPep8Naming


def classFactory(iface):  # pylint: disable=invalid-name
    """Load LDMPPlugin class from file LDMS.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """

    from LDMS.plugin import LDMPPlugin
    return LDMPPlugin(iface)

# Function to get a temporary filename that handles closing the file created by 
# NamedTemporaryFile - necessary when the file is for usage in another process 
# (i.e. GDAL)
def GetTempFilename(suffix):
    f = NamedTemporaryFile(suffix=suffix, delete=False)
    f.close()
    return f.name
