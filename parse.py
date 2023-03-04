import csv
import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool


def benchmark(func):
    def wrapper():
        import time
        start = time.time()
        func()
        finish = time.time()
        print(f'Время выполнения функции {func.__name__}, заняло: {finish - start}')
    return wrapper


def get_html(url):
    headers = {"User-Agent": "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"}
    response = requests.get(url, headers=headers)
    return response.text


def write_to_csv(data):
    with open('items.csv', 'a') as file:
        writer = csv.writer(file)
        writer.writerow((data['photo'], data['date'], data['price'], data['currency']))


def prepare_csv():
    with open('items.csv', 'w') as file:
        writer = csv.writer(file)
        writer.writerow(('Фото', 'Дата', 'Цена', 'Валюта'))


def get_total_pages_to_compare(html):
    soup = BeautifulSoup(html, 'lxml')
    pages = soup.find('div', class_='pagination').find_all('a')[-1]
    total_pages = pages.get('href').split('/page-')[-1].split('/')[0]
    return int(total_pages)


def get_total_pages(html):
    soup = BeautifulSoup(html, 'lxml')
    pages = soup.find('div', class_='pagination')
    total_pages = pages.find('a').get('href')
    first_half = total_pages.split('/page-')[0]
    second_half = total_pages.split('/page-')[-1].split('/')[-1]
    i = 2
    link = 'https://www.kijiji.ca' + first_half + '/page-' + str(i) + '/' + second_half
    while get_html(link):
        i += 100
        link = 'https://www.kijiji.ca' + first_half + '/page-' + str(i) + '/' + second_half
        res = get_total_pages_to_compare(get_html(link))
        if res < i:
            return res
        else:
            pass


def get_page_data(html):
    soup = BeautifulSoup(html, 'lxml')
    product_list = soup.find_all('div', class_='container-results large-images')[-1]
    products = product_list.find_all('div', class_='search-item regular-ad')
    print(len(products))
    # photo, date, price, currency
    for product in products:
        try:
            photo = product.find('div', class_='image').find('img').get('data-src')
        except:
            photo = ''

        try:
            from datetime import date
            alfa_date = product.find('span', class_='date-posted').text.strip('\n')
            if alfa_date[0] == '<':
                date = date.today().strftime("%d/%m/%Y")
            elif alfa_date == 'Yesterday':
                day = date.today().strftime("%d/%m/$Y").split('/')
                date = str(int(day[0])-1) + f'/{day[1]}/' + day[-1]
            else:
                date = alfa_date
        except:
            date = ''

        try:
            import re
            start = product.find('div', class_='price').text
            mid = re.sub('\n', '', start)
            price = re.sub(' ', '', mid)
            mark = price[0]
            currency = ''
            if mark == '$':
                currency = 'USD $'
            elif mark == '€':
                currency = 'EURO €'
            else:
                currency = ''
        except:
            price = ''

        data = {'photo': photo, 'date': date, 'price': price, 'currency': currency}
        write_to_csv(data)
        print(data)


@benchmark
def main():
    goods_url = 'https://www.kijiji.ca/b-apartments-condos/city-of-toronto/c37l1700273'
    total_pages = get_total_pages(get_html(goods_url))

    prepare_csv()
    with Pool(400) as pool:
        for page in range(1, total_pages+1):
            url_with_page = 'https://www.kijiji.ca/b-apartments-condos/city-of-toronto/page-' + str(page) + '/c37l1700273?ad=offering'
            html = get_html(url_with_page)
            get_page_data(html)


if __name__ == '__main__':
    main()
