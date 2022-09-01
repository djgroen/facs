.. _preparation:

.. Preparing simulations
.. ========================

=====================
Preparing simulations
=====================
To prepare simulations for a specific region, you will require to do undertake the following steps:

#. Extract building CSV files from geospatial data.
#. Acquiring validation data.
#. Acquiring demographics data.
#. Verifying the disease specification in disease.yml.
#. Defining the exact public health interventions undertaken, their timing and estimated compliance rate.


1. Extract building CSV files
=============================

This can be done e.g. using the scripts availably at https://www.github.com/djgroen/covid19-preprocess

The first thing you will need is an OSM file of the region of interest. You can obtain these e.g. by exporting them from Openstreetmaps.org, or using the OSRM tool.

Next, you need to extract locations from the OSM file. You can do this using:
`python3 extract_<location_type>.py <osm_file> > <out_dir>/<location_type>.csv`

The location types required are:

* houses
* offices
* hospitals
* parks (this includes leisure locations)
* schools
* supermarkets

All these locations will be stored in separate CSV files, so that they are easy to inspect manually. To then create a buildings.csv for FACS, simply concatenate all the previously extracted locations into one CSV file.

Notes on specific buildings:
----------------------------

**Houses**: The current extract_houses.py script generates houses randomly within the OSM residential zones. This is because in London there is no comprehensive data on individual house buildings available. Such data is available for cities in e.g. the Netherlands and Germany, so one could choose to extract individual houses there for a more accurate house distribution.

**Offices**: Many local regions have a very large mismatch between the number of houses and the number of offices, as many workers commute elsewhere. Currently, we generate *random* offices across the borough in FACS. However, explicit offices can be placed by uncommenting the line in this if statement: https://github.com/djgroen/facs/blob/1a9fd43f73ba672e3caf95c38c8c2ed6d3010ba8/readers/read_building_csv.py#L81 . If it turns out that this feature is desirable for anyone, then we will refactor the code and offer this functionality as a run-time parameter (just raise an issue in the FACS repo).

2. Acquiring validation data
============================
To do this you require region-specific data related to Covid-19 spread. These could include:

* daily hospital admissions by region.
* daily intensive care unit admissions by region.
* daily intensive care unit bed occupancy (covid patients only) by region.

If you only have validation data for a single hospital, then you could choose to make a separate validation model, covering only the catchment area of the hospital, before developing the main simulation.

3. Acquiring demographics data
==============================
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
=====================================================

One of the input files is a definition of the disease one is trying to model. We provide a YML-based specification of an example interpretation of Covid-19 in the `covid_data` subdirectory for your convenience, see: https://github.com/djgroen/facs/blob/master/covid_data/disease.yml .

Within this file we have fields for:

* *infection_rate* - indicates how fast the disease spreads.
* *mortality* - percentage of patients that do not survive the disease. This is binned, with each bin labelled with the mean age value of that bin (e.g., 4.5 for the range 0-9 years).
* *hospitalised* - percentage of patients that end up on **intensive care**. This is also binned, with each bin labelled with the mean age value of that bin (e.g., 4.5 for the range 0-9 years).
* *mortality_period* - mean duration from hospitalisation to death.
* *recovery_period* - mean duration from hospitalisation to recovery.
* *mild_recovery_period* - mean duration to recovery (i.e., no longer shedding viral particles) after infection.
* *incubation_period* - mean duration between receiving the virus and becoming infectious. NOTE: does not relate to exhibiting symptoms (!)
* *period_to_hospitalisation* - mean duration for severely ill patients between getting infected and being admitted to **intensive care**.
* *immunity_period* - mean duration for recovered people to become susceptible to the disease again.

In addition, we have a separate entry for each mutation, which can have modified properties. This is done in the following format:

.. code-block:: yml
   mutations:
     type: alpha
     infection_rate: 0.1

