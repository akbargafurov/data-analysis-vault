import logging
import pandas as pd
import requests
from bs4 import BeautifulSoup


# url and path constants
URL = "https://www.worldfootball.net/venues/champions-league-2023-2024/"
SAVE_PATH = "../../data/raw/stadiums.csv"


def get_html(url: str):
    """fetch html content from a url"""
    try:
        response = requests.get(url)
        logging.info("successfully got the webpage")
        return response.content
    except requests.RequestException as e:
        logging.error(f"error getting the page: {e}")
        return None
    

def parse_table(html_data: str):
    """parse html content and return it as a dataframe"""
    try:
        soup = BeautifulSoup(html_data, 'html.parser')
        table = soup.find("table", {"class": "standard_tabelle"})

        if not table:
            logging.error("table wasn't found in the file")
            return None

        stadium_data = [
            [cell.get_text(strip=True) for cell in row.find_all(["th", "td"]) if cell.get_text(strip=True)]
            for row in table.find_all("tr")
        ]

        if not stadium_data:
            logging.error("No data found in the table.")
            return None
        
        df = pd.DataFrame(stadium_data[1:], columns=stadium_data[0])
        logging.info("successfully parsed the table")
        return df
    except Exception as e:
        logging.error(f"error parsing the html table: {e}")
        return None
    

def save_to_csv(df: pd.DataFrame, path: str):
    """save the dataframe to a csv file"""
    try:
        df.to_csv(path, index=False)
        logging.info("successfully saved data")
    except Exception as e:
        logging.error(f"error saving data to csv {e}")


def main():
    """set up data acquisition process"""
    html_data = get_html(URL)
    if not html_data:
        logging.error("failed to get html data")
        return

    stadium_data_df = parse_table(html_data)
    if stadium_data_df is None:
        logging.error("failed to parse stadium data")
        return

    save_to_csv(stadium_data_df, SAVE_PATH)
    logging.info("data acquistion was successful!")


if __name__ == "__main__":
    main()