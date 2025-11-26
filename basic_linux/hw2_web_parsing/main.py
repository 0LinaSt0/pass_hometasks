import time
import logging
import schedule

import pandas as pd

from scraping import Scraper
from preprocessing import replace_nans
from config import (
    SITE_URL,
    DF_BOOKS_PATH,
    GET_DATA_TIME,
    define_logging
)

define_logging()


def get_books_data() -> pd.DataFrame:
    logging.info('Get book data')
    books_info = Scraper.get_books_info(SITE_URL + 'page-1.html')
    
    logging.info(f'Get data about all books. Count of books: {books_info.shape[0]}')

    logging.info('Preprocess book data')
    books_info = books_info.drop_duplicates(['book_name'], keep='last')

    books_info = replace_nans(books_info)

    logging.info(f'Data was postprocessed. Count of books: {books_info.shape[0]}')

    return books_info

# TODO: REQUIREMENTS.TXT

def main():
    books_info = get_books_data()

    print(books_info)

    books_info.to_csv(DF_BOOKS_PATH, index=False)

    logging.info('Data about books was saved. You can analyze dataframe with notebook "analyze_df_books.ipynb"')



if __name__ == '__main__':
    schedule.every().day.at(GET_DATA_TIME).do(main)
    
    logging.info(f'Started automatic script. Data about books going to be updating every day at {GET_DATA_TIME}')
    while True:
        schedule.run_pending()

        time.sleep(1) # Sleep on one second before checking again
