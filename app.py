"""
News Summarization and TTS Application
Description: A Streamlit app that fetches news articles via API, summarizes them, performs sentiment analysis,
conducts comparative analysis, and generates Hindi TTS for any company.
"""

import streamlit as st
import httpx
import json
import asyncio
import os
from utils import (
    summarize_text,
    analyze_sentiment_vader,
    comparative_analysis_vader,
    generate_hindi_tts,
    extract_topics
)

API_URL = os.getenv("API_URL", "http://localhost:8000")  # Default to local, override with env var

async def fetch_articles_async(company_name):
    """Fetch articles asynchronously via FastAPI backend"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{API_URL}/fetch_articles", json={"company": company_name}, timeout=120)
            response.raise_for_status()
            data = response.json()
            if "error" in data or not data.get("articles"):
                st.warning(f"No articles found for {company_name}. Response: {data}")
                return None
            return data
        except httpx.RequestError as e:
            st.error(f"API call failed: {e}")
            return None

def generate_report(company_name):
    """Generate structured report with metadata and Hindi TTS"""
    with st.spinner(f"Fetching and processing news articles for {company_name}..."):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        articles_data = loop.run_until_complete(fetch_articles_async(company_name))
        loop.close()

        if not articles_data or not articles_data.get("articles"):
            return

        articles = articles_data["articles"]
        report = {
            "Company": company_name,
            "Articles": [],
            "Comparative Sentiment Score": {},
            "Final Sentiment Analysis": "",
            "Audio": "[Play Hindi Speech]"
        }

        progress_bar = st.progress(0)
        for i, article in enumerate(articles[:10]):
            summary = summarize_text(article["content"])
            sentiment = analyze_sentiment_vader(article["content"])
            topics = extract_topics(article["content"])
            report["Articles"].append({
                "Title": article["title"],
                "Summary": summary,
                "Sentiment": sentiment,
                "Topics": topics,
                "Metadata": {"URL": article["url"]}
            })
            progress_bar.progress((i + 1) / 10)

        report["Comparative Sentiment Score"] = comparative_analysis_vader(report["Articles"])

        # Hindi-only Final Sentiment Analysis
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

        tts_text = report["Final Sentiment Analysis"]
        audio_file = generate_hindi_tts(tts_text)
        st.json(report)
        st.audio(audio_file, format="audio/mp3")

def main():
    st.set_page_config(page_title="News Summarizer & TTS", page_icon="📰")
    st.title("📰 News Summarizer with Hindi TTS")
    
    company_name = st.text_input("Enter Company Name (e.g., Tesla, Google, Apple):")
    if st.button("Generate Report"):
        if company_name:
            generate_report(company_name)
        else:
            st.warning("Please enter a company name.")

if __name__ == "__main__":
    main()
