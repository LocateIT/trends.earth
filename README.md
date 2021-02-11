# MISLAND QGIS PLUGIN

## General Infortmation

MISLAND-North Africa is an operational instrument relying on the international standards for reporting SDG 15.3.1 and technical approaches allowing the delivery of regular information on vegetation cover gain/loss to decision makers and environmental agencies at the first place.

The core-service provides land degradation indicators for six North African Countries at two levels:

At the regional level(North Africa action zone) where low and medium resolution EO are used.

At the pilot site level, where(customized indicators) can be developed, using medium resoultion data(landsat time series imagery and derived vegetation indices, combined with different satellite-derived climate data)
QGIS plugin for OSS Land Degradation Monitoring Service (MISLAND)


### Plugin Modules

The offline system (GIS Plugin) will have three modules: 
- input module, 
- computation module and 
- output module. 

![flow diagram](docs/resources/en/common/Land_degradation_oss_qgis.png "QGIS Plugin Flow Diagram")

The input module will enable the user to load ancillary data, e.g. rainfall, vegetation cover, wind speed data etc., required by the service model to compute various outputs. 

The computation module will implement the models and algorithms, while the output module will enable the user to download the result. Our assumption here is that the output will be a Geotiff map for the area of interest.

It’s important to note that the same functions available through the web service will be available through a GIS plugin, where more advanced analysis can be done. This will overpass data sharing issues and allow users who do not have continuous/stable internet connection and want to perform advanced analysis 

---

### Plugin Flow

Below is an illustration of flow of information from one resource to another within the QGIS Plugin architecture

