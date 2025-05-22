import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

st.markdown("""
    <style>
      .reportview-container .main .block-container {
        max-width: 100% !important;
        padding-left: 2rem;
        padding-right: 2rem;
      }
      html, body, [class*="css"]  {
        font-size: 0.8rem !important;
        text-align: center !important;
      }
      .stApp h1 {
        font-size: 2 rem !important;
      }
      .stApp h2 {
        font-size: 1.1rem !important;
      }
      .stTable table {
        font-size: 0.7rem !important;
      }
      .stDataFrame div[data-testid="stMarkdownContainer"] span {
        font-size: 0.7rem !important;
      }
    </style>
    <style>
      .stMarkdown table th,
      .stMarkdown table td {
        padding-top: 0.1rem !important;
        padding-bottom: 0.1rem !important;
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

col1, col2 = st.columns([3, 9])
with col1:
    min_ratings = st.slider(
        "Minimum Number of Ratings",
        0, 100, 50
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
    st.markdown("<div style='height:5.3em'></div>", unsafe_allow_html=True)

    # place top 10 overall movies on left
    top10_movies = (
        gt_min_df
          .drop_duplicates(subset=['movieId'])
          [['title', 'genres', 'movie_avg_rating', 'ratings_count']]
          .sort_values(by='movie_avg_rating', ascending=False)
          .head(10)
    )
    top10_movies['movie_avg_rating'] = top10_movies['movie_avg_rating'].round(2)
    
    top10_movies['genres'] = top10_movies['genres'].apply(lambda gl: ', '.join(gl) if isinstance(gl, list) else gl
)
    top10_movies = top10_movies.rename(columns={
        'title': 'Movie Title',
        'movie_avg_rating': 'Avg Rating',
        'genres' : 'Genres',
        'ratings_count': 'No of Ratings'
    })
    st.subheader("Top 10 Movies Overall")
    md_top10 = (
        top10_movies[['Movie Title','Genres','Avg Rating', 'No of Ratings']]
        .reset_index(drop=True)
        .to_markdown(index=False)
    )
    st.markdown(md_top10, unsafe_allow_html=True)

with col2:
    sel_genres = st.multiselect("Filter by Genre(s). Select the genres you want for a list of movies that are in all those genres", all_genres)

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
        'ratings_count': 'No of Ratings'
    })

    genre_header = (
        f"Top 10 Matching: {', '.join(sel_genres)}"
        if  sel_genres else
        "Top 10 Movies - No Genre Filter Applied"
    )
    st.subheader(genre_header)
    md_genre = (
        top10_genre[['Movie Title','Genres','Avg Rating', 'No of Ratings']]
        .reset_index(drop=True)
        .to_markdown(index=False)
    )
    st.markdown(md_genre, unsafe_allow_html=True)

# Add search box for movie title
col1, col2 = st.columns([4, 8])
with col1:
    search_box_text = st.text_input('Please enter the movie title')

if  search_box_text:
    found = data[data['title'].str.contains(search_box_text, case=False, na=False)]

    if  not found.empty:
        match_list = found.drop_duplicates(subset='title', keep='first')

        # Get the movie that most closely matches the search string
        best_match = match_list.iloc[0]
        bm_movie_id = best_match['movieId']
        bm_title = best_match['title']
        bm_genres = best_match['genres']
        bm_avg_rat = best_match['movie_avg_rating']

        # Get ratings for movie
        movie_ratings = found[found["movieId"] == bm_movie_id]["rating"]
        avg_rating = movie_ratings.mean()

        col_table, col_hist = st.columns([2, 1])

        with col_table:
            match_df = match_list[['title', 'genres', 'movie_avg_rating', 'ratings_count']].rename(columns={
                'title': 'Movie Title',
                'genres': 'Genres',
                'movie_avg_rating': 'Avg Rating',
                'ratings_count': 'No of Ratings'
            })
            st.subheader("Search Results")
            st.dataframe(match_df.reset_index(drop=True))
            
        # Plot histogram of ratings
        with col_hist:
            st.subheader(f"Ratings for {bm_title}")
            fig, ax = plt.subplots(figsize=(4, 0.8))
            ax.hist(movie_ratings, bins=5, edgecolor='black')
            ax.set_ylabel('Count', fontsize=6)
            ax.tick_params(axis='x', labelsize=4)
            ax.tick_params(axis='y', labelsize=4)
            st.pyplot(fig)

        st.divider()

        recs_df = load_recs()
        rec_row = recs_df[recs_df['movieId'] == bm_movie_id]

        if not rec_row.empty:
            top10_ids = rec_row.iloc[0, 1:11].tolist()
            top10_recs = (data[data['movieId'].isin(top10_ids)][['movieId', 'title', 'genres', 'movie_avg_rating']].drop_duplicates(subset=['movieId'])
)
            top10_recs['rank'] = top10_recs['movieId'].apply(lambda x: top10_ids.index(x) + 1)
            top10_recs = top10_recs.sort_values('rank')

            st.subheader(f"Top 10 Recommendations for: {bm_title}")
            st.table(
                top10_recs[['rank', 'title', 'genres', 'movie_avg_rating']].rename(columns={
                    'rank': 'Rank',
                    'title': 'Recommended Movie',
                    'genres': 'Genres',
                    'movie_avg_rating': 'Avg Rating'
                }).reset_index(drop=True)
            )
        else:
            st.warning("No recommendations found for this movie.")

    else:
        st.warning('No matching movie found.')
