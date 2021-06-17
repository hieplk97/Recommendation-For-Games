import pandas as pd
import numpy as np
import scipy.sparse as sp

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import linear_kernel
from sklearn.neighbors import NearestNeighbors

from surprise import KNNBaseline, SVD
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


class ItemBase:

    def __init__(self, reviews_data):
        self.reviews_data = reviews_data
        self.algo = self.run_knn()

    def run_knn(self):
        reader = Reader(line_format='user item rating', rating_scale=(1, 5))
        data = MyDataset(self.reviews_data, reader)
        trainset = data.build_full_trainset()
        sim_options = {'name': 'cosine', 'user_based': False}
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


class UserBase:
    def __init__(self, reviews_data, games_data):
        self.reviews_data = reviews_data
        self.games_data = games_data
        self.algo = self.run_svd()

    def run_svd(self):
        reader = Reader(line_format='user item rating', rating_scale=(1, 5))
        data = MyDataset(self.reviews_data, reader)
        trainset = data.build_full_trainset()

        algo = SVD()
        return algo.fit(trainset)

    def get_predict(self, username):
        # get the list of the game ids
        unique_ids = self.games_data['id'].unique()
        # get the list of the ids that the userid 1001 has rated
        iids = self.reviews_data.loc[self.reviews_data['username'] == 'username', 'game_id']
        # remove the rated games for the recommendations
        games_to_predict = np.setdiff1d(unique_ids, iids)

        my_recs = []
        for iid in games_to_predict:

            my_recs.append(
                (self.games_data.loc[self.games_data.id == iid, 'title'].values[0],
                 self.games_data.loc[self.games_data.id == iid, 'category'].values[0],
                 self.games_data.loc[self.games_data.id == iid, 'avg_rating'].values[0],
                 self.games_data.loc[self.games_data.id == iid, 'url'].values[0],
                 self.algo.predict(uid=username, iid=iid).est))

        result = pd.DataFrame(my_recs, columns=['title', 'category', 'avg_rating', 'url', 'predictions'])\
            .sort_values('predictions', ascending=False).head(10)

        return result[['title', 'category', 'avg_rating', 'url']]