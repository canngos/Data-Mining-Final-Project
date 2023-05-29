from flask import Flask, render_template, request
from pandas import read_csv
from pickle import load
import random

app = Flask(__name__)

def get_user_genres(username, model):
    user_shows = model[model['username'] == username]

    user_genres = user_shows['genres'].str.split(',').tolist()

    # make one list and remove duplicates
    user_genres = [item for sublist in user_genres for item in sublist]
    user_genres = list(set(user_genres))
    return user_genres

@app.route('/')
def index():
    users = read_csv('viewers.csv')
    users = users['username'].values
    users = set(users)
    shows = read_csv('cleaned_netflix_data.csv')
    shows = shows['title'].values

    return render_template('index.html', users=users, shows=shows)

@app.route('/recommend/by/user/', methods=['POST'])
def recommend():
    username = request.form.get('user')
    model = load(open('models/model_data.pkl', 'rb'))
    user_cluster = model.loc[model['username'] == username]['cluster'].values[0]

    user_shows = model.loc[model['username'] == username]['title'].values

    cluster_users = model[(model['cluster'] == user_cluster) & (model['genres'].str.contains('|'.join(get_user_genres(username, model))))]

    cluster_shows = cluster_users['title'].values

    recommendations = list(set(cluster_shows) - set(user_shows))
    
    random.shuffle(recommendations)

    return render_template('recommend_user.html', username=username, recommendations=recommendations[:10])

@app.route('/recommend/by/show/', methods=['POST'])
def recommend_by_show():
    selected_show = request.form.get('show')
    model = load(open('models/association_model.pkl', 'rb'))
    recommendations = []
    for i, show in model["antecedents"].items():
        for j in list(show):
            if j == selected_show:
                recommendations.append(list(model.iloc[i]["consequents"]))

    recommendations = list({item for item_list in recommendations for item in item_list}) # To get unique products
    
    return render_template('recommend_movie.html', show=selected_show, recommendations=recommendations[:5])
    
    