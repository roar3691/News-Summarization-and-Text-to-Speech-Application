"""
News Summarization and TTS Application
Description: A Streamlit app that fetches news articles via API, summarizes them, performs sentiment analysis,
conducts comparative analysis, and generates Hindi TTS for any company.
"""

import streamlit as st  # Web interface library for Python
import httpx  # Asynchronous HTTP client for API calls
import json  # For JSON handling (not directly used here but imported for potential debugging)
import asyncio  # For running asynchronous API requests
import os  # For accessing environment variables
from utils import (  # Import utility functions from utils.py
    summarize_text,  # Summarizes article content
    analyze_sentiment_vader,  # Analyzes sentiment using VADER
    comparative_analysis_vader,  # Compares sentiment across articles
    generate_hindi_tts,  # Generates Hindi TTS audio
    extract_topics  # Extracts key topics from content
)

# API endpoint URL, defaults to localhost:8000 unless overridden by environment variable
API_URL = os.getenv("API_URL", "http://localhost:8000")

async def fetch_articles_async(company_name):
    """Fetch articles asynchronously via FastAPI backend"""
    # Use httpx AsyncClient for non-blocking HTTP requests
    async with httpx.AsyncClient() as client:
        try:
            # Send POST request to FastAPI backend with company name
            response = await client.post(f"{API_URL}/fetch_articles", json={"company": company_name}, timeout=120)
            response.raise_for_status()  # Raise exception for HTTP errors
            data = response.json()  # Parse JSON response
            # Check if response contains an error or no articles
            if "error" in data or not data.get("articles"):
                st.warning(f"No articles found for {company_name}. Response: {data}")
                return None
            return data  # Return successful response data
        except httpx.RequestError as e:
            st.error(f"API call failed: {e}")  # Display error if request fails
            return None

def generate_report(company_name):
    """Generate structured report with metadata and Hindi TTS"""
    # Show a loading spinner while processing
    with st.spinner(f"Fetching and processing news articles for {company_name}..."):
        # Create a new event loop for async operations
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        # Fetch articles from the API
        articles_data = loop.run_until_complete(fetch_articles_async(company_name))
        loop.close()  # Clean up event loop

        # Exit if no articles were fetched
        if not articles_data or not articles_data.get("articles"):
            return

        articles = articles_data["articles"]  # Extract articles list from response
        # Initialize report structure
        report = {
            "Company": company_name,
            "Articles": [],
            "Comparative Sentiment Score": {},
            "Final Sentiment Analysis": "",
            "Audio": "[Play Hindi Speech]"
        }

        # Show progress bar while processing articles
        progress_bar = st.progress(0)
        for i, article in enumerate(articles[:10]):  # Limit to 10 articles
            summary = summarize_text(article["content"])  # Summarize content
            sentiment = analyze_sentiment_vader(article["content"])  # Analyze sentiment
            topics = extract_topics(article["content"])  # Extract topics
            # Add article details to report
            report["Articles"].append({
                "Title": article["title"],
                "Summary": summary,
                "Sentiment": sentiment,
                "Topics": topics,
                "Metadata": {"URL": article["url"]}
            })
            progress_bar.progress((i + 1) / 10)  # Update progress (0 to 1)

        # Perform comparative sentiment analysis
        report["Comparative Sentiment Score"] = comparative_analysis_vader(report["Articles"])

        # Determine final sentiment analysis in Hindi based on distribution
        dist = report["Comparative Sentiment Score"]["Sentiment Distribution"]
        if dist["Positive"] > dist["Negative"] and dist["Positive"] > dist["Neutral"]:
            report["Final Sentiment Analysis"] = (
                f"{company_name} की नवीनतम खबरें ज्यादातर सकारात्मक हैं। "
                "बाजार प्रदर्शन और नवाचार के कारण स्टॉक में वृद्धि की संभावना है।"
            )
        elif dist["Negative"] > dist["Positive"] and dist["Negative"] > dist["Neutral"]:
            report["Final Sentiment Analysis"] = (
                f"{company_name} की नवीनतम खबरें ज्यादातर नकारात्मक हैं। "
                "नियामक या बाजार चुनौतियों के कारण सावधानी बरतें।"
            )
        else:
            report["Final Sentiment Analysis"] = (
                f"{company_name} की नवीनतम खबरें संतुलित हैं। "
                "मिश्रित अवसरों और चुनौतियों के साथ स्थिर प्रदर्शन की उम्मीद है।"
            )

        # Generate Hindi TTS audio from final sentiment analysis
        tts_text = report["Final Sentiment Analysis"]
        audio_file = generate_hindi_tts(tts_text)
        st.json(report)  # Display report as JSON
        st.audio(audio_file, format="audio/mp3")  # Play audio in Streamlit

def main():
    """Main function to set up and run the Streamlit app"""
    # Configure Streamlit page settings
    st.set_page_config(page_title="News Summarizer & TTS", page_icon="📰")
    st.title("📰 News Summarizer with Hindi TTS")  # Set page title
    
    # Text input for company name
    company_name = st.text_input("Enter Company Name (e.g., Tesla, Google, Apple):")
    if st.button("Generate Report"):  # Button to trigger report generation
        if company_name:
            generate_report(company_name)  # Generate and display report
        else:
            st.warning("Please enter a company name.")  # Warn if input is empty

if __name__ == "__main__":
    main()  # Run the app if script is executed directly
