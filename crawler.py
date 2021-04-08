from urllib.request import Request, urlopen, URLError, urljoin
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import ssl
import threading
import threading
import rstr
import re
import time

from helpers import generate_url 

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
            #self.url_lock.acquire()
            #print(f"Queue List: {list(self.links_to_crawl.queue)}")
            #print(f"Queue Size: {self.links_to_crawl.qsize()}")
            link = self.links_to_crawl.get()
            #self.url_lock.release()

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
                    #response = requests.get(link)

                    soup = BeautifulSoup(response.read(),"html.parser")
                    
                    reviews_html = soup.find_all('div', class_="mainReviews")
                    
                    if(reviews_html):
                        for review in reviews_html:
                            title = review.find('p', class_="reviewTitle").getText()
                            text = review.find('p', class_="reviewText").getText()
                            consumerData = ' '.join(review.find('p', class_="consumerName").getText().split())
                            consumerReviewDate = review.find('p', class_="consumerReviewDate").getText().replace('Reviewed in ', '')
                            stars = int(review.find('div', class_="numRec").getText().split(' of ')[0].replace('(', ''))
                            review = {
                                'title':title,
                                'text':text,
                                'consumerName':consumerData.split(' from ')[0],
                                'consumerFrom':consumerData.split(' from ')[1],
                                'consumerReviewDate':consumerReviewDate,
                                'stars': stars
                            }
                            self.reviews.append(review)
                            print("new review " + str(len(self.reviews)))

                        self.have_visited.add(link)
                    else:
                        print("No reviews!")
                        new_url = generate_url(link)
                        time.sleep(15)
                        if "pid" not in new_url:
                            print(f"NEW: {new_url} OLD: {link}")
                        else:
                            self.links_to_crawl.put(new_url)
                        
                except URLError as e:
                    print(f"URL {link} threw this error {e.reason} while trying to parse")
                    self.error_links.append(link)

                
                except Exception as e:
                    print(f"URL {link} threw this error {e} while trying to parse")

                finally:
                    self.links_to_crawl.task_done()

            if self.links_to_crawl.qsize() == 0:
                break