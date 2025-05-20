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

data = load_data()

st.title('🎬 Movie Ratings Dashboard')

# Debug check
st.write("Columns in loaded data:", data.columns.tolist())

# Clean Top 10 display
drop_dups = data[['movieId', 'title', 'movie_avg_rating']].drop_duplicates()
top_10_movies = drop_dups.sort_values(by='movie_avg_rating', ascending=False).head(10)

st.subheader("Top 10 Movies by Average Rating")
for _, row in top_10_movies.iterrows():
    st.write(f"{row['title']}: {row['movie_avg_rating']:.2f}")