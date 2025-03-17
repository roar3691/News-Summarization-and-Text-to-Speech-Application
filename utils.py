"""
Utility functions with VADER sentiment analysis and TTS
"""

import re  # Regular expressions for text processing
from nltk.sentiment.vader import SentimentIntensityAnalyzer  # VADER sentiment analysis tool
import nltk  # Natural Language Toolkit
from collections import Counter  # For counting word frequencies
from gtts import gTTS  # Google Text-to-Speech library
nltk.download('vader_lexicon')  # Download VADER lexicon for sentiment analysis

# Initialize VADER sentiment analyzer
sid = SentimentIntensityAnalyzer()

def summarize_text(text):
    """Summarize by extracting first two meaningful sentences"""
    # Split text into sentences and remove empty ones
    sentences = [s.strip() for s in text.split(". ") if s.strip()]
    # Join first two sentences, append period if more than one sentence
    return ". ".join(sentences[:2]) + "." if len(sentences) > 1 else text

def analyze_sentiment_vader(text):
    """Perform sentiment analysis on full article content using VADER"""
    scores = sid.polarity_scores(text)  # Get sentiment scores
    compound = scores['compound']  # Use compound score for overall sentiment
    # Classify sentiment based on compound score thresholds
    return "Positive" if compound > 0.1 else "Negative" if compound < -0.1 else "Neutral"

def comparative_analysis_vader(articles):
    """Conduct comparative sentiment analysis across articles"""
    # Initialize sentiment distribution dictionary
    dist = {"Positive": 0, "Negative": 0, "Neutral": 0}
    for a in articles:
        dist[a["Sentiment"]] += 1  # Count occurrences of each sentiment
    
    coverage_diffs = []  # List to store comparison details
    # Compare consecutive pairs of articles
    for i in range(len(articles) - 1):
        art1, art2 = articles[i], articles[i + 1]
        # First comparison: Highlight sentiment aspects
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

        # Second comparison: Focus on topics
        comparison2 = (
            f"Article {i + 1} is focused on {', '.join(art1['Topics'])}, "
            f"whereas Article {i + 2} is about {', '.join(art2['Topics'])}."
        )
        impact2 = (
            f"Investors may react {'positively' if art1['Sentiment'] == 'Positive' else 'cautiously'} to "
            f"{art1['Topics'][0] if art1['Topics'] else 'news'} but stay "
            f"{'cautious' if art2['Sentiment'] == 'Negative' else 'optimistic'} due to "
            f"{art2['Topics'][0] if art2['Topics'] else 'developments'}."
        )
        coverage_diffs.append({"Comparison": comparison2, "Impact": impact2})
    
    # Find common and unique topics across articles
    all_topics = [topic for art in articles for topic in art["Topics"]]
    common_topics = list(set([t for t in all_topics if all_topics.count(t) > 1]))
    unique_topics = {f"Unique Topics in Article {i+1}": [t for t in art["Topics"] if t not in common_topics] 
                     for i, art in enumerate(articles)}
    
    # Return structured comparative analysis
    return {
        "Sentiment Distribution": dist,
        "Coverage Differences": coverage_diffs[:2],  # Limit to 2 comparisons for brevity
        "Topic Overlap": {"Common Topics": common_topics, **unique_topics}
    }

def extract_topics(text):
    """Extract meaningful topics from article content"""
    # Define common topics with associated keywords
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
    # Extract words of 4+ characters, convert to lowercase
    words = [w.lower() for w in re.findall(r'\b\w{4,}\b', text)]
    stop_words = {"company", "news", "http", "https", "content"}  # Words to ignore
    word_counts = Counter(w for w in words if w not in stop_words)  # Count word frequencies
    topics = []
    # Match keywords to predefined topics
    for topic, keywords in common_topics.items():
        if any(kw in word_counts for kw in keywords):
            topics.append(topic)
    # Return up to 3 topics, fallback to most common words if none match
    return topics[:3] or [word for word, _ in word_counts.most_common(3)]

def generate_hindi_tts(text):
    """Generate Hindi-only TTS audio using gTTS"""
    tts = gTTS(text, lang="hi")  # Create TTS object with Hindi language
    audio_file = "output.mp3"  # Define output file name
    tts.save(audio_file)  # Save audio to file
    return audio_file  # Return file path for playback
