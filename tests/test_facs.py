"""Basic test for facs"""

import os
import subprocess


def test_facs():
    """
    this is a simple FACS test users use a `test` borough
    """

    if os.path.exists("out.csv"):
        os.remove("out.csv")

    location = "test"
    output_dir = "."
    data_dir = "covid_data"
    start_date = "3/1/2020"
    facs_args = ["--generic_outfile"]
    simulation_period = 60

    facs_args.append("--quicktest")
    facs_args.append(f"--location={location}")
    facs_args.append(f"--output_dir={output_dir}")
    facs_args.append(f"--data_dir={data_dir}")
    facs_args.append(f"--start_date={start_date}")
    facs_args.append(f"--simulation_period={simulation_period}")

    # prepare CMD
    command = ["python3", "run.py"]
    command.extend(facs_args)

    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()

    stderr = f"{stderr}"
    stdout = f"{stdout}"

    assert stderr.find("Simulation complete") >= 0
    assert os.path.exists("out.csv")
    os.remove("out.csv")


if __name__ == "__main__":
    test_facs()
