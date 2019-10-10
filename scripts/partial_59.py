from lxml import html
from datetime import datetime


next_page_url_xpath_string = '//li[@class="previous"]/a/@href'
news_url_xpath_string = (
    '//h2[contains(concat(" ", normalize-space(@class), " ")'
    ', " post-title ")]/a/@href'
)


def get_news_title(response):
    tree = html.fromstring(response.content)
    xpath_element = tree.xpath(
        '//h1[contains(concat(" ", normalize-space(@class), " ")'
        ', " post-title ")]/text()'
    )
    if xpath_element:
        first_element = 0
        news_title = xpath_element[first_element].strip()
        news_title = news_title.replace('Compliance News: ', '')
    else:
        news_title = ''
    return news_title


def get_news_datetime(response):
    tree = html.fromstring(response.content)
    xpath_element = tree.xpath(
        '//span[contains(concat(" ", normalize-space(@class), " ")'
        ', " the-time ")]/text()'
    )
    if xpath_element:
        date_part = 0
        date_string = xpath_element[date_part].strip()
        if date_string.startswith('on'):
            date_string = date_string.replace('on', '')
        date_datetime = datetime.strptime(date_string, '%B %d, %Y')
    else:
        date_datetime = datetime.strptime('1900', '%Y')
    return date_datetime


def get_news_content_html(response):
    tree = html.fromstring(response.content)
    xpath_elements = tree.xpath(
        '//div[contains(concat(" ", normalize-space(@class), " ")'
        ', " entry-content ")]/*'
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
    xpath_elements_list = tree.xpath('//span[@class="the-tags"]/a/text()')
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
    xpath_elements_list = tree.xpath('//span[@class="the-category"]/a/text()')
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
    xpath_elements_list = tree.xpath('//h4[@class="author-box-name"]/text()')
    if xpath_elements_list:
        xpath_elements_list = [
            xpath_elements.strip() for xpath_elements in xpath_elements_list
        ]
        news_authors = '|'.join(xpath_elements_list)
    else:
        news_authors = ''
    return news_authors