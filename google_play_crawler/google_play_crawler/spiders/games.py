from scrapy import Spider
from scrapy.http import Request
from google_play_crawler.items import Game


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
        game = Game()

        game['id'] = response.meta["game_id"]
        game['category'] = response.meta['category']
        game['url'] = response.meta['url']

        game['title'] = response.xpath('//h1[@class="AHFaub"]/span/text()').extract_first()
        game['developer_name'] = response.xpath('//a[@class="hrTbp R8zArc"]/text()').extract_first()
        game['developer_url'] = response.urljoin(response.xpath('//a[@class="hrTbp R8zArc"]/@href').extract_first())
        game['avg_rating'] = response.xpath('//div[@class="BHMmbe"]/text()').extract_first()
        game['rating_count'] = response.xpath('//span[@class="EymY4b"]/span/text()').extract_first()
        price = response.xpath('//button[@jscontroller="chfSwc"]/text()').extract_first()

        if 'Buy' not in price:
            game['price'] = 'free'
        else:
            game['price'] = price.replace('Buy', '').replace('₫', '').strip()

        yield game
