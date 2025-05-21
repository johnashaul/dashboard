import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

st.markdown("""
    <style>
      /* make the main block container full-width */
      .reportview-container .main .block-container {
        max-width: 100% !important;
        padding-left: 2rem;
        padding-right: 2rem;
      }
      html, body, [class*="css"]  {
        font-size: 0.9rem !important;
      }
      .stApp h1 {
        font-size: 1.5rem !important;
      }
      .stApp h2 {
        font-size: 1.25rem !important;
      }
      .stTable table {
        font-size: 0.8rem !important;
      }
      .stDataFrame div[data-testid="stMarkdownContainer"] span {
        font-size: 0.8rem !important;
      }
    </style>
""", unsafe_allow_html=True)

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

min_ratings = st.slider(
    "Minimum Number of Ratings",
    min_value=0,
    max_value=100,
    value=50
)
gt_min_df = data[data['ratings_count'] >= min_ratings]

all_genres = sorted(set(g for genre_list in data['genres'] if isinstance(genre_list, list) for g in genre_list))

data = data[data['ratings_count'] >= min_ratings]

drop_dups = data[['movieId', 'title', 'movie_avg_rating', 'ratings_count']].drop_duplicates()
top_10_movies = drop_dups.sort_values(by='movie_avg_rating', ascending=False).head(10)
top_10_movies['movie_avg_rating'] = top_10_movies['movie_avg_rating'].round(2)


col1, col2 = st.columns(2)

with col1:
    # Put spacer to align overall table with genre table
    st.markdown("<div style='height:6em'></div>", unsafe_allow_html=True)

    # place top 10 overall movies on left
    top10_movies = (
        gt_min_df
          .drop_duplicates(subset=['movieId'])
          [['title', 'genres', 'movie_avg_rating', 'ratings_count']]
          .sort_values(by='movie_avg_rating', ascending=False)
          .head(10)
    )
    top10_movies['movie_avg_rating'] = top10_movies['movie_avg_rating'].round(2)
    top10_movies = top10_movies.rename(columns={
        'title': 'Movie Title',
        'movie_avg_rating': 'Avg Rating',
        'ratings_count': 'No. of Ratings'
    })
    st.subheader("Top 10 Movies Overall")
    st.table(top10_movies.reset_index(drop=True))

with col2:
    sel_genres = st.multiselect("Filter by Genre(s)", all_genres)

    if  sel_genres:
        df_genre = gt_min_df[
            gt_min_df['genres'].apply(lambda gl: all(g in gl for g in sel_genres))
        ]
    else:
        df_genre = gt_min_df

    top10_genre = (
        df_genre
          .drop_duplicates(subset=['movieId'])
          [['title', 'genres', 'movie_avg_rating', 'ratings_count']]
          .sort_values(by='movie_avg_rating', ascending=False)
          .head(10)
    )
    top10_genre['movie_avg_rating'] = top10_genre['movie_avg_rating'].round(2)
    top10_genre['genres'] = top10_genre['genres'].apply(lambda gl: ', '.join(gl))
    top10_genre = top10_genre.rename(columns={
        'title': 'Movie Title',
        'genres': 'Genres',
        'movie_avg_rating': 'Avg Rating',
        'ratings_count': 'No. of Ratings'
    })

    header = (
        f"Top 10 Matching: {', '.join(sel_genres)}"
        if  sel_genres else
        "Top 10 Movies - No Genre Filter Applied"
    )
    st.subheader(header)
    st.table(top10_genre.reset_index(drop=True))

# Add search box for movie title
search_box_text = st.text_input('Please enter the movie title')

if  search_box_text:
    found = data[data['title'].str.contains(search_box_text, case=False, na=False)]

    if  not found.empty:
        match_list = found.drop_duplicates(subset='title', keep='first')

        # Show only relevant columns
        match_df = match_list[['title', 'genres', 'movie_avg_rating', 'ratings_count']]
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
