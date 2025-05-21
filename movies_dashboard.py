import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

@st.cache_data
def load_data():
    movies = pd.read_csv('movies_ar.csv', encoding='ISO-8859-1', low_memory=False)
    movies['genres'] = movies['genres'].str.split('|')
    ratings = pd.read_csv('rating.csv', encoding='ISO-8859-1')
    df = ratings.merge(movies, on='movieId')
    return df
    
def load_recs():
    return pd.read_csv("top30_recs.csv")  

data = load_data()

st.title('🎬 Movie Ratings Dashboard')

st.write("Genres column types:")
st.write(data['genres'].apply(type).value_counts())

data['genres'] = data['genres'].apply(lambda x: x if isinstance(x, list) else str(x).split('|'))

genre_list = [
    "Action", "Adventure", "Animation", "Children", "Comedy", "Crime",
    "Documentary", "Drama", "Fantasy", "Film-Noir", "Horror", "Musical",
    "Mystery", "Romance", "Sci-Fi", "Thriller", "War", "Western"
]

sel_genres = st.multiselect('Filter by Genre(s)', genre_list)

if sel_genres:
    filtered_recs = data[data['genres'].apply(lambda g_list: all(g in g_list for g in selected_genres))]
else:
    filtered_recs = data



