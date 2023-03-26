import os
import sys
import subprocess


def test_facs():
    """
    this is a simple FACS test users use a `test` borough
    """
    location = "test"
    TS = "extend-lockdown"
    TM = 1
    ci_multiplier = 0.475
    output_dir = "."
    data_dir = "covid_data"
    start_date = "3/1/2020"
    facs_args = ["--generic_outfile"]
    simulation_period = 60

    facs_args.append("--quicktest")
    facs_args.append("--location=%s" % (location))
    facs_args.append("--transition_scenario=%s" % (TS))
    facs_args.append("--transition_mode=%d" % (TM))
    facs_args.append("--ci_multiplier=%f" % (ci_multiplier))
    facs_args.append("--output_dir=%s" % (output_dir))
    facs_args.append("--data_dir=%s" % (data_dir))
    facs_args.append("--start_date=%s" % (start_date))
    facs_args.append("--simulation_period=%d" % (simulation_period))

    # prepare CMD
    CMD = ["python3", "run.py"]
    CMD.extend(facs_args)

    proc = subprocess.Popen(CMD, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()

    stderr = "{}".format(stderr)
    stderr = "{}".format(stderr)

    assert stderr.find("Simulation complete") >= 0


if __name__ == "__main__":
    test_facs()
