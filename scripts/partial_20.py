from lxml import html
from datetime import datetime


next_page_url_xpath_string = (
    '//a[contains(concat(" ", normalize-space(@class), " "), " next ")]/@href'
)
news_url_xpath_string = (
    '//a[@class="button" and contains(text(), "Read More")]/@href'
)


def get_news_title(response):
    tree = html.fromstring(response.content)
    xpath_element = tree.xpath(
        '//div[contains(concat(" ", normalize-space(@class), " "), " post ")]'
        '/h1/text()'
    )
    if xpath_element:
        first_element = 0
        news_title = xpath_element[first_element].strip()
    else:
        news_title = ''
    return news_title


def get_news_datetime(response):
    tree = html.fromstring(response.content)
    xpath_element = tree.xpath(
        '//*[contains(concat(" ", normalize-space(@class), " ")'
        ', " post ")]/ul/li[not(contains(@class, "author"))]/text()'
    )
    if xpath_element:
        first_element = 0
        date_string = xpath_element[first_element].strip()
        date_datetime = datetime.strptime(date_string, '%B %d, %Y')
    else:
        date_datetime = datetime.strptime('1900', '%Y')
    return date_datetime


def get_news_content_html(response):
    tree = html.fromstring(response.content)
    xpath_elements = tree.xpath(
        '//div[contains(concat(" ", normalize-space(@class), " "), " post ")]'
        '/*[not(self::h1 or self::*[contains(concat(" "'
        ', normalize-space(@class), " "), " inline-list ")] '
        'or self::*[contains(concat(" ", normalize-space(@class), " ")'
        ', " postmetadata ")] or self::*[contains(concat(" "'
        ', normalize-space(@class), " "), " social-sidebar ")] '
        'or self::*[contains(concat(" ", normalize-space(@class), " ")'
        ', " author-box ")])]'
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
    xpath_elements_list = tree.xpath(
        '//*[contains(concat(" ", normalize-space(@class), " "), " post ")]'
        '/p[(contains(concat(" ", normalize-space(@class), " ")'
        ', " postmetadata "))]'
        '/a[not(contains(concat(" ", normalize-space(text()), " ")'
        ', " Comments "))]/text()'
    )
    if xpath_elements_list:
        xpath_elements_list = [
            xpath_elements.strip() for xpath_elements in xpath_elements_list
        ]
        news_tag = '|'.join(xpath_elements_list)
    else:
        news_tag = ''
    return news_tag


def get_news_category(response):
    news_category = ''
    return news_category


def get_news_authors(response):
    tree = html.fromstring(response.content)
    xpath_elements_list = tree.xpath(
        '//*[contains(concat(" ", normalize-space(@class), " "), " post ")]'
        '/ul/li[contains(@class, "author")]/a/text()'
    )
    if xpath_elements_list:
        xpath_elements_list = [
            xpath_elements.strip() for xpath_elements in xpath_elements_list
        ]
        news_authors = '|'.join(xpath_elements_list)
    else:
        news_authors = ''
    return news_authors