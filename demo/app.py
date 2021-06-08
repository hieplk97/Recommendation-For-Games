from flask import Flask, render_template, request
from model import TF_IDF, KNN, SurpriselibKNN, ItemBaseSVD
import data_processing

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/predict/', methods=['GET', 'POST'])
def predict():
    if request.method == "POST":
        # get form data
        name = request.form.get('game_name')
        method = request.form.get('predict_method')

        try:
            if method == 'Content-based-TF-IDF':
                result = tf_idf.get_recommendations(name)
                result.reset_index(drop=True, inplace=True)
                return render_template('predict.html',
                                       tables=[result.to_html(index=False, classes='table')],
                                       titles="Suggestion for " + name + "'s players")

            elif method == 'Content-based-KNN':
                sub_data = data_processing.load_games_by_category(name)
                features = data_processing.load_features(sub_data, method='KNN')

                knn = KNN(features, sub_data)
                result = knn.print_similar_games(name)

                return render_template('predict.html',
                                       tables=[result.to_html(index=False, classes='table')],
                                       titles="Suggestion for " + name + "'s players")
            elif method == 'SurpriseLib-KNN':
                game_id = data_processing.get_game_id_by_name(name)
                knn = SurpriselibKNN(reviews_data)
                result = knn.get_recommended_games(game_id, games_data)

                return render_template('predict.html',
                                       tables=[result.to_html(index=False, classes='table')],
                                       titles="Suggestion for " + name + "'s players")
            '''
            elif method == 'SVD':
                game_id = data_processing.get_game_id_by_name(name)
                svd.find_similar_games(game_id, games_data)'''
        except (KeyError, ValueError):
            return render_template('error.html',
                                   titles="No suggestion for " + name + "'s players")


if __name__ == '__main__':
    games_data = data_processing.load_games_data()
    game_features = data_processing.load_features(games_data, method='Content-based')
    reviews_data = data_processing.load_reviews()
    #rating_crosstab = reviews_data.pivot_table(values='score', index='username', columns='game_id', fill_value=0)

    tf_idf = TF_IDF(games_data, game_features)
    #svd = ItemBaseSVD(rating_crosstab)

    app.run(debug=True)
