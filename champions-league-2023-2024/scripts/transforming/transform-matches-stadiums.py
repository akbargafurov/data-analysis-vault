import logging
import os
import pandas as pd
import re
import sys
from geopy import Nominatim
from geopy.distance import geodesic

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
MATCH_DATA_PATH = "../../data/processed/cleansed/matches.csv"
STADIUMS_DATA_PATH = "../../data/processed/cleansed/stadiums.csv"
TRANSFORMED_DATA_PATH = "../../data/processed/transformed/matches-stadiums.csv"

# initialize geolocator and cache
geolocator = Nominatim(user_agent="geo_distance_calculator", timeout=10)
city_coords_cache = {}

# compile the score pattern
score_regex = re.compile(r"(\d+)\u2013(\d+)$")


def get_city_coords(city: str):
    """return latitude & longitude for a given city, using caching to avoid repeated requests"""
    if city not in city_coords_cache:
        try:
            location = geolocator.geocode(city)
            if not location:
                raise ValueError(f"could not geocode city: {city}")
            city_coords_cache[city] = (location.latitude, location.longitude)
        except Exception as e:
            logging.error(f"error geocoding {city}: {e}")
            raise

    return city_coords_cache[city]


def determine_result(score: str):
    """determine the match result"""
    match = score_regex.search(score)
    if match:
        home_score, away_score = int(match.group(1)), int(match.group(2))
        if home_score > away_score:
            return "Home Win"
        elif home_score < away_score:
            return "Away Win"
        else:
            return "Draw"
    return None


def determine_distance(row: pd.Series, home_stadiums: dict):
    """calculate the geodesic distance the home city and away city"""
    home_city = row["City"]
    home_coords = get_city_coords(home_city)

    away_city = home_stadiums[row["Away"]]
    away_coords = get_city_coords(away_city)

    return round((geodesic(home_coords, away_coords).kilometers), 2)


def determine_points(result: str, team: str):
    """determine the number of points a team gets"""
    if team == "Home":
        return 3 if result == "Home Win" else (1 if result == "Draw" else 0)
    elif team == "Away":
        return 3 if result == "Away Win" else (1 if result == "Draw" else 0)
    else:
        return 0


def main():
    """set up data transforming process"""
    logging.info("starting data transforming process")

    try:
        # load data
        matches = load_data(MATCH_DATA_PATH)
        stadiums = load_data(STADIUMS_DATA_PATH)

        # merge datasets on the venue
        matches_stadiums = matches.merge(stadiums, how="inner", on="Venue")

        # compute match results
        matches_stadiums["Result"] = matches_stadiums["Score"].apply(determine_result)

        # create a dictionary mapping teams to home cities
        home_stadiums = (
            matches_stadiums[["Home", "City"]]
            .drop_duplicates()
            .set_index("Home")
            .to_dict()["City"]
        )

        # compute travel distance for each match
        matches_stadiums["Travel Distance"] = matches_stadiums.apply(
            lambda row: determine_distance(row, home_stadiums), axis=1
        )

        # compute points for each team
        matches_stadiums["Home Points"] = matches_stadiums["Result"].apply(
            lambda r: determine_points(r, "Home")
        )
        matches_stadiums["Away Points"] = matches_stadiums["Result"].apply(
            lambda r: determine_points(r, "Away")
        )

        # save transformed data
        save_to_csv(matches_stadiums, TRANSFORMED_DATA_PATH)
        logging.info("data transforming was successful!")
    except Exception as e:
        logging.error(f"data transforming process failed: {e}")


if __name__ == "__main__":
    main()
