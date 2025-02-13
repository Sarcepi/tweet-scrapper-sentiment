import streamlit as st
import asyncio
import datetime
import pandas as pd
from scrape import scrape_tweets
from db_utils import load_df, setup_database, clear_database
from sentiment_utils import classify_sentiment
import nltk

# Configure the page
st.set_page_config(
    page_title="Twitter Scraping & Sentiment Analysis",
    page_icon="🐦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS with updated dark blue buttons, gradient blue main container and black-blue gradient for the sidebar
st.markdown(
    """
    <style>
    /* Set a neutral background for the entire app */
    body {
        background-color: #f0f2f6;
    }
    /* Main container styling with gradient blue background */
    .main {
        background: linear-gradient(135deg, #4facfe, #00f2fe);
        padding: 2rem;
        border-radius: 10px;
        color: #333;
    }
    /* Style for dark blue buttons */
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
    /* Sidebar headers and expanders with black-blue gradient */
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

def main():
    # Initialize the database
    setup_database()

    # Main title and description
    st.title("🐦 Twitter (X) Scraping & Sentiment Analysis")
    st.markdown("""
    Welcome to the **Twitter Scraping & Sentiment Analysis Dashboard**. This application allows you to:
    - Log into Twitter (X)
    - Scrape tweets by topic
    - Perform sentiment analysis 
    - Store and view the results

    Enjoy exploring Twitter data with a sleek design!
    """)

    # Sidebar for configuration
    st.sidebar.header("Configuration")

    with st.sidebar.expander("🔐 Twitter Login Details", expanded=True):
        name_or_email = st.text_input("Username/Email for Twitter", "")
        password = st.text_input("Twitter Password", "", type="password")
        phone = st.text_input("Phone (optional)", "")

    with st.sidebar.expander("🔍 Twitter Search Parameters", expanded=True):
        base_topic = st.text_input("Base Topic", "nvidia")
        start_date = st.date_input("Start Date", datetime.date(2024, 1, 1))
        end_date = st.date_input("End Date", datetime.date(2025, 1, 28))
        num_tweets = st.number_input("Number of Tweets to Scrape", min_value=1, value=100, step=1)

    st.write(f"**Twitter Date Range**: {start_date} to {end_date}")

    # Button to start scraping tweets
    if st.button("🚀 Start Twitter Scraping"):
        if not name_or_email or not password:
            st.warning("Please enter your Twitter username/email and password.")
        else:
            final_query = (
                f"{base_topic} until:{end_date.strftime('%Y-%m-%d')} "
                f"since:{start_date.strftime('%Y-%m-%d')} lang:en"
            )
            st.write(f"**Twitter Final Query**: `{final_query}`")

            with st.spinner("🕵️‍♂️ Scraping tweets, please wait..."):
                try:
                    asyncio.run(scrape_tweets(name_or_email, password, phone, final_query, num_tweets))
                    st.success("✅ Twitter scraping completed. Tweets stored in the database.")
                except Exception as e:
                    st.error(f"Error during Twitter scraping: {e}")

    st.markdown("---")

    # Section to view scraped tweets
    st.subheader("📄 View Scraped Tweets")
    if st.button("🔄 Load Tweets Data"):
        with st.spinner("Loading tweets data..."):
            df_tweets = load_df()
            if df_tweets.empty:
                st.warning("No tweets found in the database.")
            else:
                st.dataframe(df_tweets)

    if st.button("Clear tweets"):
        clear_database()
        st.success("Tweets database cleared.")

    st.markdown("---")

if __name__ == "__main__":
    main()
