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
                break

    def parse_category(self, response):
        sub_category_urls = response.xpath('//a[@class="LkLjZd ScJHi U8Ww7d xjAeve nMZKrb  id-track-click "]/@href').extract()
        for url in sub_category_urls:
            absolute_url = response.urljoin(url)
            yield Request(absolute_url, callback=self.parse_games)
            break

    def parse_games(self, response):
        title = response.xpath('//div[@class="WsMG1c nnK0zc"]/text()').extract()
        print(title)