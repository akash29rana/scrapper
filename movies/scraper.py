import requests
from bs4 import BeautifulSoup
import logging
from playwright.async_api import async_playwright
import asyncio

logger = logging.getLogger(__name__)

BASE_URL = "https://www.imdb.com/search/title/?title_type=feature,tv_movie&genres={genre}"


async def scrape_with_playwright(genre, update_progress):
    async with async_playwright() as p:
        
        browser = await p.chromium.launch(headless=True,args=["--start-maximized"],)  # Use headless=True for faster performance
        url = BASE_URL.format(genre=genre)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},  # Set viewport size
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        page = await context.new_page()
        await page.goto(url)
        print("started scrapping url is :",url)
        result = []
        seen_titles = set()  # To track already scraped movies by title
        total_movies = await page.query_selector(".sc-13add9d7-3.fwjHEn")
        if total_movies:
            total_movies_text = await total_movies.inner_text()
            total_movies_count = 0
            try:
                total_movies_count = int(total_movies_text.split(" of ")[1].replace(",", ""))
            except ValueError:
                logger.error("Invalid number format.")
                return result
             # Set this to the total number of movies you're scraping, or estimate it
            movies_scraped = 0
            break_now = False
            while movies_scraped != total_movies_count:
                items = await page.query_selector_all(".ipc-metadata-list-summary-item")
                new_items = []  # List to store new items on this iteration

                for item in items:
                    title = await item.query_selector(".ipc-title__text")
                    title_text = await title.inner_text()
                    # print("title_text is :" ,title_text)
                    if title_text not in seen_titles:
                        seen_titles.add(title_text)  # Mark this movie as seen

                        release_year = await item.query_selector(".sc-300a8231-7.eaXxft.dli-title-metadata-item")
                        release_year_text = await release_year.inner_text() if release_year else 0
                        try:
                            release_year_int = int(release_year_text)
                        except ValueError:
                            logger.error(f"Doesn't get value for release_year for movie : {title_text}")
                            release_year_int = 0 
                        imdb_rating = await item.query_selector(".ipc-rating-star--rating")
                        imdb_rating_text = await imdb_rating.inner_text()if imdb_rating else 0
                        try:
                            imdb_rating_float = float(imdb_rating_text)
                        except ValueError:
                            logger.error(f"Doesn't get value for imdb_rating for movie : {title_text}")
                            imdb_rating_float = 0 
                        description = await item.query_selector(".ipc-html-content-inner-div")
                        description_text = await description.inner_text() if description else ""
                        data = {
                            'title': title_text.split(' ',1)[1],
                            'description': description_text,
                            'year': release_year_int,
                            'rating':imdb_rating_float,
                            'director':"None",
                            'cast':"None",
                        }
                        new_items.append(data)
                        movies_scraped += 1
                        progress_percentage = (movies_scraped / total_movies_count) * 100
                        update_progress(progress_percentage,genre)

                    # Only process movies that haven't been seen before
                    
                
                # Add the new items to result
                result.extend(new_items)
                if break_now:
                    break
                await asyncio.sleep(1) # Putting sleep for 1 sec so that more button can get disabled if no more movies are there
                more_button = await page.query_selector(".ipc-see-more__button")
                if more_button:
                    try: 
                        await more_button.click()
                        # Wait for the new movies to load
                        await page.wait_for_selector(".ipc-metadata-list-summary-item", state="attached")
                    except Exception as e:
                        break_now = True
                        logger.error("Error clicking '50 more' button:", e)
                else:
                    break_now = True  
            
            update_progress(100,genre)
         
        await browser.close()
        print("end")
        return result
