import time
import threading
import queue
import requests
import time

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from typing import List, Optional

from schemas import Reviews
from crawler import Crawler
from helpers import generate_pages, save_cache, read_from_cache, get_total_reviews, check_url

app = FastAPI()


@app.get("/")
def read_root(*, base_url:str, number_of_threads: int = 10):
    print("The Crawler is started")
    start_time = time.time()
    
    if check_url(base_url) == False:
        return HTTPException(status_code=400, detail="Invalid url format")

    try:
        base_html = requests.get(base_url).text
        total_reviews = get_total_reviews(base_html)
    except:
        return HTTPException(status_code=400, detail="Couldn't get reviews for given url")

    links_to_crawl = queue.Queue()
    url_lock = threading.Lock()

    list(map(links_to_crawl.put, generate_pages(base_html, base_url)))
    have_visited = set()
    crawler_threads = []
    error_links = []
    reviews = read_from_cache(base_url)

    if (int(total_reviews) <= len(reviews)):
        #If amount of reviews in cache equals the amount
        #of reviews on site we are loading them from cache
        return Reviews(total=len(reviews), reviews=reviews)

    reviews = []

    if (links_to_crawl.qsize() < number_of_threads):
        number_of_threads = links_to_crawl.qsize()
        print(f"New number of threads = {number_of_threads}")
    
    for i in range(int(number_of_threads)):
        crawler = Crawler(base_url = base_url, 
                        links_to_crawl= links_to_crawl, 
                        have_visited= have_visited,
                        error_links= error_links,
                        url_lock=url_lock,
                        reviews=reviews)
        
        crawler.start()
        crawler_threads.append(crawler)


    for crawler in crawler_threads:
        crawler.join()

    print(f"Total Number of pages visited are {len(have_visited)}")
    print(f"Total Number of Errornous links: {len(error_links)}")
    print(f"Total Number of Reviews: {len(reviews)}")
    save_cache(base_url, reviews)
    print("--- %s seconds ---" % (time.time() - start_time))
    return Reviews(total=len(reviews), reviews=reviews)

client = TestClient(app)
