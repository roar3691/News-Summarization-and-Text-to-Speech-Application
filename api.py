"""
API endpoints for news fetching and processing with BeautifulSoup (non-JS scraping only)
"""

from fastapi import FastAPI  # Framework for building APIs
import requests  # HTTP client for fetching web content
from bs4 import BeautifulSoup  # Library for parsing HTML (non-JS scraping)
import time  # For adding delays between API requests
import os  # For accessing environment variables

# Initialize FastAPI app
app = FastAPI()

# Load Google Custom Search API credentials from environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")

def fetch_google_search_urls(company_name: str, num_results: int = 50):
    """Fetch URLs using Google Custom Search JSON API, targeting non-JS sites"""
    # Check if API credentials are set
    if not GOOGLE_API_KEY or not SEARCH_ENGINE_ID:
        return {"error": "Google API Key or Search Engine ID not set"}
    
    query = f"{company_name} news"  # Construct search query
    url = "https://www.googleapis.com/customsearch/v1"  # Google Custom Search API endpoint
    # Define request parameters
    params = {
        "key": GOOGLE_API_KEY,
        "cx": SEARCH_ENGINE_ID,
        "q": query,
        "num": 10,  # Max 10 results per request (API limit)
        "safe": "active",  # Enable safe search
    }
    all_urls = []  # List to store fetched URLs
    try:
        # Fetch URLs in batches (10 per request, up to 50 total)
        for start in [1, 11, 21, 31, 41]:
            params["start"] = start  # Set starting index for pagination
            response = requests.get(url, params=params, timeout=10)  # Send GET request
            response.raise_for_status()  # Raise exception for HTTP errors
            data = response.json()  # Parse JSON response
            if "items" not in data:
                print(f"No items in response for start={start}: {data}")
                break
            urls = [item["link"] for item in data.get("items", [])]  # Extract URLs from items
            all_urls.extend(urls)  # Add to total list
            print(f"Fetched {len(urls)} URLs at start={start}, total={len(all_urls)}")
            if len(all_urls) >= num_results:
                break  # Stop if we have enough URLs
            time.sleep(1)  # Delay to avoid hitting API rate limits
        print(f"Total fetched {len(all_urls)} URLs from Google Search")
        return all_urls[:num_results]  # Return up to num_results URLs
    except requests.RequestException as e:
        print(f"Error fetching URLs: {e}")
        return []  # Return empty list on error
    except Exception as e:
        print(f"Unexpected error in fetch_google_search_urls: {e}")
        return []

def scrape_article(url: str):
    """Scrape article with BeautifulSoup (non-JS), including metadata"""
    try:
        # Define headers to mimic a browser request
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"}
        response = requests.get(url, headers=headers, timeout=15)  # Fetch webpage
        response.raise_for_status()  # Raise exception for HTTP errors
        soup = BeautifulSoup(response.text, "html.parser")  # Parse HTML
        
        # Check for excessive scripts (indicative of JS-heavy page)
        script_count = len(soup.find_all("script"))
        if script_count > 30:
            print(f"Skipping {url}: Too many scripts ({script_count})")
            return {"title": url.split("/")[-1].replace("-", " "), "content": "", "url": url}
        
        # Extract title, defaulting to URL-derived if missing
        title = soup.title.string if soup.title else url.split("/")[-1].replace("-", " ")
        # Remove unwanted tags to clean content
        for tag in soup(["script", "style", "noscript", "meta", "link", "nav", "footer"]):
            tag.decompose()
        
        # Extract text content from paragraphs, divs, and articles
        content = " ".join(p.get_text(strip=True) for p in soup.find_all(["p", "div", "article"]) if p.get_text(strip=True))
        if len(content) < 10:
            print(f"Insufficient content at {url}: {len(content)} chars")
            return {"title": title, "content": "", "url": url}
        
        print(f"Successfully scraped {url}: {len(content)} chars")
        # Return article data with title, truncated content, and URL
        return {"title": title, "content": content[:2000], "url": url}
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return {"title": url.split("/")[-1].replace("-", " "), "content": "", "url": url}

@app.post("/fetch_articles")
def fetch_articles(data: dict):
    """Fetch and scrape articles, ensuring 10 non-JS results"""
    company = data.get("company")  # Extract company name from request body
    if not company:
        return {"error": "Company name required"}  # Return error if missing
    
    # Fetch URLs for the company
    urls = fetch_google_search_urls(company, num_results=50)
    if isinstance(urls, dict) and "error" in urls:
        return urls  # Return error if API credentials are missing
    
    articles = []  # List to store scraped articles
    for url in urls:
        article = scrape_article(url)  # Scrape each URL
        if article["content"]:
            articles.append(article)  # Add if content is present
        if len(articles) >= 10:
            print("Found 10 articles, stopping early")
            break  # Stop once 10 articles are found
    
    # Check if enough articles were found
    if len(articles) < 10:
        print(f"Only {len(articles)} non-JS articles found; need 10")
        return {"error": f"Only {len(articles)} non-JS articles found; need 10"}
    
    print(f"Returning {len(articles)} articles")
    return {"articles": articles[:10]}  # Return first 10 articles
