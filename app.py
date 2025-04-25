import streamlit as st
import pickle
import pandas as pd
import requests

# def fetch_poster(movie_id):
    

#   url = "https://api.themoviedb.org/3/keyword/movie_id/movies?include_adult=false&language=en-US&page=1"

#   headers = {
#       "accept": "application/json",
#       "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI3NTNmMzQ5OWVlODM1NDM4ZjE1NGRiZjgyNjIwYTk2ZSIsIm5iZiI6MTczOTE5NDIyMi4zMjcwMDAxLCJzdWIiOiI2N2E5ZmY2ZTJjNmUyMjg5N2YwNjBhODYiLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.SezDn1E6gRWLpURQQ7HoVKNMYIGmfb-Itwul5WjeUi4"
#   }

  # response = requests.get(url, headers=headers)

  # data=response.json()
  # print(data)

def fetch_poster(movie_title):
    # Step 1: Search for the movie to get its ID
    search_url = f"https://api.themoviedb.org/3/search/movie?api_key={'753f3499ee835438f154dbf82620a96e'}&query={movie_title}"
    response = requests.get(search_url)
    data = response.json()
    
    if data['results']:
        movie_id = data['results'][0]['id']  # Get first search result's movie ID
        
        # Step 2: Fetch movie details using the ID
        movie_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={'753f3499ee835438f154dbf82620a96e'}"
        movie_response = requests.get(movie_url)
        movie_data = movie_response.json()
        
        poster_path = movie_data.get('poster_path')  # Get poster path
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"  # Construct full poster URL
    
    return None

def recommend(movie):
  movie_index=movies[movies['title']==movie].index[0]
  distances=similarity[movie_index]
  movies_list=sorted(list(enumerate(distances)),reverse=True,key=lambda x:x[1])[1:6]

  recommend_movies=[]
  recommend_posters=[]
  for i in movies_list:
    movie_title = movies.iloc[i[0]].title
    poster_url = fetch_poster(movie_title)
    recommend_movies.append(movies.iloc[i[0]].title)
    recommend_posters.append(poster_url)
    
  return recommend_movies,recommend_posters
  
movies_list=pickle.load(open('movies_dickt.pkl','rb'))
movies=pd.DataFrame(movies_list)

similarity=pickle.load(open('similarity.pkl','rb'))

st.title('Movie Recommender System')

selected_movie_name=st.selectbox('What do you want to choose',
movies['title'].values)

if(st.button('Recommend')):
  recommendations,posters=recommend(selected_movie_name)
  cols=st.columns(5)
  for i in range(len(recommendations)):
        with cols[i]:  # Display each movie in a separate column
            st.image(posters[i], caption=recommendations[i], use_column_width=True)   
