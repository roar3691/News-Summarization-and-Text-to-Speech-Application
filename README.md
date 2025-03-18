# News Summarization and TTS Application

A Streamlit app that fetches news articles, summarizes them, performs sentiment analysis, conducts comparative analysis, and generates Hindi TTS for any company. Deployable on Hugging Face Spaces.

## Features
- Fetches news articles using Google Custom Search API.
- Summarizes articles and analyzes sentiment using VADER.
- Generates dynamic sentiment analysis in Hindi with Gemini API.
- Provides Hindi TTS output for accessibility.
- Includes a FastAPI endpoint for programmatic access.

## Prerequisites
- Python 3.8 or higher
- Internet connection (for API calls and package installation)
- Environment variables (set these before running):
  - `GOOGLE_API_KEY`: Your Google Custom Search API key
  - `SEARCH_ENGINE_ID`: Your Google Custom Search Engine ID
  - `GEMINI_API_KEY`: Your Google Gemini API key


### Setup
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/roar3691/NewsEcho.git
   cd NewsEcho
