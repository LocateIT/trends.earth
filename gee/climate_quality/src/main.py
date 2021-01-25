"""
Code for calculating potential carbon gains due to restoration.
"""
# Copyright 2017 Conservation International

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import random
import json

import ee

from landdegradation.util import TEImage
from landdegradation.schemas.schemas import BandInfo, CloudResultsSchema
from landdegradation.climate_quality import climate_quality
# from landdegradation.forest_change import forest_loss, forest_gain, forest_loss_year,forest_cover

def run(params, logger):
    """."""
    logger.debug("Loading parameters.")

    month = params.get('month')
    next_month = params.get('next_month')
    crs = params.get('crs') 

    geojsons = json.loads(params.get('geojsons'))
    
    # Check the ENV. Are we running this locally or in prod?
    if params.get('ENV') == 'dev':
        EXECUTION_ID = str(random.randint(1000000, 99999999))
    else:
        EXECUTION_ID = params.get('EXECUTION_ID', None)

    logger.debug("Running main script.")

    out = climate_quality(month, next_month ,geojsons[0],EXECUTION_ID, logger)

    return out.export(geojsons, 'Climate Quality', crs, logger, EXECUTION_ID)
    

