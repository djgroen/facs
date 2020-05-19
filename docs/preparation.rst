.. _preparation:

.. Preparing simulations
.. ========================

Preparing simulations
============
To prepare simulations for a specific region, you will require to do undertake the following steps:

#. Extract building CSV files from geospatial data.
#. Acquiring validation data.
#. Acquiring demographics data.
#. Verifying the disease specification in disease.yml.
#. Defining the exact public health interventions undertaken, their timing and estimated compliance rate.


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

Acquiring demographics data
---------------------------
We provide example demographics data in https://www.github.com/djgroen/facs/covid_data/age-distr.csv . This data is loaded automatically into FACS on startup.

The data contains the number of citizens by age, with a generic group for people aged 90 and over. 
The layout of the file is as follows:

    Age,<borough name>,<borough2 name>,<country name>
    0,x,x,x
    1,x,x,x
    ...
    90+,x,x,x
    
Here you can add one new column for each new scenario location that you're adding. This could be a city or a country (if you plan to do a very large scale run). It is perfectly fine to remove columns of locations that you're not using, to make the file simpler.
