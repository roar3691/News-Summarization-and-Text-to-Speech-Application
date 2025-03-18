"""
News Summarization and TTS Application
Description: A Streamlit app that fetches news articles, summarizes them, performs sentiment analysis,
conducts comparative analysis, and generates Hindi TTS for any company. Deployable on Hugging Face Spaces.
"""

# Import Streamlit for the web app interface and utility functions from utils.py
import streamlit as st
from utils import fetch_google_search_urls, scrape_article, summarize_text, analyze_sentiment_vader, comparative_analysis_vader, extract_topics, generate_dynamic_sentiment, generate_hindi_tts

# Function to generate a report based on company news
def generate_report(company_name):
    """Generate structured report with metadata and Hindi TTS"""
    # Show a loading spinner while fetching and processing data
    with st.spinner(f"Fetching and processing news articles for {company_name}..."):
        # Fetch up to 50 news article URLs for the given company
        urls = fetch_google_search_urls(company_name, num_results=50)
        articles = []  # List to store processed article data
        
        # Progress bar to show how many URLs are processed
        progress_bar = st.progress(0)
        # Loop through URLs to scrape articles
        for i, url in enumerate(urls):
            article = scrape_article(url)  # Scrape content from the URL
            if article["content"]:  # Check if article has meaningful content
                summary = summarize_text(article["content"])  # Summarize the article
                sentiment = analyze_sentiment_vader(article["content"])  # Analyze sentiment
                topics = extract_topics(article["content"])  # Extract key topics
                # Add article details to the list
                articles.append({
                    "Title": article["title"],
                    "Summary": summary,
                    "Sentiment": sentiment,
                    "Topics": topics,
                    "Metadata": {"URL": article["url"]}
                })
            # Stop after collecting 10 articles with content
            if len(articles) >= 10:
                st.write("Found 10 articles, stopping early")
                break
            # Update progress bar (i + 1 because enumerate starts at 0)
            progress_bar.progress((i + 1) / len(urls))

        # Check if we have enough articles
        if len(articles) < 10:
            st.error(f"Only {len(articles)} non-JS articles found; need 10")
            return  # Exit if not enough articles

        # Perform comparative analysis across articles
        comparative_analysis = comparative_analysis_vader(articles)
        sentiment_dist = comparative_analysis["Sentiment Distribution"]  # Get sentiment distribution
        # Generate a dynamic sentiment summary in Hindi
        final_sentiment = generate_dynamic_sentiment(company_name, articles, sentiment_dist)

        # Create the final report dictionary
        report = {
            "Company": company_name,
            "Articles": articles[:10],  # Limit to 10 articles
            "Comparative Sentiment Score": comparative_analysis,
            "Final Sentiment Analysis": final_sentiment,
            "Audio": "[Play Hindi Speech]"  # Placeholder for audio
        }

        # Generate and save Hindi TTS audio file
        audio_file = generate_hindi_tts(final_sentiment)
        st.json(report)  # Display report as JSON in the app
        st.audio(audio_file, format="audio/mp3")  # Play the audio

# Main function to run the Streamlit app
def main():
    # Set up the page title and icon
    st.set_page_config(page_title="News Summarizer & TTS", page_icon="📰")
    st.title("📰 News Summarizer with Hindi TTS")  # App title
    
    # Text input for the user to enter a company name
    company_name = st.text_input("Enter Company Name (e.g., Tesla, Google, Apple):")
    # Button to trigger report generation
    if st.button("Generate Report"):
        if company_name:  # Check if a company name is provided
            generate_report(company_name)  # Generate the report
        else:
            st.warning("Please enter a company name.")  # Warn if no input

# Run the app if this file is executed directly
if __name__ == "__main__":
    main()
