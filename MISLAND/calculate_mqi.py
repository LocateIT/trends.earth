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
from MISLAND.gui.DlgCalculateMQI import Ui_DlgCalculateMQI
from MISLAND.mqi_setup import mqi_setup_widget
from MISLAND.api import run_script


class DlgCalculateMQI(DlgCalculateBase, Ui_DlgCalculateMQI):
    def __init__(self, parent=None):
        """Constructor."""
        super(DlgCalculateMQI, self).__init__(parent)

        self.setupUi(self)

    def showEvent(self, event):
        super(DlgCalculateMQI, self).showEvent(event)

        self.mqi_setup_widget = mqi_setup_widget
        self.TabBox.insertTab(0, self.mqi_setup_widget, self.tr('Management Quality Index Setup'))

        if self.reset_tab_on_showEvent:
            self.TabBox.setCurrentIndex(0)
