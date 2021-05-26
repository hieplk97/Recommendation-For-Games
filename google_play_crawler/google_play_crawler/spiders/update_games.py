import urllib

import scrapy
import MySQLdb
from google_play_scraper import app, exceptions

from google_play_crawler.items import Game
from google_play_crawler import settings


class UpdateGamesSpider(scrapy.Spider):
    name = 'update_games'
    allowed_domains = ['play.google.com']
    start_urls = ['http://play.google.com/store/apps/category/GAME/']

    def __init__(self):
        self.conn = MySQLdb.connect(settings.MYSQL_HOST, settings.MYSQL_USER, settings.MYSQL_PASSWORD,
                                    settings.MYSQL_DBNAME)
        self.cursor = self.conn.cursor()

    def parse(self, response):
        self.cursor.execute("""SELECT id FROM games WHERE `description` is null""")
        games = self.cursor.fetchall()

        for game in games:
            game_id = game[0]
            try:
                result = app(game_id, lang='en', country='us')

                game = Game()
                game['id'] = game_id
                game['description'] = result['description']
                game['summary'] = result['summary']
                game['min_installs'] = result['minInstalls']
                game['size'] = result['size']
                game['editors_choice'] = result['editorsChoice']
                game['android_version'] = result['androidVersion']
                game['content_rating'] = result['contentRating']
                game['ad_supported'] = result['adSupported']
                game['released'] = result['released']

                yield game
            except exceptions.NotFoundError as e:
                print(game_id, "Not found")
            except TimeoutError as te:
                print('Time out')
            except urllib.error.URLError:
                pass