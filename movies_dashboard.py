import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load your datasets
@st.cache_data
def load_data():
    movies = pd.read_csv("movies.csv", encoding="ISO-8859-1", low_memory=False)
    movies['genres'] = movies['genres'].str.split('|')
    ratings = pd.read_csv("rating.csv", encoding="ISO-8859-1")
    df = ratings.merge(movies, on='movieId')
    return df

df = load_data()

st.title("🎬 Movie Ratings Dashboard")

search_query = st.text_input("🔍 Search for a movie title")

# Filter your DataFrame
if search_query:
    search_results = df[df['title'].str.contains(search_query, case=False, na=False)]
    st.write(f"Found {len(search_results)} matching movies:")
    st.dataframe(search_results[['title', 'genres', 'rating']].head(10))