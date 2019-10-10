from lxml import html
from datetime import datetime


next_page_url_xpath_string = (
    '//div[@class="gdl-pagination"]/a[contains(text(), "Next")]/@href'
)
news_url_xpath_string = '//h2[@class="blog-title"]/a/@href'


def get_news_title(response):
    tree = html.fromstring(response.content)
    xpath_element = tree.xpath('//h1[@class="blog-title"]/a/text()')
    if xpath_element:
        first_element = 0
        news_title = xpath_element[first_element].strip()
    else:
        news_title = ''
    return news_title


def get_news_datetime(response):
    tree = html.fromstring(response.content)
    xpath_element = tree.xpath(
        '//*[@class="blog-date-wrapper"]/div/text()'
    )
    if xpath_element:
        date_string = '|'.join(xpath_element)
        date_datetime = datetime.strptime(date_string, '%d|%b|%Y')
    else:
        date_datetime = datetime.strptime('1900', '%Y')
    return date_datetime


def get_news_content_html(response):
    tree = html.fromstring(response.content)
    xpath_elements = tree.xpath('//div[@class="blog-content"]/*')
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
    xpath_elements_list = tree.xpath('//div[@class="blog-tag"]/a/text()')
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
    xpath_elements_list = tree.xpath('//div[@class="blog-author"]/a/text()')
    if xpath_elements_list:
        xpath_elements_list = [
            xpath_elements.strip() for xpath_elements in xpath_elements_list
        ]
        news_authors = '|'.join(xpath_elements_list)
    else:
        news_authors = ''
    return news_authors