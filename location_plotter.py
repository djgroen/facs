import plotly.express as px
import pandas as pd


def plot_location(location, types="all", remove_houses=True):
    fname = "covid_data/" + location + "_buildings.csv"

    df = pd.read_csv(fname, names=["type", "lon", "lat", "area"])
    print(df)

    if types != "all":
        df = df[df["type"] == types]

    if remove_houses:
        df = df[df["type"] != "house"]

    fig = px.scatter_mapbox(df, lon="lon", lat="lat", color="type", zoom=10)
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    fig.show()

    return df


if __name__ == "__main__":
    df = plot_location("blackpool")
