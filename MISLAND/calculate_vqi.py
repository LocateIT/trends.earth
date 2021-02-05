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
from qgis.core import (QgsFeature, QgsPointXY, QgsGeometry, QgsJsonUtils,
    QgsVectorLayer, QgsCoordinateTransform, QgsCoordinateReferenceSystem,
    Qgis, QgsProject, QgsLayerTreeGroup, QgsLayerTreeLayer,
    QgsVectorFileWriter, QgsFields, QgsWkbTypes, QgsAbstractGeometrySimplifier)
from osgeo import ogr

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

        # reset date input on user change. Postfire dates come only after prefire dates 
        self.vqi_setup_tab.plant_start_btn.userDateChanged.connect(self.update_time_bounds)
        self.vqi_setup_tab.plant_end_btn.userDateChanged.connect(self.update_time_bounds)

        self.update_time_bounds()

    def update_time_bounds(self):
        # default dates
        end_year = QDate(2020, 12, 31)    
        # study period 
        # self.prefire_start_btn.setMinimumDate(start_year)
        self.vqi_setup_tab.plant_start_btn.setMaximumDate(end_year)
        self.vqi_setup_tab.plant_end_btn.setMinimumDate(self.vqi_setup_tab.plant_start_btn.date())
        self.vqi_setup_tab.plant_end_btn.setMaximumDate(end_year)

    def btn_cancel(self):
        self.close()

    def btn_calculate(self):

        ret = super(DlgCalculateVQI, self).btn_calculate()
        if not ret:
            return

        date_format = '{0}-{1}-{2}'
        plant_start =date_format.format(self.vqi_setup_tab.plant_start_btn.date().year(), self.vqi_setup_tab.plant_start_btn.date().month(), self.vqi_setup_tab.plant_start_btn.date().day())
        plant_end = date_format.format(self.vqi_setup_tab.plant_end_btn.date().year(), self.vqi_setup_tab.plant_end_btn.date().month(), self.vqi_setup_tab.plant_end_btn.date().day())
        
        if (plant_start == plant_end):
            QtWidgets.QMessageBox.critical(None, self.tr("Error"),
                                           self.tr("Plant Cover start and end date cannot be the same."))
            return

        self.close()

        crosses_180th, geojsons = self.aoi.bounding_box_gee_geojson()
        val = []
        n = 1

        if self.area_tab.area_fromfile.isChecked():
            for f in self.aoi.get_layer_wgs84().getFeatures():
                # Get an OGR geometry from the QGIS geometry
                geom = f.geometry()
                val.append(geom)
                n += 1

            # stringify json object 
            val_string = '{}'.format(json.loads(val[0].asJson()))

            # create ogr geometry
            val_geom = ogr.CreateGeometryFromJson(val_string)
            # simplify polygon to tolerance of 0.003
            val_geom_simplified = val_geom.Simplify(0.003)

            # fetch coordinates from json  
            coords= json.loads(val_geom_simplified.ExportToJson())['coordinates']
            geometries = json.dumps([{
                "coordinates":coords,
                "type":"Polygon"
            }])


        elif self.area_tab.area_fromadmin.isChecked():
            geometries =json.dumps([{
                "coordinates":self.get_admin_poly_geojson()['geometry']['coordinates'][0],
                "type":"Polygon"
            }])
        elif self.area_tab.area_frompoint.isChecked():
            point = QgsPointXY(float(self.area_tab.area_frompoint_point_x.text()), float(self.area_tab.area_frompoint_point_y.text()))
            crs_src = QgsCoordinateReferenceSystem(self.area_tab.canvas.mapSettings().destinationCrs().authid())
            point = QgsCoordinateTransform(crs_src, self.aoi.crs_dst, QgsProject.instance()).transform(point)
            geometries = json.dumps(json.loads(QgsGeometry.fromPointXY(point).asJson()))
        
        
        payload = {'ndvi_start':plant_start,
                   'ndvi_end': plant_end,
                   'year':'{}'.format(self.vqi_setup_tab.use_esa_tg_year.date().year()),
                   'drought_matrix':self.vqi_setup_tab.dlg_drought_agg.get_agg_as_list()[1],
                   'fire_matrix':self.vqi_setup_tab.dlg_fire_agg.get_agg_as_list()[1],
                   'erosion_matrix':self.vqi_setup_tab.dlg_erosion_agg.get_agg_as_list()[1],
                   'geojsons': geometries,
                   'crs': self.aoi.get_crs_dst_wkt(),
                   'crosses_180th': crosses_180th,
                   'task_name': self.options_tab.task_name.text(),
                   'task_notes': self.options_tab.task_notes.toPlainText()}

        # log("Payload: {}".format(payload))
        resp = run_script(get_script_slug('vegetation-quality'), payload)

        if resp:
            mb.pushMessage(QtWidgets.QApplication.translate("MISLAND", "Submitted"),
                           QtWidgets.QApplication.translate("MISLAND", "Vegetation Quality task submitted to Google Earth Engine."),
                           level=0, duration=5)
        else:
            mb.pushMessage(QtWidgets.QApplication.translate("MISLAND", "Error"),
                           QtWidgets.QApplication.translate("MISLAND", "Unable to submit vegation quality task to Google Earth Engine."),
                           level=0, duration=5)