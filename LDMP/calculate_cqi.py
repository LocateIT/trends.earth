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
from LDMP.gui.DlgCalculateProd import Ui_DlgCalculateProd as UiDialog
from LDMP.api import run_script


class DlgCalculateCQI(DlgCalculateBase, UiDialog):
    def __init__(self, parent=None):
        """Constructor."""
        super(DlgCalculateCQI, self).__init__(parent)

        self.setupUi(self)