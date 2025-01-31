import pandas as pd
import logging


# configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def load_data(path: str):
    """load data from a csv file"""
    try:
        df = pd.read_csv(path)
        logging.info("successfully loaded data")
        return df
    except Exception as e:
        logging.error(f"error loading data from csv {e}")
        raise


def save_to_csv(df: pd.DataFrame, path: str):
    """save the dataframe to a csv file"""
    try:
        df.to_csv(path, index=False)
        logging.info("successfully saved data")
    except Exception as e:
        logging.error(f"error saving data to csv {e}")
        raise