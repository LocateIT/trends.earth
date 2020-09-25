# -*- coding: utf-8 -*-
"""
/***************************************************************************
 LDMP - A QGIS plugin
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

from LDMP import log
from LDMP.calculate import DlgCalculateBase, get_script_slug
from LDMP.gui.DlgCalculateCQI import Ui_DlgCalculateCQI
from LDMP.api import run_script
from LDMP.cqi_setup import cqi_setup_widget


class DlgCalculateCQI(DlgCalculateBase, Ui_DlgCalculateCQI):
    def __init__(self, parent=None):
        """Constructor."""
        super(DlgCalculateCQI, self).__init__(parent)

        self.setupUi(self)

    def showEvent(self, event):
        super(DlgCalculateCQI, self).showEvent(event)

        self.cqi_setup_tab = cqi_setup_widget
        self.TabBox.insertTab(0, self.cqi_setup_tab, self.tr('Climate Quality Index Setup'))

        # These boxes may have been hidden if this widget was last shown on the 
        # SDG one step dialog
        self.cqi_setup_tab.groupBox_terra_period.show()
        self.cqi_setup_tab.use_custom.show()
        self.cqi_setup_tab.groupBox_custom_prec.show()
        self.cqi_setup_tab.groupBox_custom_pet.show()

        # This box may have been hidden if this widget was last shown on the 
        # SDG one step dialog
        self.cqi_setup_tab.groupBox_terra_period.show()

        if self.reset_tab_on_showEvent:
            self.TabBox.setCurrentIndex(0)

        # precipitation and potential evapotranspiration custom input layers
        self.cqi_setup_tab.use_custom_prec.populate()
        self.cqi_setup_tab.use_custom_pet.populate()
