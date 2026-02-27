import json
import feedparser
from playwright.sync_api import sync_playwright
from urllib.parse import urljoin
import sys
import os

def fetch_rss(feed_url):
    """Fetch blog posts from an RSS feed URL, trying common suffixes if needed."""
    urls_to_try = [feed_url]
    
    # Try common RSS suffixes if not already present
    base_url = feed_url.rstrip('/')
    if not (base_url.endswith('/feed') or base_url.endswith('/rss') or base_url.endswith('/xml') or base_url.endswith('/index.xml')):
        urls_to_try.append(f"{base_url}/feed")
        urls_to_try.append(f"{base_url}/rss")
        urls_to_try.append(f"{base_url}/xml")
        urls_to_try.append(f"{base_url}/index.xml")

    for url in urls_to_try:
        try:
            feed = feedparser.parse(url)
            if feed.entries:
                return [{
                    "title": entry.title,
                    "url": entry.link,
                    "source": feed.feed.title if hasattr(feed, 'feed') and hasattr(feed.feed, 'title') else url
                } for entry in feed.entries]
        except Exception as e:
            print(f"Error fetching RSS from {url}: {e}", file=sys.stderr)
            continue
    return []

def scrape_page(page_url, selector):
    """Scrape blog post links using Playwright for dynamic content support."""
    results = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(page_url, wait_until="networkidle")
            
            # Use the provided selector to find post links
            try:
                page.wait_for_selector(selector, timeout=10000)
                elements = page.query_selector_all(selector)
                
                for el in elements:
                    title = el.inner_text().strip()
                    url = el.get_attribute('href')
                    if url:
                        full_url = urljoin(page_url, url)
                        results.append({
                            "title": title or "No Title",
                            "url": full_url,
                            "source": page_url
                        })
            except Exception as e:
                print(f"Error scraping selector {selector} on {page_url}: {e}", file=sys.stderr)
            
            browser.close()
    except Exception as e:
        print(f"Playwright error on {page_url}: {e}", file=sys.stderr)
        
    return results

def run_all_scrapers(config_path='sources.json', source_name=None):
    """Run all scrapers based on the configuration file, or a specific source name."""
    if not os.path.exists(config_path):
        return {"error": "Configuration file not found"}

    try:
        with open(config_path, 'r') as f:
            sources = json.load(f)
    except Exception as e:
        return {"error": f"Failed to load config: {str(e)}"}

    all_posts = []

    # Process RSS
    for source in sources.get('rss', []):
        if source_name and source_name.lower() not in source['name'].lower():
            continue
        posts = fetch_rss(source['url'])
        all_posts.extend(posts)

    # Process Web
    for source in sources.get('web', []):
        if source_name and source_name.lower() not in source['name'].lower():
            continue
        posts = scrape_page(source['url'], source['selector'])
        all_posts.extend(posts)

    return all_posts

def main():
    results = run_all_scrapers()
    if isinstance(results, dict) and "error" in results:
        print(json.dumps(results), file=sys.stderr)
        sys.exit(1)
    
    print(json.dumps(results))

if __name__ == "__main__":
    main()
