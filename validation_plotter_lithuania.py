import pandas as pd
import plotly.express as px
import datetime as dt

dd = pd.read_csv("validation/lithuania_processed.csv", header=2)

dd = dd[["date", "infectious"]]
dd["date"] = pd.to_datetime(dd["date"]).dt.date
dd = dd[dd["infectious"] != -1]
dd.sort_values(by="date", inplace=True)
dd = dd.set_index("date")
dd = dd.rename(columns={"infectious": "data"})

df = pd.read_csv("klaipeda-measures_lt.csv")
df["date"] = pd.to_datetime(df["date"], dayfirst=True).dt.date

df = df.set_index("date")
df = pd.DataFrame(df["infectious"])
df = df.rename(columns={"infectious": "predicted"})

d = df.join(dd)

fig = px.line(d)
fig.update_layout(
    title="No. of infections over time",
    xaxis_title="Date",
    yaxis_title="No. of infections",
    legend_title="",
)
fig.show()
