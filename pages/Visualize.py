import streamlit as st
import os
from pymongo.server_api import ServerApi
import pymongo
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.tokenize import word_tokenize
from sklearn.decomposition import LatentDirichletAllocation
import plotly.express as px
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import umap
import hdbscan
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

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

def preprocess_text(text):
    # Convert to lowercase
    text = text.lower()

    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)

    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)

    # Remove special characters and numbers, but keep hyphens for compound words
    text = re.sub(r'[^a-zA-Z\s-]', '', text)

    # Tokenize the text
    tokens = word_tokenize(text)

    # Remove stopwords
    stop_words = set(stopwords.words('english'))

    # Add domain-specific stopwords
    domain_stopwords = {'scholarship', 'student', 'award', 'application', 'apply', 'program', 'opportunity'}
    stop_words.update(domain_stopwords)

    # Remove stopwords, but keep negation words
    tokens = [token for token in tokens if token not in stop_words or token in ['no', 'not', 'nor', 'neither']]

    # Lemmatization
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(token) for token in tokens]

    # Join tokens back into a string
    processed_text = ' '.join(tokens)

    # Preserve important hyphenated terms
    important_terms = ['first-generation', 'low-income', 'african-american', 'asian-american', 'native-american', 'latin-american']
    for term in important_terms:
        processed_text = processed_text.replace(term.replace('-', ' '), term)

    # Preserve DEI-related terms
    dei_terms = ['diversity', 'equity', 'inclusion', 'dei', 'minority', 'underrepresented', 'marginalized']
    for term in dei_terms:
        processed_text = processed_text.replace(term, f"DEI_{term}")

    # Preserve identity-related terms
    identity_terms = ['gender', 'race', 'ethnicity', 'lgbtq', 'disability', 'veteran', 'immigrant', 'refugee', 'indigenous', 'native']
    for term in identity_terms:
        processed_text = processed_text.replace(term, f"IDENTITY_{term}")

    return processed_text

df['processed_description'] = df['description'].apply(preprocess_text)

# TF-IDF Vectorization
vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 2))
tfidf_matrix = vectorizer.fit_transform(df['processed_description'])

# Dimensionality Reduction
umap_embeddings = umap.UMAP(n_neighbors=15, n_components=5, metric='cosine').fit_transform(tfidf_matrix)

# Clustering
hdbscan_cluster = hdbscan.HDBSCAN(min_cluster_size=5, metric='euclidean', cluster_selection_method='eom')
df['Cluster'] = hdbscan_cluster.fit_predict(umap_embeddings)

# Visualization
umap_2d = umap.UMAP(n_neighbors=15, n_components=2, metric='cosine').fit_transform(tfidf_matrix)
df['UMAP1'], df['UMAP2'] = umap_2d[:, 0], umap_2d[:, 1]

fig = px.scatter(df, x='UMAP1', y='UMAP2', color='Cluster', hover_data=['title'])
st.plotly_chart(fig)

# Topic Modeling
lda_model = LatentDirichletAllocation(n_components=10, random_state=42)
lda_output = lda_model.fit_transform(tfidf_matrix)

# Display topics
feature_names = vectorizer.get_feature_names_out()
for topic_idx, topic in enumerate(lda_model.components_):
    top_words = [feature_names[i] for i in topic.argsort()[:-10 - 1:-1]]
    st.write(f"Topic {topic_idx}: {', '.join(top_words)}")

# Combine DEI and identity keywords into a single list
dei_identity_keywords = [
    'diversity', 'equity', 'inclusion', 'minority', 'underrepresented',
    'gender', 'race', 'ethnicity', 'lgbtq', 'disability',
    'first-generation', 'low-income', 'international', 'veteran',
    'immigrant', 'refugee', 'indigenous', 'native'
]

def combined_keyword_score(text, keywords):
    # Convert text to lowercase for case-insensitive matching
    text = text.lower()
    # Count the occurrences of each keyword
    return sum(text.count(keyword) for keyword in keywords)

# Apply the scoring function to the DataFrame
df['DEI_Identity_Score'] = df['description'].apply(lambda x: combined_keyword_score(x, dei_identity_keywords))

# Visualize the combined DEI and Identity scores
fig = px.scatter(df, x='DEI_Identity_Score', y='Cluster', color='Cluster',
                 hover_data=['title', 'description'],
                 labels={'DEI_Identity_Score': 'Combined DEI & Identity Score', 'Cluster': 'Cluster'},
                 title='Scholarships by DEI & Identity Score and Cluster')

# Add jitter to y-axis to prevent overplotting
fig.update_traces(marker=dict(size=10),
                  selector=dict(mode='markers'))
fig.update_layout(yaxis=dict(tickmode='linear'),  # Show all cluster numbers
                  height=600)  # Increase height for better visibility

# Display the plot
st.plotly_chart(fig)

# Display top scoring scholarships
st.subheader("Top Scoring Scholarships for DEI & Identity")
top_scholarships = df.nlargest(10, 'DEI_Identity_Score')[['title', 'description', 'DEI_Identity_Score']]
st.table(top_scholarships)

# Display distribution of scores
st.subheader("Distribution of DEI & Identity Scores")
fig_hist = px.histogram(df, x='DEI_Identity_Score', nbins=20,
                        labels={'DEI_Identity_Score': 'Combined DEI & Identity Score'},
                        title='Distribution of Combined DEI & Identity Scores')
st.plotly_chart(fig_hist)

# from wordcloud import WordCloud

# def generate_wordcloud(text):
#     wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
#     plt.figure(figsize=(10, 5))
#     plt.imshow(wordcloud, interpolation='bilinear')
#     plt.axis('off')
#     st.pyplot(plt)

# all_descriptions = ' '.join(df['description'])
# st.subheader("Word Cloud of All Descriptions")
# generate_wordcloud(all_descriptions)

# from collections import Counter
# from nltk import ngrams

# def get_top_ngrams(text, n, top_k=10):
#     words = text.split()
#     n_grams = ngrams(words, n)
#     return Counter(n_grams).most_common(top_k)

# st.subheader("Top Bigrams and Trigrams")
# col1, col2 = st.columns(2)
# with col1:
#     st.write("Top Bigrams")
#     st.write(get_top_ngrams(all_descriptions, 2))
# with col2:
#     st.write("Top Trigrams")
#     st.write(get_top_ngrams(all_descriptions, 3))

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
