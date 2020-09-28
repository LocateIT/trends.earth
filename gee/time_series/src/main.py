"""
Code for calculating vegetation productivity trajectory.
"""
# Copyright 2017 Conservation International

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from builtins import str
from builtins import zip
import random
import re
import json

import ee

from landdegradation.productivity import productivity_trajectory
from landdegradation.schemas.schemas import TimeSeries, TimeSeriesTable, TimeSeriesTableSchema

dataset = ee.ImageCollection('LANDSAT/LE07/C01/T1_RT_TOA')
years = [1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]

# // mask landsat 7 clouds 
def maskL7clouds(image):
    qa = image.select('BQA')

    # // Bits 4 are clouds.
    cloudBitMask = 1 << 4

    # // flags should be set to zero, indicating clear conditions.
    mask = qa.bitwiseAnd(cloudBitMask).eq(0)

    return image.updateMask(mask)


def calculateNDVI(geometry):
    """
    Calculate NDVI
    """
    # // Replace country name with EGYPT, LIBYA, ALGERIA, MAURITANIA, MOROCCO, TUNISIA
    # northAfrica = ee.FeatureCollection("users/miswagrace/Sahel_sahara_boundary")

    def yearlyNDVIMean(year):
        datasets = (dataset.filterDate('{}-01-01'.format(year),'{}-12-31'.format(year))
            # // Pre-filter to get less cloudy granules.
            # // .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE',50))
            .filterBounds(geometry)
            .map(maskL7clouds)
            .mean())
                        
        ndvi = datasets.expression('(nir- red) / (nir + red)',{
            'nir':datasets.select('B4'),
            'red':datasets.select('B3')
            }
        ).rename('y{}'.format(year))
        
        return ndvi

    ndviImages = ee.Image.cat(list(map(yearlyNDVIMean, years)))

    return ndviImages

def calculateMSAVI2(geometry):
    """
    Calculate MSAVI2
    """
    # // Replace country name with EGYPT, LIBYA, ALGERIA, MAURITANIA, MOROCCO, TUNISIA
    # northAfrica = ee.FeatureCollection("users/miswagrace/Sahel_sahara_boundary")

    def yearlyMSAVI2Mean(year):
        datasets = (dataset.filterDate('{}-01-01'.format(year),'{}-12-31'.format(year))
            # // Pre-filter to get less cloudy granules.
            # // .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE',50))
            .filterBounds(geometry)
            .map(maskL7clouds)
            .mean())
                        
        msavi2 = datasets.expression('(2 * nir + 1 - ( (2 * nir + 1)**2 - 8 * (nir -red) )**(1/2) ) / 2',{
            'nir':datasets.select('B4'),
            'red':datasets.select('B3')
        }).rename('y{}'.format(year))
        
        return msavi2

    msavi2Images = ee.Image.cat(list(map(yearlyMSAVI2Mean, years)))

    return msavi2Images

def calculateSAVI(geometry):
    """
    Calculate SAVI
    """
    # // Replace country name with EGYPT, LIBYA, ALGERIA, MAURITANIA, MOROCCO, TUNISIA
    # northAfrica = ee.FeatureCollection("users/miswagrace/Sahel_sahara_boundary")

    def yearlySAVIMean(year):
        datasets = (dataset.filterDate('{}-01-01'.format(year),'{}-12-31'.format(year))
            # // Pre-filter to get less cloudy granules.
            # // .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE',50))
            .filterBounds(geometry)
            .map(maskL7clouds)
            .mean())
                        
        savi = datasets.expression('((nir - red) / (nir + red + 0.5)) * (1 + 0.5)',{
            'nir':datasets.select('B4'),
            'red':datasets.select('B3')
        }).rename('y{}'.format(year))
        
        return savi

    saviImages = ee.Image.cat(list(map(yearlySAVIMean, years)))

    return saviImages

def zonal_stats(veg_index, geojsons, EXECUTION_ID, logger):
    logger.debug("Entering zonal_stats function.")

    # =======================================
    # compute nvdi mean first for landsat 7
    # ========================================

    region = ee.Geometry(geojsons)
    
    if veg_index == 'ndvi':
        image = calculateNDVI(region).clip(region)
    elif veg_index == 'savi':
        image = calculateSAVI(region).clip(region)
    else:
        image = calculateMSAVI2(region).clip(region)

    scale = ee.Number(image.projection().nominalScale()).getInfo()

    ## This produces an average of the region over the image by year
    ## Source: https://developers.google.com/earth-engine/reducers_reduce_region
    reducers = ee.Reducer.mean() \
        .combine(reducer2=ee.Reducer.min(), sharedInputs=True) \
        .combine(reducer2=ee.Reducer.max(), sharedInputs=True) \
        .combine(reducer2=ee.Reducer.mode(), sharedInputs=True) \
        .combine(reducer2=ee.Reducer.stdDev(), sharedInputs=True)
    statsDictionary = image.reduceRegion(reducer=reducers, geometry=region, scale=scale, maxPixels=1e13)

    logger.debug("Calculating zonal_stats.")
    res = statsDictionary.getInfo()

    logger.debug("Formatting results.")
    res_clean = {}
    for key, value in list(res.items()):
        field = re.search('(?<=y[0-9]{4}_)\w*', key).group(0)
        year = re.search('(?<=y)[0-9]{4}', key).group(0)
        if field not in res_clean:
            res_clean[field] = {}
            res_clean[field]['value'] = []
            res_clean[field]['year'] = []
        res_clean[field]['value'].append(float(value))
        res_clean[field]['year'].append(int(year))

    logger.debug("Setting up results JSON.")
    timeseries = []
    for key in list(res_clean.keys()):
        # Ensure the lists are in chronological order
        year, value = list(zip(*sorted(zip(res_clean[key]['year'], res_clean[key]['value']))))
        ts = TimeSeries(list(year), list(value), key)
        timeseries.append(ts)

    timeseries_table = TimeSeriesTable('timeseries', timeseries)
    timeseries_table_schema = TimeSeriesTableSchema()
    json_result = timeseries_table_schema.dump(timeseries_table)

    return json_result


def run(params, logger):
    """."""
    logger.debug("Loading parameters.")
    geojsons = json.loads(params.get('geojsons'))
    crs = params.get('crs')
    indices = params.get('indices')

    # Check the ENV. Are we running this locally or in prod?
    if params.get('ENV') == 'dev':
        EXECUTION_ID = str(random.randint(1000000, 99999999))
    else:
        EXECUTION_ID = params.get('EXECUTION_ID', None)

    logger.debug("Running main script.")
    # TODO: Right now timeseries will only work on the first geojson - this is 
    # somewhat ok since for the most part this uses points, but should fix in 
    # the future
    json_result = zonal_stats(indices,geojsons[0], EXECUTION_ID, logger)

    return json_result
