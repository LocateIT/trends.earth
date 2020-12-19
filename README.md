# oss-MISLAND-qgis

QGIS plugin for OSS Land Degradation Monitoring Service (MISLAND)


![flow diagram](docs/resources/en/common/Land_degradation_oss_qgis.png "QGIS Plugin Flow Diagram")

### Plugin Modules

The offline system (GIS Plugin) will have three modules: 
- input module, 
- computation module and 
- output module. 

The input module will enable the user to load ancillary data, e.g. rainfall, vegetation cover, wind speed data etc., required by the service model to compute various outputs. 

The computation module will implement the models and algorithms, while the output module will enable the user to download the result. Our assumption here is that the output will be a Geotiff map for the area of interest.

It’s important to note that the same functions available through the web service will be available through a GIS plugin, where more advanced analysis can be done. This will overpass data sharing issues and allow users who do not have continuous/stable internet connection and want to perform advanced analysis 

