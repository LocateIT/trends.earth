"""
Code for downloading dataset.
"""
# Copyright 2017 Conservation International

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from builtins import str
import random
import json

import ee

from landdegradation import GEEIOError
from landdegradation.download import download


def run(params, logger):
    """."""
    logger.debug("Loading parameters.")
    asset = "users/geflanddegradation/toolbox_datasets/ndvi_modis_2001_2019"
    name = "MODIS (MOD13Q1, annual)"
    start_year = 2001
    end_year = 2015
    temporal_resolution = "annual"
    
    # geojsons = json.loads(params.get('geojsons'))
    geojsons = json.loads('[{"type": "Polygon", "coordinates": [[[36.67624230333968, -1.4171224908103], [37.131511672225884, -1.4171224908103], [37.131511672225884, -1.139361667107238], [36.67624230333968, -1.139361667107238], [36.67624230333968, -1.4171224908103]]]}]')
    logger.debug(geojsons)
    
    crs = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]'
    # Check the ENV. Are we running this locally or in prod?
    # if params.get('ENV') == 'dev':
    EXECUTION_ID = str(random.randint(1000000, 99999999))
    # else:
    #     EXECUTION_ID = params.get('EXECUTION_ID', None)

    logger.debug("Running main script.")
    out = download(asset, name, temporal_resolution, start_year, end_year, 
                   EXECUTION_ID, logger)
    return out.export(geojsons, 'download', crs, logger, EXECUTION_ID)
