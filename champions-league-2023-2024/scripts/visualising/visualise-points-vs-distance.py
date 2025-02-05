import logging
import matplotlib.pyplot as plt
import numpy as np
import os
import sys

# get the absolute path of the project root (two levels up from current script)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../"))

# add project root to sys.path
sys.path.append(PROJECT_ROOT)

from adjustText import adjust_text
from scipy.stats import pearsonr, spearmanr
from utils.io import load_data


# configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


# analysed data and visualed paths
ANALYSED_DATA_PATH = "../../data/analysed/distance-points.csv"
VISUALISED_PATH = "../../figures/points-vs-distance.png"

# team labels
TEAM_LABELS = [
    "GS",
    "FCU",
    "SEV",
    "MUN",
    "NAP",
    "LAZ",
    "SLB",
    "ATM",
    "CEL",
    "POR",
    "BRA",
    "MCI",
    "SHK",
    "CZV",
    "FCK",
    "RMA",
    "RBS",
    "FCB",
    "BAR",
    "FEY",
    "ANT",
    "INT",
    "RSO",
    "NEW",
    "YB",
    "MIL",
    "RBL",
    "PSV",
    "ARS",
    "RCL",
    "BVB",
    "PSG",
]


def create_scatter_plot(
    x: np.ndarray, y: np.ndarray, labels: list, ax: plt.Axes
) -> None:
    """create a scatterplot with x and y values and annotate with team labels"""
    ax.scatter(x, y, color="#0077BB", alpha=0.7, edgecolors="black", linewidth=0.5)

    texts = [ax.text(x[i], y[i], label, fontsize=10) for i, label in enumerate(labels)]

    adjust_text(
        texts,
        ax=ax,
        force_text=0.3,
        force_points=0.3,
        expand_text=(1.2, 1.5),
        expand_points=(1.3, 1.5),
    )


def add_trendline(x: np.ndarray, y: np.ndarray, ax: plt.Axes) -> None:
    """create a linear trendline to the data and plot it"""
    m, b = np.polyfit(x, y, 1)
    trendline_y = m * x + b
    ax.plot(x, trendline_y, color="#CC3311", linestyle="--", linewidth=0.7)


def calculate_correlations(x: np.ndarray, y: np.ndarray, ax: plt.Axes) -> None:
    """calculate and log Pearson and Spearman correlation coefficients"""
    try:
        pearson_corr, _ = pearsonr(x, y)
        spearman_corr, _ = spearmanr(x, y)

        annotation = f"Pearson: {pearson_corr:.2f}\n" f"Spearman: {spearman_corr:.2f}"
        ax.text(
            0.05,
            0.95,
            annotation,
            transform=ax.transAxes,
            fontsize=10,
            verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="#CC3311", alpha=0.2),
        )
    except Exception as e:
        logging.error(f"error calculating correlations: {e}")


def format_plot(ax: plt.Axes) -> None:
    """format the plot with ticks, labels, and grid settings"""
    ax.set_xticks(np.arange(1500, 7000, 500))
    ax.set_yticks(np.arange(0, 11, 1))

    ax.set_ylabel("number of points", fontsize=12, fontweight="bold")
    ax.set_xlabel("distance travelled (km)", fontsize=12, fontweight="bold")
    ax.set_title("away points to distance correlation", fontsize=14, fontweight="bold")

    ax.set_xlim(min(ax.get_xticks()) - 200, max(ax.get_xticks()) + 200)
    ax.grid(linestyle="--", linewidth=0.3, alpha=0.8)


def save_figure(fig: plt.Figure, filepath: str) -> None:
    """save the figure as png"""
    try:
        fig.savefig(filepath, dpi=300)
        logging.info("successfully saved figure")
    except Exception as e:
        logging.error(f"error saving figure: {e}")


def main():
    """set up visualisation process"""
    logging.info("starting visualisation process")

    # load data
    df = load_data(ANALYSED_DATA_PATH)
    if df is None:
        logging.error("failed to load data")
        return

    # extract x and y values
    x = np.array(df["Travel Distance"])
    y = np.array(df["Away Points"])

    # create figure and axis
    fig, ax = plt.subplots(figsize=(8, 8))

    # visualise data
    create_scatter_plot(x, y, TEAM_LABELS, ax)
    add_trendline(x, y, ax)
    calculate_correlations(x, y, ax)
    format_plot(ax)

    # save visualisation
    save_figure(fig, VISUALISED_PATH)
    logging.info("visualisation was successful!")


if __name__ == "__main__":
    main()
