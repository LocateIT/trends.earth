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
import numpy as np

from zipfile import ZipFile
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import QSettings

from osgeo import gdal, osr,ogr
from qgis.PyQt import QtWidgets
from qgis.core import (QgsPointXY, QgsGeometry,
    QgsCoordinateTransform, QgsCoordinateReferenceSystem, QgsProject)

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

class SoilQualityWorker(AbstractWorker):
    def __init__(self,depth, in_f, out_f):
        AbstractWorker.__init__(self)
        self.depth = depth
        self.in_f = in_f
        self.out_f = out_f

    def work(self):
        geom = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'aoi.geojson')
        ds_in = gdal.Open(self.in_f)

        # resample input layers 
        ds_in = gdal.Warp(self.in_f, ds_in,xRes=0.001, yRes=0.001, resampleAlg="bilinear")

        # mask input layers to aoi 
        ds_in = gdal.Warp(self.in_f, ds_in, cutlineDSName =geom, cropToCutline = True, dstNodata = np.nan)


        band_pm  = ds_in.GetRasterBand(1)
        band_rock_frag = ds_in.GetRasterBand(2)
        band_texture = ds_in.GetRasterBand(3)
        band_drainage = ds_in.GetRasterBand(4)
        band_default_slope = ds_in.GetRasterBand(5)

        if self.depth<15:
            depthIndex = 4
        elif self.depth>=15 and self.depth<30:
            depthIndex = 3
        elif self.depth>=30 and self.depth<75:
            depthIndex = 2
        elif self.depth>=75:
            depthIndex = 1
        else:
            log("Unexpected depth value")

        block_sizes = band_pm.GetBlockSize()
        x_block_size = block_sizes[0]
        y_block_size = block_sizes[1]
        xsize = band_pm.XSize
        ysize = band_pm.YSize

        driver = gdal.GetDriverByName("GTiff")
        ds_out = driver.Create(self.out_f, xsize, ysize, 1, gdal.GDT_Float64, 
                               ['COMPRESS=LZW'])

        src_gt = ds_in.GetGeoTransform()
        ds_out.SetGeoTransform(src_gt)
        out_srs = osr.SpatialReference()
        out_srs.ImportFromWkt(ds_in.GetProjectionRef())
        ds_out.SetProjection(out_srs.ExportToWkt())

        blocks = 0
        for y in range(0, ysize, y_block_size):
            if y + y_block_size < ysize:
                rows = y_block_size
            else:
                rows = ysize - y
            for x in range(0, xsize, x_block_size):
                if self.killed:
                    log("Processing killed by user after processing {} out of {} blocks.".format(y, ysize))
                    break
                self.progress.emit(100 * (float(y) + (float(x)/xsize)*y_block_size) / ysize)
                if x + x_block_size < xsize:
                    cols = x_block_size
                else:
                    cols = xsize - x

                # TODO: USE FIXED RECLASIFFIED SLOPE TIFF FILE 
                a_pm = band_pm.ReadAsArray(x, y, cols, rows)
                a_rock_frag = band_rock_frag.ReadAsArray(x, y, cols, rows)
                a_slope = band_default_slope.ReadAsArray(x, y, cols, rows)
                a_texture = band_texture.ReadAsArray(x, y, cols, rows)
                a_drainage = band_drainage.ReadAsArray(x, y, cols, rows)

                a_pm = a_pm.astype('float64')
                a_rock_frag = a_rock_frag.astype('float64')
                a_slope = a_slope.astype('float64')
                a_texture = a_texture.astype('float64')
                a_drainage = a_drainage.astype('float64')

                a_sqi = (a_pm*a_rock_frag*a_slope*a_texture*a_drainage*depthIndex)**(1/6)


                a_sqi[(a_sqi < 1.13)] = 1
                a_sqi[(a_sqi >= 1.13) & (a_sqi <= 1.46)] = 2
                a_sqi[(a_sqi > 1.46)] = 3
                
                a_sqi[(a_pm < 0) | (a_rock_frag < 0) | (a_slope < 0) | (a_texture < 0) | (a_drainage < 0)] = -32768

                ds_out.GetRasterBand(1).WriteArray(a_sqi, x, y)

                blocks += 1
        if self.killed:
            os.remove(self.out_f)
            return None
        else:
            return True

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
        self.sqi_setup_tab.use_custom.show()
        self.sqi_setup_tab.groupBox_rock_fragm.show()
        self.sqi_setup_tab.groupBox_texture.show()
        self.sqi_setup_tab.groupBox_drainage.show()
        self.sqi_setup_tab.groupBox_pm.show()
        
        # This box may have been hidden if this widget was last shown on the 
        # SDG one step dialog
        self.sqi_setup_tab.groupBox_usda_depth.show()

        if self.reset_tab_on_showEvent:
            self.TabBox.setCurrentIndex(0)

        self.sqi_setup_tab.use_custom_pm.populate()
        self.sqi_setup_tab.use_custom_drainage.populate()
        self.sqi_setup_tab.use_custom_texture.populate()
        self.sqi_setup_tab.use_custom_rock_frag.populate()

    def btn_calculate(self):

        ret = super(DlgCalculateSQI, self).btn_calculate()
        if not ret:
            return

        if self.sqi_setup_tab.use_default.isChecked():
            self.calculate_on_GEE()
        else:
            self.calculate_locally()

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
        
        payload = {
                    'depth': self.sqi_setup_tab.use_depth.value(),
                    'geojsons': geometries,
                    'crosses_180th': crosses_180th,
                    'crs': self.aoi.get_crs_dst_wkt(),
                    'texture_matrix':self.sqi_setup_tab.dlg_texture_agg.get_agg_as_list()[1],
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

    def get_save_raster(self):
        raster_file, _ = QtWidgets.QFileDialog.getSaveFileName(self,
                                                            self.tr('Choose a name for the output file'),
                                                            QSettings().value("MISLAND/output_dir", None),
                                                            self.tr('Raster file (*.tif)'))
        if raster_file:
            if os.access(os.path.dirname(raster_file), os.W_OK):
                QSettings().setValue("MISLAND/output_dir", os.path.dirname(raster_file))
                return raster_file
            else:
                QtWidgets.QMessageBox.critical(None, self.tr("Error"),
                                        self.tr(u"Cannot write to {}. Choose a different file.".format(raster_file)))
                return False
        
    def calculate_locally(self):
        if not self.sqi_setup_tab.use_custom.isChecked():
            QtWidgets.QMessageBox.critical(None, self.tr("Error"),
                                       self.tr("Due to the options you have chosen, this calculation must occur offline. You MUST select a custom land cover dataset."))
            return
            
        if len(self.sqi_setup_tab.use_custom_pm.layer_list) == 0:
            QtWidgets.QMessageBox.critical(None, self.tr("Error"),
                                       self.tr("You must add an parent material layer to your map before you can run the calculation."))
            return

        if len(self.sqi_setup_tab.use_custom_rock_frag.layer_list) == 0:
            QtWidgets.QMessageBox.critical(None, self.tr("Error"),
                                       self.tr("You must add a rock fragment layer to your map before you can run the calculation."))
            return
        
        if len(self.sqi_setup_tab.use_custom_texture.layer_list) == 0:
            QtWidgets.QMessageBox.critical(None, self.tr("Error"),
                                       self.tr("You must add a soil texture layer to your map before you can run the calculation."))
            return

        if len(self.sqi_setup_tab.use_custom_drainage.layer_list) == 0:
            QtWidgets.QMessageBox.critical(None, self.tr("Error"),
                                       self.tr("You must add a drainage layer to your map before you can run the calculation."))
            return

        # select the parent material, slope, soil texture, drainage and rock fragment datasets 
        pm_vrt = self.sqi_setup_tab.use_custom_pm.get_vrt()
        drainage_vrt = self.sqi_setup_tab.use_custom_drainage.get_vrt()
        texture_vrt = self.sqi_setup_tab.use_custom_texture.get_vrt()
        rock_frag_vrt = self.sqi_setup_tab.use_custom_rock_frag.get_vrt()

        soil_depth = self.sqi_setup_tab.use_depth.value()

        if self.aoi.calc_frac_overlap(QgsGeometry.fromRect(self.sqi_setup_tab.use_custom_pm.get_layer().extent())) < .99:
            QtWidgets.QMessageBox.critical(None, self.tr("Error"),
                                       self.tr("Area of interest is not entirely within the parent material layer."))
            return

        if self.aoi.calc_frac_overlap(QgsGeometry.fromRect(self.sqi_setup_tab.use_custom_drainage.get_layer().extent())) < .99:
            QtWidgets.QMessageBox.critical(None, self.tr("Error"),
                                       self.tr("Area of interest is not entirely within the drainage layer."))
            return
        if self.aoi.calc_frac_overlap(QgsGeometry.fromRect(self.sqi_setup_tab.use_custom_rock_frag.get_layer().extent())) < .99:
            QtWidgets.QMessageBox.critical(None, self.tr("Error"),
                                       self.tr("Area of interest is not entirely within the rock fragment layer."))
            return

        if self.aoi.calc_frac_overlap(QgsGeometry.fromRect(self.sqi_setup_tab.use_custom_texture.get_layer().extent())) < .99:
            QtWidgets.QMessageBox.critical(None, self.tr("Error"),
                                       self.tr("Area of interest is not entirely within the soil texture layer."))
            return

        out_f = self.get_save_raster()
        if not out_f:
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
            geometries = {
                "coordinates":coords,
                "type":"Polygon"
            }
        elif self.area_tab.area_fromadmin.isChecked():
            geometries ={
                "coordinates":self.get_admin_poly_geojson()['geometry']['coordinates'][0],
                "type":"Polygon"
            }
        elif self.area_tab.area_frompoint.isChecked():
            point = QgsPointXY(float(self.area_tab.area_frompoint_point_x.text()), float(self.area_tab.area_frompoint_point_y.text()))
            crs_src = QgsCoordinateReferenceSystem(self.area_tab.canvas.mapSettings().destinationCrs().authid())
            point = QgsCoordinateTransform(crs_src, self.aoi.crs_dst, QgsProject.instance()).transform(point)
            geometries = json.loads(QgsGeometry.fromPointXY(point).asJson())

        # write aoi geometry to file for masking output
        aoi_geom = {
            "type": "FeatureCollection",
            "features": [
                {
                "type": "Feature",
                "properties": {},
                "geometry": geometries
                }
            ]
        }

        aoi_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'aoi.geojson')
        with open(aoi_file, 'w') as filetowrite:
            filetowrite.write(json.dumps(aoi_geom))

        # Add the sqi layers to a VRT in case they don't match in resolution, 
        # and set proper output bounds
        sqi_files = [pm_vrt, texture_vrt, drainage_vrt, rock_frag_vrt]
        # in_vrt = tempfile.NamedTemporaryFile(suffix='.vrt').name
        sqi_vrts = []

        for i in range(len(sqi_files)):
            f = tempfile.NamedTemporaryFile(suffix='.vrt').name
            gdal.BuildVRT(f,
                        sqi_files[i], 
                        bandList=[i + 1],
                        resolution='highest', 
                        resampleAlg=gdal.GRA_NearestNeighbour,
                        outputBounds=self.aoi.get_aligned_output_bounds_deprecated(texture_vrt),
                        separate=True)

            sqi_vrts.append(f)

        slope_v = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'slope.tif')

        if not os.path.exists(slope_v):
            slope_zip = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'slope.zip')
            slope_unzip = ZipFile(slope_zip)
            slope_unzip.extractall(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data'))

            slope_unzip.close()
            log("Extracting slope file...")

        else:
            log("Slope.tif already exists")

        in_files = [slope_v]
        in_files.extend(sqi_vrts)
        in_vrt = tempfile.NamedTemporaryFile(suffix='.vrt').name
        log(u'Saving SQI input files to {}'.format(in_vrt))

        gdal.BuildVRT(in_vrt,
                        in_files, 
                        resolution='highest', 
                        resampleAlg=gdal.GRA_NearestNeighbour,
                        outputBounds=self.aoi.get_aligned_output_bounds_deprecated(texture_vrt),
                        separate=True)

        # sqi_band_nums = np.arange(len(lc_files)) + 6

        sqi_worker = StartWorker(SoilQualityWorker,
                                       'calculating soil quality index', soil_depth, in_vrt, 
                                       out_f )

        if not sqi_worker.success:
            QtWidgets.QMessageBox.critical(None, self.tr("Error"),
                                       self.tr("Error calculating soil quality index."), None)
            return

        band_info = [BandInfo("Soil Quality Index (cm deep)", add_to_map=True, metadata={'depth': soil_depth})]
        out_json = os.path.splitext(out_f)[0] + '.json'
        create_local_json_metadata(out_json, out_f, band_info)
        schema = BandInfoSchema()
        for band_number in range(len(band_info)):
            b = schema.dump(band_info[band_number])
            if b['add_to_map']:
                # The +1 is because band numbers start at 1, not zero
                add_layer(out_f, band_number + 1, b)

        

