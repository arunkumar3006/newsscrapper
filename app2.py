import os
import time
import random
import json
import requests
import feedparser
from bs4 import BeautifulSoup
from newspaper import Article, Config
import streamlit as st
from huggingface_hub import InferenceClient
import pandas as pd
from io import BytesIO
from docx import Document
import base64
import streamlit.components.v1 as components
from datetime import date, timedelta
import asyncio
import aiohttp
import re
from collections import Counter, defaultdict

# ============================================================================
# SIMPLE ENTITY EXTRACTOR (NO AI REQUIRED)
# ============================================================================

def extract_top_agencies(articles, query):
    """Extract top agencies/companies from articles using simple NLP"""
    
    exclude_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
        'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that',
        'these', 'those', 'what', 'which', 'who', 'when', 'where', 'why', 
        'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other',
        'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than',
        'too', 'very', 'just', 'now', 'new', 'first', 'last', 'long', 'great',
        'india', 'indian', 'us', 'uk', 'china', 'says', 'news', 'today'
    }
    
    entity_counts = Counter()
    
    for article in articles:
        headline = article.get('title', '') + ' ' + article.get('description', '')
        
        # Find capitalized words (company/agency names)
        pattern = r'\b[A-Z][A-Za-z]{1,}(?:\s+[A-Z][A-Za-z]{1,})*\b'
        matches = re.findall(pattern, headline)
        
        for match in matches:
            if len(match) > 2 and match.lower() not in exclude_words:
                entity_counts[match.strip()] += 1
    
    # Get top 10
    top_entities = entity_counts.most_common(10)
    
    results = []
    for rank, (name, count) in enumerate(top_entities, 1):
        results.append({
            "rank": rank,
            "name": name,
            "mentions": count,
            "percentage": round((count / len(articles)) * 100, 1) if articles else 0
        })
    
    return results


# ============================================================================
# GOOGLE NEWS RSS FETCHER (SIMPLE & RELIABLE)
# ============================================================================

