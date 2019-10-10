import re
from lxml import html
from datetime import datetime


next_page_url_xpath_string = '//span[@class="ccm-page-right"]/a/@href'
news_url_xpath_string = '//h4[@class="title"]/a/@href'


def get_news_title(response):
    tree = html.fromstring(response.content)
    xpath_element = tree.xpath('//h2[@class="title"]/text()')
    if xpath_element:
        first_element = 0
        news_title = xpath_element[first_element].strip()
    else:
        news_title = ''
    return news_title


def get_news_datetime(response):
    first_element = 0
    tree = html.fromstring(response.content)
    xpath_element = tree.xpath(
        '//h6[@class="date"]/text()|//strong[contains(text(), "VOLUME")]/text()'
    )
    if xpath_element:
        date_string = xpath_element[first_element]
        date_string = date_string.split('/')[first_element].replace(u'\xa0', '')
        date_string = re.sub(r' +', ' ', date_string.replace('.', ' '))
        date_string = re.sub(r'(\d)(st|nd|rd|th)', r'\1', date_string).strip()
        try:
            date_datetime = datetime.strptime(date_string, '%B %d, %Y')
        except ValueError:
            date_datetime = datetime.strptime(date_string, '%b %d, %Y')
    else:
        date_datetime = datetime.strptime('1900', '%Y')
    return date_datetime


def get_news_content_html(response):
    tree = html.fromstring(response.content)
    xpath_elements = tree.xpath('//div[@class="bd-content"]/*')
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
        '//p[@class="article_tags"]/a/text()'
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
        '//h5[contains(text(), "By: ")]/em//text()'
    )
    if xpath_elements_list:
        xpath_elements_list = [
            xpath_elements.strip() for xpath_elements in xpath_elements_list
        ]
        news_authors = '|'.join(xpath_elements_list)
    else:
        news_authors = ''
    return news_authors