import pytest
import json
from main import fetch_rss, scrape_page

def test_fetch_rss_packagemain():
    """Test fetching RSS from packagemain.tech."""
    url = "https://packagemain.tech/feed"
    posts = fetch_rss(url)
    assert isinstance(posts, list)
    if posts:
        assert "title" in posts[0]
        assert "url" in posts[0]
        assert "source" in posts[0]

def test_fetch_rss_invalid():
    """Test fetching RSS from an invalid URL."""
    url = "https://invalid.example.com/rss"
    posts = fetch_rss(url)
    assert posts == []

def test_scrape_page_selector_invalid():
    """Test scraping a page with a selector that doesn't exist."""
    url = "https://example.com"
    selector = ".non-existent-selector"
    # This should return an empty list gracefully after a timeout
    posts = scrape_page(url, selector)
    assert posts == []

def test_sources_json_format():
    """Ensure sources.json exists and has the correct keys."""
    with open('sources.json', 'r') as f:
        sources = json.load(f)
    assert "rss" in sources
    assert "web" in sources
    assert isinstance(sources['rss'], list)
    assert isinstance(sources['web'], list)
