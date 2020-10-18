Data sources
------------

LDMS draws on a number of data sources. The data sets listed below are 
owned/made available by the following organizations and individuals under 
separate terms as indicated in their respective metadata.

NDVI
~~~~

+------------------+-----------+---------+--------+------------------+
| Sensor/Dataset   | Temporal  | Spatial | Extent | License          |
+==================+===========+=========+========+==================+
| `LANDSAT7`_      | 2001-2020 | 30 m    | Global | `Public Domain`_ |
+------------------+-----------+---------+--------+------------------+
| `AVHRR/GIMMS`_   | 1982-2015 | 8 km    | Global | `Public Domain`_ |
+------------------+-----------+---------+--------+------------------+
| `MOD13Q1-coll6`_ | 2001-2016 | 250 m   | Global | `Public Domain`_ |
+------------------+-----------+---------+--------+------------------+

.. _LANDSAT7: https://developers.google.com/earth-engine/datasets/catalog/landsat
.. _AVHRR/GIMMS: https://glam1.gsfc.nasa.gov
.. _MOD13Q1-coll6:
   https://lpdaac.usgs.gov/dataset_discovery/modis/modis_products_table/mod13q1_v006
   
Soil moisture
~~~~~~~~~~~~~

+----------------+-----------+---------------+--------+------------------+
| Sensor/Dataset | Temporal  | Spatial       | Extent | License          |
+================+===========+===============+========+==================+
| `MERRA 2`_     | 1980-2016 | 0.5° x 0.625° | Global | `Public Domain`_ |
+----------------+-----------+---------------+--------+------------------+
| `ERA I`_       | 1979-2016 | 0.75° x 0.75° | Global | `Public Domain`_ |
+----------------+-----------+---------------+--------+------------------+

.. _MERRA 2: https://gmao.gsfc.nasa.gov/reanalysis/MERRA-Land
.. _ERA I: 
   https://www.ecmwf.int/en/forecasts/datasets/reanalysis-datasets/era-interim-land

Precipitation
~~~~~~~~~~~~~

+----------------------+-----------+-------------+---------+------------------+
| Sensor/Dataset       | Temporal  | Spatial     | Extent  | License          |
+======================+===========+=============+=========+==================+
| `GPCP v2.3 1 month`_ | 1979-2019 | 2.5° x 2.5° | Global  | `Public Domain`_ |
+----------------------+-----------+-------------+---------+------------------+
| `GPCC V6`_           | 1891-2019 | 1° x 1°     | Global  | `Public Domain`_ |
+----------------------+-----------+-------------+---------+------------------+
| `CHIRPS`_            | 1981-2016 | 5 km        | 50N-50S | `Public Domain`_ |
+----------------------+-----------+-------------+---------+------------------+
| `PERSIANN-CDR`_      | 1983-2015 | 25 km       | 60N-60S | `Public Domain`_ |
+----------------------+-----------+-------------+---------+------------------+

.. _GPCP v2.3 1 month: https://www.esrl.noaa.gov/psd/data/gridded/data.gpcp.html
.. _GPCC V6: https://www.esrl.noaa.gov/psd/data/gridded/data.gpcc.html
.. _CHIRPS:  http://chg.geog.ucsb.edu/data/chirps
.. _PERSIANN-CDR: http://chrsdata.eng.uci.edu

Evapotranspiration
~~~~~~~~~~~~~~~~~~

+----------------+-----------+---------+--------+------------------+
| Sensor/Dataset | Temporal  | Spatial | Extent | License          |
+================+===========+=========+========+==================+
| MOD16A2_       | 2000-2014 | 1 km    | Global | `Public Domain`_ |
+----------------+-----------+---------+--------+------------------+

.. _MOD16A2:
   https://lpdaac.usgs.gov/dataset_discovery/modis/modis_products_table/mod16a2_v006

Land cover
~~~~~~~~~~

+-----------------------+-----------+---------+--------+-----------------+
| Sensor/Dataset        | Temporal  | Spatial | Extent | License         |
+=======================+===========+=========+========+=================+
| `ESA CCI Land Cover`_ | 1992-2018 | 300 m   | Global | `CC by-SA 3.0`_ |
+-----------------------+-----------+---------+--------+-----------------+

