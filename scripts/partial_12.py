import re
from lxml import html
from datetime import datetime


next_page_url_xpath_string = (
    '//a[contains(concat(" ", normalize-space(text()), " ")'
    ', " Older Entries ")]/@href'
)
news_url_xpath_string = (
    '//a[contains(concat(" ", normalize-space(text()), " ")'
    ', " read more ")]/@href'
)


def get_news_title(response):
    tree = html.fromstring(response.content)
    xpath_element = tree.xpath('//article//h1/text()')
    if xpath_element:
        first_element = 0
        news_title = xpath_element[first_element].strip()
    else:
        news_title = ''
    return news_title


def get_news_datetime(response):
    found = re.findall(r'"datePublished":"(.*?)"', response.text)
    if found:
        first_element = 0
        date_datetime = datetime.strptime(
            found[first_element], '%Y-%m-%dT%H:%M:%S%z'
        )
        date_datetime = date_datetime.replace(tzinfo=None)
    else:
        date_datetime = datetime.strptime('1900', '%Y')
    return date_datetime


def get_news_content_html(response):
    tree = html.fromstring(response.content)
    xpath_elements = tree.xpath('//div[@class="entry-content"]/*')
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
    news_category = ''
    return news_category


def get_news_authors(response):
    found = re.findall(r'"Person","name":"(.*?)"', response.text)
    if found:
        first_element = 0
        news_authors = found[first_element]
    else:
        news_authors = ''
    return news_authors