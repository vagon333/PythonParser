import argparse
from time import sleep
from datetime import datetime
import requests
from lxml import html
from requests import RequestException
from user_agent import generate_user_agent
from app import get_last_fifty_news_url_tuple, add_news_to_base


def parse_args():
    parser = argparse.ArgumentParser(description='News source ID')
    parser.add_argument(
        '--source_id',
        type=str,
        help='Enter news source ID')
    parser.add_argument(
        '--source_url',
        type=str,
        help='Enter news source URL')
    parser.add_argument(
        '--news_buffer_size',
        type=int,
        help='Enter news buffer size')
    return parser.parse_args()


def get_request(url):
    user_agent = generate_user_agent(device_type=('desktop',))
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;'
                  'q=0.9,image/webp,image/apng,*/*;'
                  'q=0.8,application/signed-exchange;v=b3',
        'user-agent': user_agent
    }
    retry_count = 3
    while retry_count:
        if retry_count <= 0:
            return None
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == requests.codes.ok:
                return response
        except RequestException:
            pass
        else:
            retry_count -= 1


def get_news_dict_from_page(url):
    article_dict_tuple = tuple()
    next_page_url = None
    response = get_request(url)
    if response:
        tree = html.fromstring(response.text)
        article_elements_list = tree.xpath(
            '//article[contains(concat(" ", normalize-space(@class)'
            ', " "), " post ")]'
        )
        for article_element in article_elements_list:
            elements_list = article_element.xpath(
                './/a[contains(concat(" ", normalize-space(text())'
                ', " "), " read more ")]/@href'
            )
            article_url = str(elements_list[0]) if elements_list else ''
            elements_list = article_element.xpath(
                './/span[@class="published"]/text()'
            )
            article_date = elements_list[0].strip() if elements_list else None
            elements_list = article_element.xpath('.//a[@rel="author"]/text()')
            article_author = elements_list[0].strip() if elements_list else ''
            article_dict_tuple += (
                {
                    'article_url': article_url,
                    'date_string': article_date,
                    'article_author': article_author
                },
            )
        elements_list = tree.xpath(
            '//a[contains(concat(" ", normalize-space(text()), " ")'
            ', " Older Entries ")]/@href'
        )
        next_page_url = str(elements_list[0]) if elements_list else None
    return {
        'article_dict_tuple': article_dict_tuple,
        'next_page_url': next_page_url
    }


def convert_datetime(date_string):
    date_datetime = datetime.strptime(date_string, '%b %d, %Y')
    date_datetime = datetime.strftime(date_datetime, '%Y-%m-%d %H:%M:%S')
    return date_datetime


def get_news_content(tree):
    news_content = ''
    elements_list = tree.xpath(
        '//div[@class="entry-content"]/*'
    )
    if elements_list:
        content_list = []
        for element in elements_list:
            item_html = html.tostring(element, encoding='utf-8')
            content_list.append(item_html.decode('utf-8').strip())
        news_content = '\n'.join(content_list)
    return news_content


def get_news_info(news_dict, source_id):
    url = news_dict['article_url']
    response = get_request(url)
    info_tuple = tuple()
    if response:
        tree = html.fromstring(response.text)
        elements_list = tree.xpath('//article//h1/text()')
        news_title = elements_list[0].strip() if elements_list else ''
        news_datetime = (
            convert_datetime(news_dict['date_string'])
            if news_dict['date_string'] else ''
        )
        news_content = get_news_content(tree)
        news_tag = ''
        news_category = ''
        news_authors = news_dict['article_author']
        info_tuple += (
            source_id,
            url,
            news_datetime,
            news_title,
            news_content,
            news_tag,
            news_category,
            news_authors,
        )
    return info_tuple


def chunkify(items, chunk_size):
    for i in range(0, len(items), chunk_size):
        yield items[i:i+chunk_size]


def main(source_id, source_url, news_buffer_size):
    last_fifty_news_url_tuple = get_last_fifty_news_url_tuple(source_id)
    article_dict_list = []
    coincidences_count = 0
    current_news_page = source_url
    while True:
        if coincidences_count >= 3:
            break
        news_dict_from_page = get_news_dict_from_page(current_news_page)
        for article_dict in news_dict_from_page['article_dict_tuple']:
            if article_dict.get('article_url') not in last_fifty_news_url_tuple:
                article_dict_list.append(article_dict)
            else:
                coincidences_count += 1
        if news_dict_from_page['next_page_url']:
            current_news_page = news_dict_from_page['next_page_url']
        else:
            break
    if article_dict_list:
        article_dict_list.reverse()
        print(
            '\u001b[32m'
            + 'Found new news {} in news source id 12'.format(
                len(article_dict_list)
            )
            + '\u001b[0m'
        )
        for chunk in chunkify(article_dict_list, news_buffer_size):
            news_info_list = []
            for news_url in chunk:
                news_tuple = get_news_info(news_url, source_id)
                if news_tuple:
                    news_info_list.append(news_tuple)
            add_news_to_base(news_info_list)
    else:
        sleep(0.1)
        print(
            '\u001b[32m'
            + 'New news in news source id 12 not found'
            + '\u001b[0m'
        )


if __name__ == '__main__':
    args = parse_args()
    main(args.source_id, args.source_url, args.news_buffer_size)