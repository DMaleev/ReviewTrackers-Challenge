from urllib.request import Request, urlopen, URLError, urljoin
from urllib.parse import urlparse
import time
import threading
import queue
from bs4 import BeautifulSoup
import ssl
import json
import requests
import re

class Crawler(threading.Thread):
    def __init__(self,base_url, links_to_crawl,have_visited, error_links,url_lock, reviews):
       
        threading.Thread.__init__(self)
        #print(f"Web Crawler worker {threading.current_thread()} has Started")

        self.base_url = base_url
        self.links_to_crawl = links_to_crawl
        self.have_visited = have_visited
        self.error_links = error_links
        self.url_lock = url_lock
        self.reviews = reviews

    def run(self):
        # we create a ssl context so that our script can crawl
        # the https sties with ssl_handshake.

        #Create a SSLContext object with default settings.
        my_ssl = ssl.create_default_context()

        # by default when creating a default ssl context and making an handshake
        # we verify the hostname with the certificate but our objective is to crawl
        # the webpage so we will not be checking the validity of the cerfificate.
        my_ssl.check_hostname = False

        # in this case we are not verifying the certificate and any 
        # certificate is accepted in this mode.
        my_ssl.verify_mode = ssl.CERT_NONE

        # we are defining an infinite while loop so that all the links in our
        # queue are processed.

        while True:

            # In this part of the code we create a global lock on our queue of 
            # links so that no two threads can access the queue at same time
            self.url_lock.acquire()
            #print(f"Queue List: {list(self.links_to_crawl.queue)}")
            #print(f"Queue Size: {self.links_to_crawl.qsize()}")
            link = self.links_to_crawl.get()
            self.url_lock.release()

            # if the link is None the queue is exhausted or the threads are yet
            # process the links.
            print("LINK: " + link)

            if link is None:
                break

            # if The link is already visited we break the execution.
            if link in self.have_visited:
                print(f"The link {link} is already visited")
                break

            else:
                try:
                    req = Request(link, headers= {'User-Agent': 'Mozilla/5.0'})

                    response = urlopen(req, context=my_ssl)
                    self.have_visited.add(link)
                    #print(f"The URL {response.geturl()} crawled with \
                    #      status {response.getcode()}")
                        
                    soup = BeautifulSoup(response.read(),"html.parser")

                    for review in soup.find_all('div', class_="mainReviews"):
                        title = review.find('p', class_="reviewTitle").getText()
                        text = review.find('p', class_="reviewText").getText()
                        if(review.find('p', class_="consumerName")):
                            consumerName = ' '.join(review.find('p', class_="consumerName").getText().split())
                        if(review.find('p', class_="consumerReviewDate")):
                            consumerReviewDate = review.find('p', class_="consumerReviewDate").getText()

                        self.reviews.append({
                            'title':title,
                            'text':text,
                            'consumerName':consumerName,
                            'consumerReviewDate':consumerReviewDate
                        }
                        )
                        

                    for a_tag in soup.find_all('a', class_="page-link"):
                        if (a_tag.get("href") not in list(self.links_to_crawl.queue)) and (a_tag.get("href") not in self.have_visited) and (urlparse(a_tag.get("href")).path == urlparse(self.base_url).path):
                            self.links_to_crawl.put(a_tag.get("href"))
                            print(f"Added to q {a_tag.get('href')}")
                        else:
                            pass
                    if soup.find("a", {"aria-label":"Next Page"}):
                        print(True)
                    else:
                        print(False)
                except URLError as e:
                    print(f"URL {link} threw this error {e.reason} while trying to parse")

                    self.error_links.append(link)

                finally:
                    self.links_to_crawl.task_done()

            if self.links_to_crawl.qsize() == 0:
                break


print("The Crawler is started")
#base_url = input("Please Enter Website to Crawl > ")
base_url = "https://www.lendingtree.com/reviews/mortgage/grander-home-loans-inc/58426567"
number_of_threads = input("Please Enter number of Threads > ")

links_to_crawl = queue.Queue()
url_lock = threading.Lock()

base_html = requests.get(base_url).text
reviews_amount = (re.findall(">(.*?) Reviews</b>", base_html)[0])

links_to_crawl.put(base_url)

have_visited = set()
crawler_threads = []
error_links = []

reviews = []

#base_url, links_to_crawl,have_visited, error_links,url_lock
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
with open('data.json', 'w') as outfile:
        json.dump(reviews, outfile)