![flow](https://github.com/LocateIT/trends.earth/blob/master/docs/resources/en/common/QGIS_plugin_flow.png)

An end-user executes a module/script within the plugin eg. forest fires. The plugin sends this request to the backend API which creates an execution and execution logs for this instance as well as requests the script ID from the Postgresql database. The database returns metadata of the script back to the backend API which then sends the the request to [google earth engine](https://earthengine.google.com) python library on which script to run. Execution logs are then recorded in the database as the script runs from start to finish. 

On successful completion of the execution, the final result(tiff file) is exported by google earth engine to [Google Cloud Storage](https://earthengine.google.com) bucket as an object. The end-user is then able to thereafter download and visualize the result via the plugin onto QGIS. This data remains available for download by the end-user for upto 7 days. 

### INSTALLING PLUGIN FROM ZIPILE

To install from within QGIS, first launch QGIS, and then go to Plugins in the menu bar at the top of the program and select Manage and install plugins.

Then search navigate to Install from ZIP and upload the MISLAND plugin zipfile. If your plugin has been installed properly, there will be a menu bar in the top left of your QGIS.

---

### DOCUMENTATION

MISLAND QGIS Plugin documentation can be found at [MISLAND DOCS](https://misland.readthedocs.io/)

---

### DATASETS

Datasets used in running of processing scripts in MISLAND QGIS Plugin are as listed below:

#### LAND DEGRDATION (SDG 15.3.1) DATA SOURCES

| **Indicator** | **Variables** | **Data Source** |
| --- | --- | --- |
| Soil Organic Carbon | Climate Zones | Gee Asset:users/geflanddegradation/toolbox\_datasets/ipcc\_climate\_zones |
|  | Land Cover | [ESA CCI–land cover map v2.0.7–2015](http://maps.elie.ucl.ac.be/CCI/viewer/) |
|Productivity | Land Cover | [ESA CCI–land cover map v2.0.7–2015](http://maps.elie.ucl.ac.be/CCI/viewer/) |
|  |Land Productivity | Land Productivity Dynamics from Joint Research Commission (UNCCD)GEE Asset: users/geflanddegradation/toolbox\_datasets/lpd\_300m\_longlat |
|  |Global agroecological zones from IIASA | [OpenLandMap USDA soil taxonomy great groups](https://developers.google.com/earth-engine/datasets/catalog/OpenLandMap_SOL_SOL_GRTGROUP_USDA-SOILTAX_C_v01) |
|  |NDVI | [MOD13Q1.006 Terra Vegetation Indices 16-Day Global 250m](https://developers.google.com/earth-engine/datasets/catalog/MODIS_006_MOD13Q1) |
|  Land Cover | Land Cover | [ESA CCI–land cover map v2.0.7–2015](http://maps.elie.ucl.ac.be/CCI/viewer/) |

---

#### VEGETATION DEGRADATION DATA SOURCES

| **Indicator** | **Variables** | **Data Source** |
| --- | --- | --- |
| Forest Degradation Hotspots | Forest Fires | [Sentinel-2 MSI: MultiSpectral Instrument, Level-1C](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2) |
| | |[USGS Landsat 8 Surface Reflectance Tier 1](https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC08_C01_T1_SR) |
|  |Forest Change and Carbon Stocks | [Hansen Global Forest Change v1.7 (2000-2019)](https://developers.google.com/earth-engine/datasets/catalog/UMD_hansen_global_forest_change_2019_v1_7) |
| Vegetation Indices Time-series | NDVI, MSAVI2, SAVI | Landsat7 ETM+GEE Asset: users/miswagrace/ndvi\_landsat\_1999\_2020 |

---

#### MEDALUS (MEDITERRANEAN)

| **Indicator** | **Variables** | **Data Source** |
| --- | --- | --- |
| Soil Quality Index | Slope | [SRTM Digital Elevation](https://developers.google.com/earth-engine/datasets/catalog/CGIAR_SRTM90_V4) |
|  | Soil Depth | Custom User Input |
|  | Rock Fragments | Harmonized World Soil Database
 |
|  | Parent Material | [Digital Sol Map of the world](http://www.fao.org/geonetwork/srv/en/metadata.show%3Fid=14116) |
|  | Drainage | Harmonized World Soil Database
 |
|  |Soil Texture | [OpenLandMap Soil texture class (USDA system)](https://developers.google.com/earth-engine/datasets/catalog/OpenLandMap_SOL_SOL_TEXTURE-CLASS_USDA-TT_M_v02) |
| Climate Quality Index | Precipitation | [TerraClimate Monthly Climate and Climatic Water Balance for Global Terrestrial Surfaces](developers.google.com/earth-engine/datasets/catalog/IDAHO_EPSCOR_TERRACLIMATE) |
|  | Potential Evapotranspiration | [TerraClimate Monthly Climate and Climatic Water Balance for Global Terrestrial Surfaces](developers.google.com/earth-engine/datasets/catalog/IDAHO_EPSCOR_TERRACLIMATE) |
| Vegetation Quality Index | Fire Risk | [ESA CCI–land cover map v2.0.7–2015](http://maps.elie.ucl.ac.be/CCI/viewer/) |
|  |Drought Resistance | [ESA CCI–land cover map v2.0.7–2015](http://maps.elie.ucl.ac.be/CCI/viewer/) |
|  |Erosion Protection | [ESA CCI–land cover map v2.0.7–2015](http://maps.elie.ucl.ac.be/CCI/viewer/) |
|  |Plant Cover | [PROBA-V C1 Top Of Canopy Daily Synthesis 100m](https://developers.google.com/earth-engine/datasets/catalog/VITO_PROBAV_C1_S1_TOC_100M) |
| Land Management Quality Index | Land Use Intensity | [ESA CCI–land cover map v2.0.7–2015](http://maps.elie.ucl.ac.be/CCI/viewer/) |
|  |Population Density | [GPWv411: Population Density (Gridded Population of the World Version 4.11)](https://developers.google.com/earth-engine/datasets/catalog/CIESIN_GPWv411_GPW_Population_Density) |

More info on datasources and data coding visit https://misland.readthedocs.io/en/latest/Introduction/data.html

---

### Aknowledgement
Special appreciation to the Trends.Earth. Conservation International. Available online at http://trends.earth .2018. for providing input on the implementation of the SDG 15.3 and LDN indicators in MISLAND-North Africa, on the UNCCD reporting process, and also provided early input and testing of the tool.

The project also acknowledges the contribution of national and regional stakeholders; Algerian Space Agency(ASAL), ASAL (Algeria), DRC (Egypt), LCRSSS (Libya), CRTS (Morocco), AL-Aasriya University of Nouakchott (Mauritania) and CNCT (Tunisia) for the national level and CRTEAN and CRASTE-LF for the regional level

---

### Getting help

Contact the MISLAND-North Africa team with any comments or suggestions. If you have specific bugs to report or improvements to the tool that you would like to suggest, you can also submit them in the issue tracker on Github for MISLAND-North Africa.

---

### License

MISLAND is free and open-source. It is licensed under the [GNU General Public License, version 2.0 or later](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html).

This site and the products of MISLAND are made available under the terms of the [Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0). The boundaries and names used, and the designations used, in MISLAND do not imply official endorsement or acceptance by OSS, or its partner organizations and contributors.