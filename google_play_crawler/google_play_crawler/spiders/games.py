import scrapy
from scrapy import Spider
from scrapy.http import Request


class GamesSpider(Spider):
    name = 'games'
    allowed_domains = ['play.google.com']
    start_urls = ['https://play.google.com/store/apps/category/GAME']

    def parse(self, response):
        categories = response.xpath('//a[@class="r2Osbf"]/@href').extract()
        for category in categories:
            if 'GAME_' in category:
                absolute_url = response.urljoin(category)
                yield Request(absolute_url, callback=self.parse_category)


    def parse_category(self, response):
        category_name = response.xpath('//span[@class="TwyJFf"]/text()').extract_first()
        sub_category_urls = response.xpath(
            '//a[@class="LkLjZd ScJHi U8Ww7d xjAeve nMZKrb  id-track-click "]/@href').extract()
        for url in sub_category_urls:
            absolute_url = response.urljoin(url)
            yield Request(absolute_url, callback=self.parse_games, meta={'category': category_name})

    def parse_games(self, response):
        category_name = response.meta["category"]
        game_urls = response.xpath('//div[@class="b8cIId ReQCgd Q9MA7b"]/a/@href').extract()
        for url in game_urls:
            absolute_url = response.urljoin(url)
            game_id = url.split('=')[1]
            yield Request(absolute_url, callback=self.parse_detail,
                          meta={'game_id': game_id, 'category': category_name, 'url': absolute_url})

    def parse_detail(self, response):
        game_id = response.meta["game_id"]
        category = response.meta['category']
        url = response.meta['url']

        title = response.xpath('//h1[@class="AHFaub"]/span/text()').extract_first()
        developer_name = response.xpath('//a[@class="hrTbp R8zArc"]/text()').extract_first()
        developer_url = response.urljoin(response.xpath('//a[@class="hrTbp R8zArc"]/@href').extract_first())
        rating = response.xpath('//div[@class="BHMmbe"]/text()').extract_first()
        rating_count = response.xpath('//span[@class="EymY4b"]/span/text()').extract_first()
        price = response.xpath('//button[@jscontroller="chfSwc"]/text()').extract_first()

        if 'Buy' not in price:
            price = 'free'
        else:
            price = price.replace('Buy', '').replace('₫', '').strip()

        yield {'id': game_id,
               'title': title,
               'url': url,
               'category': category,
               'rating': rating,
               'rating_count': rating_count,
               'price': price,
               'developer_name': developer_name,
               'developer_url': developer_url}
