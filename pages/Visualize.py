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

import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer

nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')
nltk.download('wordnet')

def advanced_preprocess(text):
    # Convert to lowercase
    text = text.lower()

    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)

    # Tokenize
    tokens = nltk.word_tokenize(text)

    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token not in stop_words]

    # Lemmatization
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in tokens]

    return ' '.join(lemmatized_tokens)

df['processed_description'] = df['description'].apply(advanced_preprocess)

# Vectorize the text data
@st.cache_resource
def vectorize_text(texts):
    vectorizer = TfidfVectorizer(max_features=1000)
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

from wordcloud import WordCloud
import matplotlib.pyplot as plt

def generate_wordcloud(text):
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    st.pyplot(plt)

all_descriptions = ' '.join(df['description'])
st.subheader("Word Cloud of All Descriptions")
generate_wordcloud(all_descriptions)

from collections import Counter
from nltk import ngrams

def get_top_ngrams(text, n, top_k=10):
    words = text.split()
    n_grams = ngrams(words, n)
    return Counter(n_grams).most_common(top_k)

st.subheader("Top Bigrams and Trigrams")
col1, col2 = st.columns(2)
with col1:
    st.write("Top Bigrams")
    st.write(get_top_ngrams(all_descriptions, 2))
with col2:
    st.write("Top Trigrams")
    st.write(get_top_ngrams(all_descriptions, 3))

from gensim import corpora
from gensim.models.ldamodel import LdaModel
from gensim.parsing.preprocessing import STOPWORDS
import gensim

def preprocess(text):
    return [word for word in gensim.utils.simple_preprocess(text) if word not in STOPWORDS]

texts = df['description'].apply(preprocess)
dictionary = corpora.Dictionary(texts)
corpus = [dictionary.doc2bow(text) for text in texts]

lda_model = LdaModel(corpus=corpus, id2word=dictionary, num_topics=5, random_state=100)

st.subheader("LDA Topic Modeling")
for idx, topic in lda_model.print_topics(-1):
    st.write(f'Topic: {idx}')
    st.write(topic)

from textblob import TextBlob

def get_sentiment(text):
    return TextBlob(text).sentiment.polarity

df['sentiment'] = df['description'].apply(get_sentiment)

st.subheader("Sentiment Distribution")
fig, ax = plt.subplots()
ax.hist(df['sentiment'], bins=20)
ax.set_xlabel('Sentiment Score')
ax.set_ylabel('Frequency')
st.pyplot(fig)

import textstat

def get_readability_scores(text):
    return {
        'flesch_reading_ease': textstat.flesch_reading_ease(text),
        'smog_index': textstat.smog_index(text),
        'flesch_kincaid_grade': textstat.flesch_kincaid_grade(text)
    }

df['readability_scores'] = df['description'].apply(get_readability_scores)
readability_df = pd.DataFrame(df['readability_scores'].tolist())

st.subheader("Text Complexity Distribution")
for column in readability_df.columns:
    st.write(f"{column} Distribution")
    st.line_chart(readability_df[column])

df['description_length'] = df['description'].str.len()

st.subheader("Description Length Distribution")
fig, ax = plt.subplots()
ax.hist(df['description_length'], bins=20)
ax.set_xlabel('Description Length')
ax.set_ylabel('Frequency')
st.pyplot(fig)
