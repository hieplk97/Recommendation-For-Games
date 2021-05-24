# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Game(scrapy.Item):
    # define the fields for your item here like:
    id = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    category = scrapy.Field()
    avg_rating = scrapy.Field()
    rating_count = scrapy.Field()
    price = scrapy.Field()
    developer_name = scrapy.Field()
    developer_url = scrapy.Field()
    description = scrapy.Field()
    summary = scrapy.Field()
    min_installs = scrapy.Field()
    editors_choice = scrapy.Field()
    size = scrapy.Field()
    android_version = scrapy.Field()
    content_rating = scrapy.Field()
    ad_supported = scrapy.Field()
    released = scrapy.Field()


class Review(scrapy.Item):
    review_id = scrapy.Field()
    username = scrapy.Field()
    score = scrapy.Field()
    content = scrapy.Field()
    like = scrapy.Field()
    date = scrapy.Field()
    game_title = scrapy.Field()
    game_id = scrapy.Field()
    game_category = scrapy.Field()
