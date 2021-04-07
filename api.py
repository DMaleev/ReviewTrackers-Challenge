import time
import threading
import queue
import json
import requests
import time

from fastapi import FastAPI
from typing import List

from schemas import Review
from crawler import Crawler
from helpers import generate_pages

app = FastAPI()


@app.get("/", response_model=List[Review])
def read_root(*, base_url:str, number_of_threads: int = 25):
    print("The Crawler is started")
    start_time = time.time()

    links_to_crawl = queue.Queue()
    url_lock = threading.Lock()

    list(map(links_to_crawl.put, generate_pages(base_url)))

    have_visited = set()
    crawler_threads = []
    error_links = []

    reviews = []

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
    with open('data.json', 'w') as outfile:
            json.dump(reviews, outfile)
    print("--- %s seconds ---" % (time.time() - start_time))
    return reviews
