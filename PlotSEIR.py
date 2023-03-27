"""Simple plotter"""

import sys

import pandas as pd
import plotly as py
import plotly.graph_objects as go

df = pd.read_csv(sys.argv[1], delimiter=",")

df["new cases"] = df["exposed"].diff(1) + df["infectious"].diff(1)

fig = go.Figure()

# Add traces
fig.add_trace(
    go.Scatter(
        x=df["#time"],
        y=df["susceptible"],
        mode="lines+markers",
        name="susceptible",
        line=dict(color="orange"),
    )
)
fig.add_trace(
    go.Scatter(
        x=df["#time"],
        y=df["exposed"],
        mode="lines+markers",
        name="exposed",
        line=dict(color="purple"),
    )
)
fig.add_trace(go.Bar(x=df["#time"], y=df["new cases"], name="change in # affected"))
fig.add_trace(
    go.Scatter(
        x=df["#time"],
        y=df["infectious"],
        mode="lines+markers",
        name="infectious",
        line=dict(color="red"),
    )
)
fig.add_trace(
    go.Scatter(
        x=df["#time"],
        y=df["recovered"],
        mode="lines+markers",
        name="recovered",
        line=dict(color="green"),
    )
)
fig.add_trace(
    go.Scatter(
        x=df["#time"],
        y=df["dead"],
        mode="lines+markers",
        name="dead",
        line=dict(color="black"),
    )
)

py.offline.plot(fig, filename=f"{sys.argv[2]}.html")
