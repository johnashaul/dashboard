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

def clean_genres(val):
    if isinstance(val, list):
        return val
    elif pd.isna(val):
        return []
    else:
        return str(val).split('|')

data['genres'] = data['genres'].apply(clean_genres)

# Extract unique genres safely
all_genres = sorted({genre.strip() for genres in data['genres'] for genre in genres})

# Multiselect widget
selected_genres = st.multiselect('Filter by Genre(s)', all_genres)

selected_genres = st.multiselect('Filter by Genre(s)', all_genres)

if selected_genres:
    # Match all selected genres (AND logic)
    filtered_recs = data[data['genres'].apply(lambda g_list: all(g in g_list for g in selected_genres))]
else:
    filtered_recs = data

# Get top 10 by average rating
top10_for_genres = (
    filtered_recs[['movieId', 'title', 'genres', 'movie_avg_rating']]
    .drop_duplicates()
    .sort_values(by='movie_avg_rating', ascending=False)
    .head(10)
)
top10_for_genres['movie_avg_rating'] = top10_for_genres['movie_avg_rating'].round(2)
top10_for_genres['Genres'] = top10_for_genres['genres'].apply(lambda g: ', '.join(g))

# Display top 10 filtered movies
st.subheader('Top 10 Movies Matching Genre Filter')
st.table(
    top10_for_genres[['title', 'Genres', 'movie_avg_rating']].rename(columns={
        'title': 'Movie Title',
        'movie_avg_rating': 'Average Rating'
    }).reset_index(drop=True)
)

min_ratings = st.sidebar.slider("Minimum Number of Ratings", 0, 100, 50)
data = data[data['ratings_count'] >= min_ratings]

drop_dups = data[['movieId', 'title', 'movie_avg_rating', 'ratings_count']].drop_duplicates()
top_10_movies = drop_dups.sort_values(by='movie_avg_rating', ascending=False).head(10)
top_10_movies['movie_avg_rating'] = top_10_movies['movie_avg_rating'].round(2)

top_10_movies = top_10_movies.rename(columns={
    'title': 'Movie Title',
    'movie_avg_rating': 'Average Rating',
    'ratings_count': 'No of Ratings'
})

st.subheader("Top 10 Movies by Average Rating")
st.dataframe(top_10_movies.reset_index(drop=True))

search_box_text = st.text_input('Please enter the movie title')

if search_box_text:
    found = data[data['title'].str.contains(search_box_text, case=False, na=False)]

    if not found.empty:
        match_list = found.drop_duplicates(subset='title', keep='first')

        # Show only relevant columns
        match_df = match_list[['title', 'genres', 'movie_avg_rating']]
        st.subheader('Search Results')
        st.dataframe(match_df.reset_index(drop=True))

        # Get the movie that most closely matches the search string
        best_match = match_list.iloc[0]
        bm_movie_id = best_match['movieId']
        bm_title = best_match['title']
        bm_genres = best_match['genres']
        bm_avg_rat = best_match['movie_avg_rating']

        # Get ratings for movie
        movie_ratings = found[found["movieId"] == bm_movie_id]["rating"]
        avg_rating = movie_ratings.mean()

        # Plot histogram of ratings
        fig, ax = plt.subplots(figsize=(3, 2))
        ax.hist(movie_ratings, bins=5, edgecolor='black', color='#2c7fb8')
        ax.set_xlabel('Rating')
        ax.set_ylabel('Count')
        ax.set_title(f'Rating Distribution for:\n{bm_title}')
        st.pyplot(fig)

        st.divider()

        recs_df = load_recs()
        rec_row = recs_df[recs_df['movieId'] == bm_movie_id]

        if not rec_row.empty:
            top10_ids = rec_row.iloc[0, 1:11].tolist()
            top10_movies = data[data['movieId'].isin(top10_ids)][['movieId', 'title', 'genres', 'movie_avg_rating']].drop_duplicates()
            top10_movies['rank'] = top10_movies['movieId'].apply(lambda x: top10_ids.index(x) + 1)
            top10_movies = top10_movies.sort_values('rank')

            st.subheader(f"Top 10 Recommendations for: {bm_title}")
            st.table(
                top10_movies[['rank', 'title', 'genres', 'movie_avg_rating']].rename(columns={
                    'rank': 'Rank',
                    'title': 'Recommended Movie',
                    'genres': 'Genres',
                    'movie_avg_rating': 'Average Rating'
                }).reset_index(drop=True)
            )
        else:
            st.warning("No recommendations found for this movie.")

    else:
        st.warning('No matching movie found.')
