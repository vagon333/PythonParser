from lxml import html
from datetime import datetime
from urllib.parse import urlparse, urlunparse


def remove_url_params(news_url):
    parsed_url = urlparse(news_url)
    parsed_url = parsed_url._replace(query='')
    news_url = urlunparse(parsed_url)
    return news_url


next_page_url_xpath_string = (
    '//a[contains(concat(" ", normalize-space(@class), " ")'
    ', " load-more ")]/@href'
)
news_url_xpath_string = '//ul[@class="list feed"]/li[not(@class)]//h4/a/@href'


def get_news_title(response):
    tree = html.fromstring(response.content)
    xpath_elements_list = tree.xpath(
        '//*[@class="bsp-page-title-wrapper"]/h1//text()[normalize-space()]'
    )
    if xpath_elements_list:
        xpath_elements_list = [
            xpath_elements.strip() for xpath_elements in xpath_elements_list
        ]
        news_title = ' '.join(xpath_elements_list)
    else:
        news_title = ''
    return news_title


def get_news_datetime(response):
    tree = html.fromstring(response.content)
    xpath_element = tree.xpath(
        '//div[@class="bsp-tags"][contains(./div/text(), "Published")]/ul/li'
        '/text()'
    )
    if xpath_element:
        first_element = 0
        date_string = xpath_element[first_element].strip()
        date_string = date_string.replace('EST', '-0500')
        date_string = date_string.replace('EDT', '-0400')
        date_datetime = datetime.strptime(date_string, '%B %d %Y, %I:%M%p %z')
        date_datetime = date_datetime.replace(tzinfo=None)
    else:
        date_datetime = datetime.strptime('1900', '%Y')
    return date_datetime


def get_news_content_html(response):
    tree = html.fromstring(response.content)
    xpath_elements = tree.xpath(
        '//div[contains(concat(" ", normalize-space(@class), " ")'
        ', " article-body ")]'
        '/*[not(self::div[contains(concat(" ", normalize-space(@class), " ")'
        ', " action-bar ")] '
        'or self::div[contains(concat(" ", normalize-space(@class), " ")'
        ', " PaywallModuleContainer ")] '
        'or self::div[contains(concat(" ", normalize-space(@class), " ")'
        ', " author-module ")] '
        'or self::div[contains(concat(" ", normalize-space(@class), " ")'
        ', " reprint-guidelines ")])]'
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
        '//div[@class="bsp-tags"][contains(./div/text(), "More in")]//a/text()'
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
        '//div[@class="bsp-tags"][contains(./div/text(), "By")]//a/text()'
    )
    if xpath_elements_list:
        xpath_elements_list = [
            xpath_elements.strip() for xpath_elements in xpath_elements_list
        ]
        news_authors = '|'.join(xpath_elements_list)
    else:
        news_authors = ''
    return news_authors