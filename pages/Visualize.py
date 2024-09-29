import streamlit as st
import os
from pymongo.server_api import ServerApi
import pymongo
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import plotly.express as px
from sklearn.decomposition import PCA
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv('MONGO_URI')

# MongoDB connection
@st.cache_resource
def init_connection():
    return pymongo.MongoClient(MONGO_URI, server_api=ServerApi('1'))

client = init_connection()

# Function to get data from MongoDB
@st.cache_data
def get_data():
    db = client['scholarship_db']
    scholarships = db['scholarships'].find()
    scholarships = list(scholarships)
    return scholarships

# Load the data
data = get_data()

# Convert to DataFrame
df = pd.DataFrame(data)

# Preprocess the text data
@st.cache_data
def preprocess_text(text):
    # You can add more preprocessing steps here if needed
    return text.lower()

df['processed_description'] = df['description'].apply(preprocess_text)

# Vectorize the text data
@st.cache_resource
def vectorize_text(texts):
    vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
    return vectorizer, vectorizer.fit_transform(texts)

vectorizer, tfidf_matrix = vectorize_text(df['processed_description'])

# Streamlit app
st.title('K-means Clustering on Scholarship Descriptions')

# Sidebar for user input
st.sidebar.header('Clustering Parameters')
k = st.sidebar.slider('Number of clusters (k)', 2, 10, 3)
max_words = st.sidebar.slider('Number of top words per cluster', 5, 20, 10)

# Perform k-means clustering
@st.cache_data
def perform_clustering(_matrix, n_clusters):
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    return kmeans.fit(_matrix)

kmeans = perform_clustering(tfidf_matrix, k)

# Add cluster labels to the original dataframe
df['Cluster'] = kmeans.labels_

# Perform PCA for visualization
pca = PCA(n_components=2)
pca_result = pca.fit_transform(tfidf_matrix.toarray())
df['PCA1'] = pca_result[:, 0]
df['PCA2'] = pca_result[:, 1]

# Create the scatter plot
fig = px.scatter(df, x='PCA1', y='PCA2', color='Cluster', hover_data=['title'])
st.plotly_chart(fig)

# Display cluster information
st.subheader('Cluster Information')
for i in range(k):
    st.write(f"Cluster {i}:")
    cluster_data = df[df['Cluster'] == i]
    st.write(cluster_data[['title', 'description']].head())

    # Get top words for this cluster
    cluster_center = kmeans.cluster_centers_[i]
    top_words_idx = cluster_center.argsort()[::-1][:max_words]
    top_words = [vectorizer.get_feature_names_out()[idx] for idx in top_words_idx]
    st.write(f"Top words: {', '.join(top_words)}")
    st.write("---")

# Display raw data
if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(df)
