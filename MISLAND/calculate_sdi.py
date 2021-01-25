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

from qgis.core import QgsGeometry
from qgis.utils import iface
mb = iface.messageBar()

from MISLAND import log
from MISLAND.api import run_script
from MISLAND.calculate import DlgCalculateBase, get_script_slug, MaskWorker, \
    json_geom_to_geojson
from MISLAND.lc_setup import lc_setup_widget, lc_define_deg_widget
from MISLAND.layers import add_layer, create_local_json_metadata, get_band_infos, \
    delete_layer_by_filename
from MISLAND.schemas.schemas import BandInfo, BandInfoSchema
from MISLAND.gui.DlgCalculateSDISummaryTableAdmin import Ui_DlgCalculateSDISummaryTableAdmin
from MISLAND.worker import AbstractWorker, StartWorker
from MISLAND.summary import *
from MISLAND.summary_numba import merge_xtabs, xtab

from MISLAND.calculate_numba import ldn_make_prod5, ldn_recode_state, \
    ldn_recode_traj, ldn_total_by_trans, ldn_total_deg


class DlgCalculateSDISummaryTableAdmin(DlgCalculateBase, Ui_DlgCalculateSDISummaryTableAdmin):
    def __init__(self, parent=None):
        super(DlgCalculateSDISummaryTableAdmin, self).__init__(parent)

        self.setupUi(self)

        self.browse_output_file_layer.clicked.connect(self.select_output_file_layer)
        self.browse_output_file_table.clicked.connect(self.select_output_file_table)


    def showEvent(self, event):
        super(DlgCalculateSDISummaryTableAdmin, self).showEvent(event)

        self.combo_layer_sqi.populate()
        self.combo_layer_vqi.populate()
        self.combo_layer_cqi.populate()
        self.combo_layer_mqi.populate()

    def select_output_file_layer(self):
        f, _ = QtWidgets.QFileDialog.getSaveFileName(self,
                                              self.tr('Choose a filename for the output file'),
                                              QSettings().value("MISLAND/output_dir", None),
                                              self.tr('Filename (*.json)'))
        if f:
            if os.access(os.path.dirname(f), os.W_OK):
                QSettings().setValue("MISLAND/output_dir", os.path.dirname(f))
                self.output_file_layer.setText(f)
            else:
                QtWidgets.QMessageBox.critical(None, self.tr("Error"),
                                           self.tr(u"Cannot write to {}. Choose a different file.".format(f)))

    def select_output_file_table(self):
        f, _ = QtWidgets.QFileDialog.getSaveFileName(self,
                                              self.tr('Choose a filename for the summary table'),
                                              QSettings().value("MISLAND/output_dir", None),
                                              self.tr('Summary table file (*.xlsx)'))
        if f:
            if os.access(os.path.dirname(f), os.W_OK):
                QSettings().setValue("MISLAND/output_dir", os.path.dirname(f))
                self.output_file_table.setText(f)
            else:
                QtWidgets.QMessageBox.critical(None, self.tr("Error"),
                                           self.tr(u"Cannot write to {}. Choose a different file.".format(f)))
