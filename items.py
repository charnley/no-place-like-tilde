
import scrapy


class ApartmentItem(scrapy.Item):

    url = scrapy.Field()
    address = scrapy.Field()
    rent = scrapy.Field()

    title = scrapy.Field()
    description = scrapy.Field()

    apartment_type = scrapy.Field()
    rooms = scrapy.Field()
    floor = scrapy.Field()
    livingspace = scrapy.Field()
    available = scrapy.Field()

    images = scrapy.Field()
    appendix = scrapy.Field()


if __name__ == "__main__":

    apartment = ApartmentItem(url="http:/google.com", rent=1600)
    apartment['feature_rooms'] = 4

    print(apartment)

