from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsProcessingProvider

from .carbon import TCSummary
from .utilities import GenerateMask, ClipRaster


class Provider(QgsProcessingProvider):

    def loadAlgorithms(self, *args, **kwargs):
        self.addAlgorithm(TCSummary())
        self.addAlgorithm(GenerateMask())
        self.addAlgorithm(ClipRaster())

    def id(self, *args, **kwargs):
        return 'trendsearth'

    def name(self, *args, **kwargs):
        return self.tr('LDMS')

    def icon(self):
        """Should return a QIcon which is used for your provider inside
        the Processing toolbox.
        """
        return QIcon(':/plugins/LDMP/trend_plugin_logo.png')
