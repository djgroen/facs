import pandas as pd
import matplotlib
matplotlib.use('Pdf')
import matplotlib.pyplot as plt
import numpy as np
import sys
import warnings
from datetime import datetime

warnings.filterwarnings("ignore")



def load_output_data(out_dir):
    facs_output = pd.read_csv(
        "%s/out.csv" % (out_dir), sep=',', encoding='latin1')

    return facs_output
        

if __name__ == "__main__":
    d_sim = load_output_data(sys.argv[1])
    d_sif = load_output_data(sys.argv[2])
    start_date = datetime.strptime('1/3/2020', '%d/%m/%Y')

    # dict building
    comparison_table = {'days':[], 'admissions':[], 'admissions sim':[]}

    for index, row in d_sif.iterrows():
        day = int(row['#time'])
        adm = int(row['num hospitalisations today'])
        adm_sim = d_sim.loc[d_sim['#time'] == day]['num hospitalisations today'].values[0]
        comparison_table['days'].append(day) 
        comparison_table['admissions'].append(adm) #admissions for SIF (stable intermediate form).
        comparison_table['admissions sim'].append(adm_sim)

    # conversion from dict to DF.
    d_val = pd.DataFrame.from_dict(comparison_table)

    # df extension
    d_val['cum admissions'] = d_val['admissions'].cumsum()
    d_val['cum admissions sim'] = d_val['admissions sim'].cumsum()
    d_val['admissions error'] = (d_val["cum admissions"] - d_val['cum admissions sim']).abs()

    print("input directory: {}".format(sys.argv[1]))
    print("totals:")
    print("  length: {}".format(len(d_val['cum admissions sim'])))
    print("  cumulative admissions SIF: {}".format(d_val['cum admissions'].iloc[-1]))
    print("  cumulative admissions this code: {}".format(d_val['cum admissions sim'].iloc[-1]))
    print("  MAPE: {}".format(d_val['admissions error'].mean() / d_val['cum admissions'].mean()))

    #print(d_val['admissions error'].mean(), d_val['cum admissions'].mean(), d_val['admissions error'].mean() / d_val['cum admissions'].mean())
