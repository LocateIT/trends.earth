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
import json

from qgis.PyQt import QtWidgets, uic

from qgis.PyQt.QtCore import QDate, QTextCodec

from MISLAND import log
from MISLAND.calculate import DlgCalculateBase, get_script_slug
from MISLAND.gui.DlgTimeseries import Ui_DlgTimeseries
from MISLAND.api import run_script

from qgis.gui import QgsMapToolEmitPoint, QgsMapToolPan
from qgis.utils import iface

mb = iface.messageBar()

indices_set = {
    "ndvi":"NDVI (Humid zones)",
    "msavi2":"MSAVI2 (Arid and Stepic zones)",
    "savi":"SAVI (Desert Areas)"
}
class DlgTimeseries(DlgCalculateBase, Ui_DlgTimeseries):
    def __init__(self, parent=None):
        """Constructor."""
        super(DlgTimeseries, self).__init__(parent)

        self.setupUi(self)

        self.task_name.textChanged.connect(self.get_title)

        self.get_title()

        
    def get_title(self):

        log("{}".format(self.task_name.text()))
        self.task_name.text()

    def btn_cancel(self):
        self.close()

    def btn_calculate(self):
        # Note that the super class has several tests in it - if they fail it
        # returns False, which would mean this function should stop execution
        # as well.
        ret = super(DlgTimeseries, self).btn_calculate()
        if not ret:
            return

        self.close()

        if self.ndvi.isChecked():
            indices = 'NDVI'
        elif self.savi.isChecked():
            indices = 'SAVI'
        else:
            indices = 'MSAVI2'

        crosses_180th, geojsons = self.aoi.bounding_box_gee_geojson()
        payload = {'crosses_180th': crosses_180th,
                   'geojsons': json.dumps(geojsons),
                   'crs': self.aoi.get_crs_dst_wkt(),
                   'indices':indices,
                   'title':self.task_name.text(),
                   'task_name': self.options_tab.task_name.text(),
                   'task_notes': self.options_tab.task_notes.toPlainText()}
        # This will add in the method parameter
        # payload.update(self.scripts['productivity']['trajectory functions'][self.traj_indic.currentText()]['params'])

        resp = run_script(get_script_slug('time-series'), payload)

        if resp:
            mb.pushMessage(self.tr("Submitted"),
                           self.tr("Time series calculation task submitted to Google Earth Engine."),
                           level=0, duration=5)
        else:
            mb.pushMessage(self.tr("Error"),
                           self.tr("Unable to submit time series calculation task to Google Earth Engine."),
                           level=1, duration=5)
