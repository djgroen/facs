.. FACS documentation master file, created by
   sphinx-quickstart on Fri Apr 24 15:16:11 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Flu And Coronavirus Simulator (FACS)
====================================

FACS is an agent-based modelling code that models the spread of flu and coronaviruses in local regions. Up to now, we have used it to model the spread of Covid-19 in various regions of Europe:

* **The United Kingdom:** Greater London, South-East and North-West of England
* **Lithuania:** The region of Klaipėda
* **Romania:** The city of Călărași
* **Türkiye:** The cities of Ankara and Istanbul

The code can be repurposed to model other regions, and its current (sequential) implementation should be able to run up to 2 million households within a reasonable time frame. It also supports  the implementation of lockdown measures, vaccination programmes, track and trace and mutated versions of the virus.

What sets FACS apart from many other codes is that we have a partially automated location extraction approach from OpenStreetMaps data (the scripts reside at https://www.github.com/djgroen/covid19-preprocess), that we resolve a wide range of different location types (e.g., supermarkets, offices, parks, schools, leisure locations and hospitals) and that we have a specific algorithm for modeling infections *within* these locations, taking into account the physical size of each location.

We are currently finalizing a first journal paper about FACS, and will link to it from this page once it has become available.

Quick installation notes
========================

To install FACS, simply clone the GitHub repository, and ensure the dependencies are met.
 
.. code:: console

          git clone https://github.com/djgroen/facs.git


These dependencies are:

* PyYaml
* numpy
* pandas

How to run the code
-------------------
To run a simple simulation of a basic test dataset, type:
`python3 run.py -g --location=test --output_dir=.`

Here, the `-g` flag indicates that output will be written to out.csv, instead of an output file with a more specific name.

To run a simulation of the Borough of Brent, type:
`python3 run.py --location=brent --measures_yml=measures --output_dir=.`

Note that in this case, we explicitly specify the measures YML file that we wish to use. This is done in the format:
`covid_data/<measures_yml>.yml`

So in this case FACS will use the file `covid_data/measures.yml`.

Outputs are written as CSV files in the output\_dir. E.g. for the test run you will get:
covid\_out\_infections.csv
test-extend-lockdown-62.csv

There is a hardcoded lockdown in run.py which is representative for the UK. This can be disabled by selecting the transition scenario "no-measures".

We also included a simple plotting script. This could be called e.g. as follows:
`python3 PlotSEIR.py out.csv test`
(this has not been tested in a while, as we usually use FabCovid19 for plotting these days)

Citing FACS
-----------

Our journal paper on FACS has now been accepted, and can be found here:
https://bura.brunel.ac.uk/handle/2438/20914

The BibTex code is here::

  @article{mahmood2020facs,
    title={FACS: A geospatial agent-based simulator for analyzing COVID-19 spread and public health measures on local regions},
    author={Mahmood, Imran and Arabnejad, Hamid and Suleimenova, Diana and Sassoon, Isabel and Marshan, Alaa and Serrano, Alan and Louvieris, Panos and Anagnostou, Anastasia and Taylor, S and Bell, David and others},
    year={2020},
    journal={Journal of Simulation (in press)}
    publisher={Taylor \& Francis}
  }

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   preparation
   advanced_usage
   fabcovid19
   acknowledgements


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
