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
from unidecode import unidecode

DATE = str(datetime.now())
class DocItem(scrapy.Item):
    title = scrapy.Field()
    date_closing = scrapy.Field()
    reference_number = scrapy.Field()
    solicitation_number = scrapy.Field()
    region = scrapy.Field()
    description = scrapy.Field()
    contact = scrapy.Field()
    url = scrapy.Field()
    pdf = scrapy.Field()

with open('results.json','w+') as f:
    f.close()

DATE = str(datetime.now())

class ContractCrawler(CrawlSpider):
    
    #keyword file
    keywords = set(open("keywords.txt").read().splitlines())
    
    custom_settings = {
        'LOG_LEVEL' : 'INFO',
        'ROBOTSTXT_OBEY': "True",
        'USER_AGENT' :'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        'CONCURRENT_REQUESTS_PER_DOMAIN' : str(50),
        'RETRY_ENABLED': 'False',
        'FEED_FORMAT' : 'json',
        'FEED_URI' : 'out/'+DATE+'/results.json'
    }

    name = "contract_crawler"
    allowed_domains = ['buyandsell.gc.ca']
    #put start url here
    start_urls = ["https://buyandsell.gc.ca/procurement-data/search/site?f%5B0%5D=sm_facet_procurement_data%3Adata_data_tender_notice&f%5B1%5D=ss_publishing_status%3ASDS-SS-005"]
    rules = (Rule(LinkExtractor(restrict_xpaths=(['//ul[@class="search-results"]//h2/a','//li[@class="pager-next"]/a'])),callback='parse_item',follow=True),)
    
    def parse_item(self, response: HtmlResponse):
        print(response.url)
        if "search/site" not in response.url:
            #remove unidecode if you want unicode with all accents
            soup = BeautifulSoup(unidecode(response.text),'html.parser')
            article_text = soup.find("article", {"class":"data-table"}).get_text()
            if any(keyword in article_text for keyword in self.keywords):
                item = DocItem()
                item['title'] = soup.find(id='cont').get_text()
                item['date_closing'] = soup.find("dd",{"class":"data date-closing"}).get_text() 
                item['reference_number'] = soup.find("dd",{"class":"data reference-number"}).get_text()
                item['solicitation_number'] = soup.find("dd",{"class":'data solicitation-number'}).get_text()
                item['region'] = soup.find("dd",{"class":'data region-delivery'}).get_text()
                item['description'] =  soup.find('div',{'class':'field-content tender_description'}).get_text()
                name = soup.find(id='data-contact-name')
                email = soup.find(id='data-contact-email')
                phone = soup.find(id='data-contact-phone')
                address = soup.find(id='data-contact-address')

                contact_info = []
                for info in [name,email,phone,address]:
                    if info is None:
                        info = "none"
                    else:
                        info = info.get_text()

                #item['contact'] = contact_info
                
                item['contact'] = {}
                item['contact']['name'] = checkNone(name)
                item['contact']['email'] = checkNone(email)
                item['contact']['phone'] = checkNone(phone)
                item['contact']['address'] = checkNone(address)

                files = []
                solicitation_parent = soup.find('table',{'class':'sticky-enabled'})
                if solicitation_parent is not None:
                    for tr in solicitation_parent.findAll('tr', {"class":"odd"}):
                        files.append(tr.find('a').attrs['href'])
                
                item['pdf'] = [f for f in files if '.pdf' or '.PDF' in f]
                item['url'] = response.url
                yield item

def checkNone(item):
    if item is None:
        return 'none'
    else:
        return item.get_text()


process = CrawlerProcess()
process.crawl(ContractCrawler)
process.start()

#Pretty print for readability


