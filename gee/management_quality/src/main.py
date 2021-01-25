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
from landdegradation.management_quality import management_quality

def run(params, logger):
    """."""
    logger.debug("Loading parameters.")
    year = params.get('year')
    lu_matrix = params.get('lu_matrix')
    crs = params.get('crs') 

    geojsons = json.loads(params.get('geojsons'))
    
    # Check the ENV. Are we running this locally or in prod?
    if params.get('ENV') == 'dev':
        EXECUTION_ID = str(random.randint(1000000, 99999999))
    else:
        EXECUTION_ID = params.get('EXECUTION_ID', None)

    logger.debug("Running main script.")

    out = management_quality(year,lu_matrix, geojsons[0],EXECUTION_ID, logger)

    return out.export(geojsons, 'Management Quality', crs, logger, EXECUTION_ID)
    

