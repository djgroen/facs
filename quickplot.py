import pandas as pd

pd.options.plotting.backend = "plotly"
import sys

df = pd.read_csv(sys.argv[1])
fig = df.plot()
fig.show()
