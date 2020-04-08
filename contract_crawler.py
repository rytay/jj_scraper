import sys
import os
from datetime import datetime
import json
import requests
from collections import OrderedDict
#Scrapy
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

#Define fields to extract
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

DATE = str(datetime.now())


#Default start page, you can change this value
START_PAGE = "https://buyandsell.gc.ca/procurement-data/search/site?f%5B0%5D=sm_facet_procurement_data%3Adata_data_tender_notice&f%5B1%5D=ss_publishing_status%3ASDS-SS-005"
while(True):
    use_start = input('Use preprogammed start page? (y/n), "e" to exit : ').lower()
    if(use_start == 'n'):
        START_PAGE = input("Enter the start page for crawler: ")
        if(START_PAGE == 'e'):
            continue
        break
    elif(use_start == 'y'):
        break
    elif(use_start == 'e'):
        print("Exiting...")
        exit();
    else:
        print('Invalid choice. Enter "y" or "n", or "e" to exit (not case sensitive)')
        continue

class ContractCrawler(CrawlSpider):
    
    #keyword file to reference
    keywords = set(open("keywords.txt").read().lower().splitlines())
    
    custom_settings = {
        'LOG_LEVEL' : 'INFO',
        'ROBOTSTXT_OBEY': "True",
        'USER_AGENT' :'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        'CONCURRENT_REQUESTS_PER_DOMAIN' : str(50),
        'RETRY_ENABLED': 'False',
        'FEED_FORMAT' : 'json',
        #Sets output folder and json file
        'FEED_URI' : 'out/'+DATE+'/results.json'
    }

    name = "contract_crawler"
    allowed_domains = ['buyandsell.gc.ca']
    #put start url here
    start_urls = [START_PAGE]
    #Rules for pages that crawler will visit. Must be inside search-results element or pager-next href
    rules = (Rule(LinkExtractor(restrict_xpaths=(['//ul[@class="search-results"]//h2/a','//li[@class="pager-next"]/a'])),callback='parse_item',follow=True),)
    
    #Parse relevant pages and extract their details. Put into output json file
    def parse_item(self, response: HtmlResponse):
        print(response.url)
        if "search/site" not in response.url:
            #unidecode strips the accents of characters
            soup = BeautifulSoup(unidecode(response.text),'html.parser')
            article_text = soup.find("article", {"class":"data-table"}).get_text().lower()
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
           
                item['contact'] = {}
                item['contact']['name'] = checkNone(name)
                item['contact']['email'] = checkNone(email)
                item['contact']['phone'] = checkNone(phone)
                item['contact']['address'] = checkNone(address)

                #Finds all pdfs that are in english
                files = []
                solicitation_parent = soup.find('table',{'class':'sticky-enabled'})
                if solicitation_parent is not None:
                    for tr in solicitation_parent.findAll('tr', {"class":"odd"}):
                        files.append(tr.find('a').attrs['href'])
                #ensures the file is a pdf
                item['pdf'] = [f for f in files if '.pdf' or '.PDF' in f]
                item['url'] = response.url
                return item
#Checks if the value of item is none and replaces it with a string. Avoids referencing None later on.
def checkNone(item):
    if item is None:
        return 'none'
    else:
        return item.get_text()

#Start the crawler
process = CrawlerProcess()
process.crawl(ContractCrawler)
process.start()

#Pretty print for better readability
#Reads in the file and overwrites it indented.
with open('out/'+DATE+'/results.json' ,'r+') as f:
    data=json.load(f)
    json_string = json.dumps(data,indent=4)
    f.truncate(0)
    f.seek(0)
    f.write(json_string)

