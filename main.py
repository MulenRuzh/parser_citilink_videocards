"""
Парсер видеокарт с сайта Ситилинк
"""
import os
import requests
from bs4 import BeautifulSoup
import csv

URL = 'https://www.citilink.ru/catalog/videokarty/'
HEADERS = {
           'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36',
           'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
           }
HOST = 'https://www.citilink.ru'
FILE = 'data.csv'


def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r


def get_pages_count(html):
    soup = BeautifulSoup(html, 'html.parser')
    pagination = soup.find_all('a', class_='PaginationWidget__page js--PaginationWidget__page PaginationWidget__page_next PaginationWidget__page-link')
    if pagination:
        return int(pagination[-1].get_text(strip=True))
    else:
        return 1


def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='product_data__gtm-js product_data__pageevents-js ProductCardHorizontal js--ProductCardInListing js--ProductCardInWishlist')

    videocards = []
    for item in items:
        try:
            videocards.append({
                'title': item.find('a', class_='ProductCardHorizontal__title').get_text(strip=True).replace('Видеокарта', ''),
                'link': HOST + item.find('a', class_='Link').get('href'),
                'id_product': item.find('div', class_='ProductCardHorizontal__vendor-code').get_text(strip=True).replace('Код товара:\xa0', ''),
                'price': item.find('span', class_='ProductCardHorizontal__price_current-price js--ProductCardHorizontal__price_current-price').get_text(strip=True) + 'p',
                            })
        except:
            pass
    return videocards


def save_file(items, path):
     with open(path, 'w', newline='') as file:
        fieldnames = ['Видеокарта', 'Цена', 'Код товара', 'Ссылка']
        writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        for item in items:
            i = {
                'Видеокарта': item['title'],
                'Цена': item['price'],
                'Код товара': item['id_product'],
                'Ссылка': item['link']
            }
            writer.writerow(i)


def parse():
    html = get_html(URL)
    if html.status_code == 200:
        videocards = []
        pages_count = get_pages_count(html.text)
        for page in range(1, pages_count + 1):
            print(f'Парсинг страницы {page} из {pages_count}...')
            html = get_html(URL, params={'page': page})
            videocards.extend(get_content(html.text))
        print(f'Получено {len(videocards)} видеокарт')
        save_file(videocards, FILE)
        videocards = get_content(html.text)
        os.startfile(FILE)
    else:
        print('Error')


parse()
