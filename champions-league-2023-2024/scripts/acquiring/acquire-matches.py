import logging
import pandas as pd
import requests
from bs4 import BeautifulSoup


# url and path constants
URL = 'https://fbref.com/en/comps/8/2023-2024/schedule/2023-2024-Champions-League-Scores-and-Fixtures'
SAVE_PATH = "../data/raw/matches.csv"


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
        table = soup.find('table', {'id': 'sched_all'})

        if not table:
            logging.error("table wasn't found in the file")
            return None

        rows = table.find_all('tr')
        match_data = [
            [cell.get_text(strip=True) for cell in row.find_all(["th", "td"])]
            for row in rows
        ]

        if len(match_data) <= 1:
            logging.error("no data was found in the table")
            return None
        
        df = pd.DataFrame(match_data[1:], columns=match_data[0])
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

    match_data_df = parse_table(html_data)
    if not match_data_df:
        logging.error("failed to parse match data")
        return

    save_to_csv(match_data_df, SAVE_PATH)
    logging.info("data acquistion was successful!")
    

if __name__ == "__main__":
    main()