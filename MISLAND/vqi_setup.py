
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
from MISLAND.gui.WidgetVQISetup import Ui_WidgetVQISetup
from MISLAND.gui.DlgCalculateLCSetAggregation import Ui_DlgCalculateLCSetAggregation


class AggTableModel(QAbstractTableModel):
    def __init__(self, datain, parent=None, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.classes = datain
        
        # Column names as tuples with json name in [0], pretty name in [1]
        # Note that the columns with json names set to to INVALID aren't loaded
        # into the shell, but shown from a widget.
        colname_tuples = [('Initial_Code', QtWidgets.QApplication.translate('DlgCalculateSetAggregation', 'Input code')),
                          ('Initial_Label', QtWidgets.QApplication.translate('DlgCalculateSetAggregation', 'Input class')),
                          ('Final_Label', QtWidgets.QApplication.translate('DlgCalculateSetAggregation', 'Output class'))]
        self.colnames_json = [x[0] for x in colname_tuples]
        self.colnames_pretty = [x[1] for x in colname_tuples]

    def rowCount(self, parent):
        return len(self.classes)

    def columnCount(self, parent):
        return len(self.colnames_json)

    def data(self, index, role):
        if not index.isValid():
            return None
        elif role != Qt.DisplayRole:
            return None
        return self.classes[index.row()].get(self.colnames_json[index.column()], '')

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.colnames_pretty[section]
        return QAbstractTableModel.headerData(self, section, orientation, role)


# Function to read a file defining soil quality aggegation
def read_class_file(f):
    if not os.access(f, os.R_OK):
        QtWidgets.QMessageBox.critical(None,
                QtWidgets.QApplication.translate("Error"),
                QtWidgets.QApplication.translate(u"Cannot read {}.".format(f), None))
        return None

    with open(f) as class_file:
        classes = json.load(class_file)
    if (not isinstance(classes, list)
            or not len(classes) > 0
            or not isinstance(classes[0], dict)
            or 'Initial_Code' not in classes[0]
            or 'Final_Code' not in classes[0]
            or 'Final_Label' not in classes[0]):

        QtWidgets.QMessageBox.critical(None,
                                   QtWidgets.QApplication.translate('DlgCalculateSetAggregation', "Error"),
                                   QtWidgets.QApplication.translate('DlgCalculateSetAggregation',
                                                                u"{} does not appear to contain a valid class definition.".format(f)))
        return None
    else:
        log(u'Loaded class definition from {}'.format(f))
        return classes


class DlgCalculateSetAggregation(QtWidgets.QDialog, Ui_DlgCalculateLCSetAggregation):
    def __init__(self, default_classes, final_classes, parent=None):
        super(DlgCalculateSetAggregation, self).__init__(parent)

        self.default_classes = default_classes
        self.final_classes = final_classes
        self.setupUi(self)
        
        self.btn_save.clicked.connect(self.btn_save_pressed)
        self.btn_load.clicked.connect(self.btn_load_pressed)
        self.btn_reset.clicked.connect(self.reset_class_table)
        self.btn_close.clicked.connect(self.btn_close_pressed)

        # Setup the class table so that the table is defined when a user first 
        # loads the dialog
        self.reset_class_table()

    def btn_close_pressed(self):
        self.close()

    def btn_load_pressed(self):
        f, _ = QtWidgets.QFileDialog.getOpenFileName(self,
                                              self.tr('Select a definition file'),
                                              QSettings().value("MISLAND/lc_deNonef_dir", ),
                                              self.tr('Management Quality definition (*.json)'))
        if f:
            if os.access(f, os.R_OK):
                QSettings().setValue("MISLAND/st_def_dir", os.path.dirname(f))
            else:
                QtWidgets.QMessageBox.critical(None, self.tr("Error"),
                                           self.tr(u"Cannot read {}. Choose a different file.".format(f), None))
        else:
            return
        classes = read_class_file(f)

        if classes:
            self.setup_class_table(classes)

    def btn_save_pressed(self):
        f, _ = QtWidgets.QFileDialog.getSaveFileName(self,
                                              QtWidgets.QApplication.translate('DlgCalculateSetAggregation',
                                                                           'Choose where to save this definition'),
                                              QSettings().value("MISLAND/st_def_dir", None),
                                              QtWidgets.QApplication.translate('DlgCalculateSetAggregation',
                                                                           'Management Quality definition (*.json)'))
        if f:
            if os.access(os.path.dirname(f), os.W_OK):
                QSettings().setValue("MISLAND/st_def_dir", os.path.dirname(f))
            else:
                QtWidgets.QMessageBox.critical(None, self.tr("Error"),
                                           self.tr(u"Cannot write to {}. Choose a different file.".format(f), None))
                return

            class_def = self.get_agg_as_dict_list()
            with open(f, 'w') as outfile:
                json.dump(class_def, outfile, sort_keys=True, indent=4, 
                          separators=(',', ': '), default=json_serial)

    def get_agg_as_dict(self):
        '''Returns the chosen soil_texture definition as a dictionary'''
        out = {}
        for row in range(0, self.remap_view.model().rowCount()):
            initial_code = self.remap_view.model().index(row, 0).data()
            label_widget_index = self.remap_view.model().index(row, self.remap_view.model().columnCount() - 1)
            label_widget = self.remap_view.indexWidget(label_widget_index)
            out[initial_code] = self.final_classes[label_widget.currentText()]
        return out

    def get_agg_as_dict_list(self):
        '''Returns the chosen soil_texture definition as a list of dictionaries'''
        out = []
        for row in range(0, self.remap_view.model().rowCount()):
            this_out = {}
            initial_code = self.remap_view.model().index(row, 0).data()
            this_out['Initial_Code'] = initial_code
            initial_label = self.remap_view.model().index(row, 1).data()
            this_out['Initial_Label'] = initial_label
            # Get the currently assigned label for this code
            label_widget_index = self.remap_view.model().index(row, self.remap_view.model().columnCount() - 1)
            label_widget = self.remap_view.indexWidget(label_widget_index)
            this_out['Final_Label'] = label_widget.currentText()
            this_out['Final_Code'] = self.final_classes[this_out['Final_Label']]

            out.append(this_out)
        # Sort output by initial code
        out = sorted(out, key=lambda k: k['Initial_Code'])
        return out

    def get_agg_as_list(self):
        '''Returns a list describing how to aggregate the soil_texture data'''
        out = [[], []]
        for row in range(0, self.remap_view.model().rowCount()):
            initial_code = self.remap_view.model().index(row, 0).data()

            # Get the currently assigned label for this code
            label_widget_index = self.remap_view.model().index(row, 2)
            label_widget = self.remap_view.indexWidget(label_widget_index)
            final_code = self.final_classes[label_widget.currentText()]
            out[0].append(initial_code)
            out[1].append(final_code)
        return out

    def setup_class_table(self, classes):
        default_codes = sorted([c['Initial_Code'] for c in self.default_classes])
        input_codes = sorted([c['Initial_Code'] for c in classes])
        new_codes = [c for c in input_codes if c not in default_codes]
        missing_codes = [c for c in default_codes if c not in input_codes]
        if len(new_codes) > 0:
            QtWidgets.QMessageBox.warning(None, self.tr("Warning"),
                                      self.tr(u"Some of the class codes ({}) in the definition file do not appear in the chosen data file.".format(', '.join([str(c) for c in new_codes]), None)))
        if len(missing_codes) > 0:
            QtWidgets.QMessageBox.warning(None, self.tr("Warning"),
                                      self.tr(u"Some of the class codes ({}) in the data file do not appear in the chosen definition file.".format(', '.join([str(c) for c in missing_codes]), None)))

        # Setup a new classes list with the new class codes for all classes 
        # included in default calsses, and and any other class codes that are 
        # missing added from the default class list
        classes = [c for c in classes if c['Initial_Code'] in default_codes]
        classes.extend([c for c in self.default_classes if c['Initial_Code'] not in input_codes])

        table_model = AggTableModel(classes, parent=self)
        proxy_model = QSortFilterProxyModel()
        proxy_model.setSourceModel(table_model)
        self.remap_view.setModel(proxy_model)

        # Add selector in cell
        for row in range(0, len(classes)):
            lc_classes = QtWidgets.QComboBox()
            lc_classes.currentIndexChanged.connect(self.lc_class_combo_changed)
            # Add the classes in order of their codes
            lc_classes.addItems(sorted(list(self.final_classes.keys()), key=lambda k: self.final_classes[k]))
            ind = lc_classes.findText(classes[row]['Final_Label'])
            if ind != -1:
                lc_classes.setCurrentIndex(ind)
            self.remap_view.setIndexWidget(proxy_model.index(row, self.remap_view.model().columnCount() - 1), lc_classes)

        self.remap_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.remap_view.setColumnWidth(1, 450)
        self.remap_view.horizontalHeader().setStretchLastSection(True)
        return True

    def lc_class_combo_changed(self, index):
        if self.sender().currentText() == self.tr('No data'):
            class_color = "rgb(197, 197, 197, 255)"
        elif self.sender().currentText() == self.tr('Good'):
            class_color = "rgb(64, 201, 127, 255)"
        elif self.sender().currentText() == self.tr('Moderate'):
            class_color = "rgb(33, 159, 255, 255)"
        elif self.sender().currentText() == self.tr('Poor'):
            class_color = "rgb(254, 238, 179, 255)"
        elif self.sender().currentText() == self.tr('Very Poor'):
            class_color = "rgb(245, 205, 225, 255)"
        else:
            class_color = "rgb(197, 197, 197, 255)"

        #TODO: Fix this so color coding is working
        # Note double brackets to escape for string.format
        # gradient = QLinearGradient(1, .5, .6, .5)
        # gradient.setColorAt(.6, QColor(class_color))
        # gradient.setColorAt(.8, QColor('rgb(30, 2, 215)'))
        # self.sender().setItemData(index, gradient, Qt.BackgroundRole)
        self.sender().setStyleSheet('''QComboBox {{background-color:{class_color};}}'''.format(class_color=class_color))

    def reset_class_table(self):
        self.setup_class_table(self.default_classes)

class VQISetupWidget(QtWidgets.QWidget, Ui_WidgetVQISetup):
    def __init__(self, parent=None):
        super(VQISetupWidget, self).__init__(parent)

        self.setupUi(self)

        default_erosion_class_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                         'data', 'land_cover_classes_ESA_to_erosion.json')
        self.dlg_erosion_agg = DlgCalculateSetAggregation(read_class_file(default_erosion_class_file),{'No data': -32768,
                              '1.0': 10,
                              '1.1': 11,
                              '1.2': 12,
                              '1.3': 13,
                              '1.4': 14,
                              '1.5': 15,
                              '1.6': 16,
                              '1.7': 17,
                              '1.8': 18,
                              '2.0': 20,
                              },  parent=self)

        default_fire_class_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                         'data', 'land_cover_classes_ESA_to_fire.json')
        self.dlg_fire_agg = DlgCalculateSetAggregation(read_class_file(default_fire_class_file),{'No data': -32768,
                              '1.0': 10,
                              '1.1': 11,
                              '1.2': 12,
                              '1.3': 13,
                              '1.4': 14,
                              '1.5': 15,
                              '1.6': 16,
                              '1.7': 17,
                              },  parent=self)

        default_drought_class_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                         'data', 'land_cover_classes_ESA_to_drought.json')
        self.dlg_drought_agg = DlgCalculateSetAggregation(read_class_file(default_drought_class_file),{'No data': -32768,
                              '1.0': 10,
                              '1.1': 11,
                              '1.2': 12,
                              '1.3': 13,
                              '1.4': 14,
                              '1.5': 15,
                              '1.6': 16,
                              '2.0': 20,
                              },  parent=self)
        # self.use_default.toggled.connect(self.Sqi_source_changed)
        # self.use_default.toggled.connect(self.Sqi_source_changed)

        # # self.use_custom.toggled.connect(self.cqi_source_changed)
        # # Below is a bugfix for checkable group boxes created in QtDesigner - 
        # # if they aren't checked by default in Qt Designer then checking them 
        # # in the final gui doesn't enable their children. 
        # self.use_default.setChecked(False)

        self.use_erosion_agg_edit.clicked.connect(self.erosion_agg_custom_edit)
        self.use_drought_agg_edit.clicked.connect(self.drought_agg_custom_edit)
        self.use_fire_agg_edit.clicked.connect(self.fire_agg_custom_edit)

        # self.Sqi_source_changed()


    # def Sqi_source_changed(self):
    #     if self.use_default.isChecked():
    #         self.groupBox_texture_agg.setEnabled(True)
    #         self.groupBox_pm_agg.setEnabled(True)
    #         self.groupBox_pm.setEnabled(False)
    #         self.groupBox_rock_fragm.setEnabled(False)
    #         self.groupBox_slope.setEnabled(False)
    #         self.groupBox_texture.setEnabled(False)
    #         self.groupBox_drainage.setEnabled(False)
    #     else:
    #         self.groupBox_texture_agg.setEnabled(False)
    #         self.groupBox_pm_agg.setEnabled(False)
    #         self.groupBox_pm.setEnabled(True)
    #         self.groupBox_rock_fragm.setEnabled(True)
    #         self.groupBox_slope.setEnabled(True)
    #         self.groupBox_texture.setEnabled(True)
    #         self.groupBox_drainage.setEnabled(True)
            
    def erosion_agg_custom_edit(self):
        self.dlg_erosion_agg.exec_()

    def fire_agg_custom_edit(self):
        self.dlg_fire_agg.exec_()

    def drought_agg_custom_edit(self):
        self.dlg_drought_agg.exec_()

vqi_setup_widget = VQISetupWidget()