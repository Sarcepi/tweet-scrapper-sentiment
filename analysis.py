import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import nltk
from nltk.tokenize import TweetTokenizer
from nltk.corpus import stopwords
import string
from db_utils import setup_database, get_tweets_dataframe
import gensim.corpora as corpora
from gensim.models import LdaModel, Word2Vec
from sklearn.decomposition import PCA

st.set_page_config(
    page_title="Twitter Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stButton>button {
         background-color: #001f3f;
         color: white;
         border: none;
         border-radius: 5px;
         padding: 10px 20px;
         font-size: 16px;
         transition: background-color 0.3s ease;
    }
    .stButton>button:hover {
         background-color: #00264d;
    }
    [data-testid="stSidebar"] .css-1d391kg {
         background: linear-gradient(135deg, #000428, #004e92) !important;
         border: 2px solid #004e92 !important;
         border-radius: 5px !important;
         padding: 10px;
         margin-bottom: 10px;
         color: white;
    }
    </style>
    """, unsafe_allow_html=True
)

setup_database()
df = get_tweets_dataframe()
df["Sentiment"] = df["Sentiment"].replace({"Negativo": "Negative", "Positivo": "Positive"})

st.title("Analysis")
st.subheader("Tweets Extracted")
st.dataframe(df)

df['date'] = pd.to_datetime(df['Date'])
df['date_only'] = df['date'].dt.date

df_grouped = df.groupby(['date_only', 'Sentiment']).size().reset_index(name='Count')
df_pivot = df_grouped.pivot(index='date_only', columns='Sentiment', values='Count').fillna(0)

fig_time = px.line(
    df_pivot,
    x=df_pivot.index,
    y=df_pivot.columns,
    labels={'value': 'Número de Tweets', 'date_only': 'Fecha'},
    title='Número de Tweets por Sentiment a lo largo del Tiempo'
)
st.plotly_chart(fig_time)

nltk.download('stopwords')
stop_words = set(stopwords.words('english'))
sentiment_counts = df['Sentiment'].value_counts().reset_index()
sentiment_counts.columns = ['Sentiment', 'Count']
fig = px.pie(sentiment_counts, names="Sentiment", values="Count", title="Sentiment counts")
st.plotly_chart(fig)

tokenizer = TweetTokenizer()
df['tokens'] = df['Tweet'].apply(tokenizer.tokenize)

def remove_punctuation(tokens):
    return [token for token in tokens if token not in string.punctuation]

df['filtered_tokens'] = df['tokens'].apply(remove_punctuation)
df['filtered_tokens'] = df['filtered_tokens'].apply(
    lambda tokens: [
        token_clean
        for token in tokens
        for token_clean in [token.replace('’', '').strip()]
        if token_clean and any(c.isalnum() for c in token_clean) and token_clean.lower() not in stop_words
    ]
)
df['filtered_tokens'] = df['filtered_tokens'].apply(
    lambda tokens: [token for token in tokens if token.lower() not in stop_words]
)

df_exploded = df.explode('filtered_tokens')
token_summary = df_exploded.groupby('filtered_tokens').agg(
    Count=('filtered_tokens', 'count'),
    Most_Common_Sentiment=('Sentiment', lambda x: x.value_counts().idxmax()),
    Sentiments=('Sentiment', lambda x: list(x))
).reset_index()

top_10_tokens = token_summary.sort_values('Count', ascending=False).head(10)
fig2 = px.bar(top_10_tokens, x='filtered_tokens', y='Count', title="Top 10 words in the data")
st.plotly_chart(fig2)

negative_tokens = token_summary[token_summary['Most_Common_Sentiment'] == 'Negative']
top10_negative = negative_tokens.sort_values(by='Count', ascending=False).head(10)
fig3 = px.bar(top10_negative, x='filtered_tokens', y='Count', color_discrete_sequence=['red'], title="Top 10 negative associated words")
st.plotly_chart(fig3)

positive_tokens = token_summary[token_summary['Most_Common_Sentiment'] == 'Positive']
top10_positive = positive_tokens.sort_values(by='Count', ascending=False).head(10)
fig4 = px.bar(top10_positive, x='filtered_tokens', y='Count', color_discrete_sequence=['green'], title="Top 10 positive associated words")
st.plotly_chart(fig4)

st.dataframe(top_10_tokens)

w2v_model = Word2Vec(
    sentences=df['filtered_tokens'],  
    vector_size=100,    
    window=5,            
    min_count=2,         
    workers=4,           
    seed=42
)

dictionary = corpora.Dictionary(df['filtered_tokens'])
dictionary.filter_extremes(no_below=5, no_above=0.5)
corpus = [dictionary.doc2bow(tokens) for tokens in df['filtered_tokens']]
lda_model = LdaModel(
    corpus=corpus,
    id2word=dictionary,
    num_topics=5,
    random_state=42,
    passes=10,
    per_word_topics=True
)

topics = lda_model.print_topics(num_words=10)
for topic_id, topic in topics:
    print(f"Topic {topic_id}: {topic}")

words = w2v_model.wv.index_to_key[:100]
word_vectors = np.array([w2v_model.wv[word] for word in words])
pca = PCA(n_components=2)
result = pca.fit_transform(word_vectors)
df_pca = pd.DataFrame(result, columns=['PC1', 'PC2'])
df_pca['word'] = words

fig5 = px.scatter(
    df_pca, 
    x='PC1', 
    y='PC2', 
    text='word',
    title='PCA Projection of Word Embeddings',
    template='plotly_white'
)
fig5.update_traces(textposition='top center')
st.plotly_chart(fig5)

st.header("Topic Analysis")
topics = lda_model.print_topics(num_words=10)
for topic in topics:
    topic_id, topic_words = topic
    st.markdown(f"**Topic {topic_id}:** {topic_words}")
