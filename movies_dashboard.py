import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load your datasets
@st.cache_data
def load_data():
    ratings = pd.read_csv("ratings.csv")  # Adjust path as needed
    movies = pd.read_csv("movies.csv")
    df = ratings.merge(movies, on='movieId')
    return df

df = load_data()
data_load_state.text("Done! (using st.cache_data)")

st.title("🎬 Movie Ratings Dashboard")

