import pickle
from collections import defaultdict
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import rc
from matplotlib.colors import LinearSegmentedColormap

def get_overview(df_responses, df_background, userid="user_id"):
    """Print overview information about the dataset"""
    
    num_users = df_background[userid].nunique()
    sex = df_background["sex"].value_counts()
    total_responses = df_responses[userid].value_counts()
    min_responses = min(total_responses)
    mean_responses = total_responses.mean()
    max_responses = max(total_responses)
    ages = [2021 - age for age in df_background["yob"]]
    
    print(f"Number of users: {num_users}")
    print(f"Total number of responses: {df_responses.shape[0]}")
    print(f"Sex breakdown: {sex}")
    print(f"Ages: min {min(ages)}, max {max(ages)} ")
    print(f"Num of users with > 80 responses: {total_responses[total_responses >= 80].shape[0]}")
    print(f"Num of responses: min {min_responses}, avg {mean_responses}, max {max_responses}")
    

def vote_by_user(
    dataframe,
    dataset="dorn",
    show_percentages=False,
    preference_label="thermal_cozie",
    fontsize=40,
):
    """
    Original code by Dr. Federico Tartarini
    https://github.com/FedericoTartarini
    """

    df = dataframe.copy()
    df[preference_label] = df[preference_label].map(
        {9.0: "Warmer", 10.0: "No Change", 11.0: "Cooler"}
    )
    _df = (
        df.groupby(["user_id", preference_label])[preference_label]
        .count()
        .unstack(preference_label)
    )
    _df.reset_index(inplace=True)

    df_total = _df.sum(axis=1)
    df_rel = _df[_df.columns[1:]].div(df_total, 0) * 100
    df_rel["user_id"] = _df["user_id"]

    # sort properly
    df_rel["user_id"] = df_rel["user_id"].str.replace(dataset, "").astype(int)
    df_rel = df_rel.sort_values(by=["user_id"], ascending=False)
    df_rel["user_id"] = dataset + df_rel["user_id"].astype(str)
    df_rel = df_rel.reset_index(drop=True)

    # plot a Stacked Bar Chart using matplotlib
    rc("text.latex", preamble=r"\usepackage{cmbright}")
    rc("text", usetex=True)

    df_rel.plot(
        x="user_id",
        kind="barh",
        stacked=True,
        mark_right=True,
        cmap=LinearSegmentedColormap.from_list(
            preference_label,
            [
                "tab:blue",
                "tab:green",
                "tab:red",
            ],
            N=3,
        ),
        width=0.95,
        figsize=(16, 16),
    )

    plt.legend(
        bbox_to_anchor=(0.5, 1.02),
        loc="center",
        borderaxespad=0,
        ncol=3,
        frameon=False,
        fontsize=fontsize,
    )
    sns.despine(left=True, bottom=True, right=True, top=True)

    plt.tick_params(labelsize=fontsize * 0.75)
    plt.xlabel(r"Percentage [\%]", size=fontsize)
    plt.ylabel("User ID", size=fontsize)

    if show_percentages:
        # add percentages
        for index, row in df_rel.drop(["user_id"], axis=1).iterrows():
            cum_sum = 0
            for ix, el in enumerate(row):
                if np.isnan(el):
                    el = 0
                    
                if ix == 1:
                    plt.text(
                        cum_sum + el / 2 if not np.isnan(cum_sum) else el / 2,
                        index,
                        str(int(np.round(el, 0))) + "\%",
                        va="center",
                        ha="center",
                        size=fontsize * 0.6,
                    )
                cum_sum += el

    plt.tight_layout()
    plt.savefig(f"img/{dataset}_vote_dist.png", pad_inches=0, dpi=300)
    plt.show()
    
def tmp_skin_nb_survey(df_responses, fontsize=40):
    """
    Original code by Dr. Federico Tartarini
    https://github.com/FedericoTartarini
    """
    
    labels = {
        "percentage": "Percentage [%]",
        "subjects": "Participant ID",
        "heart_rate": "Heart rate [beats per minute]",
        "accuracy": "Prediction accuracy [%]",
        "data_points": "Training data points",
    }
    
    rc("text.latex", preamble=r"\usepackage{cmbright}")
    rc("text", usetex=True)
    
    fig, ax = plt.subplots(1, 1, sharex=True, sharey=True, figsize=(16, 16))
    surveys_completed = []
    df = df_responses.copy()

    df_count = df.groupby(["user_id"])["user_id"].count()
    df = df[["user_id", "skin_temp", "nb_temp"]].copy().set_index("user_id")

    df.columns = ["skin temp", r"nb temp"]
    # sort properly
    df.index = df.index.str.replace("enth", "").astype(int)
    df = df.sort_index()
    df.index = "enth" + df.index.astype(str)

    df = df.stack().reset_index()
    df.columns = ["user_id", "sensor", "value"]

    sns.violinplot(
        x="user_id",
        y="value",
        data=df,
        cut=0,
        scale="count",
        split=True,
        hue="sensor",
        inner="quartile",
        linewidth=1,
        ax=ax,
    )

    for ix, user in enumerate(df_count.index):
        ax.text(
            ix,
            37,
            df_count[df_count.index == user].values[0],
            horizontalalignment="center",
            verticalalignment="center",
            rotation=45,
            fontsize=fontsize
        )

    surveys_completed.append(df_count.values)
    
    plt.ylabel("Temperature [°C]", size=fontsize)
    plt.ylim((22, 37.5))
    plt.tick_params(labelsize=fontsize * 0.75)
    plt.xticks(rotation=45)

    if ax.get_subplotspec().rowspan.start == 1:
        ax.set(
            xlabel=labels["subjects"],
        )
        ax.get_legend().remove()
    else:
        ax.set(
            xlabel="",
        )
        ax.legend(
            bbox_to_anchor=(0, 1.02, 1, 0.2),
            loc="lower center",
            frameon=False,
            fontsize=fontsize,
            ncol=2,
        )

    sns.despine(left=True, bottom=True, right=True)
    ax.grid(axis="y", alpha=0.3)
    plt.xlabel("User ID", size=fontsize)
    plt.tight_layout()
    plt.savefig("img/tmp_skin_survey.png")


def surveys_plot(df_surveys, fontsize=40):
    columns = ["hsps", "swls", "extraversion", "agreeableness", "conscientiousness", "emotional_stability", "openness_to_experiences"]
    df_b5 = df_surveys[columns]
    df_b5.columns = ["HSPS", "SWLS", "Extraversion", "Agreeableness", "Conscientiousness", "Emotional stability", "Opennes to experiences"]

    means = [df_b5[column].mean() for column in df_b5.columns]
    stds = [np.std(df_b5[column]) for column in df_b5.columns]

    # SWLS needs to be rescaled
    means[1] = means[1]/5
    stds[1] = stds[1]/5

    fig, ax = plt.subplots(1, 1, figsize=(16,16))
    x_pos = np.arange(len(df_b5.columns))
    ax.bar(x_pos, means, yerr=stds, align='center', alpha=0.5, ecolor='black')
    ax.set_ylabel("Scores", size=fontsize)
    ax.set_xlabel("On-boarding surveys", size=fontsize)
    ax.set_xticks(np.arange(len(df_b5.columns)))
    ax.set_ylim((1, 7))
    ax.set_xticklabels(df_b5.columns)
    plt.tick_params(labelsize=fontsize * 0.75)
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.savefig("img/surveys.png")
    plt.show()