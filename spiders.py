"""

Apartment scrape and obj model for homegate

"""

from urllib import parse

import json
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging

import items

import models
from sqlalchemy.orm import sessionmaker

engine = models.db_connect()
Session = sessionmaker(bind=engine)

def parse_get_url(url):

    url = parse.urlsplit(url)
    url = parse.parse_qs(url.query)
    url = dict(url)
    url = {k: v[0] for k, v in url.items()}

    return url["ep"]

def check_url(url):
    """

    TODO this is the wrong way to do it

    """

    session = Session()
    exists = session.query(models.ApartmentModel).filter_by(url=url).count() > 0

    return exists


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
            self.start_urls = [self.base_url_apartment_list]

            print(self.start_urls)

        if homegate_index:
            self.start_urls = [self.base_url_apartment.format(homegate_index)]

    def start_requests(self):

        for url in self.start_urls:
            if "matching-list" in url:
                yield scrapy.Request(url, callback=self.parse)
            else:
                yield scrapy.Request(url, callback=self.parse_apartment)


    def parse(self, response, childs=True, **kwargs):

        if self.debug:
            print('Parsing {}'.format(response.url))

        # Find all apartment indexes

        apartment_selector = "div > a"
        apartments = response.css(apartment_selector + "::attr(href)").extract()
        apartments = [apartment for apartment in apartments if "rent" in apartment]
        # apartments = [apartment.replace("/rent/", "") for apartment in apartments]
        # apartments = [int(apartment) for apartment in apartments]

        # Find apartment info
        for a in apartments:

            idx = a.replace("/rent/", "")
            idx = int(idx)
            sel = f"a[href='{a}']"

            # addr
            sel_data = "ResultlistItem_data_"
            selector = f"{sel} div[class^='{sel_data}'] > p ::text"
            addr = response.css(selector).extract()
            addr = addr[-1]

            # price
            sel_price = "ListingPriceSimple_price"
            selector = f"{sel} span[class^='{sel_price}'] ::text"
            price = response.css(selector).extract()
            try:
                value = price[2]
                value = value.replace(",", "")
                value = value.split(".")
                value = value[0]
                value = float(value)
            except:
                value = None

            # rooms
            sel_room = "RoomNumber_value_"
            selector = f"{sel} span[class^='{sel_room}'] ::text"
            n_rooms = response.css(selector).extract()
            n_rooms = "".join(n_rooms)
            n_rooms = n_rooms.replace("rm", "")
            try:
                n_rooms = float(n_rooms)
            except:
                n_rooms = None

            # square meter
            sel_sqm = "LivingSpace_value_"
            selector = f"{sel} span[class^='{sel_sqm}'] ::text"
            square_meters = response.css(selector).extract()
            square_meters = "".join(square_meters).replace("m2", "")
            try:
                square_meters = float(square_meters)
            except:
                square_meters = None

            # Init item
            item = items.ApartmentItem()
            item['url'] = self.base_url_apartment.format(idx)
            item['rooms'] = n_rooms
            item['livingspace'] = square_meters
            item['rent'] = value
            item['address'] = addr
            item['description'] = None
            item['images'] = None
            item['appendix'] = None

            yield item


        # old
        # apartments = response.css(".result-item-list a.detail-page-link::attr(href)").extract()

        # OLD VERSION
        # for apartment in apartments:
        #     apartment_url = self.base_url_apartment.format(apartment)
        #
        #     exists = check_url(apartment_url)
        #     if exists: continue
        #
        #     # TODO make partional function call with kwargs
        #     kwargs = {
        #         "addr": None,
        #     }
        #
        #     request = scrapy.Request(url=apartment_url, callback=self.parse_apartment, cb_kwargs=kwargs)
        #     yield request


        # Next page
        # next_page = response.css(".paginator-container li.next a::attr(href)").extract()

        if childs:

            sel_next = "HgPaginationSelector_centerBox_"
            # selector = f"nav[class^='{sel_next}'] a[class^='HgPaginationSelector_nextPreviousArrow_'] ::attr(href)"
            selector = f"nav[class^='{sel_next}'] a ::attr(href)"
            next_page = response.css(selector).extract()

            next_page = [parse_get_url(url) for url in next_page]
            next_page = [int(url) for url in next_page]
            try:
                max_pages = max(next_page)
            except:
                max_pages = 0

            for ep in range(2, max_pages+1):

                next_page_url = self.base_url_apartment_list + "&ep=" + str(ep)

                print(next_page_url)

                kwargs = {
                    'childs': False
                }

                request = scrapy.Request(url=next_page_url, callback=self.parse, cb_kwargs=kwargs)

                yield request



    def parse_apartment(self, response, **kwargs):

        if "addr" in kwargs:
            address = kwargs["addr"]
        else:
            address = None

        # Sells title
        # title = response.css('h1.title::text').extract()
        # title = title[0]
        title = ""

        # Apartment images
        find_imgs = response.css('.glide__track img::attr(data-lazy)').extract()

        # Appendix (such as floor plan)
        # appendix = response.css(".detail-address-addendum a::attr(href)").extract()
        appendix = []
        appendix = set(appendix)
        appendix = list(appendix)

        # Addresse
        selector = scrapy.Selector(response)
        address = selector.xpath('//address[contains(@class, "AddressDetails_address_")]')
        # address = response.css('address[class*="AddressDetails_address_"]')
        # address = response.css(".detail-address-link *::text").extract()

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

        item['description'] = title + "\n" + description

        item['images'] = list(find_imgs)
        item['appendix'] = list(appendix)

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

    basel_zip = [
        4000,
        4001,
        4002,
        4005,
        4009,
        4010,
        4018,
        4019,
        4020,
        4030,
        4031,
        4039,
        4041,
        4051,
        4052,
        4052,
        4053,
        4054,
        4055,
        4056,
        4057,
        4058,
        4059,
        4070,
        4075,
        4089,
        4091
    ]

    basel_zip += [4102, 4123, 4127, 4132, 4133]
    # for zipcode in basel_zip:
    #     process.crawl(ApartmentSpider, area="zip-{}".format(zipcode))

    # area = ["land", "city-basel"]

    process.crawl(ApartmentSpider, area="city-basel")
    # process.crawl(ApartmentSpider, homegate_index=108889746)
    # process.crawl(ApartmentSpider, homegate_index=109457421)
    # process.crawl(ApartmentSpider, area="zip-4059")
    # print(check_url("https://www.homegate.ch/rent/2147611144"))

    # process.crawl(ApartmentSpider, homegate_index=3000223774)


    process.start() # the script will block here until the crawling is finished


if __name__ == "__main__":
    main()
