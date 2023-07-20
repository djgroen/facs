"""Plot the histograms of the data."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def pre_process_data(dataframe: pd.DataFrame, location: str) -> pd.DataFrame:
    """Pre-process the data for plotting."""

    test = dataframe[location].value_counts()
    test_df = pd.DataFrame(test)
    test_df = test_df.rename(columns={location: "count"})
    test_df = test_df.reset_index()
    test_df = test_df.sort_values(by=["index"])

    return test_df


regions = ["calarasi", "klaipeda", "harrow"]
colors = ["red", "green", "blue"]

fig, ax = plt.subplots(1, 3, figsize=(15, 5), sharey=False)
for axis in ax:
    axis.set_yscale("log")

print("Region,Park,Hospital,Supermarket,Office,School,Leisure,Shopping,Overall")

for rindex, region in enumerate(regions):
    dataframe = pd.read_csv(f"location_graphs/data/{region.lower()}_network.csv")

    degrees = []
    print(region.title(), end=",")

    for index, location in enumerate(dataframe.columns):
        if location in [
            # "office",
            #     "hospital",
            #     "school",
            #     "park",
            #     "leisure",
            #     "shopping",
        ]:
            continue

        test_df = pre_process_data(dataframe, location)
        degrees.extend(list(test_df["count"]))
        print("{:.2f}".format(test_df["count"].mean()), end=",")

    his = ax[rindex].hist(
        degrees,
        bins=50,
        histtype="step",
        color=colors[rindex],
        label=region.title(),
    )
    # print(sum(his[0]))
    # y = his[1][:-1]
    # x = his[0]

    # fit = np.polyfit(x, np.log(y), deg=1)
    # print(fit)

    # print(x)
    # print(np.exp(fit[1]) * np.exp(fit[0] * x))

    # ax[rindex].plot(x, np.exp(fit[1]) * np.exp(fit[0] * x), color="black")

    # print(len(x))
    # print(len(y))

    degrees = np.array(degrees)
    # print(len(degrees))
    print("{:.2f}".format(degrees.mean()))
    # print(degrees.std())

plt.show()


regions = [
    "Park",
    "Hospital",
    "Supermarket",
    "Office",
    "School",
    "Leisure",
    "Shopping",
    "Overall",
]
calarasi = [4564.67, 13694.00, 9129.33, 133.27, 2608.38, 2028.74, 7825.14, 785.72]
klaipeda = [2786.52, 11610.50, 2402.17, 133.20, 1290.06, 548.53, 1180.73, 592.52]
harrow = [1264.03, 12008.25, 3202.20, 133.06, 738.97, 432.73, 787.43, 513.33]

x = np.arange(8)
width = 0.2

plt.figure(figsize=(10, 5))
plt.bar(x - 0.2, calarasi, width, color="red")
plt.bar(x, klaipeda, width, color="green")
plt.bar(x + 0.2, harrow, width, color="blue")
plt.xticks(x, regions)
plt.xlabel("Amenities")
plt.ylabel("Mean no. of visitors")
plt.legend(["Călărași", "Klaipėda", "Harrow"])
plt.savefig("degree_distribution.png")
plt.show()
