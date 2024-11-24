import re
import logging
import requests
from typing import Union

import bs4
from bs4 import BeautifulSoup

import numpy as np
import pandas as pd

from config import (
    define_logging,
    SITE_URL, 
    BOOK_INFO_COLS, 
    STARS_NUMS
)

define_logging()




class Scraper:

    def __get_book_link(product_pod: bs4.element.ResultSet) -> str:
        try:
            book_link = SITE_URL + product_pod.find('a')['href']
        except:
            book_link = None
        
        return book_link


    def __get_next_page_url(soup_html: BeautifulSoup) -> str:
        try:
            next_page_url = \
                SITE_URL + soup_html.find(class_='next').find('a')['href']
        except:
            next_page_url = None
        
        return next_page_url


    def get_soup_html(page_url: str) -> Union[BeautifulSoup, None]:
        try:
            result = requests.get(page_url)
            result.raise_for_status()
            result = result.content
            
            soup_html = BeautifulSoup(result, 'html.parser')

            logging.info('Get page content successfuly')

        except Exception as e:
            logging.error(e)
            soup_html = None

        return soup_html


    def get_info_about_book(book_link: str) -> pd.DataFrame:

        if not (soup_html := Scraper.get_soup_html(book_link)):
            return pd.DataFrame(columns=BOOK_INFO_COLS)

        book_info = {}

        all_info = soup_html.find('article', class_='product_page')
        
        # Get all main info
        main_info = all_info.find('div', class_='row')

        book_info['book_name'] = main_info.find('h1').text
        book_info['rating'] = STARS_NUMS[
            main_info.find(class_='star-rating').get('class')[1]
        ]
        book_info['availability_count'] = int(
            re.findall(
                r'\d+', 
                main_info.find('p', class_='availability').text.strip()
            )[0]
        )

        # Get description
        try:
            description_info = all_info.find('div', id='product_description').find_next_sibling().text
        except:
            description_info = np.nan
        book_info['product_description'] = description_info

        # Get product info
        product_info = all_info.find('table')
        names = product_info.find_all('th')
        infos = product_info.find_all('td')

        info = {name.text: info.text for name, info in zip(names, infos)}

        book_info['price_inc_tax'] = float(
            re.findall(
                r'\d+\.\d+', 
                info['Price (incl. tax)']
            )[0]
        )

        book_info['extra_characteristics'] = info

        return pd.DataFrame([book_info])


    def get_books_info(
        page_url: str,
        books_info: pd.DataFrame = pd.DataFrame(columns=BOOK_INFO_COLS)
    ) -> pd.DataFrame:
        if not page_url or not (soup_html := Scraper.get_soup_html(page_url)): 
            return books_info

        logging.info(f'GET {page_url.split('/')[-1].split('.')[0]} BOOKS')
        for el in soup_html.find_all(class_='product_pod'):
            book_link = Scraper.__get_book_link(el)
            book_info = Scraper.get_info_about_book(book_link)

            books_info = pd.concat([books_info, book_info], ignore_index=True)
        
        next_page_url = Scraper.__get_next_page_url(soup_html)

        books_info = Scraper.get_books_info(next_page_url, books_info) 

        return books_info