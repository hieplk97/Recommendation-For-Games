import urllib.error

from scrapy import Spider
from google_play_scraper import Sort, reviews_all

import MySQLdb
from google_play_crawler import settings
from google_play_crawler.items import Review


class CommentsSpider(Spider):
    name = 'comments'
    allowed_domains = ['play.google.com']
    start_urls = ['https://play.google.com/store/apps/category/GAME/']

    def __init__(self):
        self.conn = MySQLdb.connect(settings.MYSQL_HOST, settings.MYSQL_USER, settings.MYSQL_PASSWORD,
                                    settings.MYSQL_DBNAME, charset="utf8", use_unicode=True)
        self.cursor = self.conn.cursor()

    def parse(self, response):
        self.cursor.execute("""SELECT id, url, title, category 
                               FROM games 
                               WHERE id NOT IN (SELECT DISTINCT r.game_id FROM  games_db.reviews r)""")
        games = self.cursor.fetchall()

        for game in games:

            game_id = game[0]
            url = game[1] + '&showAllReviews=true'
            title = game[2]
            category = game[3]
            try:
                results = reviews_all(game_id,
                                      sleep_milliseconds=1000,  # defaults to 0
                                      lang='en',  # defaults to 'en'
                                      country='us',  # defaults to 'us'
                                      sort=Sort.MOST_RELEVANT,  # defaults to Sort.MOST_RELEVANT
                                      )

                for result in results:
                    review = Review()
                    review['review_id'] = result['reviewId']
                    review['username'] = result['userName']
                    review['score'] = result['score']
                    review['content'] = result['content']
                    review['like'] = result['thumbsUpCount']
                    review['date'] = result['at']
                    review['game_id'] = game_id
                    review['game_title'] = title
                    review['game_category'] = category

                    yield review
            except TimeoutError as te:
                print('Time out')
            except urllib.error.URLError:
                pass