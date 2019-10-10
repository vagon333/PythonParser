from lxml import html
from datetime import datetime


next_page_url_xpath_string = '//a[contains(@title, "Go to next page")]/@href'
news_url_xpath_string = '//div[@class="view-content"]/div//a/@href'


def get_news_title(response):
    tree = html.fromstring(response.content)
    xpath_element = tree.xpath('//h1[@id="node-title"]/text()')
    if not xpath_element:
        xpath_element = tree.xpath('//div[@class="node-title"]/text()')
    if xpath_element:
        first_element = 0
        news_title = xpath_element[first_element].strip()
    else:
        news_title = ''
    return news_title


def get_news_datetime(response):
    tree = html.fromstring(response.content)
    xpath_element = tree.xpath(
        '//span[@class="date-display-single"]/@content'
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
        '//div[contains(concat(" ", normalize-space(@class), " ")'
        ', " field--name-field-pr-body ")]/div/div/*'
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
        '//div[contains(concat(" ", normalize-space(@class), " ")'
        ', " field--name-field-pr-topic ")]/div[@class="field__items"]'
        '/div/text()'
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
    tree = html.fromstring(response.content)
    xpath_elements_list = tree.xpath(
        '//div[contains(concat(" ", normalize-space(@class), " ")'
        ', " field--name-field-pr-component ")]/div[@class="field__items"]'
        '/div/a/text()'
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
        '//div[contains(concat(" ", normalize-space(@class), " ")'
        ', " field--name-field-speech-speaker ")]'
        '/div[@class="field__items"]/div/a/text()'
    )
    if xpath_elements_list:
        xpath_elements_list = [
            xpath_elements.strip() for xpath_elements in xpath_elements_list
        ]
        news_authors = '|'.join(xpath_elements_list)
    else:
        news_authors = ''
    return news_authors