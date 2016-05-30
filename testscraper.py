from bs4 import BeautifulSoup
from urllib.request import urlopen

scrapingURL = "http://www.gregreda.com/2013/03/03/web-scraping-101-with-python/"

def get_page_title(page_url):
    html = urlopen(page_url).read()
    soup = BeautifulSoup(html, "lxml")
    article_title = soup.find("h1", "article-title")
    return article_title.string

def print_pretty_soup(page_url):
    html = urlopen(page_url).read()
    soup = BeautifulSoup(html, "lxml")
    article_title = soup.find("h1", "article-title")
    print(article_title.prettify())

# print(get_page_title(scrapingURL))
print_pretty_soup(scrapingURL)
