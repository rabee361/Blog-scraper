# Blog Scraper & API 🚀

A robust, containerized blog scraper that fetches post links from RSS feeds and dynamic web pages using Playwright. It includes a FastAPI layer for easy integration with services like n8n.

## 🛠 Technologies & Libraries

- **Python 3.12**: Core programming language.
- **FastAPI**: Modern, fast (high-performance) web framework for building APIs.
- **Playwright**: Reliable end-to-end testing for modern web apps, used here for scraping dynamic/JS-heavy pages.
- **feedparser**: Powerful library for parsing RSS/Atom feeds.
- **uv**: Extremely fast Python package installer and resolver.
- **Docker**: For consistent environments and easy deployment.
- **pytest**: Functional and unit testing framework.

## 📁 Project Structure

- `api.py`: The FastAPI application layer. Exposes endpoints for scraping and fetching.
- `main.py`: Core logic for RSS parsing and Playwright scraping. Can be run as a CLI tool.
- `sources.json`: Central configuration file for defining RSS feeds and web scraping targets.
- `Dockerfile`: Multi-stage build for a slim, efficient container.
- `requirements.txt`: List of Python dependencies.
- `tests/`: Directory containing automated tests.
  - `test_scraper.py`: Tests for RSS logic, scraping logic, and config format.

## 🚀 Getting Started

### 1. Installation

**Using a virtual environment:**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
python -m playwright install chromium
```

### 2. Running Locally

**Run as a CLI tool:**
```bash
python main.py
```

**Run as an API:**
```bash
python api.py
```
After running, visit `http://localhost:4040/docs` to see the interactive API documentation.

## 🐳 Docker Setup

### Build the Image
```bash
docker build -t blog-scraper .
```

### Run the Container
```bash
docker run -p 4040:4040 blog-scraper
```
The API will be available at `http://localhost:4040`.

## 🧪 Testing

The project uses `pytest` for validation.

**Run tests:**
```bash
python -m pytest tests/test_scraper.py
```

### What's tested?
- **RSS Parsing**: Verifies successful fetching from real-world feeds (e.g., Package Main).
- **Error Handling**: Ensures the scraper handles invalid URLs and missing selectors gracefully.
- **Configuration**: Validates the structure of `sources.json`.

## ⚙️ Configuration (`sources.json`)

```json
{
  "rss": [
    { "name": "Source Name", "url": "https://example.com/feed" }
  ],
  "web": [
    { 
      "name": "Dynamic Source", 
      "url": "https://example.com/blog", 
      "selector": "a.post-link" 
    }
  ]
}
```
*Note: The script automatically tries adding `/feed` or `/rss` to URLs if they don't directly point to an XML feed.*
