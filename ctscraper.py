from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
import csv
import shutil
from time import sleep
import datetime
import os

# The website
BASE_URL = "http://www.ct-examplesite.com/"

# The sitemap (contains all the product page links)
SITEMAP_REL_URL = "storesitemap.aspx"
SITEMAP_URL = BASE_URL + SITEMAP_REL_URL

# Afuresertib product page URL; for testing purposes
AFUR_REL_URL = "afuresertib-details.aspx"
AFUR_URL = BASE_URL + AFUR_REL_URL

# Product csv filename
PROD_CSV = "ct_prod_prices.csv"

# Just counting the number of requests I'm making
num_of_requests = 0

# Make a page into a soup so I don't have to keep writing this
def make_soup(page_url):
    html = urlopen(page_url).read()
    soup = BeautifulSoup(html, "lxml")
    global num_of_requests
    num_of_requests += 1
    print(num_of_requests)
    return soup

# Make a soup of the site that we can use globally so that we don't keep
# indiscriminately loading the page and screwing with example site
# ct_soup = make_soup(BASE_URL)

# Test function: gets the title of the sitemap page. May work on other pages
# but not guaranteed. Returns a NavigableString containing the page title.
def get_title_test():
    soup = make_soup(BASE_URL + SITEMAP_REL_URL)
    article_title = soup.find("span", "CommonPageTopTitle").string
    return article_title

# Get the product page URLs; returns a sorted list of distinct strings which
# are the relative URLs for the product pages.
def get_prod_links(page_url):
    soup = make_soup(page_url)
    product_table = soup.find_all("li", class_="StoreSiteMapProductListItem")
    link_list = []
    for x in product_table:
        # Every product page rel url looks like [product]-details.aspx, so...
        link = x.find("a", href=re.compile("-details\.aspx"))
        if link is not None and link.has_attr("href"):
            link_list.append(link["href"])
    return sorted(list(set(link_list)))

# Clear the current prod_price table
def clear_file(filename):
    open(filename, "w").close()

# Store a backup of the prod_prices table
def backup_prod_prices():
    t = datetime.datetime.now()
    timestamp = "{0}-{1}-{2}_{3}h{4}m{5}s".format(t.year, t.month, t.day, t.hour, t.minute, t.second)
    shutil.copy(PROD_CSV, os.getcwd() + "\prod_prices_backup\ct_prod_prices_backup_{}.csv".format(timestamp))

# Store a backup of the ct_prod_list table
def backup_prod_list():
    t = datetime.datetime.now()
    timestamp = "{0}-{1}-{2}_{3}h{4}m{5}s".format(t.year, t.month, t.day, t.hour, t.minute, t.second)
    shutil.copy("ct_prod_list.txt", os.getcwd() + "\prod_prices_backup\ct_prod_list_backup_{}.txt".format(timestamp))

# Creates a dictionary of the sizes and prices of a particular product, and
# returns a list containing the product name and the size:price dictionary
def get_size_prices(page_url):
    soup = make_soup(page_url)
    prod_name = soup.find("div", class_="ProductQuickInfoName").span.string
    price_table = soup.find("table", id="ctl01_uxPlaceHolder_uxProductFormView_ctl01_uxTabContainerResponsive_TabPanel33_uxOptionGroupDetails_uxOptionGroupDetail")
    if price_table is None:
        return [prod_name, {"no sizes available":"N/A"}]
    price_rows = price_table.find_all("tr")
    price_dict = {}
    for row in price_rows:
        if row.td is not None:
            cells = row.find_all("td", class_="tt")
            price_dict[str(cells[0].span.string)] = str(cells[1].span.string)
    return [prod_name, price_dict]

# Appends a price dictionary (from get_size_prices()) to a .csv file, preceded
# on each line by the name of the compound. Sorted alphabetically by key,
# e.g. 10 mg will come before 100 mg, but 100 mg will come before 50 mg.
def add_dict_to_csv(named_price_dict):
    with open(PROD_CSV, "a") as dict_file:
        writer = csv.writer(dict_file)
        name = named_price_dict[0]
        for key, value in sorted(named_price_dict[1].items()):
            writer.writerow([name, key, value])

# Populates a .txt file with example site's full list of products
# CHANGE SO THAT IT USES THE NAMES OF THE CPDs, NOT THE sub-URL
def add_prod_list_to_txt(page_url, backup=True):
    if backup == True:
        backup_prod_list()
    clear_file("ct_prod_list.txt")
    with open("ct_prod_list.txt", "a") as prod_list_file:
        prod_links = get_prod_links(page_url)
        for prod_link in prod_links:
            prod_list_file.write(prod_link.replace("-details.aspx", "\n"))

# Retrieve the example site's price tables and store them in a .csv file.
# Takes ~3 sec per item scraped, or a little over 12 min for all products.
# Set limit=False to get all products, or set limiter=(some number) to get
# the corresponding number of products (mainly there to make sure you don't
# just go full-blast every time you call the function without the limiter).
# Calling the function without arguments just gives you the first product
# (alphabetically) on the site.
def get_all_prod_prices(limit=True, limiter=1, backup=True):
    if backup == True:
        backup_prod_prices()
    clear_file(PROD_CSV)
    p_links = get_prod_links(SITEMAP_URL)
    if limit == True:
        for i in range(limiter):
            new_named_price_dict = get_size_prices(BASE_URL + p_links[i])
            add_dict_to_csv(new_named_price_dict)
            sleep(1)
    else:
        for i in range(len(p_links)):
            new_named_price_dict = get_size_prices(BASE_URL + p_links[i])
            add_dict_to_csv(new_named_price_dict)
            sleep(1)

if __name__ == "__main__":
    add_prod_list_to_txt(SITEMAP_URL)
    get_all_prod_prices(limit=False)
