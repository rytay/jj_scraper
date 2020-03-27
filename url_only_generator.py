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

keywords = set(open("keywords.txt").read().splitlines())
date = datetime.now()


class ContractUrlCrawler(CrawlSpider):
    
    #keyword file
    keywords = set(open("keywords.txt").read().splitlines())
    urls = []
    date = str(datetime.now())
    custom_settings = {
        'LOG_LEVEL' : 'INFO',
        'ROBOTSTXT_OBEY': "True",
        'USER_AGENT' :'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        'CONCURRENT_REQUESTS_PER_DOMAIN' : str(50),
        'RETRY_ENABLED': 'False'
    }

    name = "contract_url_crawler"
    allowed_domains = ['buyandsell.gc.ca']
    start_urls = ["https://buyandsell.gc.ca/procurement-data/search/site?f%5B0%5D=sm_facet_procurement_data%3Adata_data_tender_notice&f%5B1%5D=ss_publishing_status%3ASDS-SS-005"]
    rules = (Rule(LinkExtractor(restrict_xpaths=(['//ul[@class="search-results"]//h2/a','//li[@class="pager-next"]/a'])),callback='parse_item',follow=True),)
    
def parse_item(self, response: HtmlResponse):
        print(response.url)
        if "search/site" not in response.url:
            soup = BeautifulSoup(response.text,'html.parser')
            article_text = soup.find("article", {"class":"data-table"}).get_text()
            
            if any(keyword in article_text for keyword in self.keywords):
                with open(self.date+'.txt','w') as f:
                    f.write(response.url+'\n\n')
        return scrapy.Item()

process = CrawlerProcess()
process.crawl(ContractUrlCrawler)
process.start()
