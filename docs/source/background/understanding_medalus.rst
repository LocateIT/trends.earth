.. _medalus:

Desertification Assessment Using MEDALUS
=========================================

The Mediterranean Desertification and Land Use (MEDALUS) model, which takes into account soil,
climate, vegetation and management indexes will be employed to identify the sensitivity of 
areas to desertification. The susceptibility to desertification is typically dependent on 
place-specific socio-ecological conditions, interactions, and adaptation strategies. 

As such the MEDALUS model applies composite indices (key indicators) in the assessment of 
potential and actual land degradation.The indices considered are as discussed below and 
the summarized methodology is as shown below:

.. image:: /static/documentation/understanding_medalus/medalus_flow.png
   :align: center

Sub-indicators
--------------

.. _indicator-sqi:

Soil Quality Index
~~~~~~~~~~~~~~~~~~

The impact of the soil factor to the process of desertification is determined by the strength of 
cohesion between soil particles, water retention ability of the soil, soil texture, and structure. 
The soil quality index (SQI), developed by OSS, that will be used is based on four parameters:

-parent material
-soil depth
-soil texture
-slope

The formula used to compute the SQI from the above-mentioned parameters is as shown below:

SQI =(Parent material * Depth * Texture * slope)^1/4

.. _indicator-vqi:

Vegetation Quality Index
~~~~~~~~~~~~~~~~~~~~~~~~

Vegetation plays a key role in preventing desertification by providing shelter against wind 
and water erosion. Plant cover promotes infiltration of water and reduces runoff, residual plant 
materials from senescent vegetation enriches the soil with organic which improves its structure and 
cohesion. 

VQI =(FR * PE * DR * C)^1/4

where: 
    VQI is the vegetation quality index; 
    FR is the fire risk; PEis the protection against erosion; 
    DR is the drought resistance; 
    Cis the coverage.

FR, PE , and DR will be derived from Land use land cover maps, and the sub-index Cis extracted from 
Normalized Difference Vegetation Index(NDVI).

.. _indicator-cqi:

Climate Quality Index
~~~~~~~~~~~~~~~~~~~~~~

Adverse climate conditions such as recurrent and prolonged drought, increase the susceptibility of 
land to desertification. The Climate Quality Index(CQI) is analyzed using the aridity index (AI), 
using the formula:

AI = P/PET

Where AI is the Aridity index; P is the yearly mean precipitation; and PET is the mean potential 
evapotranspiration. Using the index the area is classified as shown in table below:

+-----------------+-----------------------------------+------------------+
| CQI             | Climatic zones                    | Classification   |
+=================+===================================+==================+
| < 0.002         | hyper- arid                       | 2                |
+-----------------+-----------------------------------+------------------+
| 0.002 - 0.03    | Arid                              | 1,75             |
+-----------------+-----------------------------------+------------------+
| 0.20 - 0.50     | Semi-arid                         | 1,50             |
+-----------------+-----------------------------------+------------------+
| 0.50 - 0.65     | Dry sub-humid                     | 1,25             |
+-----------------+-----------------------------------+------------------+
| > 0.65          | Humid                             | 1                |
+-----------------+-----------------------------------+------------------+


.. _indicator-aqi:

Anthropogenic Quality Index
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Anthropic Quality Index is the measure of human pressure that affects the vulnerability of an 
ecosystem to desertification. Deforestation and vegetation loss are linked to human activities 
such as overgrazing, logging, and poor agricultural practices. The AQI will be calculated using 
human and livestock pressures. Human pressure is derived from population density whereas grazing 
pressure will be calculated from livestock population using the formula shown below:

AQI = (Human pressure * livestock pressure)^1/2

.. _indicator-isd:

Index of Susceptibility to Desertification (ISD)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The final layer (ISD) will be obtained from the geometric average of the quality indices as shown in the formula;
ISD = ( SQI * CQI * VQI * AQI) ^ 1/4

The SDI will be classified according to the following classes of sensitivity to desertification:

+-----------------+-----------------------------------+---------------------------------------------------------------+
| Classes         | ISD                               | Description                                                   |
+=================+===================================+===============================================================+
| 1               | < 1,2                             | Non affected areas or very low sensitivity to desertification |
+-----------------+-----------------------------------+---------------------------------------------------------------+
| 2               | 1,2 <= ISD < 1,3                  | Low sensitivity to desertification                            |
+-----------------+-----------------------------------+---------------------------------------------------------------+
| 3               | 1,3 <= ISD < 1,4                  | Medium sensitivity to desertification                         |
+-----------------+-----------------------------------+---------------------------------------------------------------+
| 4               | 1,4 <= ISD < 1,6                  | Sensitive areas to desertification                            |
+-----------------+-----------------------------------+---------------------------------------------------------------+
| 5               | ISD 1,6                           | Very sensitive areas to desertification                       |
+-----------------+-----------------------------------+---------------------------------------------------------------+

