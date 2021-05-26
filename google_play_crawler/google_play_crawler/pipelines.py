# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import MySQLdb
from google_play_crawler import settings


class GameCrawlerPipeline:
    def __init__(self):
        self.conn = MySQLdb.connect(settings.MYSQL_HOST, settings.MYSQL_USER, settings.MYSQL_PASSWORD,
                                    settings.MYSQL_DBNAME, charset="utf8mb4", use_unicode=False)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):

        try:
            if spider.name == 'games':
                self.cursor.execute("""INSERT INTO games (id, title, url, category, avg_rating, 
                                                          rating_count, price, developer_name, developer_url) 
                                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                                    (item['id'].encode('utf-8'),
                                     item['title'].encode('utf-8'),
                                     item['url'].encode('utf-8'),
                                     item['category'].encode('utf-8'),
                                     item['avg_rating'].encode('utf-8'),
                                     item['rating_count'].encode('utf-8'),
                                     item['price'].encode('utf-8'),
                                     item['developer_name'].encode('utf-8'),
                                     item['developer_url'].encode('utf-8')))
            elif spider.name == 'comments':
                if item['content'] is not None:
                    self.cursor.execute("""INSERT INTO reviews (id, username, score, content, like_count, date,
                                                                 game_id, game_title, game_category) 
                                                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                                        (item['review_id'].encode('utf-8'),
                                         item['username'].encode('utf-8'),
                                         int(item['score']),
                                         item['content'].encode('utf-8'),
                                         int(item['like']),
                                         item['date'],
                                         item['game_id'].encode('utf-8'),
                                         item['game_title'].encode('utf-8'),
                                         item['game_category'].encode('utf-8')))

            elif spider.name == 'update_games':
                self.cursor.execute("""UPDATE games SET description = %s, summary = %s, min_installs = %s, 
                editors_choice = %s, size = %s, android_version = %s, content_rating = %s, ad_supported = %s, 
                released = %s WHERE id = %s """,
                                    (item['description'],
                                     item['summary'],
                                     item['min_installs'],
                                     item['editors_choice'],
                                     item['size'],
                                     item['android_version'],
                                     item['content_rating'],
                                     item['ad_supported'], 
                                     item['released'],
                                     item['id']))
            self.conn.commit()
        except MySQLdb.Error as e:
            print("Error %d: %s" % (e.args[0], e.args[1]))
        return item
