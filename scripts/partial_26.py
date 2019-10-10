from lxml import html
from datetime import datetime


next_page_url_xpath_string = (
    '//div[@class="searchNextN"]/a[contains(text(), "Next")]/@href'
)
news_url_xpath_string = '//div[@class="searchWrapper"]//a/@href'


def get_news_title(response):
    tree = html.fromstring(response.content)
    xpath_element = tree.xpath('//div[@class="insightsArticleTitle"]/text()')
    if xpath_element:
        first_element = 0
        news_title = xpath_element[first_element].strip()
    else:
        news_title = ''
    return news_title


def get_news_datetime(response):
    tree = html.fromstring(response.content)
    xpath_element = tree.xpath('//div[@class="articleDate"]/text()')
    if xpath_element:
        first_element = 0
        date_part = 0
        date_string = xpath_element[first_element].strip()
        date_string = date_string.split(' / ')[date_part].strip()
        date_datetime = datetime.strptime(date_string, '%B %Y')
    else:
        date_datetime = datetime.strptime('1900', '%Y')
    return date_datetime


def get_news_content_html(response):
    tree = html.fromstring(response.content)
    xpath_elements = tree.xpath(
        '//div[@class="hp-insights"]/*[not(self::div[@class="articleDate"] '
        'or self::div[@class="insightsAuthor"] '
        'or self::div[@class="insightsArticleTitle"])]'
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
    news_category = ''
    return news_category


def get_news_authors(response):
    tree = html.fromstring(response.content)
    xpath_element = tree.xpath('//div[@class="insightsAuthor"]/text()')
    if xpath_element:
        first_element = 0
        news_authors = xpath_element[first_element].replace('By ', '')
        news_authors = '|'.join(news_authors.split(' and '))
    else:
        news_authors = ''
    return news_authors
