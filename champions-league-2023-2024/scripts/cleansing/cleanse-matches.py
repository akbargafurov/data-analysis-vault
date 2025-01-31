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
# raw and cleansed data paths
RAW_DATA_PATH = "../../data/raw/matches.csv"
CLEANSED_DATA_PATH = "../../data/processed/cleansed/matches.csv"

# list of unnecessary columns
UNNECESSARY_COLUMNS = [
    "Wk",
    "Day",
    "Date",
    "Time",
    "xG",
    "xG.1",
    "Referee",
    "Match Report",
    "Notes",
]

# list of country codes
COUNTRY_CODES = [
    "it",
    "es",
    "eng",
    "de",
    "fr",
    "nl",
    "ua",
    "tr",
    "pt",
    "at",
    "dk",
    "be",
    "sct",
    "rs",
    "ch",
]

# dictionary with incorrect and correct stadiums names
STADIUMS_TO_FIX = {
    "Volksparkstadion (1953)": "Volksparkstadion",
    "Stadium Metropolitano": "Estadio Cívitas Metropolitano",
    "Trainingsgelände Allianz Arena": "Allianz Arena",
    "Arsenal Stadium": "Emirates Stadium",
    "Fælledparken Kunst": "Parken",
    "Estádio Do Dragão": "Estádio do Dragão",
}


def drop_unnecessary_columns(df: pd.DataFrame, columns: list):
    """drop specified columns"""
    logging.info("removing unnecessary columns")
    return df.drop(columns=columns, axis=1)


def drop_missing_values(df: pd.DataFrame):
    """drop empty rows"""
    logging.info("removing empty rows")
    return df.dropna().reset_index(drop=True)


def filter_group_stage(df: pd.DataFrame):
    """filter the dataset to include only group stage fixtures"""
    logging.info("filtering only group stage matches")
    return df[df["Round"] == "Group stage"].drop(columns=["Round"], axis=1)


def clean_club_names(df: pd.DataFrame, country_codes: list):
    """clean club names by removing country codes"""
    away_pattern = r"^[a-z]{2,3}"
    df["Away"] = df["Away"].str.replace(away_pattern, "", regex=True)

    for i, home in df["Home"].items():
        for away in df["Away"]:
            for country in country_codes:
                if away + country == home:
                    df.at[i, "Home"] = away

    logging.info("successfully cleaned club names")
    return df


def clean_attendance(df: pd.DataFrame):
    """remove commas from attendance and convert it into integers"""
    logging.info("cleaning attendance column")
    df["Attendance"] = df["Attendance"].str.replace(",", "").astype(int)
    return df


def fix_stadium_names(df: pd.DataFrame, stadiums_to_fix: dict):
    """replaces incorrect stadium names with correct ones"""
    logging.info("fixing stadium names")
    df["Venue"] = df["Venue"].replace(stadiums_to_fix)

    df.loc[
        (df["Home"] == "RB Salzburg") & (df["Venue"] == "Red Bull Arena"), "Venue"
    ] = "Red Bull Arena (Salzburg)"
    df.loc[
        (df["Home"] == "RB Leipzig") & (df["Venue"] == "Red Bull Arena"), "Venue"
    ] = "Red Bull Arena (Leipzig)"
    df.loc[
        (df["Home"] == "Milan") & (df["Venue"] == "Stadio Giuseppe Meazza"), "Venue"
    ] = "Stadio San Siro"

    logging.info("successfully fixed stadium names")
    return df


def main():
    """set up data cleansing process"""
    logging.info("starting data cleaning process")

    try:
        # load data
        df = load_data(RAW_DATA_PATH)

        # apply transformations
        df = drop_unnecessary_columns(df, UNNECESSARY_COLUMNS)
        df = drop_missing_values(df)
        df = filter_group_stage(df)
        df = clean_club_names(df, COUNTRY_CODES)
        df = clean_attendance(df)
        df = fix_stadium_names(df, STADIUMS_TO_FIX)

        # save cleansed data
        save_to_csv(df, CLEANSED_DATA_PATH)
        logging.info("data cleansing was successful!")
    except Exception as e:
        logging.error(f"data cleansing process failed: {e}")


if __name__ == "__main__":
    main()