.. _ESA CCI Land Cover: https://www.esa-landcover-cci.org
.. _CC by-SA 3.0: https://creativecommons.org/licenses/by-sa/3.0/igo

Soil carbon
~~~~~~~~~~~

+-----------------------+----------+---------+--------+-----------------+
| Sensor/Dataset        | Temporal | Spatial | Extent | License         |
+=======================+==========+=========+========+=================+
| `Soil Grids (ISRIC)`_ | Present  | 250 m   | Global | `CC by-SA 4.0`_ |
+-----------------------+----------+---------+--------+-----------------+

.. _Soil Grids (ISRIC): https://www.soilgrids.org/
.. _CC by-SA 4.0: https://creativecommons.org/licenses/by-sa/4.0
.. _JPL public: https://www.jpl.nasa.gov/imagepolicy/

Agroecological Zones
~~~~~~~~~~~~~~~~~~~~

+---------------------------------------------------+----------+---------+--------+------------------+
| Sensor/Dataset                                    | Temporal | Spatial | Extent | License          |
+===================================================+==========+=========+========+==================+
| `FAO - IIASA Global Agroecological Zones (GAEZ)`_ | 2000     | 8 km    | Global | `Public Domain`_ |
+---------------------------------------------------+----------+---------+--------+------------------+

.. _FAO - IIASA Global Agroecological Zones (GAEZ): http://www.fao.org/nr/gaez/en


Soil Quality
~~~~~~~~~~~~~~
+---------------------------+----------+---------+--------+---------------------+
| Sensor/Dataset            | Temporal | Spatial | Extent | License             |
+===========================+==========+=========+========+=====================+
| `Soil Texture and Depth`_ | Present  | 250 m   | Global | `CC by-SA 4.0`_     |
+---------------------------+----------+---------+--------+---------------------+
| `Parent Material`_        | Present  | N/A     | Global | `CC by-SA 4.0`_     |
+---------------------------+----------+---------+--------+---------------------+
| `Slope`_                  | Present  | 30 m    | Global  | `JPL public`_      |
+---------------------------+----------+---------+--------+---------------------+

.. _Soil Texture and Depth: https://cmr.earthdata.nasa.gov/search/concepts/C1000000240-LPDAAC_ECS.html
.. _Parent Material: https://doi.pangaea.de/10.1594/PANGAEA.788537
.. _Slope: https://developers.google.com/earth-engine/datasets/catalog/OpenLandMap_SOL_SOL_TEXTURE-CLASS_USDA-TT_M_v02

Climate
~~~~~~~~~~~~~~~~~~~~

+---------------------------------------------------+----------+---------+--------+------------------+
| Sensor/Dataset                                    | Temporal | Spatial | Extent | License          |
+===================================================+==========+=========+========+==================+
| `Terra Climate`_                                  | 1985-2019| 30 m    | Global | `Public Domain`_ |
+---------------------------------------------------+----------+---------+--------+------------------+

.. _Terra Climate: https://developers.google.com/earth-engine/datasets/catalog/IDAHO_EPSCOR_TERRACLIMATE#description


Administrative Boundaries
~~~~~~~~~~~~~~~~~~~~~~~~~

+--------------------------------------------+----------+---------+--------+------------------+
| Sensor/Dataset                             | Temporal | Spatial | Extent | License          |
+============================================+==========+=========+========+==================+
| `Natural Earth Administrative Boundaries`_ | Present  | 10/50m  | Global | `Public Domain`_ |
+--------------------------------------------+----------+---------+--------+------------------+

.. note::
    The `Natural Earth Administrative Boundaries`_ provided in LDMS 
    are in the `public domain`_. The boundaries and names used, and the 
    designations used, in LDMS do not imply official endorsement or 
    acceptance by Conservation International Foundation, or by its partner 
    organizations and contributors.

    If using LDMS for official purposes, it is recommended that users 
    choose an official boundary provided by the designated office of their 
    country.

.. _Natural Earth Administrative Boundaries: http://www.naturalearthdata.com

.. _Public Domain: https://creativecommons.org/publicdomain/zero/1.0
