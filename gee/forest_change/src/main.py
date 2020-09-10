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
from landdegradation.forest_change import forest_loss, forest_gain, forest_loss_year,forest_cover

def run(params, logger):
    """."""
    logger.debug("Loading parameters.")
    # calc_loss = True
    # calc_gain = True
    # calc_cover = True    

    calc_gain=params.get('calc_gain')    
    calc_loss=params.get('calc_loss')    
    calc_cover=params.get('calc_cover')    

    # year = 2019
    # year = params.get('year')
    
    geojsons = json.loads(params.get('geojsons'))
    # geojsons = json.loads('[{"type": "Polygon", "coordinates": [[[36.67624230333968, -1.4171224908103], [37.131511672225884, -1.4171224908103], [37.131511672225884, -1.139361667107238], [36.67624230333968, -1.139361667107238], [36.67624230333968, -1.4171224908103]]]}]')
    logger.debug(geojsons)
    
    crs = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]'
    # Check the ENV. Are we running this locally or in prod?
    if params.get('ENV') == 'dev':
        EXECUTION_ID = str(random.randint(1000000, 99999999))
    else:
        EXECUTION_ID = params.get('EXECUTION_ID', None)

    logger.debug("Running main script.")
    
    outs = []
    for geojson in geojsons:
        this_out = None
        if calc_loss:
            loss = forest_loss(geojson, EXECUTION_ID, logger)
            
            if not this_out:
                this_out = loss
            else:
                this_out.merge(loss)

        if calc_gain:
            gain = forest_gain(geojson, EXECUTION_ID, logger)

            if not this_out:
                this_out = gain
            else:
                this_out.merge(gain)

        if calc_cover:
            cover = forest_cover(geojson, EXECUTION_ID, logger)

            if not this_out:
                this_out = cover
            else:
                this_out.merge(cover)

        outs.append(this_out.export([geojson], 'Forest Change', crs, logger, 
                                    EXECUTION_ID))
    
    # First need to deserialize the data that was prepared for output from 
    # the productivity functions, so that new urls can be appended
    schema = CloudResultsSchema()
    logger.debug("Deserializing")
    final_output = schema.load(outs[0])
    for o in outs[1:]:
        this_out = schema.load(o)
        final_output.urls.extend(this_out.urls)
    logger.debug("Serializing")
    # Now serialize the output again and return it
    return schema.dump(final_output)
