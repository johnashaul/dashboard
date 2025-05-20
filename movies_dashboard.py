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

drop_dups = data[['movieId', 'title', 'average_score', 'ratings_count']].drop_duplicates()

top_10 = drop_dups.sort_values(by='movie_avg_rating', ascending=False).head(10)

st.title("Top 10 Movies by Average Rating")

for _, row in top_10_movies.iterrows():
    st.write(f"{row['title']}: {row['movie_avg_rating']:.2f}}")

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