async def fetch_google_news_async(query, duration=1, max_results=100):
    """Fetch maximum news from Google News RSS"""
    
    rss_url = f"https://news.google.com/rss/search?q={requests.utils.quote(query)}%20when%3A{duration}d&hl=en-IN&gl=IN&ceid=IN:en"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(rss_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    content = await response.text()
                    feed = feedparser.parse(content)
                    
                    articles = []
                    for entry in feed.entries[:max_results]:
                        # Clean HTML from description
                        raw_description = entry.get('summary', '')
                        soup = BeautifulSoup(raw_description, 'html.parser')
                        clean_description = soup.get_text(separator=' ', strip=True)
                        clean_description = ' '.join(clean_description.split())  # Remove extra whitespace
                        
                        articles.append({
                            'title': entry.get('title', ''),
                            'description': clean_description if clean_description else 'No description available',
                            'link': entry.get('link', ''),
                            'source': entry.get('source', {}).get('title', 'Unknown'),
                            'published': entry.get('published', '')
                        })
                    
                    return articles
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []

def fetch_google_news(query, duration=1, max_results=100):
    """Sync wrapper for async fetch"""
    return asyncio.run(fetch_google_news_async(query, duration, max_results))


# ============================================================================
# STREAMLIT UI
# ============================================================================

st.set_page_config(page_title="News Intelligence", layout="wide")

# Logo and title
if os.path.exists("Mavericks logo.png"):
    st.image("Mavericks logo.png", width=150)
st.title("📰 News Intelligence System")

# Initialize session state
if "articles" not in st.session_state:
    st.session_state.articles = []
if "agencies" not in st.session_state:
    st.session_state.agencies = []

# Input section
col1, col2 = st.columns(2)
with col1:
    query = st.text_input("🔍 Enter Keyword", "Chemical Industry", help="Enter any topic, company, or sector")
with col2:
    duration = st.number_input("📅 Duration (days)", min_value=1, max_value=30, value=7, help="How many days back to search")

st.markdown("---")

# ============================================================================
# BUTTON 1: GET TOP AGENCIES (TRAINED ON MAXIMUM HEADLINES)
# ============================================================================

st.subheader("🏆 Top Agencies/Companies Analysis")
st.info("📊 Analyzes 100 news headlines to identify top trending agencies and companies")

if st.button("🚀 Get Top Agencies List", type="primary", use_container_width=True):
    with st.spinner(f"🔍 Fetching maximum news headlines for '{query}'..."):
        # Fetch maximum articles
        articles = fetch_google_news(query, duration, max_results=100)
        st.session_state.articles = articles
        
        if not articles:
            st.error("❌ No news found. Try a different keyword or increase duration.")
        else:
            st.success(f"✅ Analyzed {len(articles)} news headlines")
            
            # Extract top agencies
            with st.spinner("🤖 Analyzing entities and ranking agencies..."):
                agencies = extract_top_agencies(articles, query)
                st.session_state.agencies = agencies
            
            if agencies:
                st.markdown("### 📋 Top 10 Agencies/Companies")
                st.markdown(f"*Based on analysis of {len(articles)} news articles about '{query}'*")
                
                # Display as nice cards
                for agency in agencies:
                    rank = agency['rank']
                    name = agency['name']
                    mentions = agency['mentions']
                    pct = agency['percentage']
                    
                    # Color coding
                    if pct >= 10:
                        badge = "🟢"
                        color = "green"
                    elif pct >= 5:
                        badge = "🟡"
                        color = "orange"
                    else:
                        badge = "🟠"
                        color = "gray"
                    
                    st.markdown(f"""
                    <div style='padding: 10px; margin: 5px 0; border-left: 4px solid {color}; background-color: #f0f2f6;'>
                        <strong>{badge} {rank}. {name}</strong><br>
                        <small>📰 Mentioned in {mentions} articles ({pct}% of total)</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Download option
                df = pd.DataFrame(agencies)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Agencies List (CSV)",
                    data=csv,
                    file_name=f"top_agencies_{query.replace(' ', '_')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("⚠️ No agencies found. Try a different keyword.")

# ============================================================================
# BUTTON 2: GET NEWS HEADLINES
# ============================================================================

st.markdown("---")
st.subheader("📰 News Headlines")
st.info("📋 Get list of latest news headlines for your keyword")

if st.button("📡 Get News Headlines", use_container_width=True):
    with st.spinner(f"📡 Fetching news headlines for '{query}'..."):
        articles = fetch_google_news(query, duration, max_results=100)
        st.session_state.articles = articles
        
        if not articles:
            st.error("❌ No news found. Try a different keyword or increase duration.")
        else:
            st.success(f"✅ Found {len(articles)} news articles")
            
            # Display headlines
            st.markdown(f"### 📋 {len(articles)} Headlines about '{query}'")
            
            for i, article in enumerate(articles, 1):
                with st.expander(f"📰 {i}. {article['title']}", expanded=(i <= 3)):
                    st.markdown(f"**Source:** {article['source']}")
                    st.markdown(f"**Published:** {article['published']}")
                    st.markdown(f"**Description:** {article['description']}")
                    st.markdown(f"[🔗 Read full article]({article['link']})")
            
            # Download option
            df = pd.DataFrame(articles)
            
            # Excel download
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='News')
            buffer.seek(0)
            
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="📥 Download Headlines (Excel)",
                    data=buffer,
                    file_name=f"news_headlines_{query.replace(' ', '_')}.xlsx",
                    mime="application/vnd.ms-excel"
                )
            with col2:
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Headlines (CSV)",
                    data=csv,
                    file_name=f"news_headlines_{query.replace(' ', '_')}.csv",
                    mime="text/csv"
                )

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.caption("💡 **How it works:** Button 1 analyzes 100 headlines to find top agencies. Button 2 shows all headlines. Both use Google News RSS (no API key needed).")
