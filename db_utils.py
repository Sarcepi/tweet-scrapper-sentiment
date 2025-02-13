import sqlite3
import pandas as pd

DB_NAME = "tweets_sentiment.db" 
def setup_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tweets_sentiment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Tweet TEXT,
            Date TEXT,
            Sentiment TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_tweets_dataframe(db_name=DB_NAME):
    conn = sqlite3.connect(db_name)
    df = pd.read_sql("SELECT * FROM tweets_sentiment", conn)
    conn.close()
    return df


def clear_database():
    """
    Delete all records from the tweets_sentiment table.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tweets_sentiment")
    conn.commit()
    conn.close()
    print("Database cleared.")


def insert_tweet(tweet_text, tweet_date, sentiment):
    """
    Insert a single tweet into the database.
    """
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tweets_sentiment (Tweet, Date, Sentiment) VALUES (?, ?, ?)",
            (tweet_text, tweet_date, sentiment),
        )
        conn.commit()
        conn.close()
        print(f"Inserted tweet: {tweet_text[:50]}...")  
    except Exception as e:
        print(f"Error inserting tweet: {e}")


def load_df():
    """
    Load all tweets from the database into a pandas DataFrame.
    """
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM tweets_sentiment", conn)
    conn.close()
    print(f"Loaded {len(df)} tweets from the database.")
    return df


def clear_database_news():
    """
    Delete all records from the news_sentiment table.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM news_sentiment")
    conn.commit()
    conn.close()
    print("Database cleared.")