from fastapi import FastAPI, HTTPException, Query
from main import fetch_rss, scrape_page, run_all_scrapers
import uvicorn
import json
import os

app = FastAPI(title="Blog Scraper API", root_path="/blog")

@app.get("/")
def read_root():
    return {"message": "Blog Scraper API is running on port 4040"}

@app.get("/sources")
def get_sources():
    """Return the content of the sources.json file."""
    sources_path = "sources.json"
    if not os.path.exists(sources_path):
        raise HTTPException(status_code=404, detail="sources.json file not found")
    
    try:
        with open(sources_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading sources.json: {str(e)}")

@app.get("/fetch")
def fetch_all(source: str = Query(None, description="The name of the source to fetch from")):
    """Fetch blog posts from sources.json, optionally filtered by source name."""
    results = run_all_scrapers(source_name=source)
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
