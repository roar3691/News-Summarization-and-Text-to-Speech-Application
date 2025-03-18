# Import FastAPI for creating an API and utility functions
from fastapi import FastAPI
from utils import fetch_google_search_urls, scrape_article, summarize_text, analyze_sentiment_vader, extract_topics, comparative_analysis_vader, generate_dynamic_sentiment

app = FastAPI(title="News Sentiment API")  # Initialize FastAPI app

# Define an API endpoint to get sentiment analysis
@app.get("/sentiment/{company_name}")
async def get_sentiment(company_name: str):
    """API endpoint to generate sentiment analysis for a company"""
    urls = fetch_google_search_urls(company_name, num_results=50)  # Fetch URLs
    articles = []  # List to store article data
    
    # Process URLs to collect articles
    for url in urls:
        article = scrape_article(url)  # Scrape the article
        if article["content"]:  # If there’s content
            summary = summarize_text(article["content"])  # Summarize it
            sentiment = analyze_sentiment_vader(article["content"])  # Analyze sentiment
            topics = extract_topics(article["content"])  # Extract topics
            # Add article details to the list
            articles.append({
                "Title": article["title"],
                "Summary": summary,
                "Sentiment": sentiment,
                "Topics": topics,
                "Metadata": {"URL": article["url"]}
            })
        if len(articles) >= 10:  # Stop at 10 articles
            break

    # Check if enough articles were found
    if len(articles) < 10:
        return {"error": f"Only {len(articles)} articles found; need 10"}

    # Perform comparative analysis
    comparative_analysis = comparative_analysis_vader(articles)
    sentiment_dist = comparative_analysis["Sentiment Distribution"]  # Get sentiment counts
    # Generate final sentiment in Hindi
    final_sentiment = generate_dynamic_sentiment(company_name, articles, sentiment_dist)

    # Return the structured response
    return {
        "Company": company_name,
        "Articles": articles[:10],
        "Comparative Sentiment Score": comparative_analysis,
        "Final Sentiment Analysis": final_sentiment
    }
