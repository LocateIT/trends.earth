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

from LDMP import log
from LDMP.calculate import DlgCalculateBase, get_script_slug
from LDMP.gui.DlgCalculateCQI import Ui_DlgCalculateCQI
from LDMP.api import run_script
from LDMP.cqi_setup import cqi_setup_widget
from LDMP.schemas.schemas import BandInfo, BandInfoSchema
from LDMP.layers import create_local_json_metadata, add_layer
from LDMP.worker import AbstractWorker, StartWorker

class ClimateQualityWorker(AbstractWorker):
    def __init__(self, in_f, out_f):
        AbstractWorker.__init__(self)
        self.in_f = in_f
        self.out_f = out_f

    def work(self):
        ds_in = gdal.Open(self.in_f)

        band_prec = ds_in.GetRasterBand(1)
        band_pet = ds_in.GetRasterBand(2)


        block_sizes = band_prec.GetBlockSize()
        x_block_size = block_sizes[0]
        y_block_size = block_sizes[1]
        xsize = band_prec.XSize
        ysize = band_prec.YSize

        driver = gdal.GetDriverByName("GTiff")
        ds_out = driver.Create(self.out_f, xsize, ysize, 4, gdal.GDT_Int16, 
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

                a_prec = band_prec.ReadAsArray(x, y, cols, rows)
                a_pet = band_pet.ReadAsArray(x, y, cols, rows)

                # calculate aridity index 
                a_cqi = a_prec/a_pet
                a_cqi[(a_prec < 1) | (a_pet < 1)] <- -32768

                ds_out.GetRasterBand(1).WriteArray(a_prec, x, y)
                ds_out.GetRasterBand(2).WriteArray(a_pet, x, y)
                ds_out.GetRasterBand(3).WriteArray(a_cqi, x, y)

                blocks += 1

            
        if self.killed:
            os.remove(out_file)
            return None
        else:
            return True


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
        # self.cqi_setup_tab.use_custom.show()
        # self.cqi_setup_tab.groupBox_custom_prec.show()
        # self.cqi_setup_tab.groupBox_custom_pet.show()

        # This box may have been hidden if this widget was last shown on the 
        # SDG one step dialog
        self.cqi_setup_tab.groupBox_terra_period.show()

        if self.reset_tab_on_showEvent:
            self.TabBox.setCurrentIndex(0)

        # precipitation and potential evapotranspiration custom input layers
        # self.cqi_setup_tab.use_custom_prec.populate()
        # self.cqi_setup_tab.use_custom_pet.populate()

    def btn_calculate(self):

        ret = super(DlgCalculateCQI, self).btn_calculate()
        if not ret:
            return

        if self.cqi_setup_tab.use_terra.isChecked():
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
                    'year': self.cqi_setup_tab.use_terra_year.date().year(),
                    'geojsons': geometries,
                    'crosses_180th': crosses_180th,
                    'crs': self.aoi.get_crs_dst_wkt(),
                    'task_name': self.options_tab.task_name.text(),
                    'task_notes': self.options_tab.task_notes.toPlainText()}

        resp = run_script(get_script_slug('climate-quality'), payload)

        if resp:
            mb.pushMessage(QtWidgets.QApplication.translate("LDMP", "Submitted"),
                           QtWidgets.QApplication.translate("LDMP", "Climate quality task submitted to Google Earth Engine."),
                           level=0, duration=5)
        else:
            mb.pushMessage(QtWidgets.QApplication.translate("LDMP", "Error"),
                           QtWidgets.QApplication.translate("LDMP", "Unable to submit climate quality task to Google Earth Engine."),
                           level=0, duration=5)

    def get_save_raster(self):
        raster_file, _ = QtWidgets.QFileDialog.getSaveFileName(self,
                                                        self.tr('Choose a name for the output file'),
                                                        QSettings().value("LDMP/output_dir", None),
                                                        self.tr('Raster file (*.tif)'))
        if raster_file:
            if os.access(os.path.dirname(raster_file), os.W_OK):
                QSettings().setValue("LDMP/output_dir", os.path.dirname(raster_file))
                return raster_file
            else:
                QtWidgets.QMessageBox.critical(None, self.tr("Error"),
                                           self.tr(u"Cannot write to {}. Choose a different file.".format(raster_file)))
                return False
                
    def calculate_locally(self):
        if not self.cqi_setup_tab.use_custom.isChecked():
            QtWidgets.QMessageBox.critical(None, self.tr("Error"),
                                       self.tr("Due to the options you have chosen, this calculation must occur offline. You MUST select a custom precipitation or evapotranspiration layer dataset."))
            return
        if len(self.cqi_setup_tab.use_custom_prec.layer_list) == 0:
            QtWidgets.QMessageBox.critical(None, self.tr("Error"),
                                       self.tr("You must add a yearly mean precipitation layer to your map before you can run the calculation."), None)
            return

        if len(self.cqi_setup_tab.use_custom_pet.layer_list) == 0:
            QtWidgets.QMessageBox.critical(None, self.tr("Error"),
                                       self.tr("You must add mean potential evapotranspiration layer to your map before you can run the calculation."), None)
            return

        # Select the initial and final bands from initial and final datasets 
        # (in case there is more than one lc band per dataset)
        custom_prec_vrt = self.cqi_setup_tab.use_custom_prec.get_vrt()
        custom_pet_vrt = self.cqi_setup_tab.use_custom_pet.get_vrt()

        # if self.aoi.calc_frac_overlap(QgsGeometry.fromRect(self.cqi_setup_tab.use_custom_prec.get_layer().extent())) < .99:
        #     QtWidgets.QMessageBox.critical(None, self.tr("Error"),
        #                                self.tr("Area of interest is not entirely within the precipitation layer."), None)
        #     return

        # if self.aoi.calc_frac_overlap(QgsGeometry.fromRect(self.cqi_setup_tab.use_custom_pet.get_layer().extent())) < .99:
        #     QtWidgets.QMessageBox.critical(None, self.tr("Error"),
        #                                self.tr("Area of interest is not entirely within the potential evapotranspiration layer."), None)
        #     return

        out_f = self.get_save_raster()
        if not out_f:
            return

        self.close()

        # Add the custom layers to a VRT in case they don't match in resolution, 
        # and set proper output bounds
        in_vrt = tempfile.NamedTemporaryFile(suffix='.vrt').name
        gdal.BuildVRT(in_vrt,
                      [custom_prec_vrt, custom_pet_vrt], 
                      resolution='highest', 
                      resampleAlg=gdal.GRA_NearestNeighbour,
                      outputBounds=self.aoi.get_aligned_output_bounds_deprecated(custom_prec_vrt),
                      separate=True)

        #TODO : Fix this 
        lc_change_worker = StartWorker(ClimateQualityWorker,
                                       'calculating land cover change', in_vrt, 
                                       out_f)
        if not lc_change_worker.success:
            QtWidgets.QMessageBox.critical(None, self.tr("Error"),
                                       self.tr("Error calculating land cover change."), None)
            return

        band_info = [BandInfo("Aridity Index", add_to_map=True)]
        out_json = os.path.splitext(out_f)[0] + '.json'
        create_local_json_metadata(out_json, out_f, band_info)
        schema = BandInfoSchema()
        for band_number in range(len(band_info)):
            b = schema.dump(band_info[band_number])
            if b['add_to_map']:
                # The +1 is because band numbers start at 1, not zero
                add_layer(out_f, band_number + 1, b)

        

