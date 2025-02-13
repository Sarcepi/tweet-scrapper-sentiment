import asyncio
from playwright.async_api import async_playwright
from tqdm.asyncio import tqdm
from db_utils import clear_database, setup_database, insert_tweet,DB_NAME
from sentiment_utils import classify_sentiment
import sqlite3

async def scrape_tweets(name_or_email, password, phone, final_query, num_tweets):
   
    setup_database()
    clear_database()  

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        )
        page = await browser.new_page()
        await page.goto("https://x.com/home")
        await page.wait_for_load_state("networkidle")

        # ---------------------- 1. LOGIN ----------------------
        try:
            login_button = page.locator('xpath=//*[@id="layers"]/div/div/div/div/div/div[2]/button[1]')
            await login_button.click()
            print("Click on 'Iniciar sesión' button.")
        except Exception as e:
            print(f"Could not click on the first login button: {e}")

        try:
            second_button = page.locator(
                'xpath=//*[@id="react-root"]/div/div/div[2]/main/div/div/div[1]/'
                'div[1]/div/div[3]/div[3]/a/div'
            )
            await second_button.wait_for(state="visible")
            await second_button.click()
            print("Click on the secondary login button.")
        except Exception as e:
            print(f"Could not click on the secondary login button: {e}")

        try:
            email_input = page.locator(
                'xpath=//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/'
                'div/div/div[2]/div[2]/div/div/div/div[4]/label/div/div[2]/div/input'
            )
            await email_input.fill(name_or_email)
            await email_input.press("Enter")
            print("Successfully entered email/username.")
        except Exception as e:
            print(f"Error filling the email/username field: {e}")

        await asyncio.sleep(2)

        try:
            password_input = page.locator(
                'xpath=//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/'
                'div/div/div[2]/div[2]/div[1]/div/div/div[3]/div/label/div/div[2]/div[1]/input'
            )
            if await password_input.is_visible():
                await password_input.fill(password)
                print("Password entered directly.")
            else:
               
                phone_input = page.locator(
                    'xpath=/html/body/div/div/div/div[1]/div[2]/div/div/div/div/div/'
                    'div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div[2]/label/'
                    'div/div[2]/div/input'
                )
                await phone_input.fill(phone)
                await phone_input.press("Enter")
                print("Phone number entered.")
                
                await asyncio.sleep(2)
                await password_input.fill(password)
                print("Password entered after phone.")
        except Exception as e:
            print(f"Error entering password or phone: {e}")

        try:
            next_button = page.locator(
                'xpath=/html/body/div/div/div/div[1]/div[2]/div/div/div/div/div/'
                'div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div/button'
            )
            await next_button.click()
            print("Click on 'Next' / 'Login' button.")
        except Exception as e:
            print(f"Could not click on the login button: {e}")
        
        await asyncio.sleep(5)

        # ---------------------- 2. SEARCH ----------------------
        try:
            
            search_input = page.locator(
                'xpath=/html/body/div[1]/div/div/div[2]/main/div/div/div/div[2]/div/div[2]/div/div/div/div/div[1]/div/div/div/form/div[1]/div/div/div/div/div[2]/div/input'
            )
            await search_input.click()
            await search_input.fill(final_query) 
            await search_input.press("Enter")
            print(f"Search performed for topic: {final_query}")
        except Exception as e:
            print(f"Error performing the search: {e}")

# ---------------------- 3. OPTIMIZED TWEET EXTRACTION ----------------------
   
        tweets_observados = set()
        target_tweets = num_tweets
        scroll_attempts = 0
        max_scroll_attempts = target_tweets * 2 

        try:
            pbar = tqdm(total=target_tweets, desc="Scraping tweets")
            
            while (len(tweets_observados) < target_tweets 
                and scroll_attempts < max_scroll_attempts):

                if page.is_closed():
                    raise Exception("Page closed unexpectedly")
                await asyncio.sleep(5)

                tweet_elements = await page.locator('//article[@role="article"]').all()
                
                new_tweets = []
                for tweet_element in tweet_elements:
                    try:

                        if len(tweets_observados) >= target_tweets:
                            break
                            
                        tweet_text = await tweet_element.locator('[data-testid="tweetText"]').text_content()
                        tweet_date = await tweet_element.locator('time').get_attribute('datetime')
                        
                        if tweet_text and tweet_date:
                            tweet_text = tweet_text.strip()
                            tweet_date = tweet_date.strip()
                            unique_key = (tweet_text, tweet_date)
                            
                            if unique_key not in tweets_observados:
                                new_tweets.append((tweet_text, tweet_date))

                    except Exception as e:
                        print(f"Error extracting tweet: {e}")
                        continue

                if new_tweets:

                    sentiments = [classify_sentiment(tweet[0]) for tweet in new_tweets]
                    
                    try:
                        conn = sqlite3.connect(DB_NAME)
                        cursor = conn.cursor()
                        cursor.executemany(
                            "INSERT INTO tweets_sentiment (Tweet, Date, Sentiment) VALUES (?, ?, ?)",
                            [(tweet[0], tweet[1], sentiment) for tweet, sentiment in zip(new_tweets, sentiments)]
                        )
                        conn.commit()
                        conn.close()
                    except Exception as e:
                        print(f"Batch insert error: {e}")
                    
                    tweets_observados.update({(t[0], t[1]) for t in new_tweets})
                    pbar.update(len(new_tweets))

                try:
                    prev_height = await page.evaluate("document.body.scrollHeight")
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await asyncio.wait_for(page.wait_for_load_state("networkidle"), timeout=5)
                    await asyncio.sleep(0.25)
                    
                    new_height = await page.evaluate("document.body.scrollHeight")
                    scroll_attempts += 1 if prev_height == new_height else 0
                except (TimeoutError, Exception) as e:
                    print(f"Scroll error: {e}")
                    scroll_attempts += 1

        finally:
            pbar.close()
            if not page.is_closed():
                await page.close()
            print(f"Scraping complete. Total tweets stored: {len(tweets_observados)}")