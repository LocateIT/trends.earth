# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MISLAND - A QGIS plugin
 This plugin supports monitoring and reporting of land degradation to the UNCCD 
 and in support of the SDI Land Degradation Neutrality (LDN) target.
                              -------------------
        begin                : 2017-05-23
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Conservation International
        email                : trends.earth@conservation.org
 ***************************************************************************/
"""

from builtins import range
import os
import json
import tempfile

import numpy as np

#import cProfile

from osgeo import ogr, osr, gdal

import openpyxl
from openpyxl.drawing.image import Image

from qgis.PyQt import QtWidgets, uic, QtXml
from qgis.PyQt.QtCore import QSettings, QDate
from qgis.core import (QgsPointXY, QgsGeometry,
    QgsCoordinateTransform, QgsCoordinateReferenceSystem,QgsProject)

from qgis.utils import iface
mb = iface.messageBar()

from MISLAND import log
from MISLAND.api import run_script
from MISLAND.calculate import DlgCalculateBase, get_script_slug, MaskWorker, \
    json_geom_to_geojson
from MISLAND.layers import add_layer, create_local_json_metadata, get_band_infos, \
    delete_layer_by_filename
from MISLAND.schemas.schemas import BandInfo, BandInfoSchema
from MISLAND.gui.DlgCalculateSDISummaryTableAdmin import Ui_DlgCalculateSDISummaryTableAdmin
from MISLAND.worker import AbstractWorker, StartWorker

class SDIWorker(AbstractWorker):
    def __init__(self, in_f, out_f):
        AbstractWorker.__init__(self)
        self.in_f = in_f
        self.out_f = out_f

    def work(self):
        geom = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'aoi.geojson')
        ds_in = gdal.Open(self.in_f)

        # resample input layers 
        ds_in = gdal.Warp(self.in_f, ds_in,xRes=0.001, yRes=0.001, resampleAlg="bilinear")

        # mask input layers to aoi 
        ds_in = gdal.Warp(self.in_f, ds_in, cutlineDSName =geom, cropToCutline = True, dstNodata = np.nan)


        band_sqi = ds_in.GetRasterBand(1)
        band_vqi = ds_in.GetRasterBand(2)
        band_cqi = ds_in.GetRasterBand(3)
        band_mqi = ds_in.GetRasterBand(4)


        block_sizes = band_sqi.GetBlockSize()
        x_block_size = block_sizes[0]
        y_block_size = block_sizes[1]
        xsize = band_sqi.XSize
        ysize = band_sqi.YSize

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

                a_sqi = band_sqi.ReadAsArray(x, y, cols, rows)
                a_vqi = band_vqi.ReadAsArray(x, y, cols, rows)
                a_cqi = band_cqi.ReadAsArray(x, y, cols, rows)
                a_mqi = band_mqi.ReadAsArray(x, y, cols, rows)

                a_sqi = a_sqi.astype('float64')
                a_vqi = a_vqi.astype('float64')
                a_cqi = a_cqi.astype('float64')
                a_mqi = a_mqi.astype('float64')

                # calculate sensitivity desertification index
                a_sdi = (a_sqi * a_vqi * a_cqi * a_mqi)** (1/4)

                a_sdi[(a_sdi < 1.2)] = 1
                a_sdi[(a_sdi >= 1.2) & (a_sdi < 1.3)] = 2
                a_sdi[(a_sdi >= 1.3) & (a_sdi < 1.4)] = 3
                a_sdi[(a_sdi >= 1.4) & (a_sdi < 1.6)] = 4
                a_sdi[(a_sdi >= 1.6)] = 5
                a_sdi[(a_sqi < 0) | (a_vqi < 0) | (a_cqi < 0) | (a_mqi < 0)] = -32768

                ds_out.GetRasterBand(1).WriteArray(a_sdi, x, y)
   
                blocks += 1
 
        if self.killed:
            os.remove(self.out_f)
            return None
        else:
            return True

class DlgCalculateSDISummaryTableAdmin(DlgCalculateBase, Ui_DlgCalculateSDISummaryTableAdmin):
    def __init__(self, parent=None):
        super(DlgCalculateSDISummaryTableAdmin, self).__init__(parent)

        self.setupUi(self)

    def showEvent(self, event):
        super(DlgCalculateSDISummaryTableAdmin, self).showEvent(event)

        self.combo_layer_sqi.populate()
        self.combo_layer_vqi.populate()
        self.combo_layer_cqi.populate()
        self.combo_layer_mqi.populate()

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
        
    def btn_calculate(self):
        # Note that the super class has several tests in it - if they fail it
        # returns False, which would mean this function should stop execution
        # as well.
        ret = super(DlgCalculateSDISummaryTableAdmin, self).btn_calculate()
        if not ret:
            return

        ######################################################################
        # Check that all needed input layers are selected

        if len(self.combo_layer_sqi.layer_list) == 0:
                QtWidgets.QMessageBox.critical(None, self.tr("Error"),
                                           self.tr("You must add a Soil Quality Indicator layer to your map before you can use the SDI calculation tool."))
                return

        if len(self.combo_layer_vqi.layer_list) == 0:
                QtWidgets.QMessageBox.critical(None, self.tr("Error"),
                                           self.tr("You must add a Vegatation Quality Indicator layer to your map before you can use the SDI calculation tool."))
                return

        if len(self.combo_layer_cqi.layer_list) == 0:
                QtWidgets.QMessageBox.critical(None, self.tr("Error"),
                                           self.tr("You must add a Climate Quality Indicator layer to your map before you can use the SDI calculation tool."))
                return

        if len(self.combo_layer_mqi.layer_list) == 0:
                QtWidgets.QMessageBox.critical(None, self.tr("Error"),
                                           self.tr("You must add a Management Quality Indicator layer to your map before you can use the SDI calculation tool."))
                return

        #######################################################################
        # Check that the layers cover the full extent needed
        if self.aoi.calc_frac_overlap(QgsGeometry.fromRect(self.combo_layer_sqi.get_layer().extent())) < .99:
                QtWidgets.QMessageBox.critical(None, self.tr("Error"),
                                           self.tr("Area of interest is not entirely within the Soil Quality Indicator layer."))
                return

        if self.aoi.calc_frac_overlap(QgsGeometry.fromRect(self.combo_layer_vqi.get_layer().extent())) < .99:
                QtWidgets.QMessageBox.critical(None, self.tr("Error"),
                                           self.tr("Area of interest is not entirely within the Vegetation Quality Indicator layer."))
                return

        if self.aoi.calc_frac_overlap(QgsGeometry.fromRect(self.combo_layer_cqi.get_layer().extent())) < .99:
                QtWidgets.QMessageBox.critical(None, self.tr("Error"),
                                           self.tr("Area of interest is not entirely within the Climate Quality Indicator layer."))
                return

        if self.aoi.calc_frac_overlap(QgsGeometry.fromRect(self.combo_layer_mqi.get_layer().extent())) < .99:
                QtWidgets.QMessageBox.critical(None, self.tr("Error"),
                                           self.tr("Area of interest is not entirely within the Management Quality Indicator layer."))
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


        #######################################################################
        # Load all datasets to VRTs (to select only the needed bands)

        sqi_vrt = self.combo_layer_sqi.get_vrt()
        vqi_vrt = self.combo_layer_vqi.get_vrt()
        cqi_vrt = self.combo_layer_cqi.get_vrt()
        mqi_vrt = self.combo_layer_mqi.get_vrt()

        # Add the custom layers to a VRT in case they don't match in resolution, 
        # and set proper output bounds
        in_vrt = tempfile.NamedTemporaryFile(suffix='.vrt').name
        gdal.BuildVRT(in_vrt,
                      [sqi_vrt, vqi_vrt, cqi_vrt, mqi_vrt], 
                      resolution='highest', 
                      resampleAlg=gdal.GRA_NearestNeighbour,
                      outputBounds=self.aoi.get_aligned_output_bounds_deprecated(sqi_vrt),
                      separate=True)

        lc_change_worker = StartWorker(SDIWorker,
                                       'calculating Sensitivity Desertification index', in_vrt, 
                                       out_f)
        if not lc_change_worker.success:
            QtWidgets.QMessageBox.critical(None, self.tr("Error"),
                                       self.tr("Error calculating Sensitivity Desertification index."), None)
            return

        band_info = [BandInfo("Sensitivity Desertification Index", add_to_map=True)]
        out_json = os.path.splitext(out_f)[0] + '.json'
        create_local_json_metadata(out_json, out_f, band_info)
        schema = BandInfoSchema()
        for band_number in range(len(band_info)):
            b = schema.dump(band_info[band_number])
            if b['add_to_map']:
                # The +1 is because band numbers start at 1, not zero
                add_layer(out_f, band_number + 1, b)

        