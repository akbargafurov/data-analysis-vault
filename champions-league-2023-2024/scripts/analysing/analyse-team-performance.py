import pandas as pd
import logging
import sys
import os

# get the absolute path of the project root (two levels up from current script)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../"))

# add project root to sys.path
sys.path.append(PROJECT_ROOT)

from utils.io import load_data, save_to_csv


# configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


# define constants
# transformed and analysed data paths
TRANSFORMED_DATA_PATH = "../../data/processed/transformed/matches-stadiums.csv"
ANALYSED_DATA_PATH = "../../data/analysed/distance-points.csv"


def analyse_away_team_performance(df: pd.DataFrame) -> pd.DataFrame:
    """analyse the correlation between away teams' perfomance and travel distance"""
    try:
        logging.info("analysing away team performance")

        away_distance_df = df[["Away", "Travel Distance", "Away Points"]]
        result_df = (
            away_distance_df.groupby("Away")
            .sum()
            .sort_values("Travel Distance", ascending=False)
            .reset_index()
        )

        return result_df
    except Exception as e:
        logging.error(f"error analysing away team performance: {e}")
        raise


def main():
    """set up data analysis process"""
    logging.info("starting data analysis process")

    try:
        # load data
        df = load_data(TRANSFORMED_DATA_PATH)

        # analyse data
        result_df = analyse_away_team_performance(df)

        # save analysed data
        save_to_csv(result_df, ANALYSED_DATA_PATH)
        logging.info("data analysis was successful!")
    except Exception as e:
        logging.error(f"data analysis process failed: {e}")


if __name__ == "__main__":
    main()
