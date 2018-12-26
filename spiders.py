"""

Apartment scrape and obj model for homegate

"""
# import SQLalchemey
# import sqlite
# import googletrans

from urllib import parse

import json
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging

class ApartmentsSpider(scrapy.Spider):
    """

    Get list of currently avaliable apartment indexes

    """

    name = "apartment_list_spider"
    debug = True

    base_url = ""

    def __init__(self, area=None, **kwargs):
        super().__init__(**kwargs)

        self.base_url = "https://www.homegate.ch/rent/real-estate/{:s}/matching-list?tab=list&o=sortToplisting-desc".format(area)

        # minimum rooms
        self.base_url += "&ac=2"

        offset = "&ep=30"

        # Set first request url
        self.start_urls = [self.base_url + offset]


    def parse(self, response):

        if self.debug:
            print('Parsing {}'.format(response.url))

        # Find all apartment indexes

        apartments = response.css(".result-item-list a.detail-page-link::attr(href)").extract()
        apartments = [apartment.replace("/rent/", "") for apartment in apartments]
        apartments = [int(apartment) for apartment in apartments]

        for apartment in apartments:
            yield {"apartment": apartment}

        # Next page
        next_page = response.css(".paginator-container li.next a::attr(href)").extract()

        if next_page:
            next_page = next_page[0]
            # next_page = next_page.split("?")
            # next_page = next_page[-1]
            next_page = parse.urlsplit(next_page)
            next_page = parse.parse_qs(next_page.query)
            next_page = dict(next_page)
            next_page = {k: v[0] for k, v in next_page.items()}

            ep = next_page["ep"]

            next_page_url = self.base_url + "&ep=" + ep
            request = scrapy.Request(url=next_page_url)

            yield request



class ApartmentSpider(scrapy.Spider):
    """

    spider for endividual apartments on homegate

    """

    name = "apartmentspider"
    debug = True

    def __init__(self, homegate_index=None, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = ["https://www.homegate.ch/rent/{:d}".format(homegate_index)]

    def parse(self, response):

        if self.debug:
            print('Parsing {}'.format(response.url))

        yield {"url" : response.url}

        # Sells title
        title = response.css('h1.title::text').extract()
        yield {"title" : title[0]}

        # Apartment images
        find_imgs = response.css('.slide img::attr(data-lazy)').extract()
        for img in find_imgs:
            yield {"img_url": img}

        # Appendix (such as floor plan)
        appendix = response.css(".detail-address-addendum a::attr(href)").extract()
        appendix = set(appendix)
        appendix = list(appendix)
        for app in appendix:
            yield {"appendix": app}

        # Addresse
        address = response.css(".detail-address-link *::text").extract()
        address = [add.strip() for add in address]
        address = list(filter(None, address))
        address = ", ".join(address)
        yield {"address" : address}

        # Description
        description = response.css(".description-content *::text").extract()
        description = "\n".join(description)
        yield {"description" : description}

        # Features (such as sizes etc)
        features = response.css(".detail-key-data li")

        for feature in features:
            # Extract feature_name and feature_value
            texts = feature.css("span::text").extract()
            texts = [text.strip() for text in texts]
            texts = list(filter(None, texts))

            if len(texts) > 1:

                name = texts[0]
                name = name.lower()
                name = name.replace(" ", "_")

                value = texts[1]

                yield {name : value}


        # Extra Features (such as cats)

        # Rent
        rents = response.css('.detail-price li')
        for feature in rents:

            # Get name
            texts = feature.css("span::text").extract()
            texts = [text.strip() for text in texts]
            texts = list(filter(None, texts))

            if len(texts) > 2:

                name = texts[0]
                name = name.lower()
                name = name.replace(" ", "_")

                currency = texts[1]

                value = texts[2]
                value = value.replace(",", "")
                value = value.split(".")
                value = value[0]
                value = float(value)

                yield {name : value}


class ApartmentPipeline(object):

    def open_spider(self, spider):
        self.file = open('item.jl', 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item


def main():
    """

    Scrape homegate.ch for apartments

    """

    configure_logging({'LOG_FORMAT': '%(levelname)s: %(message)s'})

    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'FEED_FORMAT': 'json',
        'FEED_URI': 'result.json',
        'LOG_LEVEL': 'WARNING',
    })

    process.crawl(ApartmentsSpider, area="city-basel")

    # process.crawl(ApartmentSpider, homegate_index=108889746)
    # process.crawl(ApartmentSpider, homegate_index=109457421)
    process.start() # the script will block here until the crawling is finished


if __name__ == "__main__":
    main()
