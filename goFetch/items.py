import scrapy


class Dog(scrapy.Item):
    name = scrapy.Field()
    sex = scrapy.Field()
    breed = scrapy.Field()
    age = scrapy.Field()
    weight = scrapy.Field()
    color = scrapy.Field()
    bio = scrapy.Field()
