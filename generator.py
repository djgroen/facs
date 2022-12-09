import numpy as np
import yaml

def population_generator(region, config_file, output_file):

    with open(config_file, 'r') as ff:
        pars = yaml.safe_load(ff)

    pop = []

    while len(pop) < int(pars['population']):

        rr = np.random.normal(float(pars['mu']), float(pars['sigma']), int(pars['population']))
        rr = [x for x in rr if x>0 and x<91]

        pop.extend(rr)

    pop = pop[:pars['population']]
    pop = [int(x) for x in pop]

    with open(output_file, 'w') as gg:
        gg.write('Age,{}'.format(region))
        gg.write('\n')
        for i in range(91):
            gg.write('{},{}'.format(i, pop.count(i)))
            gg.write('\n')


if __name__ == '__main__':
    population_generator('test_calarasi', 'population_generator.yml', '../config_files/test_calarasi/covid_data/age-distr.csv')