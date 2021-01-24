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

from future import standard_library
standard_library.install_aliases()
import os
import json

from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import QDate

from qgis.utils import iface
mb = iface.messageBar()

from MISLAND import log
from MISLAND.calculate import DlgCalculateBase, get_script_slug
from MISLAND.gui.DlgCalculateVQI import Ui_DlgCalculateVQI
from MISLAND.vqi_setup import vqi_setup_widget
from MISLAND.api import run_script


class DlgCalculateVQI(DlgCalculateBase, Ui_DlgCalculateVQI):
    def __init__(self, parent=None):
        """Constructor."""
        super(DlgCalculateVQI, self).__init__(parent)

        self.setupUi(self)

    def showEvent(self, event):
        super(DlgCalculateVQI, self).showEvent(event)

        self.vqi_setup_tab = vqi_setup_widget
        self.TabBox.insertTab(0, self.vqi_setup_tab, self.tr('Vegetation Quality Index Setup'))

        if self.reset_tab_on_showEvent:
            self.TabBox.setCurrentIndex(0)
