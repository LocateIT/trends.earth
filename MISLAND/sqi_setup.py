
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
from MISLAND.gui.WidgetSQISetup import Ui_WidgetSQISetup

class SQISetupWidget(QtWidgets.QWidget, Ui_WidgetSQISetup):
    def __init__(self, parent=None):
        super(SQISetupWidget, self).__init__(parent)

        self.setupUi(self)

        self.use_usda.toggled.connect(self.Sqi_source_changed)
        # self.use_custom.toggled.connect(self.cqi_source_changed)

        self.Sqi_source_changed()


    def Sqi_source_changed(self):
        if self.use_usda.isChecked():
            self.groupBox_usda_depth.setEnabled(True)


sqi_setup_widget = SQISetupWidget()