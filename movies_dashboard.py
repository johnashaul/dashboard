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
data_load_state.text("Done! (using st.cache_data)")

st.title("🎬 Movie Ratings Dashboard")

