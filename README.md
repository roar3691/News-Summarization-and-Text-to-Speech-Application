# News Summarization and Text-to-Speech Application

## Overview
This project is a web-based application that extracts news articles for a given company, summarizes them, performs sentiment analysis, conducts comparative analysis, and generates Hindi TTS output. It uses a Streamlit frontend (`app.py`) and a FastAPI backend (`api.py`) for API communication.

## Repository Structure
- `app.py`: Main Streamlit frontend script.
- `api.py`: FastAPI backend for news fetching and scraping.
- `utils.py`: Utility functions for summarization, sentiment analysis, and TTS.
- `requirements.txt`: List of Python dependencies.
- `README.md`: This file with setup and usage instructions.

## Features
- **News Extraction**: Fetches and summarizes 10 non-JS articles using BeautifulSoup.
- **Sentiment Analysis**: Analyzes article content with VADER (Positive, Negative, Neutral).
- **Comparative Analysis**: Compares sentiment and topics across articles.
- **Hindi TTS**: Generates Hindi audio using gTTS.
- **API**: FastAPI backend serves news data to the Streamlit frontend.

## Setup Instructions
### Prerequisites
- Python 3.8+ installed
- Git for cloning the repository
- Google Custom Search API Key & Search Engine ID (free tier: 100 queries/day)

### Installation
1. **Clone the Repository**:
   ```bash
   git clone [https://github.com/roar3691/NewsEcho.git]
   cd NewsEcho
