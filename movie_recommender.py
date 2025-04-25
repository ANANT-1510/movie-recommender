import numpy as np
import pandas as pd
import ast
import re
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import requests

ps = PorterStemmer()


movies = pd.read_csv('tmdb_5000_movies.csv')
credits = pd.read_csv('tmdb_5000_credits.csv')


movies = movies.merge(credits, on='title')


movies = movies[['id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew']]


movies.dropna(inplace=True)


def preprocess_text(text):
    return " ".join([ps.stem(word) for word in text.lower().split()])


def clean_list(lst):
    return [re.sub(r"\s+", "", i) for i in lst]


def convert(obj):
    L = []
    for i in ast.literal_eval(obj):
        L.append(i['name'])
    return L

def convert3(obj):
    L = []
    for i in ast.literal_eval(obj)[:3]:  # Take only top 3 actors
        L.append(i['name'])
    return L

def fetch_director(obj):
    L = []
    for i in ast.literal_eval(obj):
        if i['job'] == 'Director':
            L.append(i['name'])
            break
    return L


movies['genres'] = movies['genres'].apply(convert)
movies['keywords'] = movies['keywords'].apply(convert)
movies['cast'] = movies['cast'].apply(convert3)
movies['crew'] = movies['crew'].apply(fetch_director)


def generate_tag(genres, keywords, cast, crew, overview):
    genres = clean_list(genres)
    keywords = clean_list(keywords)
    cast = clean_list(cast)
    crew = clean_list(crew)
    overview = overview.lower().split()
    
    tag = cast + crew + genres + keywords + overview
    return preprocess_text(" ".join(tag))


movies['tag'] = movies.apply(lambda x: generate_tag(x['genres'], x['keywords'], x['cast'], x['crew'], x['overview']), axis=1)


df = movies[['id', 'title', 'tag']]


cv = CountVectorizer(max_features=5000, stop_words='english')
vectors = cv.fit_transform(df['tag']).toarray()

similarity = cosine_similarity(vectors)




# Function to recommend movies
def recommend(movie_title, new_movie=None):
    if movie_title in df['title'].values:
        # If the movie is in the dataset, fetch its index
        movie_index = df[df['title'] == movie_title].index[0]
        distances = similarity[movie_index]
    elif new_movie:
        # If a new movie is provided, preprocess it and calculate similarity
        new_tag = generate_tag(new_movie['genres'], new_movie['keywords'], new_movie['cast'], new_movie['crew'], new_movie['overview'])
        
        # Convert new tag into vector using the existing vectorizer
        new_vector = cv.transform([new_tag]).toarray()
        
        # Compute cosine similarity with all movies
        distances = cosine_similarity(new_vector, vectors).flatten()
        # print(distances)
    else:
        print("Movie not found. Please provide a new movie description.")
        return
    
    # Get the top 5 most similar movies
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    # print(movies_list)

    # Print recommended movies
    print(f"Movies similar to '{movie_title}':")
    for i in movies_list:
        print(df.iloc[i[0]].title)
        # print (i)

# Example Usage:
recommend("Batman Begins")
new_movie = {
    "genres": ["Action", "Adventure", "Sci-Fi"],
    "keywords": ["superhero", "villain", "fight"],
    "cast": ["JohnDoe", "JaneDoe", "Smith"],
    "crew": ["DirectorName"],
    "overview": "A new superhero rises to save the city from destruction."
}

recommend("New Superhero Movie", new_movie=new_movie)

pickle.dump(df.to_dict(), open('movies_dickt.pkl', 'wb'))
pickle.dump(similarity, open('similarity.pkl', 'wb'))
