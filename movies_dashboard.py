import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load your datasets
@st.cache_data
def load_data():
    movies = pd.read_csv("movies.csv", encoding="ISO-8859-1", low_memory=False)
    ratings = pd.read_csv("rating.csv", encoding="ISO-8859-1")
    df = ratings.merge(movies, on='movieId')
    return df

df = load_data()

st.title("🎬 Movie Ratings Dashboard")

st.sidebar.header("Filters")
genre_filter = st.sidebar.multiselect(
    "Select Genre(s):",
    options=sorted({g for sublist in df['genres'].str.split('|') for g in sublist}),
    default=[]
)

min_ratings = st.sidebar.slider("Minimum Number of Ratings", 0, 100, 50)

# Filter by selected genres
if genre_filter:
    df = df[df['genres'].apply(lambda g: any(genre in g for genre in genre_filter))]

# Group data
movie_stats = df.groupby(['movieId', 'title', 'genres']).agg(
    rating_count=('rating', 'count'),
    avg_rating=('rating', 'mean')
).reset_index()

# Apply min ratings filter
movie_stats = movie_stats[movie_stats['rating_count'] >= min_ratings]

# ------------------ METRICS ------------------ #
col1, col2, col3 = st.columns(3)
col1.metric("📽️ Total Movies Rated", df['movieId'].nunique())
col2.metric("👥 Total Users", df['userId'].nunique())
col3.metric("⭐ Average Rating", f"{df['rating'].mean():.2f}")

# ------------------ CHARTS ------------------ #
st.subheader("Top 10 Highest Rated Movies (with filters)")
top_movies = movie_stats.sort_values(by='avg_rating', ascending=False).head(10)
st.dataframe(top_movies[['title', 'avg_rating', 'rating_count']])

st.subheader("Top 10 Most Rated Movies")
most_rated = movie_stats.sort_values(by='rating_count', ascending=False).head(10)
st.dataframe(most_rated[['title', 'rating_count', 'avg_rating']])

# ------------------ PLOT ------------------ #
st.subheader("Ratings Distribution")

fig, ax = plt.subplots()
df['rating'].hist(bins=10, edgecolor='black', ax=ax)
ax.set_xlabel("Rating")
ax.set_ylabel("Frequency")
st.pyplot(fig)