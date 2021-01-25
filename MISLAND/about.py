# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MISLAND - A QGIS plugin
 This plugin supports monitoring and reporting of land degradation to the UNCCD 
 and in support of the SDG Land Degradation Neutrality (LDN) target.
                              -------------------
        begin                : 2017-05-23
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Conservation International
        email                : trends.earth@conservation.org
 ***************************************************************************/
"""

import os
import sys

from MISLAND import __version__

from qgis.PyQt import QtWidgets, uic

# Need to use this below approach to load the dialog to about the import
# resources_rc problem you get with QGIS plugins when loading resources. See:
# https://gis.stackexchange.com/a/202162/25916
sys.path.append(os.path.dirname(__file__))
FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'gui', 'DlgAbout.ui'),
                               resource_suffix='')


class DlgAbout(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(DlgAbout, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        # Add version number to about dialog
        self.textBrowser.setHtml(self.textBrowser.toHtml().replace('VERSION_NUMBER', __version__))
