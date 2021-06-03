from flask import Flask, render_template, request
import model

app = Flask(__name__)

games_data = model.load_data()
game_features = model.load_features(games_data)
cosine_sim, indices = model.run_tf_idf(games_data, game_features)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/predict/', methods=['GET', 'POST'])
def predict():
    if request.method == "POST":
        # get form data
        name = request.form.get('game_name')
        method = request.form.get('predict_method')
        if method == 'Content-based':
            try:
                result = model.get_recommendations(name, cosine_sim, indices, games_data)
                result.reset_index(drop=True, inplace=True)
                return render_template('predict.html',
                                       tables=[result.to_html(classes='data')],
                                       titles="Suggestion for " + name + "'s players")
            except KeyError as e:
                render_template('predict.html',
                                titles="No suggestion for " + name + "'s players")

    pass


if __name__ == '__main__':
    app.run(debug=True)
