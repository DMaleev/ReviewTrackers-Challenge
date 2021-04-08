import re
import math
import random
import string
import rstr
import requests
from typing import List
import json
from urllib.parse import urlparse

def check_url(base_url) -> bool:
    url = urlparse(base_url)
    if url.netloc in ("lendingtree.com", "www.lendingtree.com"):
        if re.fullmatch("\/reviews\/(.*?)\/(.*?)\/[0-9]+", url.path):
            return True
    return False

def get_total_reviews(base_html):
    return re.findall(">(.*?) Reviews</b>", base_html)[0]

def generate_pages(base_html, base_url) -> List:
    reviews_amount = get_total_reviews(base_html)
    sort_key = list(re.findall("sort=(.*?)&", base_html)[0])
    pages = []
    for i in range(math.ceil(int(reviews_amount)/10)):
        sort_key = rstr.xeger(r'cm[A-Z]\d[a-z][A-Z][A-Z]\d[a-z]\d[A-Z][a-z][a-z][A-Z][a-z]\d[a-z][A-Z][A-Z][a-z][A-Z]\d[A-Z][a-z][a-z]\d[A-Z]=&')
        pages.append(f"{base_url}?sort={sort_key}pid={i+1}")
    return pages

def generate_url(base_url) -> str:
    new_sort_key = rstr.xeger(r'sort=cm[A-Z]\d[a-z][A-Z][A-Z]\d[a-z]\d[A-Z][a-z][a-z][A-Z][a-z]\d[a-z][A-Z][A-Z][a-z][A-Z]\d[A-Z][a-z][a-z]\d[A-Z]')
    return (re.sub("sort=(.*?)&", new_sort_key, base_url))
    
def save_cache(base_url, reviews):
    company_id = base_url.split('/')[-1]
    with open(f'cache/{company_id}.json', 'w') as outfile:
        json.dump(reviews, outfile)

def read_from_cache(base_url):
    cache_file_path = f"cache/{base_url.split('/')[-1]}.json"
    try:
        f = open(cache_file_path, "r")
        json_array = json.loads(f.read())
        reviews = []

        return json_array
    except FileNotFoundError:
        print("No Cache")
        return []