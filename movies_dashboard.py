import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load your datasets
@st.cache_data
def load_data():
    movies = pd.read_csv("movies_ar.csv", encoding="ISO-8859-1", low_memory=False)
    movies['genres'] = movies['genres'].str.split('|')
    ratings = pd.read_csv("rating.csv", encoding="ISO-8859-1")
    df = ratings.merge(movies, on='movieId')
    return df

data = load_data()

st.title("🎬 Movie Ratings Dashboard")

search_box_text = st.text_input("Please enter the movie title")

if search_box_text:
    found = data[data["title"].str.contains(search_term, case=False, na=False)]

    if not found.empty:
        match_list = found.drop_duplicates(subset="title", keep="first")

        # Show only relevant columns
        match_df = match_list[["title", "genres", "avg_rating"]]

        st.subheader("Search Results")
        st.dataframe(match_df.reset_index(drop=True))
    else:
        st.warning("No matching movie found.")