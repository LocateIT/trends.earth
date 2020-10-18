.. _forestfire:

Forest Fires
============

Burnt areas and forest fires will be highlighted and mapped out form remotely sensed Landsat/Sentinel 
data using the Normalized Burn Ratio (NBR). NBR is designed to highlight burned areas and estimate 
burn severity. It uses near-infrared (NIR) and shortwave-infrared (SWIR) wavelengths. Before fire events, 
healthy vegetation has very high NIR reflectance and a low SWIR reflectance. In contrast, recently burned 
areas show low reflectance in the NIR and high reflectance in the SWIR band. 

The NBR will be calculated for Landsat/Sentinel images before the fire (pre-fire NBR) and after the 
fire (post-fire NBR). The difference between the pre-fire NBR and the post-fire NBR referred to as 
delta NBR (dNBR) is computed to highlight the areas of forest disturbance by fire event. 

Classification of the dNBR will be used for burn severity assessment, as areas with higher dNBR 
values indicate more severe damage whereas areas with negative dNBR values might show increased 
vegetation productivity. dNBR will be classified according to burn severity ranges proposed by the 
United States Geological Survey(USGS)

.. image:: /static/documentation/understanding_forest_fires/forestfire_flow.png
   :align: center