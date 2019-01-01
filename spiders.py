"""

Apartment scrape and obj model for homegate

"""
# import googletrans
# import googlemaps
# TODO check for high-speed internet
# https://www.wingo.ch/de/internet

from urllib import parse

import json
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging

import items


class ApartmentSpider(scrapy.Spider):
    """

    Get list of currently avaliable apartment indexes

    """

    name = "HomegateSpider"
    start_urls = []
    debug = False

    base_url_apartment = "https://www.homegate.ch/rent/{:d}"
    base_url_apartment_list = "https://www.homegate.ch/rent/real-estate/{:s}/matching-list?tab=list&o=sortToplisting-desc"

    def __init__(self, area=None, homegate_index=None, **kwargs):
        super().__init__(**kwargs)

        if area:

            self.base_url_apartment_list = self.base_url_apartment_list.format(area)

            # minimum rooms
            # self.base_url_apartment_list += "&ac=2"

            # offset = "&ep=30"

            # Set first request url
            self.start_urls = [self.base_url_apartment_list + offset]

        if homegate_index:
            self.start_urls = [self.base_url_apartment.format(homegate_index)]


    def parse(self, response):

        if self.debug:
            print('Parsing {}'.format(response.url))

        # Find all apartment indexes

        apartments = response.css(".result-item-list a.detail-page-link::attr(href)").extract()
        apartments = [apartment.replace("/rent/", "") for apartment in apartments]
        apartments = [int(apartment) for apartment in apartments]

        for apartment in apartments:
            apartment_url = self.base_url_apartment.format(apartment)
            request = scrapy.Request(url=apartment_url, callback=self.parse_apartment)
            yield request

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

            next_page_url = self.base_url_apartment_list + "&ep=" + ep
            request = scrapy.Request(url=next_page_url)

            yield request


    def parse_apartment(self, response):

        # Sells title
        title = response.css('h1.title::text').extract()
        title = title[0]

        # Apartment images
        find_imgs = response.css('.slide img::attr(data-lazy)').extract()
        for img in find_imgs:
            pass

        # Appendix (such as floor plan)
        appendix = response.css(".detail-address-addendum a::attr(href)").extract()
        appendix = set(appendix)
        appendix = list(appendix)
        for app in appendix:
            pass

        # Addresse
        address = response.css(".detail-address-link *::text").extract()
        address = [add.strip() for add in address]
        address = list(filter(None, address))
        address = ", ".join(address)

        # Description
        description = response.css(".description-content *::text").extract()
        description = "\n".join(description)

        # Features (such as sizes etc)
        features = response.css(".detail-key-data li")
        features_dict = {}

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

                features_dict[name] = value

        # Extra Features (such as cats)

        # Rent
        rents = response.css('.detail-price li')
        rents_dict = {}
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

                rents_dict[name] = value


        # Init item
        item = items.ApartmentItem()

        item['url'] = response.url

        try:
            item['rooms'] = float(features_dict['rooms'])
        except:
            item['rooms'] = None

        try:
            item['livingspace'] = float(features_dict['living_space'])
        except:
            item['livingspace'] = None

        try:
            item['rent'] = rents_dict['rent']
        except:
            item['rent'] = None

        item['address'] = address

        yield item


def main():
    """

    Scrape homegate.ch for apartments

    """

    configure_logging({'LOG_FORMAT': '%(levelname)s: %(message)s'})

    settings = {}
    settings['USER_AGENT'] = 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    settings['FEED_FORMAT'] = 'json'
    settings['FEED_URI'] = 'result.json'
    settings['LOG_LEVEL'] = 'WARNING'
    settings['ITEM_PIPELINES'] = {'pipelines.ApartmentPipeline': 300}

    process = CrawlerProcess(settings)

    # process.crawl(ApartmentSpider, area="zip-4056")
    process.crawl(ApartmentSpider, area="city-basel")
    # process.crawl(ApartmentSpider, homegate_index=108889746)
    # process.crawl(ApartmentSpider, homegate_index=109457421)

    process.start() # the script will block here until the crawling is finished


if __name__ == "__main__":
    main()
