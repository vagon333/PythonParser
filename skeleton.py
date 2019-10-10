import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import sys
import pymssql
import argparse
import requests
from requests.exceptions import RequestException
from user_agent import generate_user_agent
import importlib
from lxml import html
from datetime import datetime
from time import sleep
from time import time
from queue import Queue
import threading
from math import ceil


db_config = {
    'server': '192.168.1000.5000',
    'user': 'DBUser',
    'password': 'FreeAccess',
    'db_name': 'ComplianceGear'
}


def init_db_connect(server, user, password, db_name):
    try:
        conn = pymssql.connect(server, user, password, db_name)
    except pymssql.InterfaceError:
        print('Failed to connect to database "{}"'.format(db_name))
        sys.exit(1)
    else:
        return conn


def get_rows_from_db(sql_query, sql_value):
    with init_db_connect(**db_config) as conn:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(sql_query, sql_value)
        rows = cursor.fetchall()
    return rows


def add_rows_to_db(sql_value):
    with init_db_connect(**db_config) as conn:
        cursor = conn.cursor()
        for row in sql_value:
            cursor.callproc('spAddNewsArticle', row)
        conn.commit()


def get_last_news_date_from_db(source_id):
    sql_query = (
        """
        SELECT TOP 1 ArticleDate
        FROM cgNews 
        WHERE cgNewsSourceID = %s 
        ORDER BY ArticleDate DESC
        """
    )
    last_news_date_list = get_rows_from_db(sql_query, source_id)
    if last_news_date_list:
        first_element = 0
        last_news_date = last_news_date_list[first_element]['ArticleDate']
    else:
        last_news_date = datetime.strptime('1900', '%Y')
    return last_news_date


def get_news_source_for_parsing():
    sql_query = (
        """
        SELECT * 
        FROM cgNewsSources 
        WHERE ReadyToRoll = %s
        """
    )
    sql_value = 1
    rows_list = get_rows_from_db(sql_query, sql_value)
    return rows_list


def chunkify(items, chunk_size):
    for i in range(0, len(items), chunk_size):
        yield items[i:i+chunk_size]


def parse_args():
    parser = argparse.ArgumentParser(description='News source ID')
    parser.add_argument(
        '--partial_file_name',
        type=str,
        help='Enter partial file name')
    parser.add_argument(
        '--source_id',
        type=str,
        help='Enter news source ID')
    parser.add_argument(
        '--source_url',
        type=str,
        help='Enter news source URL')
    parser.add_argument(
        '--buffer_size',
        type=int,
        help='Enter news buffer size')
    parser.add_argument(
        '--pool_size',
        type=int,
        help='Enter thread pool size')
    return parser.parse_args()


def get_request(url, proxies=None, params=None):
    user_agent = generate_user_agent(device_type=('desktop',))
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;'
                  'q=0.9,image/webp,image/apng,*/*;'
                  'q=0.8,application/signed-exchange;v=b3',
        'user-agent': user_agent
    }
    second = 0
    retry_count = 10
    while retry_count:
        sleep(second)
        if retry_count <= 0:
            return None
        try:
            response = requests.get(
                url, headers=headers, proxies=proxies, params=params, timeout=30
            )
            if response.status_code == requests.codes.ok:
                return response
        except RequestException:
            pass
        finally:
            retry_count -= 1
            second += 10


def get_news_info(news_url, source_id):
    costume_module = importlib.import_module(f'partial_{source_id}')
    response = get_request(news_url)
    try:
        news_url = costume_module.remove_url_params(news_url)
    except AttributeError:
        pass
    if response is not None:
        try:
            news_title = costume_module.get_news_title(response)
        except AttributeError:
            news_title = ''
        try:
            news_datetime = costume_module.get_news_datetime(response)
        except AttributeError:
            news_datetime = datetime.strptime('1900', '%Y')
        try:
            news_content_html = costume_module.get_news_content_html(response)
        except AttributeError:
            news_content_html = ''
        try:
            news_tag = costume_module.get_news_tag(response)
        except AttributeError:
            news_tag = ''
        try:
            news_category = costume_module.get_news_category(response)
        except AttributeError:
            news_category = ''
        try:
            news_authors = costume_module.get_news_authors(response)
        except AttributeError:
            news_authors = ''
        info_tuple = (
            source_id,
            news_url,
            news_datetime,
            news_title,
            news_content_html,
            news_tag,
            news_category,
            news_authors,
        )
    else:
        print(f'{news_url} !!!!!!!!!!!!!!!!!!!! news skip !!!!!!!!!!!!!!!!!!!!')
        info_tuple = tuple()
    return info_tuple


def get_news_urls_from_source(source_url):
    next_page_url_xpath_string = parsing_module.next_page_url_xpath_string
    news_url_xpath_string = parsing_module.news_url_xpath_string
    response = get_request(source_url)
    first_element = 0
    url_count = 0
    while True:
        try:
            tree = html.fromstring(response.content)
        except AttributeError:
            print('Page retry')
        tree.make_links_absolute(source_url)
        xpath_elements_list = tree.xpath(news_url_xpath_string)
        if xpath_elements_list:
            for url in xpath_elements_list:
                url_count += 1
                queue.put(url.strip())
        xpath_elements_list = tree.xpath(next_page_url_xpath_string)
        if xpath_elements_list:
            next_page_url = xpath_elements_list[first_element].strip()
            response = get_request(next_page_url)
        else:
            break
        if not [thread for thread in running_threads_list if thread.is_alive()]:
            queue.queue.clear()
            break


def append_new_news_to_db(news_info_list_from_source, buffer_size):
    for chunk in chunkify(news_info_list_from_source, buffer_size):
        add_rows_to_db(chunk)


def threader():
    news_datetime = 2
    while True:
        item_from_queue = queue.get()
        news_info = get_news_info(item_from_queue, args.source_id)
        if news_info:
            if (
                    news_info[news_datetime] < last_news_date_in_db and
                    news_info[news_datetime] != datetime.strptime('1900', '%Y')
            ):
                break
            all_news_info_list.append(news_info)
        queue.task_done()


def start_threads(count):
    threads_list = []
    for i in range(count):
        thread = threading.Thread(target=threader)
        thread.daemon = True
        threads_list.append(thread)
    for thread in threads_list:
        thread.start()
    return threads_list


def main():
    splitter = '|'
    source_urls_list = args.source_url.split(splitter)
    start_time = time()
    for source_url in source_urls_list:
        get_news_urls_from_source(source_url)
        if queue.queue:
            queue.join()
    unique_news_info_list = list(set(all_news_info_list))
    news_datetime = 2
    sorted_news_info_list = sorted(
        unique_news_info_list,
        key=lambda info_tuple: info_tuple[news_datetime]
    )
    print(f'Collected {len(sorted_news_info_list)} news in {ceil(time() - start_time)} seconds from source id {args.source_id}')
    append_new_news_to_db(sorted_news_info_list, 20)


if __name__ == '__main__':
    threads_count = 10
    args = parse_args()
    parsing_module = importlib.import_module(f'partial_{args.source_id}')
    last_news_date_in_db = get_last_news_date_from_db(args.source_id)
    queue = Queue()
    running_threads_list = start_threads(threads_count)
    all_news_info_list = []
    main()
