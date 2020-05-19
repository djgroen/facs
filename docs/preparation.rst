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


1. Extract building CSV files
--------------------------

This can be done e.g. using the scripts availably at https://www.github.com/djgroen/covid19-preprocessing

2. Acquiring validation data
-------------------------
To do this you require region-specific data related to Covid-19 spread. These could include:
* daily hospital admissions by region.
* daily intensive care unit admissions by region.
* daily intensive care unit bed occupancy (covid patients only) by region.

If you only have validation data for a single hospital, then you could choose to make a separate validation model, covering only the catchment area of the hospital, before developing the main simulation.

3. Acquiring demographics data
---------------------------
We provide example demographics data in https://www.github.com/djgroen/facs/covid_data/age-distr.csv . This data is loaded automatically into FACS on startup.

The data contains the number of citizens by age, with a generic group for people aged 90 and over. 
The layout of the file is as follows::

    Age,<borough name>,<borough2 name>,<country name>
    0,x,x,x
    1,x,x,x
    ...
    90+,x,x,x
    
Here you can add one new column for each new scenario location that you're adding. This could be a city or a country (if you plan to do a very large scale run). It is perfectly fine to remove columns of locations that you're not using, to make the file simpler.

4. Verifying the disease specification in disease.yml
-----------------------------------------------------

One of the input files is a definition of the disease one is trying to model. We provide a YML-based specification of an example interpretation of Covid-19 in the `covid_data` subdirectory for your convenience, see: https://github.com/djgroen/facs/blob/master/covid_data/disease_covid19.yml .

The exact format may still be subject to change, but among others we have fields for:

* *infection_rate* - indicates how fast the disease spreads.
* *mortality* - percentage of patients that do not survive the disease. This is binned, with each bin labelled with the mean age value of that bin (e.g., 4.5 for the range 0-9 years).
* *hospitalised* - percentage of patients that end up on **intensive care**. This is also binned, with each bin labelled with the mean age value of that bin (e.g., 4.5 for the range 0-9 years).
* *mortality_period* - mean duration from hospitalisation to death.
* *recovery_period* - mean duration from hospitalisation to recovery.
* *mild_recovery_period* - mean duration to recovery (i.e., no longer shedding viral particles) after infection.
* *incubation_period* - mean duration between receiving the virus and becoming infectious. NOTE: does not relate to exhibiting symptoms (!)
* *period_to_hospitalisation* - mean duration for severely ill patients between getting infected and being admitted to **intensive care**.
