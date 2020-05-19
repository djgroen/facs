Advanced usage
==============

Running with a specific data directory
--------------------------------------

FACS can be run with a different input data directory as follows:
`python3 run.py --location=brent --transition_scenario=extend-lockdown --transition_mode=1 --output_dir=. --data_dir=/home/derek/covid19-postprocess/flacs_input_private`

Performing quick tests
----------------------

Quick tests can be triggered with the '-q' flag. This sets the house ratio to 100 (default is 2), which means that households will be less well distributed.
However, as a number of calculations are performed on the house level (not the household level), this setting speeds up the code by up to an order of magnitude.
`python3 run.py -q --location=brent --transition_scenario=extend-lockdown --transition_mode=1 --output_dir=.`
