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
from MISLAND.gui.DlgCalculateProd import Ui_DlgCalculateProd as UiDialog
from MISLAND.api import run_script


class DlgCalculateSQI(DlgCalculateBase, UiDialog):
    def __init__(self, parent=None):
        """Constructor."""
        super(DlgCalculateSQI, self).__init__(parent)

        self.setupUi(self)

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
import tempfile

from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import QSettings

from osgeo import gdal, osr,ogr
from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtCore import QDate
from qgis.core import (QgsFeature, QgsPointXY, QgsGeometry, QgsJsonUtils,
    QgsVectorLayer, QgsCoordinateTransform, QgsCoordinateReferenceSystem,
    Qgis, QgsProject, QgsLayerTreeGroup, QgsLayerTreeLayer,
    QgsVectorFileWriter, QgsFields, QgsWkbTypes, QgsAbstractGeometrySimplifier)

from qgis.core import QgsGeometry
from qgis.utils import iface
mb = iface.messageBar()

from MISLAND import log
from MISLAND.calculate import DlgCalculateBase, get_script_slug
from MISLAND.gui.DlgCalculateSQI import Ui_DlgCalculateSQI
from MISLAND.api import run_script
from MISLAND.sqi_setup import sqi_setup_widget
from MISLAND.schemas.schemas import BandInfo, BandInfoSchema
from MISLAND.layers import create_local_json_metadata, add_layer
from MISLAND.worker import AbstractWorker, StartWorker


class DlgCalculateSQI(DlgCalculateBase, Ui_DlgCalculateSQI):
    def __init__(self, parent=None):
        """Constructor."""
        super(DlgCalculateSQI, self).__init__(parent)

        self.setupUi(self)

    def showEvent(self, event):
        super(DlgCalculateSQI, self).showEvent(event)

        self.sqi_setup_tab = sqi_setup_widget
        self.TabBox.insertTab(0, self.sqi_setup_tab, self.tr('Soil Quality Index Setup'))

        # These boxes may have been hidden if this widget was last shown on the 
        # SDG one step dialog
        self.sqi_setup_tab.groupBox_usda_depth.show()
        # self.cqi_setup_tab.use_custom.show()
        self.sqi_setup_tab.groupBox_rock_fragm.show()
        self.sqi_setup_tab.groupBox_slope.show()
        self.sqi_setup_tab.groupBox_texture.show()
        self.sqi_setup_tab.groupBox_drainage.show()
        self.sqi_setup_tab.groupBox_pm.show()
        
        # self.cqi_setup_tab.groupBox_custom_prec.show()
        # self.cqi_setup_tab.groupBox_custom_pet.show()

        # This box may have been hidden if this widget was last shown on the 
        # SDG one step dialog
        # self.sqi_setup_tab.groupBox_usda_depth.show()

        if self.reset_tab_on_showEvent:
            self.TabBox.setCurrentIndex(0)

    def btn_calculate(self):

        ret = super(DlgCalculateSQI, self).btn_calculate()
        if not ret:
            return

        self.calculate_on_GEE()


    def calculate_on_GEE(self):
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
        
        log('{}'.format(self.sqi_setup_tab.use_depth.value()))

        payload = {
                    'depth': self.sqi_setup_tab.use_depth.value(),
                    'geojsons': geometries,
                    'crosses_180th': crosses_180th,
                    'crs': self.aoi.get_crs_dst_wkt(),
                    'texture_matrix':self.sqi_setup_tab.dlg_texture_agg.get_agg_as_list()[1],
                    'pmaterial_matrix':self.sqi_setup_tab.dlg_pm_agg.get_agg_as_list()[1],
                    'task_name': self.options_tab.task_name.text(),
                    'task_notes': self.options_tab.task_notes.toPlainText()}

        resp = run_script(get_script_slug('soil-quality'), payload)

        if resp:
            mb.pushMessage(QtWidgets.QApplication.translate("MISLAND", "Submitted"),
                           QtWidgets.QApplication.translate("MISLAND", "Soil quality task submitted to Google Earth Engine."),
                           level=0, duration=5)
        else:
            mb.pushMessage(QtWidgets.QApplication.translate("MISLAND", "Error"),
                           QtWidgets.QApplication.translate("MISLAND", "Unable to submit climate quality task to Google Earth Engine."),
                           level=0, duration=5)

                

        

