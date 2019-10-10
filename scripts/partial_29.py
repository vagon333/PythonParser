import re
from lxml import html
from datetime import datetime, timedelta


next_page_url_xpath_string = '//span[@id="tie-next-page"]/a/@href'
news_url_xpath_string = '//h2[@class="post-title"]/a/@href'


def get_news_title(response):
    tree = html.fromstring(response.content)
    xpath_element = tree.xpath(
        '//div[@class="post-inner"]//span[@itemprop="name"]/text()'
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
        '//div[@class="post-inner"]//span[@class="tie-date"]/text()'
    )
    if xpath_element:
        first_element = 0
        date_string = xpath_element[first_element].strip()
        date_today = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        ago_value = int(re.sub(r'[^0-9]', '', date_string))
        if 'min' in date_string:
            date_datetime = date_today - timedelta(minutes=ago_value)
        elif 'hour' in date_string:
            date_datetime = date_today - timedelta(hours=ago_value)
        elif 'day' in date_string:
            date_datetime = date_today - timedelta(days=ago_value)
        else:
            date_datetime = datetime.strptime(date_string, '%B %d, %Y')
    else:
        date_datetime = datetime.strptime('1900', '%Y')
    return date_datetime


def get_news_content_html(response):
    tree = html.fromstring(response.content)
    xpath_elements = tree.xpath(
        '//div[@class="post-inner"]//div[@class="entry"]/*'
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
    xpath_elements_list = tree.xpath('//p[@class="post-tag"]/a/text()')
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
    xpath_elements_list = tree.xpath('//span[@class="post-cats"]/a/text()')
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
    xpath_element = tree.xpath(
        '//h3[contains(text(), "About Author")]/a/text()'
    )
    if xpath_element:
        first_element = 0
        news_authors = xpath_element[first_element].replace('By ', '')
        news_authors = '|'.join(news_authors.split(' and '))
    else:
        news_authors = ''
    return news_authors