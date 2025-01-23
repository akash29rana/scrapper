
Movie Scraper Project

This project provides a movie scraping service that allows users to search movies by genre and title, with efficient bulk operations to add movies to the database. Scraping is done asynchronously to avoid blocking other requests, and logging is integrated for better error tracking.

Bulk Query Handling for Efficient Database Operations
- To efficiently insert a large number of movies into the database, bulk operations are utilized. "create_movies_in_bulk" method ensures the movies are inserted in batches, minimizing database overhead and improving performance.

Asyncio for Asynchronous Scraping
- To avoid blocking the server during scraping operations, I use asyncio to perform scraping concurrently. This allows the server to handle other requests while the scraping is in progress.

Logging for Error Tracking
- To keep track of errors, a logging mechanism is integrated into the project. This helps monitor and troubleshoot issues during scraping or when interacting with the API.


How to install dependencies:
    
     python3 -m venv env
     source env/bin/activate
- Go to project folder in which manage.py is there
-     pip install -r requirements.txt

How to run project
- Go to project folder in which manage.py is there
-     python manage.py runserver

I use redis to save progress of the scrapping, So if you don't run your redis server your progress will not be shown.

Install redis
- For Mac => Run command in terminal 
-     brew install redis
- For ubuntu =>  Run command in terminal 
-     sudo apt update
      sudo apt install redis-server

Run Redis
- Mac/Linux => Run command in terminal
-     redis-server

Steps to run scrapper 
- In browser go to "http://localhost:8000/search/"
- You can search movies through genre you can use multiple genre like this e.g : "action,comedy"
- Then scrapping will be started and you have to wait till then


API calls to get movies-
- GET => "http://localhost:8000/api/movies/" => will get all the movies
- GET => "http://localhost:8000/api/movies/?title=movie_name" => will get the particular movie
- GET => "http://localhost:8000/api/movies/?genre=movie_genre" => will get the movie with same genre

API calls to add movies-
- POST => "http://localhost:8000/api/movies/" => will ADD the movie. sample content :
-     {
            "title": "Movie Title",
            "release_year": 2023,
            "imdb_rating": 7.5,
            "director": "Director Name",
            "cast": "Cast Names",
            "plot_summary": "Brief plot summary of the movie"
        }
    


Conclusion

This project is designed to scrape movies efficiently by handling bulk insertions, using asynchronous scraping, and implementing a logging mechanism for better error handling. By following the steps mentioned above, you can easily set up the project, run the scraper, and interact with the API.




