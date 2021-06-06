from flask import Flask, render_template, request
from model import TF_IDF, KNN
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
            if method == 'Content-based TF-IDF':
                tf_idf = TF_IDF()
                cosine_sim, indices = tf_idf.run_tf_idf(games_data, game_features)

                result = tf_idf.get_recommendations(name, cosine_sim, indices, games_data)
                result.reset_index(drop=True, inplace=True)
                return render_template('predict.html',
                                       tables=[result.to_html(index=False,classes='table')],
                                       titles="Suggestion for " + name + "'s players")

            elif method == 'Content-based KNN':
                sub_data = data_processing.load_games_by_category(name)
                features = data_processing.load_features(sub_data, method='KNN')

                knn = KNN()
                distances, indices = knn.predict(features)
                result = knn.print_similar_games(name, sub_data, indices)

                return render_template('predict.html',
                                       tables=[result.to_html(index=False,classes='table')],
                                       titles="Suggestion for " + name + "'s players")
        except (KeyError, ValueError):
            return render_template('error.html',
                                   titles="No suggestion for " + name + "'s players")


if __name__ == '__main__':
    games_data = data_processing.load_games_data()
    game_features = data_processing.load_features(games_data, method='Content-based')
    app.run(debug=True)
