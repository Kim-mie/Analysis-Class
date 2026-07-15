import streamlit as st
import pandas as pd

st.title("Automobile Data Dashboard")

# Load data
columns = [
    "symboling","normalized-losses","make","fuel-type","aspiration",
    "num-of-doors","body-style","drive-wheels","engine-location",
    "wheel-base","length","width","height","curb-weight",
    "engine-type","num-of-cylinders","engine-size","fuel-system",
    "bore","stroke","compression-ratio","horsepower",
    "peak-rpm","city-mpg","highway-mpg","price"
]

url = "https://archive.ics.uci.edu/ml/machine-learning-databases/autos/imports-85.data"
df = pd.read_csv(url, names=columns)

# Clean data
df.replace("?", pd.NA, inplace=True)

num_cols = ['price','horsepower','bore','stroke','peak-rpm']
for col in num_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

df = df.dropna()

# Show dataset
st.subheader("Dataset Preview")
st.write(df.head())

# Descriptive stats
st.subheader("Descriptive Statistics")
st.write(df.describe())

# Column analysis
column = st.selectbox("Select a column", df.select_dtypes(include='number').columns)

st.subheader(f"Statistics for {column}")
st.write(df[column].describe())

# Correlation
st.subheader("Correlation")
st.write(df[['price','horsepower','engine-size']].corr())



