import re
from lxml import html
from datetime import datetime


next_page_url_xpath_string = (
    '//a[contains(concat(" ", normalize-space(@class), " "), " next ")]/@href'
)
news_url_xpath_string = (
    '//a[contains(translate(concat(" ", normalize-space(text()), " ")'
    ', "M", "m"), " Read more ")]/@href'
)


def get_news_title(response):
    tree = html.fromstring(response.content)
    xpath_element = tree.xpath('//h1//text()')
    if xpath_element:
        first_element = 0
        news_title = xpath_element[first_element].strip()
    else:
        news_title = ''
    return news_title


def get_news_datetime(response):
    tree = html.fromstring(response.content)
    xpath_element = tree.xpath(
        '//span[contains(concat(" ", normalize-space(@class), " ")'
        ', " date ")]/text()|//div[@class="article-details"]/ul/li[1]/text()'
    )
    if xpath_element:
        first_element = 0
        date_string = xpath_element[first_element].strip()
        date_string = re.sub(r'[^0-9.]', '', date_string)
        date_datetime = datetime.strptime(date_string, '%m.%d.%y')
    else:
        date_datetime = datetime.strptime('1900', '%Y')
    return date_datetime


def get_news_content_html(response):
    tree = html.fromstring(response.content)
    xpath_elements = tree.xpath(
        '//article/*[not(self::header) '
        'and not(self::div[@class="social-share"])]'
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
    news_tag = ''
    return news_tag


def get_news_category(response):
    tree = html.fromstring(response.content)
    xpath_elements_list = tree.xpath(
        '//span[contains(concat(" ", normalize-space(@class), " "), " cat ")]'
        '/text()|//a[@target="_parent"]/text()'
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
    news_authors = ''
    return news_authors
