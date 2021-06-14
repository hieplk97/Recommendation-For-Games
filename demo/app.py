from flask import Flask, render_template, request
from model import TF_IDF, KNN, ItemBase, UserBase
import data_processing

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/user')
def user():
    return render_template('user-base.html')


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
                knn = ItemBase(reviews_data)
                result = knn.get_recommended_games(game_id, games_data)

                return render_template('predict.html',
                                       tables=[result.to_html(index=False, classes='table')],
                                       titles="Suggestion for " + name + "'s players")
            else:
                username = request.form.get('username')
                userbase = UserBase(reviews_data, games_data)
                result = userbase.get_predict(username)

                return render_template('predict.html',
                                       tables=[result.to_html(index=False, classes='table')],
                                       titles="Suggestion for user:" + username)

        except (KeyError, ValueError) as e:
            print(e)
            return render_template('error.html',
                                   titles="No suggestion for ")


if __name__ == '__main__':
    games_data = data_processing.load_games_data()
    game_features = data_processing.load_features(games_data, method='Content-based')
    reviews_data = data_processing.load_reviews()
    tf_idf = TF_IDF(games_data, game_features)

    app.run(debug=True)
