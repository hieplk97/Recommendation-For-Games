import pandas as pd
import numpy as np
import re

from sklearn.preprocessing import RobustScaler

from sqlalchemy import create_engine

db_connection_str = 'mysql+pymysql://root:123456@localhost:3306/games_db'
db_connection = create_engine(db_connection_str)


def pre_process(text):
    # lowercase
    text = text.lower()
    # remove tags
    text = re.sub("", "", text)
    # remove special characters and digits
    text = re.sub("(\\d|\\W)+", " ", text)
    return text


def categorise_size(row):
    if row['size_num'] < 0:
        return 'Varies With Device'
    elif row['size_num'] < 20:
        return 'Tiny'
    elif row['size_num'] < 100:
        return 'Small'
    elif row['size_num'] < 500:
        return 'Medium'
    else:
        return 'Large'


def load_games_by_category(game_name):
    sql = "SELECT * FROM games WHERE games.category = (SELECT category FROM games WHERE games.title = '" + game_name + "') "
    sub_data = pd.read_sql(sql, con=db_connection)
    sub_data = pre_processing(sub_data)

    return sub_data


def load_games_data():
    games_data = pd.read_sql('SELECT * FROM games', con=db_connection)
    games_data = pre_processing(games_data)

    return games_data


def pre_processing(games_data):
    # Convert price vnd to usd
    games_data['price'] = round(games_data['price'].str.replace(',', '').replace('free', '0').astype(float) / 23000,
                                2)
    # Convert string to float
    games_data['rating_count'] = games_data['rating_count'].str.replace(',', '').astype(float)
    # Create is_free column base on price
    games_data['is_free'] = np.where(games_data['price'] != 0, True, False)
    # Convert ad_supported to bool
    games_data['ad_supported'] = games_data['ad_supported'].astype(bool)
    # Convert editors_choice to bool
    games_data['editors_choice'] = games_data['editors_choice'].astype(bool)
    # Fill nan of size
    games_data['size'] = games_data['size'].fillna("Varies with device")
    # drop nan of content_rating
    games_data = games_data[games_data['content_rating'].notna()]
    games_data['size'] = np.where(games_data['size'].str.match(r'^\d*\.?\d*M'),
                                  pd.to_numeric(games_data['size'].str.replace('M', ''), errors='coerce'),
                                  np.where(games_data['size'].str.match(r'^\d*\.?\d*G'),
                                           pd.to_numeric(games_data['size'].str.replace('G', ''),
                                                         errors='coerce') * 1024,
                                           np.where(games_data['size'].str.match(r'^\d*\.?\d*K'),
                                                    round(pd.to_numeric(games_data['size'].str.replace('K', ''),
                                                                        errors='coerce') / 1024, 1), '-1')))
    games_data['min_installs'] = np.where(games_data['min_installs'] > 100000000, 100000000,
                                          np.where(games_data['min_installs'] < 5000, 5000,
                                                   games_data['min_installs']))
    games_data['size_num'] = games_data['size'].astype(float)
    games_data['size'] = games_data.apply(categorise_size, 1)
    games_data.drop(columns=['size_num'], inplace=True)
    games_data['description'] = games_data['description'].apply(lambda x: pre_process(x))

    return games_data


def load_features(games_data, method):
    if method == 'KNN':
        game_features = pd.concat([pd.get_dummies(games_data[["content_rating"]]),
                                   pd.get_dummies(games_data[["size"]]),
                                   games_data[["avg_rating"]],
                                   games_data[["rating_count"]]], axis=1)
    else:
        game_features = pd.concat([pd.get_dummies(games_data[["category"]]),
                                   pd.get_dummies(games_data[["content_rating"]]),
                                   pd.get_dummies(games_data[["size"]]),
                                   games_data[["avg_rating"]],
                                   games_data[["rating_count"]]], axis=1)

    robust_scaler = RobustScaler()
    game_features = robust_scaler.fit_transform(game_features)
    game_features = np.round(game_features, 2)
    return game_features
