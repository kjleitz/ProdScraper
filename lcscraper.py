from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
import re
import csv
import shutil
from time import sleep
import datetime
import os

# The website
BASE_URL = "http://www.lc-examplesite.com/"

# The sitemap (contains all the product page links)
SITEMAP_REL_URL = "product_name_index"
SITEMAP_URL = BASE_URL + SITEMAP_REL_URL

# Afuresertib product page URL; for testing purposes
AFUR_REL_URL = "products/a-6802-afuresertib-free"
AFUR_URL = BASE_URL + AFUR_REL_URL

# Product csv filename
PROD_CSV = "lc_prod_prices.csv"

# Just counting the number of requests I'm making
num_of_requests = 0

# Make a page into a soup so I don't have to keep writing this
def make_soup(page_url):
    firefox_UA = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1"
    html = urlopen(Request(page_url, headers={"User-Agent": firefox_UA})).read()
    soup = BeautifulSoup(html, "lxml")
    global num_of_requests
    num_of_requests += 1
    print("Requests: {}".format(num_of_requests))
    return soup

def get_title_test(page_url):
    soup = make_soup(page_url)
    title = soup.find("h1", class_="product_names").string
    return title

# Return a list of all the product links
def get_prod_links(page_url):
    soup = make_soup(page_url)
    prod_select = soup.find("div", "list_a").find("select")
    select_list = prod_select.find_all("option", value=re.compile("products"))
    rel_url_list = []
    for prod in select_list:
        rel_url_list.append(prod["value"])
    return rel_url_list

def get_size_prices(page_url):
    soup = make_soup(page_url)
    prod_name = str(soup.find("h1", class_="product_names").string)
    table_list = soup.find_all("li", class_="prizes")
    del_list = []
    for line in table_list:
        if len(line["class"]) > 1:
            del_list.append(line)
    for item in del_list:
        table_list.remove(item)
    price_dict = {}
    for line in table_list:
        prod_size = line.find(string=re.compile("mg", re.IGNORECASE))
        if prod_size is not None:
            prod_price = str(line.next_sibling.next_sibling.string).strip()
            price_dict[str(prod_size)] = prod_price
    return [prod_name, price_dict]

# Appends a price dictionary (from get_size_prices()) to a .csv file, preceded
# on each line by the name of the compound. Sorted alphabetically by key,
# e.g. 10 mg will come before 100 mg, but 100 mg will come before 50 mg.
# For a good idea on encoding and decoding unicode in Python read this:
# http://pythoncentral.io/encoding-and-decoding-strings-in-python-3-x/
# It helped me a lot with understanding the strings, and understanding
# why I was screwing up so much with unicode errors
def add_dict_to_csv(named_price_dict):
    with open(PROD_CSV, "a") as dict_file:
        writer = csv.writer(dict_file)
        name = named_price_dict[0]
        name = name.encode("utf-8")
        name = name.decode("latin-1")
        for key, value in sorted(named_price_dict[1].items()):
            writer.writerow([name, key, value])

# Store a backup of the lc_prod_prices.csv table
def backup_prod_prices():
    t = datetime.datetime.now()
    timestamp = "{0}-{1}-{2}_{3}h{4}m{5}s".format(t.year, t.month, t.day, t.hour, t.minute, t.second)
    shutil.copy(PROD_CSV, os.getcwd() + "\prod_prices_backup\lc_prod_prices_backup_{}.csv".format(timestamp))

# Clear the current prod_price table
def clear_file(filename):
    open(filename, "w").close()

# Retrieve the LC price tables and store them in a .csv file (~240 products).
# Takes ~3 sec per item scraped, or a little under 11 min for all products.
# Set limit=False to get all products, or set limiter=(some number) to get
# the corresponding number of products (mainly there to make sure you don't
# just go full-blast every time you call the function without the limiter).
# Calling the function without arguments just gives you the first product
# (alphabetically) on the site.
def get_all_prod_prices(limit=True, limiter=1, backup=True):
    if backup == True:
        backup_prod_prices()
    clear_file(PROD_CSV)
    p_links = get_prod_links(BASE_URL)
    if limit == True:
        for i in range(limiter):
            new_named_price_dict = get_size_prices(BASE_URL + p_links[i])
            add_dict_to_csv(new_named_price_dict)
            sleep(2)
    else:
        for link in p_links:
            new_named_price_dict = get_size_prices(BASE_URL + link)
            add_dict_to_csv(new_named_price_dict)
            sleep(2)

# TODO: Make a comparison function (between example site product tables)
if __name__ == "__main__":
    get_all_prod_prices(False)
