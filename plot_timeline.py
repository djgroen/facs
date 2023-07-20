""" Plots the timeline of Calarasi, Klaipeda and Harrow for SA paper"""

import matplotlib.pyplot as plt
import pandas as pd


def collect_data(col_name: str) -> pd.DataFrame:
    """Collect the data for a locationtype."""

    dataframe = pd.DataFrame()

    dataframe["time"] = range(1, 401)

    regions = ["calarasi", "klaipeda", "harrow"]

    for region in regions:
        temp_df = pd.DataFrame()
        for replica in range(1, 51):
            file_location = f"/home/arindam/FabSim3/results/measures_uk_{region}_archer2_128_replica_{replica}/out.csv"
            temp_df[f"run_{replica}"] = pd.read_csv(file_location)[col_name]

        dataframe[region] = temp_df.mean(axis=1)
        dataframe[f"{region}_std"] = temp_df.std(axis=1)

    return dataframe


if __name__ == "__main__":
    regions = ["calarasi", "klaipeda", "harrow"]
    labels = ["Călărași", "Klaipėda", "Harrow"]
    columns = ["infectious", "num hospitalisations today"]
    colors = ["red", "green", "blue"]

    all_data = {}

    fig, axes = plt.subplots(1, 2, figsize=(15, 5), sharey=False)

    for index, column in enumerate(columns):
        ax = axes[index]

        data = collect_data(column)
        all_data[column] = data
        print(data.head())

        # plt.suptitle("Timeline of Calarasi, Klaipeda and Harrow", fontsize=16)
        # ax.set_xlabel("Time (days)")
        # ax.set_ylabel(column.title())

        ax.set_xlabel("Time (days)")
        if column == "infectious":
            ax.set_ylabel("No. of infectious people")
        elif column == "num hospitalisations today":
            ax.set_ylabel("No. of new hospital admissions on each day")
        # ax.set_yscale("log")

        for index, region in enumerate(regions):
            ax.plot(
                data["time"],
                data[region],
                "-",
                markersize=2,
                color=colors[index],
                label=labels[index],
            )

            ax.fill_between(
                data["time"],
                data[region] + 1.96 * data[f"{region}_std"],
                data[region] - 1.96 * data[f"{region}_std"],
                color=colors[index],
                alpha=0.2,
            )

    plot_fname = "timeline_combined.png"
    plt.legend()
    plt.savefig(plot_fname, dpi=300, bbox_inches="tight")
    plt.close()

    # Plot the hospitalisation/infection ratio

    fig, ax = plt.subplots()
    # plt.suptitle("Timeline of Calarasi, Klaipeda and Harrow", fontsize=16)
    ax.set_xlabel("Time (days)")
    ax.set_ylabel("Hospitalisation/Infection Ratio")
    # ax.set_yscale("log")

    for index, region in enumerate(regions):
        data_mean = (
            all_data["num hospitalisations today"][region]
            / all_data["infectious"][region]
        )
        error = data_mean * (
            all_data["num hospitalisations today"][f"{region}_std"]
            / all_data["num hospitalisations today"][region]
            + all_data["infectious"][f"{region}_std"] / all_data["infectious"][region]
        )

        ax.plot(
            data["time"],
            data_mean,
            "-",
            markersize=2,
            color=colors[index],
            label=labels[index],
        )

        # ax.fill_between(
        #     data["time"],
        #     data_mean + 1.96 * error,
        #     data_mean - 1.96 * error,
        #     color=colors[index],
        #     alpha=0.2,
        # )

    plt.legend()
    plot_fname = "timeline_hospitalisation_infection_ratio.png"
    plt.savefig(plot_fname, dpi=300, bbox_inches="tight")
    plt.close()
