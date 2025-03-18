# Import necessary libraries for web requests, parsing, text processing, and AI
import requests
from bs4 import BeautifulSoup
from collections import Counter
import re
import time
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import os
import subprocess
import sys
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from gtts import gTTS

# Function to install Python packages if they’re missing
def install(package):
    """Install a package using pip dynamically"""
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Try to import BeautifulSoup; install it if not found
try:
    from bs4 import BeautifulSoup
except ModuleNotFoundError:
    install("beautifulsoup4==4.12.3")
    from bs4 import BeautifulSoup

# Try to import gTTS; install it if not found
try:
    from gtts import gTTS
except ModuleNotFoundError:
    install("gTTS")
    from gtts import gTTS

# Try to import google.generativeai; install it if not found
try:
    import google.generativeai as genai
    from google.generativeai.types import GenerationConfig
except ModuleNotFoundError:
    install("google-generativeai")
    import google.generativeai as genai
    from google.generativeai.types import GenerationConfig

# Download VADER lexicon for sentiment analysis quietly (no output)
nltk.download('vader_lexicon', quiet=True)
sid = SentimentIntensityAnalyzer()  # Initialize VADER sentiment analyzer

# Get API keys from environment variables
GEMINI_API_KEY = "GEMINI_API_KEY") #Replace with actual gemini api key
GOOGLE_API_KEY = ("GOOGLE_API_KEY") #Replace with actual Google api key
SEARCH_ENGINE_ID = ("SEARCH_ENGINE_ID") #Replace with actual Google search engine ID

def fetch_google_search_urls(company_name: str, num_results: int = 50):
    """Fetch URLs using Google Custom Search JSON API, targeting non-JS sites"""
    # Check if API credentials are set
    if not GOOGLE_API_KEY or not SEARCH_ENGINE_ID:
        print("Google API Key or Search Engine ID not set.")
        return []
    
    query = f"{company_name} news"  # Search query
    url = "https://www.googleapis.com/customsearch/v1"  # Google API endpoint
    params = {  # Parameters for the API request
        "key": GOOGLE_API_KEY,
        "cx": SEARCH_ENGINE_ID,
        "q": query,
        "num": 10,  # Fetch 10 results per request
        "safe": "active",
    }
    all_urls = []  # List to store all fetched URLs
    try:
        # Fetch URLs in batches (Google API limits to 10 per request)
        for start in [1, 11, 21, 31, 41]:
            params["start"] = start  # Starting index for pagination
            response = requests.get(url, params=params, timeout=10)  # Make the API call
            response.raise_for_status()  # Raise an error if request fails
            data = response.json()  # Parse JSON response
            if "items" not in data:  # No more results
                break
            urls = [item["link"] for item in data.get("items", [])]  # Extract URLs
            all_urls.extend(urls)  # Add to the list
            if len(all_urls) >= num_results:  # Stop if we have enough
                break
            time.sleep(1)  # Pause to avoid rate limiting
        return all_urls[:num_results]  # Return up to num_results URLs
    except requests.RequestException:
        return []  # Return empty list if there’s an error

def scrape_article(url: str):
    """Scrape article with BeautifulSoup (non-JS), including metadata"""
    try:
        # Set a user-agent to mimic a browser
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"}
        response = requests.get(url, headers=headers, timeout=15)  # Fetch the webpage
        response.raise_for_status()  # Check for request errors
        soup = BeautifulSoup(response.text, "html.parser")  # Parse HTML
        
        # Skip if the page has too many scripts (likely JS-heavy)
        script_count = len(soup.find_all("script"))
        if script_count > 30:
            return {"title": url.split("/")[-1].replace("-", " "), "content": "", "url": url}
        
        # Extract title or use URL-derived fallback
        title = soup.title.string if soup.title else url.split("/")[-1].replace("-", " ")
        # Remove unwanted tags (scripts, styles, etc.)
        for tag in soup(["script", "style", "noscript", "meta", "link", "nav", "footer"]):
            tag.decompose()
        
        # Extract text from paragraphs, divs, or articles
        content = " ".join(p.get_text(strip=True) for p in soup.find_all(["p", "div", "article"]) if p.get_text(strip=True))
        if len(content) < 10:  # Skip if content is too short
            return {"title": title, "content": "", "url": url}
        
        return {"title": title, "content": content[:2000], "url": url}  # Return article data
    except Exception:
        # Fallback if scraping fails
        return {"title": url.split("/")[-1].replace("-", " "), "content": "", "url": url}

def summarize_text(text):
    """Summarize by extracting first two meaningful sentences"""
    sentences = [s.strip() for s in text.split(". ") if s.strip()]  # Split into sentences
    return ". ".join(sentences[:2]) + "." if len(sentences) > 1 else text  # Return first two or full text

def analyze_sentiment_vader(text):
    """Perform sentiment analysis on full article content using VADER"""
    scores = sid.polarity_scores(text)  # Get sentiment scores
    compound = scores['compound']  # Use compound score for overall sentiment
    # Classify sentiment based on compound score
    return "Positive" if compound > 0.1 else "Negative" if compound < -0.1 else "Neutral"

