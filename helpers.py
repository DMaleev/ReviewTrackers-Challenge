import re
import math
import random
import string
import rstr
import requests
from typing import List


def generate_pages(base_url) -> List:
    base_html = requests.get(base_url).text
    reviews_amount = re.findall(">(.*?) Reviews</b>", base_html)[0]
    sort_key = list(re.findall("sort=(.*?)&", base_html)[0])
    pages = []
    for i in range(math.ceil(int(reviews_amount)/10)):
        sort_key = rstr.xeger(r'cm[A-Z]\d[a-z][A-Z][A-Z]\d[a-z]\d[A-Z][a-z][a-z][A-Z][a-z]\d[a-z][A-Z][A-Z][a-z][A-Z]\d[A-Z][a-z][a-z]\d[A-Z]=')
        pages.append(f"{base_url}?sort={sort_key}&pid={i+1}")
        
    return pages

def generate_url(base_url) -> str:
    new_sort_key = rstr.xeger(r'sort=cm[A-Z]\d[a-z][A-Z][A-Z]\d[a-z]\d[A-Z][a-z][a-z][A-Z][a-z]\d[a-z][A-Z][A-Z][a-z][A-Z]\d[A-Z][a-z][a-z]\d[A-Z]')
    return(re.sub("sort=(.*?)=", new_sort_key, base_url))