In this example we define a mutation named `alpha`, which has a modified infection rate of 1.0. Other parameters cannot be overridden yet at this time, but we are open to supporting this in the near future.

5. Defining the exact public health interventions undertaken
============================================================

Detailed documentation for this step has yet to be developed, as the format is still subject to change. However, by default FACS will look at the file in `covid_data/measures.yml` to extract the exact interventions required for the run. Below, we will explain how you can customize the interventions:

The restrictions and measures including government interventions taken to mitigate the spread of disease are specified in a `yml` file named `measures_<location>.yml`. In this file, a list of dates on which the restrictions were imposed or modified is given. Corresponding to each date, a description of the restrictions are given. These restrictions can be defined in terms the following heads.

- **`case_isolation`**: A binary value which determines if infected people go into quarantine.
- **`household_isolation`**: A binary value which decides if all members of the household go into quarantine when at least one of its members is isolated.
- **`traffic_multiplier`**: Volume of internal traffic within the region as compared to the normal (a non-lock-down situation).
- **`external_multiplier`**: Volume of external traffic coming into (or going out of) the region as compared to the normal (a non-lock-down situation).
- **`work_from_home`**: Fraction of workforce which is working from home.
- **`social_distancing`**: Fraction of the population that complies with the social distancing guidelines.
- **`mask_uptake`**: Fraction of the population wearing masks outside of the house.
- **`mask_uptake_shopping`**: Fraction of the population wearing masks while in shops or supermarkets.
- **`track_trace_efficiency`**: Fraction of the population who escape the track and trace system.
- **`closure`**: List of building types which are closed for the public.
- **`partial_closure`**: List of tuples which define the extent of closures (on a scale from 0-1) for building types.

In addition to to list of dates, the `yml` file should also have a key called `keyworker_fraction` with a value giving the fraction of key workers in the population. This is the fraction of employees who go to the workplace despite the lock-down. A sample section of a measures file is given below.::

  keyworker_fraction: 0.2

  1/3/2020:
    case_isolation: True
    household_isolation: True
    traffic_multiplier: 0.8

  12/3/2020:
    partial_closure: 
      leisure: 0.3
    work_from_home: 0.325
    social_distance: 0.25
    mask_uptake: 0.05
    traffic_multiplier: 0.4
    external_multiplier: 0.7

  20/3/2020:
    closure: ["leisure"]
    partial_closure: 
      shopping: 0.3
    work_from_home: 0.45
    mask_uptake: 0.2
    mask_uptake_shopping: 0.6
    traffic_multiplier: 0.3
    external_multiplier: 0.7


The above example highlights following two two important features of the restrictions and measures file.

At the start of the simulations, no restrictions are assumed. In other words,::

   case_isolation: False
   household_isolation: False
   traffic_multiplier: 1.0
   external_multiplier: 1.0
   work_from_home: 0.0
   social_distancing: 0.0
   mask_uptake: 0.0
   mask_uptake_shopping: 0.0
   track_trace_efficiency: 1.0
   closure: []
   partial_closure: []
  
   
Therefore, in the above example, on 1/3/2020, only `case_isolation` and `household_isolation` are switched to True. There are no other restrictions applied.
   
If for a particular date, a variable is not mentioned, then its value remains unchanged. In the above example, `social_distancing` is not mentioned for 20/3/2020. Therefore, its value is assumed to be 0.25, which remains unchanged from 12/3/2020.

Lastly, note that interventions related to public transport are not yet incorporated into this format. However, we hope to do this in Q2/Q3 2021.

6. Defining the vaccination strategy
====================================

Similarly, FACS is also able to read the vaccination strategy from a file. By default, the file in `covid_date/vaccinations.yml` will be read to extract the vaccination strategy.

You can find a realistic example of this file in this repository.

Booster vaccine mechanisms are not yet supported in this file format, but the effect of boosters can be mimicked by modifying the vaccine efficacy over time.
