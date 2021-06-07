import pandas as pd
import numpy as np
import scipy.sparse as sp

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import linear_kernel
from sklearn.neighbors import NearestNeighbors

from surprise import KNNBaseline
from surprise import Reader

from data_processing import MyDataset


class TF_IDF:

    def __init__(self, games_data, game_features):
        self.games_data = games_data
        self.game_features = game_features
        self.cosine_sim, self.indices = self.run_tf_idf()

    def run_tf_idf(self):
        # Define a TF-IDF Vectorizer Object. Remove all english stop words such as 'the', 'a'
        tfidf = TfidfVectorizer(stop_words='english')
        # Construct the required TF-IDF matrix by fitting and transforming the data
        tfidf_matrix = tfidf.fit_transform(self.games_data['description'])
        # Output the shape of tfidf_matrix
        matrix = sp.hstack((tfidf_matrix, self.game_features), format='csr')
        # Compute the cosine similarity matrix
        cosine_sim = linear_kernel(matrix, matrix)
        # Construct a reverse map of indices and game titles
        indices = pd.Series(self.games_data.index, index=self.games_data['title']).drop_duplicates()

        return cosine_sim, indices

    def get_recommendations(self, title):
        # Get the index of the game that matches the title
        idx = self.indices[title]
        # Get the pairwsie similarity scores of all games with that game
        sim_scores = list(enumerate(self.cosine_sim[idx]))
        # Sort the games based on the similarity scores
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        # Get the scores of the 10 most similar games
        sim_scores = sim_scores[1:11]
        # Get the game indices
        game_indices = [i[0] for i in sim_scores]
        # Return the top 10 most similar games
        return self.games_data[['title', 'category', 'avg_rating', 'url']].iloc[game_indices]


class KNN:

    def __init__(self, features, sub_data):
        self.features = features
        self.sub_data = sub_data
        self.indices = self.predict()

    def get_index_from_name(self, name):
        return self.sub_data[self.sub_data["title"] == name].index.tolist()[0]

    def print_similar_games(self, name):
        found_id = self.get_index_from_name(name)
        return self.sub_data[['title', 'category', 'avg_rating', 'url']].iloc[self.indices[found_id][1:]]

    def predict(self):
        nbrs = NearestNeighbors(n_neighbors=11, algorithm='kd_tree')
        knn = nbrs.fit(self.features)
        distances, indices = knn.kneighbors(self.features)

        return indices


class SurpriselibKNN:

    def __init__(self, reviews_data):
        self.reviews_data = reviews_data
        self.algo = self.run_knn()

    def run_knn(self):
        reader = Reader(line_format='user item rating', rating_scale=(1, 5))
        data = MyDataset(self.reviews_data, reader)
        trainset = data.build_full_trainset()
        sim_options = {'name': 'pearson_baseline', 'user_based': False}
        algo = KNNBaseline(sim_options=sim_options)
        algo.fit(trainset)

        return algo

    def get_recommended_games(self, game_id, games_data):
        inner_id = self.algo.trainset.to_inner_iid(game_id)
        # Retrieve inner ids of the nearest neighbors of Toy Story.
        neighbors = self.algo.get_neighbors(inner_id, k=10)
        # Convert inner ids of the neighbors into names.
        neighbors = (self.algo.trainset.to_raw_iid(inner_id) for inner_id in neighbors)

        games = []
        for game in neighbors:
            games.append(game)
        return games_data[games_data['id'].isin(games)][['title', 'category', 'avg_rating', 'url']]


class ItemBaseSVD:

    def __init__(self, rating_crosstab):
        self.rating_crosstab = rating_crosstab
        self.corr_mat = self.run_SVD()

    def run_SVD(self):
        SVD = TruncatedSVD(n_components=12, random_state=5)
        X = self.rating_crosstab.T
        resultant_matrix = SVD.fit_transform(X)
        corr_mat = np.corrcoef(resultant_matrix)

        return corr_mat

    def find_similar_games(self, game_id, games_data):
        col_idx = self.rating_crosstab.columns.get_loc(game_id)
        corr_specific = self.corr_mat[col_idx]
        result = pd.DataFrame({'corr_specific': corr_specific, 'id': self.rating_crosstab.columns}).sort_values(
            'corr_specific', ascending=False)
        result = pd.merge(result, games_data, on='id')
        return result[['title', 'category', 'avg_rating', 'url']].head(10)
