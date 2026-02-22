from fastapi import FastAPI, HTTPException, Query
from main import fetch_rss, scrape_page, run_all_scrapers
import uvicorn

app = FastAPI(title="Blog Scraper API")

@app.get("/")
def read_root():
    return {"message": "Blog Scraper API is running on port 4040"}

@app.get("/fetch")
def fetch_all():
    """Fetch all blog posts from sources.json."""
    results = run_all_scrapers()
    if isinstance(results, dict) and "error" in results:
        raise HTTPException(status_code=500, detail=results["error"])
    return {"posts": results}

@app.get("/rss")
def get_rss(url: str = Query(..., description="The RSS feed URL")):
    """Fetch posts from a specific RSS feed URL."""
    posts = fetch_rss(url)
    if not posts:
        return {"message": "No posts found or failed to fetch", "posts": []}
    return {"posts": posts}

@app.get("/scrape")
def get_scrape(url: str = Query(..., description="The page URL to scrape"), 
               selector: str = Query(..., description="CSS selector for post links")):
    """Scrape posts from a specific page URL using Playwright."""
    posts = scrape_page(url, selector)
    if not posts:
        return {"message": "No posts found or failed to scrape", "posts": []}
    return {"posts": posts}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=4040)
