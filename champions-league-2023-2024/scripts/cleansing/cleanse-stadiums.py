import pandas as pd
import logging
import re
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
RAW_DATA_PATH = "../../data/raw/stadiums.csv"
MATCH_DATA_PATH = "../../data/processed/cleansed/matches.csv"
CLEANSED_DATA_PATH = "../../data/processed/cleansed/stadiums.csv"

# dictionary with incorrect and correct stadiums names
STADIUMS_TO_FIX = {
    "Marakana": "Stadion Rajko Mitić",
    "De Kuip": "Stadion Feijenoord",
    "Estádio da Luz": "Estádio do Sport Lisboa e Benfica",
    "Olímpic Lluís Companys": "Estadi Olímpic Lluís Companys",
    "Cívitas Metropolitano": "Estadio Cívitas Metropolitano",
    "Ramón Sánchez Pizjuán": "Estadio Ramón Sánchez Pizjuán",
    "Santiago Bernabéu": "Estadio Santiago Bernabéu",
    "Diego Maradona": "Stadio Diego Armando Maradona",
    "Giuseppe Meazza": "Stadio Giuseppe Meazza",
    "Olimpico": "Stadio Olimpico",
}

# dictionary with similar stadium names
CITY_STADIUM_FIXES = {
    "Wals-Siezenheim": "Red Bull Arena (Salzburg)",
    "Leipzig": "Red Bull Arena (Leipzig)",
}


def preprocess_stadium_data(df: pd.DataFrame):
    """introduce minor changes"""
    logging.info("preprocessing stadium data")
    df.rename(columns={"stadium": "Venue"}, inplace=True)
    df["Capacity"] = (df["Capacity"] * 1000).astype(int)

    # remove the last row
    df.drop(index=(len(df) - 1), inplace=True, axis=1)

    return df


def get_unique_stadium_names(matches_df: pd.DataFrame):
    """extract unique stadium names from the matches dataframe"""
    return set(matches_df["Venue"].dropna().unique())


def fix_stadium_names(df: pd.DataFrame, stadiums: set):
    """dynamically correct stadium names"""
    logging.info("fixing stadium name dynamically")

    for arena in df["Venue"]:
        for stadium in stadiums:
            if re.match(rf"{arena.lower()}", stadium.lower()):
                df["Venue"] = df["Venue"].str.replace(arena, stadium, regex=True)

    return df


def apply_manual_stadium_names(df: pd.DataFrame):
    """apply predefined manual fixes for stadium names."""
    logging.info("applying manual stadium name fixes")

    df["Venue"] = df["Venue"].replace(STADIUMS_TO_FIX)

    for city, venue in CITY_STADIUM_FIXES.items():
        df.loc[df["City"] == city, "Venue"] = venue

    return df


def add_new_stadium(df: pd.DataFrame):
    """add 'San Siro' as Milan's home stadium"""
    logging.info("adding Milan's home stadium")

    milano = df[df["City"] == "Milano"].copy()
    milano["Venue"] = "Stadio San Siro"

    return pd.concat([df, milano], ignore_index=True)


def main():
    """set up data cleansing process"""
    logging.info("starting data cleaning process")

    try:
        # load data
        df_stadiums = load_data(RAW_DATA_PATH)
        df_matches = load_data(MATCH_DATA_PATH)

        # apply transformations
        df_stadiums = preprocess_stadium_data(df_stadiums)
        unique_stadiums = get_unique_stadium_names(df_matches)
        df_stadiums = fix_stadium_names(df_stadiums, unique_stadiums)
        df_stadiums = apply_manual_stadium_names(df_stadiums)
        df_stadiums = add_new_stadium(df_stadiums)

        # save cleansed data
        save_to_csv(df_stadiums, CLEANSED_DATA_PATH)
        logging.info("data cleansing was successful!")
    except Exception as e:
        logging.error(f"data cleansing process failed: {e}")


if __name__ == "__main__":
    main()
