import pandas as pd
import scipy.sparse as sp

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from sklearn.neighbors import NearestNeighbors


class TF_IDF:

    def run_tf_idf(self, games_data, game_features):
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

    def get_recommendations(self, title, cosine_sim, indices, games_data):
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
        return games_data[['title', 'category', 'avg_rating', 'url']].iloc[game_indices]

class KNN:

    def get_index_from_name(self, name, data):
        return data[data["title"] == name].index.tolist()[0]

    def print_similar_games(self, name, data, indices):
        found_id = self.get_index_from_name(name, data)
        return data[['title', 'category', 'avg_rating', 'url']].iloc[indices[found_id][1:]]

    def predict(self, data):
        nbrs = NearestNeighbors(n_neighbors=11, algorithm='kd_tree')
        knn = nbrs.fit(data)
        distances, indices = knn.kneighbors(data)

        return distances, indices
