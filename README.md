# Twitter Scraping & Sentiment Analysis Dashboard

Welcome to my personal project where I merge web scraping, natural language processing, and interactive data visualization to bring Twitter insights to life! This repository showcases an end-to-end solution that not only scrapes tweets in real-time but also performs sentiment analysis and topic modeling—all within a sleek, user-friendly dashboard.

---

## Overview

This project is designed to:

- **Scrape Tweets:** Automate the extraction of tweets from Twitter (X) using asynchronous Playwright.
- **Perform Sentiment Analysis:** Leverage a state-of-the-art transformer model (`cardiffnlp/twitter-roberta-base-sentiment-latest`) to classify tweets into Negative, Neutral, or Positive sentiments.
- **Store & Manage Data:** Utilize an SQLite database to store and manage tweet data for persistent analysis.
- **Preprocess & Analyze Text:** Clean and tokenize tweet texts with NLTK, and uncover hidden themes using LDA topic modeling and Word2Vec embeddings.
- **Visualize Data:** Create interactive charts and graphs with Plotly and Streamlit to explore trends and word distributions over time.

---

## Key Features

### Real-Time Twitter Scraping
- **Automated Login & Navigation:** Use asynchronous Playwright to navigate and log into Twitter seamlessly.
- **Dynamic Tweet Extraction:** Efficiently scrape tweets based on customizable search queries and date ranges.

### Sentiment Analysis
- **State-of-the-Art Model:** Classify sentiments using a cutting-edge transformer model fine-tuned for Twitter data.
- **Data-Driven Insights:** Visualize sentiment trends over time with interactive line and pie charts.

### Interactive Data Dashboard
- **Streamlit-Powered Interface:** Enjoy a modern, responsive dashboard with intuitive controls and real-time updates.
- **Comprehensive Visualizations:** Dive deep into tweet trends, popular keywords, and topic distributions with dynamic Plotly charts.

### 🔍 NLP & Topic Modeling
- **Text Preprocessing:** Clean and tokenize tweets to filter out noise and enhance analysis.
- **Topic Extraction:** Discover trending topics using LDA and visualize word embeddings via PCA projections.

---

## Technologies Used

- **Python**: The core programming language for the project.
- **Streamlit**: For building an interactive and visually appealing dashboard.
- **Playwright**: Asynchronous web scraping for robust Twitter data extraction.
- **SQLite**: Lightweight database for storing tweet data.
- **NLTK**: Natural language processing for text cleaning and tokenization.
- **Hugging Face Transformers**: Advanced sentiment analysis with pretrained models.
- **Gensim**: Topic modeling and word embeddings.
- **Plotly**: Interactive data visualizations.

---
