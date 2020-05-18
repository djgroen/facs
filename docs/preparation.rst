.. _preparation:

.. Preparing simulations
.. ========================

Overview
============
To prepare simulations for a specific region, you will require to do undertake the following steps:
1. Extract building CSV files from geospatial data.
2. Acquiring validation data.
3. Acquiring demographics data.
4. Verifying the disease specification in disease.yml.
5. Defining the exact public health interventions undertaken, their timing and estimated compliance rate.


Extract building CSV files
--------------------------

This can be done e.g. using the scripts availably at https://www.github.com/djgroen/covid19-preprocessing

Acquiring validation data
-------------------------
To do this you require region-specific data related to Covid-19 spread. These could include:
* daily hospital admissions by region.
* daily intensive care unit admissions by region.
* daily intensive care unit bed occupancy (covid patients only) by region.

If you only have validation data for a single hospital, then you could choose to make a separate validation model, covering only the catchment area of the hospital, before developing the main simulation.
