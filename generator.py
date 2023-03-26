import numpy as np
import yaml
import argparse
import os


def population_generator(region, config_file, output_file):
    with open(config_file, "r") as ff:
        pars = yaml.safe_load(ff)

    pop = []

    while len(pop) < int(pars["population"]):
        rr = np.random.normal(
            float(pars["mu"]), float(pars["sigma"]), int(pars["population"])
        )
        rr = [x for x in rr if x > 0 and x < 91]

        pop.extend(rr)

    pop = pop[: pars["population"]]
    pop = [int(x) for x in pop]

    with open(output_file, "w") as gg:
        gg.write("Age,{}".format(region))
        gg.write("\n")
        for i in range(91):
            gg.write("{},{}".format(i, pop.count(i)))
            gg.write("\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--location", action="store", default="test_calarasi", help="Name of location."
    )
    parser.add_argument(
        "--cwd", action="store", default=".", help="Current working directory"
    )
    args = parser.parse_args()
    print(args)

    population_generator(
        args.location, "covid_data/population_generator.yml", "covid_data/age-distr.csv"
    )
