import pandas as pd
import numpy as np

import scipy
import scipy.sparse as sp
import re

from sklearn.preprocessing import RobustScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
# Import linear_kernel
from sklearn.metrics.pairwise import linear_kernel
from sklearn.metrics import mean_squared_error
from sklearn.decomposition import TruncatedSVD


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


def load_data():
    games_data = pd.read_csv('games.csv')
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


def load_features(games_data):
    game_features = pd.concat([pd.get_dummies(games_data[["category"]]),
                               pd.get_dummies(games_data[["content_rating"]]),
                               pd.get_dummies(games_data[["size"]]),
                               games_data[["avg_rating"]],
                               games_data[["rating_count"]]], axis=1)

    robust_scaler = RobustScaler()
    game_features = robust_scaler.fit_transform(game_features)
    game_features = np.round(game_features, 2)
    return game_features


def run_tf_idf(games_data, game_features):
    # Define a TF-IDF Vectorizer Object. Remove all english stop words such as 'the', 'a'
    tfidf = TfidfVectorizer(stop_words='english')
    # Construct the required TF-IDF matrix by fitting and transforming the data
    tfidf_matrix = tfidf.fit_transform(games_data['description'])
    # Output the shape of tfidf_matrix
    matrix = sp.hstack((tfidf_matrix, game_features), format='csr')
    # Compute the cosine similarity matrix
    cosine_sim = linear_kernel(matrix, matrix)
    # Construct a reverse map of indices and game titles
    indices = pd.Series(games_data.index, index=games_data['title']).drop_duplicates()

    return cosine_sim, indices


def get_recommendations(title, cosine_sim, indices, games_data):
    # Get the index of the game that matches the title
    idx = indices[title]
    # Get the pairwsie similarity scores of all games with that game
    sim_scores = list(enumerate(cosine_sim[idx]))
    # Sort the games based on the similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    # Get the scores of the 10 most similar games
    sim_scores = sim_scores[1:11]
    # Get the game indices
    game_indices = [i[0] for i in sim_scores]
    # Return the top 10 most similar games
    return games_data[['title', 'category', 'avg_rating']].iloc[game_indices]
