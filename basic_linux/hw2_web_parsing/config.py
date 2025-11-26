import logging


def define_logging():
    ''' Define logger settings '''
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )


DF_BOOKS_PATH = 'sources/books_data.csv'

SITE_URL = 'https://books.toscrape.com/catalogue/'


INT_INFO_COLS = [
    'rating',                   # int
    'availability_count',       # int
]

FLOAT_INFO_COLS = [
    'price_inc_tax',            # float
]


NUMERIC_INFO_COLS = INT_INFO_COLS + FLOAT_INFO_COLS


STR_INFO_COLS = [
    'book_name',                # str
    'product_description',      # str
]

DICT_INFO_COLS = [
    'extra_characteristics',    # dict
]

BOOK_INFO_COLS = STR_INFO_COLS + NUMERIC_INFO_COLS + DICT_INFO_COLS


STARS_NUMS = {
    'One': 1,
    'Two': 2,
    'Three': 3,
    'Four': 4,
    'Five': 5
}


GET_DATA_TIME = '19:00'
