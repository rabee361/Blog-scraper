import json
import base64
import importlib
import feedparser
from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright
from urllib.parse import urljoin
from pagesnap import hook_page, page_snap
import sys
import os
import re

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
                feed_metadata = getattr(feed, "feed", {})
                source_title = url

                if isinstance(feed_metadata, dict):
                    source_title = str(feed_metadata.get("title") or url)

                return [{
                    "title": entry.title,
                    "url": entry.link,
                    "source": source_title
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

def normalize_post(post):
    """Normalize a post payload used for offline HTML downloads."""
    if not isinstance(post, dict):
        raise ValueError("Invalid post payload")

    url = str(post.get("url") or "").strip()
    if not url:
        raise ValueError("Post URL is required")

    title = str(post.get("title") or "offline-page").strip() or "offline-page"
    source = str(post.get("source") or "").strip()

    return {
        "title": title,
        "url": url,
        "source": source,
    }

def slugify_filename(title):
    """Create a filesystem-safe filename slug for downloaded HTML pages."""
    normalized_title = re.sub(r"[^\w\s-]", "", str(title or "").strip().lower())
    slug = re.sub(r"[-\s]+", "-", normalized_title).strip("-")
    return slug or "offline-page"

def encode_post_payload(post):
    """Encode a post object for transport in a download URL."""
    normalized_post = normalize_post(post)
    payload = json.dumps(normalized_post, ensure_ascii=False).encode("utf-8")
    return base64.urlsafe_b64encode(payload).decode("ascii").rstrip("=")

def decode_post_payload(payload):
    """Decode a base64-url encoded post payload."""
    if not payload:
        raise ValueError("Post payload is required")

    padded_payload = payload + "=" * (-len(payload) % 4)

    try:
        decoded_payload = base64.urlsafe_b64decode(padded_payload.encode("ascii"))
        post = json.loads(decoded_payload.decode("utf-8"))
    except Exception as exc:
        raise ValueError("Invalid post payload") from exc

    return normalize_post(post)

async def build_offline_html(post):
    """Capture a fully embedded offline HTML page for a post URL using pagesnap."""
    normalized_post = normalize_post(post)

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            await hook_page(page)
            await page.goto(normalized_post["url"], wait_until="domcontentloaded")
            await page.wait_for_load_state("networkidle")
            embedded_html = await page_snap(page)
        finally:
            await browser.close()

    return {
        "filename": f"{slugify_filename(normalized_post['title'])}.html",
        "content": embedded_html,
        "post": normalized_post,
    }

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
