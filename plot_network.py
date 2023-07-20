"""Plot a network of an area."""

import matplotlib.pyplot as plt
import pandas as pd


def pre_process_data(dataframe: pd.DataFrame, location: str) -> pd.DataFrame:
    """Pre-process the data for plotting."""

    test = dataframe[location].value_counts()
    test_df = pd.DataFrame(test)
    test_df = test_df.rename(columns={location: "count"})
    test_df = test_df.reset_index()
    test_df = test_df.sort_values(by=["index"])

    return test_df


def pad_data(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Pad the data for plotting."""

    for checker in range(len(dataframe)):
        if checker not in dataframe["index"]:
            dataframe = dataframe.append(
                {"index": checker, "count": 0}, ignore_index=True
            )
    dataframe = dataframe.sort_values(by=["index"])
    return dataframe


def location_plotter(location: str, regions: list[str], log: bool = False) -> None:
    """Plot the data for a locationtype."""

    colors = ["red", "blue", "green"]

    plt.figure(figsize=(15, 5))
    plt.suptitle(f"Network of {location.title()}", fontsize=16)

    for index, region in enumerate(regions):
        dataframe = pd.read_csv(f"location_graphs/data/{region.lower()}_network.csv")
        test_df = pad_data(pre_process_data(dataframe, location))
        plt.subplot(1, 3, index + 1)
        if log:
            plt.yscale("log")
        plt.plot(
            test_df["index"], test_df["count"], "o-", markersize=2, color=colors[index]
        )
        plt.axhline(y=test_df["count"].mean(), color="magenta", linestyle="--")
        plt.axhline(y=test_df["count"].median(), color="black", linestyle="--")
        plt.title(region.title())

        plt.xlabel("Index of the location")
        if index == 0:
            plt.ylabel("Number of households connected")

    if log:
        plot_fname = f"location_graphs/plots/location_plots/{location}_network_log.png"
    else:
        plot_fname = f"location_graphs/plots/location_plots/{location}_network.png"

    plt.savefig(plot_fname)


def region_plotter(region: str, log: bool = False) -> None:
    """The main plotting function of the program."""

    plt.figure(figsize=(15, 15))
    plt.suptitle(f"Network of {region.title()}", fontsize=20)

    dataframe = pd.read_csv(f"location_graphs/data/{region.lower()}_network.csv")
    for index, location in enumerate(dataframe.columns):
        test_df = pad_data(pre_process_data(dataframe, location))
        plt.subplot(3, 3, index + 1)
        if log:
            plt.yscale("log")
            plot_fname = f"location_graphs/plots/region_plots/{region}_network_log.png"
        else:
            plot_fname = f"location_graphs/plots/region_plots/{region}_network.png"
        plt.plot(test_df["index"], test_df["count"], "o-", markersize=2, color="black")
        plt.title(location.title())

    plt.savefig(plot_fname)


if __name__ == "__main__":
    for region_name in ["calarasi", "klaipeda", "harrow"]:
        region_plotter(region_name, log=False)
        region_plotter(region_name, log=True)

    for location_name in [
        "park",
        "hospital",
        "supermarket",
        "office",
        "school",
        "leisure",
        "shopping",
    ]:
        location_plotter(location_name, ["calarasi", "klaipeda", "harrow"], log=False)
        location_plotter(location_name, ["calarasi", "klaipeda", "harrow"], log=True)
