# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class profileItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = scrapy.Field()
    org = scrapy.Field()
    title = scrapy.Field()
    interests = scrapy.Field()

class publicationItem(scrapy.Item):
	title = scrapy.Field()
	authors = scrapy.Field()
	date = scrapy.Field()
	publisher = scrapy.Field()
	description = scrapy.Field()
	citations = scrapy.Field()
	url = scrapy.Field()

