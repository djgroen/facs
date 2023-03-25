import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

df = pd.read_csv("harrow_network.csv")

print(df)

dd = {}

# for location in df.columns:

#     dd[location] = [set(f"{location}_{x}" for x in df[location])]

# print(dd)

for location in df.columns:

    test = df[location].value_counts()

    print(np.histogram(test))

    print(location, len(list(test)))

    plt.hist(np.histogram(test))

    plt.show()
