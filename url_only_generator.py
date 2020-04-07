import sys
import os
from datetime import datetime
import json
import requests
from collections import OrderedDict
import scrapy
from scrapy import Request
from scrapy.spiders import CrawlSpider,Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from scrapy.crawler import CrawlerProcess
from scrapy.http import HtmlResponse
from scrapy.exceptions import CloseSpider
import re
#Beautiful soup
from bs4 import BeautifulSoup

#This class only generates links with your keywords. Might be easier than extracting data.

if not os.path.exists('out'):
    os.makedirs('out')

#Default start page, you can change this
start_page = "https://buyandsell.gc.ca/procurement-data/search/site?f%5B0%5D=sm_facet_procurement_data%3Adata_data_tender_notice&f%5B1%5D=ss_publishing_status%3ASDS-SS-005"
while(True):
    use_start = input('Use preprogammed start page? (y/n), "e" to exit : ').lower()
    if(use_start == 'n'):
        start_at = input("Enter the start page for crawler: ")
        break
    elif(use_start == 'y'):
        break
    elif(use_start == 'e'):
        print("Exiting...")
        exit();
    else:
        print('Invalid choice. Enter "y" or "n", or "e" to exit (not case sensitive)')
        continue

class ContractCrawlerUrl(CrawlSpider):
    
    #keyword file
    keywords = set(open("keywords.txt").read().lower().splitlines())
    date = str(datetime.now())
    custom_settings = {
        'LOG_LEVEL' : 'INFO',
        'ROBOTSTXT_OBEY': "True",
        'USER_AGENT' :'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        'CONCURRENT_REQUESTS_PER_DOMAIN' : str(50),
        'RETRY_ENABLED': 'False'
    }

    name = "contract_crawler_url"
    allowed_domains = ['buyandsell.gc.ca']
    start_urls = [start_at]
    rules = (Rule(LinkExtractor(restrict_xpaths=(['//ul[@class="search-results"]//h2/a','//li[@class="pager-next"]/a'])),callback='parse_item',follow=True),)
    
    def parse_item(self, response: HtmlResponse):
        print(response.url)
        if "search/site" not in response.url:
            soup = BeautifulSoup(response.text,'html.parser')
            article_text = soup.find("article", {"class":"data-table"}).get_text().lower()
            if any(keyword in article_text for keyword in self.keywords):
                with open('out/'+self.date+'.txt', 'a') as f:
                    title = soup.find(id='cont').get_text()
                    f.write(title+'\n')
                    f.write(response.url+'\n\n')
            return

def checkNone(item):
    if item is None:
        return 'none'
    else:
        return item.get_text()



process = CrawlerProcess()
process.crawl(ContractCrawlerUrl)
process.start()

#Pretty print for readability
'''
with open('results.json' ,'w+') as f:
    data=json.load(f)
    f.write(json.dumps(data, indent=1))
'''