def comparative_analysis_vader(articles):
    """Conduct comparative sentiment analysis across articles"""
    # Count sentiment types
    dist = {"Positive": 0, "Negative": 0, "Neutral": 0}
    for a in articles:
        dist[a["Sentiment"]] += 1
    
    coverage_diffs = []  # List for comparing articles
    # Compare pairs of articles
    for i in range(len(articles) - 1):
        art1, art2 = articles[i], articles[i + 1]
        comparison1 = (
            f"Article {i + 1} highlights {art1['Sentiment'].lower()} aspects like "
            f"{', '.join(art1['Topics'])}, while Article {i + 2} discusses "
            f"{art2['Sentiment'].lower()} issues around {', '.join(art2['Topics'])}."
        )
        impact1 = (
            f"The first article {'boosts confidence' if art1['Sentiment'] == 'Positive' else 'raises concerns'} "
            f"about {art1['Topics'][0] if art1['Topics'] else 'performance'}, "
            f"while the second {'boosts confidence' if art2['Sentiment'] == 'Positive' else 'raises concerns'} "
            f"about {art2['Topics'][0] if art2['Topics'] else 'challenges'}."
        )
        coverage_diffs.append({"Comparison": comparison1, "Impact": impact1})

    # Find common and unique topics across articles
    all_topics = [topic for art in articles for topic in art["Topics"]]
    common_topics = list(set([t for t in all_topics if all_topics.count(t) > 1]))
    unique_topics = {f"Unique Topics in Article {i+1}": [t for t in art["Topics"] if t not in common_topics] 
                     for i, art in enumerate(articles)}
    
    # Return structured analysis
    return {
        "Sentiment Distribution": dist,
        "Coverage Differences": coverage_diffs[:2],  # Limit to 2 comparisons
        "Topic Overlap": {"Common Topics": common_topics, **unique_topics}
    }

def extract_topics(text):
    """Extract meaningful topics from article content"""
    # Define common topics and their keywords
    common_topics = {
        "sales": ["sales", "revenue", "market", "growth"],
        "stock market": ["stock", "shares", "price", "investors"],
        "innovation": ["technology", "new", "latest", "innovation"],
        "electric vehicles": ["electric", "vehicle", "ev", "car"],
        "regulations": ["regulation", "regulatory", "law", "policy"],
        "autonomous vehicles": ["self-driving", "autonomous", "fsd", "driverless"],
        "finance": ["finance", "funding", "loans", "credit"],
        "protests": ["protest", "activist", "demonstration"],
        "trade": ["trade", "tariff", "export", "import"]
    }
    # Extract words longer than 3 characters
    words = [w.lower() for w in re.findall(r'\b\w{4,}\b', text)]
    stop_words = {"company", "news", "http", "https", "content"}  # Words to ignore
    word_counts = Counter(w for w in words if w not in stop_words)  # Count word frequency
    topics = []
    # Check for matching keywords in common topics
    for topic, keywords in common_topics.items():
        if any(kw in word_counts for kw in keywords):
            topics.append(topic)
    # Return up to 3 topics, or top 3 words if none match
    return topics[:3] or [word for word, _ in word_counts.most_common(3)]

def generate_dynamic_sentiment(company_name, articles, sentiment_dist):
    """Generate dynamic sentiment analysis using Gemini API"""
    genai.configure(api_key=GEMINI_API_KEY)  # Set up Gemini API with key
    model = genai.GenerativeModel("gemini-1.5-flash")  # Load the Gemini model
    
    # Combine article summaries into a single string
    article_summaries = "\n".join([f"Article {i+1}: {art['Summary']} (Sentiment: {art['Sentiment']}, Topics: {', '.join(art['Topics'])})" 
                                  for i, art in enumerate(articles)])
    # Create prompt for Gemini
    prompt = f"""
    Analyze the sentiment of recent news articles for {company_name} based on the following data:
    Sentiment Distribution: Positive={sentiment_dist['Positive']}, Negative={sentiment_dist['Negative']}, Neutral={sentiment_dist['Neutral']}
    Article Summaries:
    {article_summaries}

    Provide a concise final sentiment analysis in Hindi, incorporating key topics and potential market impacts.
    The output should be 2-3 sentences long and reflect the overall sentiment trend.
    """
    
    # Configure how Gemini generates text
    generation_config = GenerationConfig(
        temperature=0.7,  # Controls randomness (0-1)
        top_p=0.95,  # Limits token choices (cumulative probability)
        top_k=64,  # Limits token choices (top k)
        max_output_tokens=65536,  # Max length of output
    )
    
    # Generate content in a streaming fashion
    response = model.generate_content(
        contents=prompt,
        generation_config=generation_config,
        stream=True
    )
    
    response_text = ""  # Build response from chunks
    for chunk in response:
        response_text += chunk.text
    
    return response_text.strip()  # Return cleaned-up text

def generate_hindi_tts(text):
    """Generate Hindi-only TTS audio using gTTS"""
    tts = gTTS(text, lang="hi")  # Create TTS object in Hindi
    audio_file = "output.mp3"  # Filename for the audio
    tts.save(audio_file)  # Save the audio file
    return audio_file  # Return the filename
