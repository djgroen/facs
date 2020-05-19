.. FACS documentation master file, created by
   sphinx-quickstart on Fri Apr 24 15:16:11 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Flu And Coronavirus Simulator (FACS)
=================================

Dependencies
-------------------
* PyYaml
* numpy

How to run the code
-------------------
To run a simple simulation of a basic test dataset, type:
`python3 run.py --location=test --transition_scenario=extend-lockdown --transition_mode=1 --output_dir=.`

To run a simulation of the Borough of Brent, type:
`python3 run.py --location=brent --transition_scenario=extend-lockdown --transition_mode=1 --output_dir=.`

Outputs are written as CSV files in the output\_dir. E.g. for the test run you will get:
covid\_out\_infections.csv
test-extend-lockdown-62.csv

There is a hardcoded lockdown in run.py which is representative for the UK. This can be disabled by selecting the transition scenario "no-measures".

We also included a simple plotting script. This can be called e.g. as follows:
`python3 PlotSEIR.py test-extend-lockdown-62.csv test`

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   preparation
   advanced_usage
   acknowledgements


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
