from lxml import html
from datetime import datetime
from urllib.parse import urlparse, urlunparse


def remove_url_params(news_url):
    parsed_url = urlparse(news_url)
    parsed_url = parsed_url._replace(query='')
    news_url = urlunparse(parsed_url)
    return news_url


next_page_url_xpath_string = (
    '//a[contains(concat(" ", normalize-space(@class), " "), " next ")]/@href'
)
news_url_xpath_string = '//*[@itemprop="url"]/@href'


def get_news_title(response):
    tree = html.fromstring(response.content)
    xpath_element = tree.xpath(
        '//*[contains(concat(" ", normalize-space(@class), " ")'
        ', " post-title ")]/text()'
    )
    if xpath_element:
        first_element = 0
        news_title = xpath_element[first_element].strip()
        news_title = news_title.replace(u'\u200b', '')
    else:
        news_title = ''
    return news_title


def get_news_datetime(response):
    tree = html.fromstring(response.content)
    xpath_element = tree.xpath(
        '//time[@class="value-title"]/@datetime'
    )
    if xpath_element:
        first_element = 0
        date_string = xpath_element[first_element].strip()
        date_datetime = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S%z')
        date_datetime = date_datetime.replace(tzinfo=None)
    else:
        date_datetime = datetime.strptime('1900', '%Y')
    return date_datetime


def get_news_content_html(response):
    tree = html.fromstring(response.content)
    xpath_elements = tree.xpath(
        '//*[contains(concat(" ", normalize-space(@class), " ")'
        ', " post-content ")]/*[not(self::div[@class="tagcloud"])]'
    )
    if xpath_elements:
        content_list = []
        for xpath_element in xpath_elements:
            item_html = html.tostring(xpath_element, encoding='utf-8')
            content_list.append(item_html.decode('utf-8').strip())
        news_content_html = '\n'.join(content_list)
    else:
        news_content_html = ''
    return news_content_html


def get_news_tag(response):
    tree = html.fromstring(response.content)
    xpath_elements_list = tree.xpath('//*[@rel="tag"]/text()')
    if xpath_elements_list:
        xpath_elements_list = [
            xpath_elements.strip() for xpath_elements in xpath_elements_list
        ]
        news_tag = '|'.join(xpath_elements_list)
    else:
        news_tag = ''
    return news_tag


def get_news_category(response):
    tree = html.fromstring(response.content)
    xpath_elements_list = tree.xpath(
        '//*[contains(concat(" ", normalize-space(@rel), " ")'
        ', " category ")]/text()'
    )
    if xpath_elements_list:
        xpath_elements_list = [
            xpath_elements.strip() for xpath_elements in xpath_elements_list
        ]
        news_category = '|'.join(xpath_elements_list)
    else:
        news_category = ''
    return news_category


def get_news_authors(response):
    tree = html.fromstring(response.content)
    xpath_elements_list = tree.xpath(
        '//section[@class="author-info"]/div/a/text()'
    )
    if not xpath_elements_list:
        xpath_elements_list = tree.xpath(
            '//div[contains(concat(" ", normalize-space(@class), " ")'
            ', " post-content ")]/h3[contains(text(), "In this episode")]'
            '/following-sibling::*[contains(@id, "attachment")]'
            '/p[contains(@id, "caption")]/text()[1]'
        )
    if xpath_elements_list:
        xpath_elements_list = [
            xpath_elements.strip() for xpath_elements in xpath_elements_list
        ]
        news_authors = '|'.join(xpath_elements_list)
    else:
        xpath_elements_list = tree.xpath(
            '//div[contains(concat(" ", normalize-space(@class), " ")'
            ', " post-content ")]/p[contains(text(), "By ") '
            'and following-sibling::span[@class="drop-caps"]]/text()'
        )
        if xpath_elements_list:
            first_element = 0
            news_authors = xpath_elements_list[first_element].replace('By ', '')
            if '; ' in news_authors:
                news_authors = news_authors.strip().replace(' and ', '; ')
                news_authors_list = news_authors.split(';')
            else:
                news_authors = news_authors.strip().replace(' and ', ', ')
                news_authors_list = news_authors.split(',')
            news_authors_list = [
                element.strip() for element in news_authors_list if element
            ]
            news_authors = '|'.join(news_authors_list)
        else:
            news_authors = ''
    return news_authors
