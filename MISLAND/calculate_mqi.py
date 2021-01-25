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

        self.mqi_setup_tab = mqi_setup_widget
        self.TabBox.insertTab(0, self.mqi_setup_tab, self.tr('Management Quality Index Setup'))

        if self.reset_tab_on_showEvent:
            self.TabBox.setCurrentIndex(0)

    def btn_cancel(self):
        self.close()

    def btn_calculate(self):

        ret = super(DlgCalculateMQI, self).btn_calculate()
        if not ret:
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
        
        payload = {'year':self.mqi_setup_tab.use_esa_tg_year.date().year(),
                   'lu_matrix':self.mqi_setup_tab.dlg_lu_agg.get_agg_as_list()[1],
                   'geojsons': geometries,
                   'crs': self.aoi.get_crs_dst_wkt(),
                   'crosses_180th': crosses_180th,
                   'task_name': self.options_tab.task_name.text(),
                   'task_notes': self.options_tab.task_notes.toPlainText()}

        resp = run_script(get_script_slug('management-quality'), payload)

        if resp:
            mb.pushMessage(QtWidgets.QApplication.translate("MISLAND", "Submitted"),
                           QtWidgets.QApplication.translate("MISLAND", "Management Quality task submitted to Google Earth Engine."),
                           level=0, duration=5)
        else:
            mb.pushMessage(QtWidgets.QApplication.translate("MISLAND", "Error"),
                           QtWidgets.QApplication.translate("MISLAND", "Unable to submit management quality task to Google Earth Engine."),
                           level=0, duration=5)