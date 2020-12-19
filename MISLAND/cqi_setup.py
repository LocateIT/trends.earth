
from builtins import str
from builtins import range
import os
import json

from qgis.PyQt import QtWidgets
from qgis.PyQt.QtGui import QRegExpValidator, QFont, QPainter, QLinearGradient, \
    QColor
from qgis.PyQt.QtCore import QSettings, QDate, Qt, QSize, QAbstractTableModel, \
    QRegExp, QJsonValue, QSortFilterProxyModel

from qgis.utils import iface
mb = iface.messageBar()

from MISLAND import log
from MISLAND.gui.WidgetCQISetup import Ui_WidgetCQISetup

class CQISetupWidget(QtWidgets.QWidget, Ui_WidgetCQISetup):
    def __init__(self, parent=None):
        super(CQISetupWidget, self).__init__(parent)

        self.setupUi(self)

        self.use_terra.toggled.connect(self.cqi_source_changed)
        self.use_custom.toggled.connect(self.cqi_source_changed)

        self.cqi_source_changed()


    def cqi_source_changed(self):
        if self.use_terra.isChecked():
            self.groupBox_terra_period.setEnabled(True)
            self.groupBox_custom_pet.setEnabled(False)
            self.groupBox_custom_prec.setEnabled(False)
        elif self.use_custom.isChecked():
            self.groupBox_terra_period.setEnabled(False)
            self.groupBox_custom_pet.setEnabled(True)
            self.groupBox_custom_prec.setEnabled(True)

cqi_setup_widget = CQISetupWidget()