import os
import requests
import feedparser
from bs4 import BeautifulSoup
import streamlit as st
import pandas as pd
from io import BytesIO
from docx import Document
import asyncio
import aiohttp
import re
from collections import Counter, defaultdict

# Import enhanced modules
from enhanced_extractor import extract_top_agencies_enhanced
from gdelt_fetcher import fetch_gdelt_simple

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

st.set_page_config(page_title="News Intelligence", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS to hide GitHub menu and style the app
st.markdown("""
<style>
    /* Hide GitHub menu and share button */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Hide the deploy button and other top-right items */
    .stDeployButton {display: none;}
    button[kind="header"] {display: none;}
    
    /* Style improvements */
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* Theme toggle button styling */
    .theme-toggle {
        position: fixed;
        top: 10px;
        right: 10px;
        z-index: 999;
    }
</style>
""", unsafe_allow_html=True)

# Initialize theme in session state
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

# Theme toggle button in top right
col_theme = st.columns([0.9, 0.1])
with col_theme[1]:
    if st.button("🌓" if st.session_state.theme == 'dark' else "🌞", help="Toggle theme"):
        st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
        st.rerun()

# Apply theme-specific CSS
if st.session_state.theme == 'light':
    st.markdown("""
    <style>
        .stApp {
            background-color: #FFFFFF;
            color: #000000;
        }
        .stMarkdown, .stText {
            color: #000000;
        }
    </style>
    """, unsafe_allow_html=True)

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
# DEEP ANALYSIS MODE
# ============================================================================

st.subheader("🏆 Top Agencies/Companies Analysis")
st.info("📊 Analyzes 1000+ news articles from multiple global sources for maximum accuracy")

if st.button("🚀 Analyze Top Agencies", type="primary", use_container_width=True):
    with st.spinner(f"🔍 Fetching news articles for '{query}'..."):
        # Fetch from multiple sources (multi-source aggregation)
        articles = fetch_gdelt_simple(query, duration, max_articles=1000)
        st.session_state.articles = articles
        
        if not articles:
            st.error("❌ No news found. Try a different keyword or increase duration.")
            st.session_state.agencies = []
        else:
            st.success(f"✅ Fetched {len(articles)} news articles from multiple global sources")
            
            # Extract top agencies with enhanced extractor
            with st.spinner("🤖 Analyzing entities and ranking agencies..."):
                agencies = extract_top_agencies_enhanced(articles, query, min_mentions=5)
                st.session_state.agencies = agencies
                st.session_state.agencies_query = query
                st.session_state.analysis_mode = "Deep Analysis"

# Display agencies if available (outside button block)
if st.session_state.agencies:
    st.markdown("### 📋 Top 10 Agencies/Companies")
    
    # Show analysis mode and article count
    analysis_mode = st.session_state.get('analysis_mode', 'Standard')
    st.markdown(f"**Analysis Mode:** {analysis_mode} | **Articles Analyzed:** {len(st.session_state.articles)} | **Keyword:** '{st.session_state.get('agencies_query', query)}'")
    
    st.markdown("---")
    
    # Display as enhanced cards with confidence and entity type
    for agency in st.session_state.agencies:
        rank = agency['rank']
        name = agency['name']
        mentions = agency['mentions']
        pct = agency['percentage']
        confidence = agency.get('confidence', 0)
        entity_type = agency.get('entity_type', 'company')
        context_diversity = agency.get('context_diversity', 0)
        
        # Color coding based on confidence
        if confidence >= 80:
            badge = "🟢"
            color = "#28a745"
        elif confidence >= 60:
            badge = "🟡"
            color = "#ffc107"
        else:
            badge = "🟠"
            color = "#fd7e14"
        
        # Theme-aware card styling
        if st.session_state.theme == 'light':
            bg_color = "#f8f9fa"
            text_color = "#000000"
            border_color = color
        else:
            bg_color = "#1e1e1e"
            text_color = "#FAFAFA"
            border_color = color
        
        # Entity type emoji
        type_emoji = {
            "company": "🏢",
            "company (acronym)": "🏭",
            "government_agency": "🏛️",
            "research_org": "🔬"
        }.get(entity_type, "🏢")
        
        st.markdown(f"""
        <div style='padding: 15px; margin: 8px 0; border-left: 5px solid {border_color}; background-color: {bg_color}; color: {text_color}; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div>
                    <strong style='font-size: 1.1em;'>{badge} {rank}. {name}</strong> {type_emoji}
                    <br>
                    <small style='color: {text_color}; opacity: 0.8;'>
                        📰 {mentions} mentions ({pct}%) • 
                        🎯 Confidence: {confidence}% • 
                        📊 Diversity: {context_diversity} sources
                    </small>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Download option
    df = pd.DataFrame(st.session_state.agencies)
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download Agencies List (CSV)",
        data=csv,
        file_name=f"top_agencies_{st.session_state.get('agencies_query', query).replace(' ', '_')}.csv",
        mime="text/csv"
    )

# ============================================================================
# BUTTON 2: GET NEWS HEADLINES
# ============================================================================

st.markdown("---")
st.subheader("📰 News Headlines")
st.info("📋 Get list of latest news headlines for your keyword")

if st.button("📡 Get News Headlines", use_container_width=True):
    with st.spinner(f"📡 Fetching news headlines for '{query}'..."):
        articles = fetch_google_news(query, duration, max_results=100)
        
        if not articles:
            st.error("❌ No news found. Try a different keyword or increase duration.")
            st.session_state.headlines = []
        else:
            st.success(f"✅ Found {len(articles)} news articles")
            st.session_state.headlines = articles
            st.session_state.headlines_query = query  # Store query for display

# Display headlines if available (outside button block)
if 'headlines' in st.session_state and st.session_state.headlines:
    st.markdown(f"### 📋 {len(st.session_state.headlines)} Headlines about '{st.session_state.get('headlines_query', query)}'")
    
    for i, article in enumerate(st.session_state.headlines, 1):
        with st.expander(f"📰 {i}. {article['title']}", expanded=(i <= 3)):
            st.markdown(f"**Source:** {article['source']}")
            st.markdown(f"**Published:** {article['published']}")
            st.markdown(f"**Description:** {article['description']}")
            st.markdown(f"[🔗 Read full article]({article['link']})")
    
    # Download option
    df = pd.DataFrame(st.session_state.headlines)
    
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
            file_name=f"news_headlines_{st.session_state.get('headlines_query', query).replace(' ', '_')}.xlsx",
            mime="application/vnd.ms-excel"
        )
    with col2:
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Headlines (CSV)",
            data=csv,
            file_name=f"news_headlines_{st.session_state.get('headlines_query', query).replace(' ', '_')}.csv",
            mime="text/csv"
        )

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.caption("💡 **How it works:** Button 1 analyzes 100 headlines to find top agencies. Button 2 shows all headlines. Both use Google News RSS (no API key needed).")
