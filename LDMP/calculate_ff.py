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

import os
import sys
import json


from LDMP import __version__

from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtCore import QDate

from qgis.utils import iface
from LDMP import log

mb = iface.messageBar()
from LDMP.calculate import DlgCalculateBase, get_script_slug
from LDMP.gui.DlgCalculateForestFire import Ui_DlgCalculateForestFire as UiDialog
from LDMP.api import run_script

# Need to use this below approach to load the dialog to about the import
# resources_rc problem you get with QGIS plugins when loading resources. See:
# https://gis.stackexchange.com/a/202162/25916
# sys.path.append(os.path.dirname(__file__))
# FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'gui', 'DlgCalculateForestFire.ui'),
#                                resource_suffix='')


class DlgCalculateForestFire(DlgCalculateBase, UiDialog):
    def __init__(self, parent=None):
        """Constructor."""
        super(DlgCalculateForestFire, self).__init__(parent)

        self.setupUi(self)


        # self.radio_landsat8.toggled.connect(self.update_time_bounds)
        self.radio_landsat8.toggled.connect(self.radio_landsat8_toggled)

        self.radio_landsat8_toggled()

        # reset date input on user change. Postfire dates come only after prefire dates 
        self.prefire_start_btn.userDateChanged.connect(self.update_time_bounds)
        self.prefire_end_btn.userDateChanged.connect(self.update_time_bounds)
        self.postfire_start_btn.userDateChanged.connect(self.update_time_bounds)

        self.update_time_bounds()

    def radio_landsat8_toggled(self):
        if self.radio_sentinel2.isChecked():
            start_year = QDate(2015, 6, 24)
            self.prefire_start_btn.setDate(start_year)
        else:
            start_year = QDate(2015, 2, 12)
            self.prefire_start_btn.setDate(start_year)

        self.update_time_bounds()

    def update_time_bounds(self):
        # default dates
        start_year = QDate(2012, 1, 1)
        end_year = QDate(2030, 1, 1)    
        # study period 
        self.prefire_start_btn.setMinimumDate(start_year)
        self.prefire_start_btn.setMaximumDate(end_year)
        self.prefire_end_btn.setMinimumDate(self.prefire_start_btn.date())
        self.prefire_end_btn.setMaximumDate(end_year)
        self.postfire_start_btn.setMinimumDate(self.prefire_end_btn.date())
        self.postfire_start_btn.setMaximumDate(end_year)
        self.postfire_end_btn.setMinimumDate(self.postfire_start_btn.date())
        self.postfire_end_btn.setMaximumDate(end_year)

    def btn_cancel(self):
        self.close()

    def btn_calculate(self):

        ret = super(DlgCalculateForestFire, self).btn_calculate()
        if not ret:
            return

        self.close()
        
        if self.radio_landsat8.isChecked():
            prod_mode= 'L8'
        else:
            prod_mode = 'S2'

        crosses_180th, geojsons = self.aoi.bounding_box_gee_geojson()

        prefire_start ='{0}-{1}-{2}'.format(self.prefire_start_btn.date().year(), self.prefire_start_btn.date().month(), self.prefire_start_btn.date().day())
        prefire_end = '{0}-{1}-{2}'.format(self.prefire_end_btn.date().year(), self.prefire_end_btn.date().month(), self.prefire_end_btn.date().day())
        postfire_start = '{0}-{1}-{2}'.format(self.postfire_start_btn.date().year(), self.postfire_start_btn.date().month(), self.postfire_start_btn.date().day())
        postfire_end = '{0}-{1}-{2}'.format(self.postfire_end_btn.date().year(), self.postfire_end_btn.date().month(), self.postfire_end_btn.date().day())
        payload = {'prod_mode': prod_mode,
                   'prefire_start_btn':prefire_start,
                   'prefire_end_btn': prefire_end,
                   'postfire_start_btn': postfire_start,
                   'postfire_end_btn': postfire_end,
                   'geojsons': json.dumps(geojsons),
                   'crs': self.aoi.get_crs_dst_wkt(),
                   'crosses_180th': crosses_180th,
                   'task_name': self.options_tab.task_name.text(),
                   'task_notes': self.options_tab.task_notes.toPlainText()}

        resp = run_script(get_script_slug('forest-fire'), payload)

        if resp:
            mb.pushMessage(QtWidgets.QApplication.translate("LDMP", "Submitted"),
                           QtWidgets.QApplication.translate("LDMP", "Forest Fire task submitted to Google Earth Engine."),
                           level=0, duration=5)
        else:
            mb.pushMessage(QtWidgets.QApplication.translate("LDMP", "Error"),
                           QtWidgets.QApplication.translate("LDMP", "Unable to submit forest fire task to Google Earth Engine."),
                           level=0, duration=5)
