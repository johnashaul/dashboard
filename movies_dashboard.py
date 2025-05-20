import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load your datasets
@st.cache_data
def load_data():
    movies = pd.read_csv('movies_ar.csv', encoding='ISO-8859-1', low_memory=False)
    movies['genres'] = movies['genres'].str.split('|')
    ratings = pd.read_csv('rating.csv', encoding='ISO-8859-1')
    df = ratings.merge(movies, on='movieId')
    return df

data = load_data()
data.to_csv('merged_file.csv')

st.title('🎬 Movie Ratings Dashboard')

movie_stats = data.groupby(['movieId', 'title', 'genres']).agg(
    rating_count=('rating', 'count'),
    avg_rating=('rating', 'mean')
).reset_index()

st.subheader('Top 10 Rated Movies')
top_movies = movie_stats.sort_values(by='avg_rating', ascending=False).head(10)
st.dataframe(top_movies[['title', 'avg_rating', 'rating_count']])


search_box_text = st.text_input('Please enter the movie title')

if search_box_text:
    found = data[data['title'].str.contains(search_box_text, case=False, na=False)]

    if not found.empty:
        match_list = found.drop_duplicates(subset='title', keep='first')

        # Show only relevant columns
        match_df = match_list[['title', 'genres', 'movie_avg_rating']]

        st.subheader('Search Results')
        st.dataframe(match_df.reset_index(drop=True))
        
        best_match = match_list.iloc[0]
        bm_movie_id = best_match['movieId']
        bm_title = best_match['title']
        bm_genres = best_match['genres']
        bm_avg_rat = best_match['movie_avg_rating']
        
        movie_ratings = found[found["movieId"] == bm_movie_id]["rating"]
        avg_rating = movie_ratings.mean()

        fig, ax = plt.subplots(figsize=(3, 2))
        ax.hist(movie_ratings, bins=5, edgecolor='black', color='#2c7fb8')
        ax.set_xlabel('Rating')
        ax.set_ylabel('Count')
        ax.set_title(f'Rating Distribution for:\n{bm_title}')
        st.pyplot(fig)
        
        st.divider()
        
    else:
        st.warning('No matching movie found.')