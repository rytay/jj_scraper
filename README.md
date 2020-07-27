# jj_scraper
Aggregate relevant information and webpages for JJ's government tender notices.

* url_generator.py generates urls only

* contract_crawler.py aggregates relevant information from each page into a results.json file

Crawls and scrapes government tender notice pages from buyandsell.gc.ca. Selects pages that have provided keywords. Has the option to aggregate links only or extract relevant information and create JSON files of results. May implement a recommender in the future based on previous data consisting of user selected tender notices.
