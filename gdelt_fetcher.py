"""
GDELT News Fetcher
Fetches news from GDELT Project for massive-scale analysis
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict
import re

def fetch_gdelt_news(keyword: str, days: int = 7, max_articles: int = 1000) -> List[Dict]:
    """
    Fetch news from GDELT using their public CSV exports
    
    GDELT provides real-time global news monitoring with 250,000+ events/day
    This function uses GDELT's GKG (Global Knowledge Graph) export
    
    Args:
        keyword: Search keyword
        days: Number of days to look back
        max_articles: Maximum articles to return
    
    Returns:
        List of article dictionaries with title, description, source, link, published
    """
    
    try:
        articles = []
        
        # GDELT updates every 15 minutes with new CSV files
        # We'll fetch the last few days of data
        end_date = datetime.now()
        
        for day_offset in range(min(days, 3)):  # Limit to 3 days for performance
            target_date = end_date - timedelta(days=day_offset)
            date_str = target_date.strftime('%Y%m%d')
            
            # GDELT GKG CSV URL pattern
            # Format: http://data.gdeltproject.org/gdeltv2/YYYYMMDDHHMMSS.gkg.csv.zip
            # We'll try to fetch the most recent files for each day
            
            for hour in [23, 18, 12, 6, 0]:  # Sample different times of day
                for minute in [45, 30, 15, 0]:
                    timestamp = f"{date_str}{hour:02d}{minute:02d}00"
                    url = f"http://data.gdeltproject.org/gdeltv2/{timestamp}.gkg.csv.zip"
                    
                    try:
                        # Try to fetch the file
                        response = requests.get(url, timeout=10)
                        
                        if response.status_code == 200:
                            # Parse CSV
                            from io import BytesIO
                            import zipfile
                            
                            with zipfile.ZipFile(BytesIO(response.content)) as z:
                                csv_filename = z.namelist()[0]
                                with z.open(csv_filename) as f:
                                    # GDELT GKG has no header, use column indices
                                    df = pd.read_csv(f, sep='\t', header=None, low_memory=False)
                                    
                                    # Key columns:
                                    # 0: GKGRECORDID
                                    # 1: DATE
                                    # 4: SourceCommonName
                                    # 3: DocumentIdentifier (URL)
                                    # 7: V2Themes
                                    
                                    if df.empty:
                                        continue
                                    
                                    # Filter by keyword in themes or URL
                                    keyword_lower = keyword.lower()
                                    
                                    for idx, row in df.iterrows():
                                        themes = str(row.get(7, '')).lower()
                                        url_text = str(row.get(3, '')).lower()
                                        
                                        if keyword_lower in themes or keyword_lower in url_text:
                                            article_url = str(row.get(3, ''))
                                            
                                            # Extract title from URL (last part)
                                            title = article_url.split('/')[-1].replace('-', ' ').replace('_', ' ')
                                            title = re.sub(r'\.html?$', '', title, flags=re.IGNORECASE)
                                            title = title[:200] if title else 'Article'
                                            
                                            articles.append({
                                                'title': title.title(),
                                                'description': themes[:200],  # Use themes as description
                                                'source': str(row.get(4, 'Unknown')),
                                                'link': article_url,
                                                'published': str(row.get(1, ''))
                                            })
                                            
                                            if len(articles) >= max_articles:
                                                return articles
                    
                    except Exception as e:
                        # File might not exist for this timestamp, continue
                        continue
            
            if len(articles) >= max_articles:
                break
        
        return articles[:max_articles]
    
    except Exception as e:
        print(f"GDELT fetch error: {e}")
        return []


def fetch_gdelt_simple(keyword: str, days: int = 7, max_articles: int = 1000) -> List[Dict]:
    """
    Simplified GDELT fetcher using Google News RSS as fallback with larger scraping
    
    Since GDELT's CSV format can be complex, this uses an alternative approach:
    - Scrapes multiple news aggregators
    - Combines results for larger dataset
    """
    
    articles = []
    
    # Fetch from multiple Google News RSS feeds with different parameters
    import feedparser
    import asyncio
    import aiohttp
    
    async def fetch_rss_async(url):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        content = await response.text()
                        feed = feedparser.parse(content)
                        return feed.entries
        except:
            return []
        return []
    
    async def fetch_all_sources():
        # Multiple RSS feeds for better coverage
        urls = [
            f"https://news.google.com/rss/search?q={keyword}%20when%3A{days}d&hl=en-US&gl=US&ceid=US:en",
            f"https://news.google.com/rss/search?q={keyword}%20when%3A{days}d&hl=en-GB&gl=GB&ceid=GB:en",
            f"https://news.google.com/rss/search?q={keyword}%20when%3A{days}d&hl=en-IN&gl=IN&ceid=IN:en",
            f"https://news.google.com/rss/search?q={keyword}%20when%3A{days}d&hl=en-AU&gl=AU&ceid=AU:en",
        ]
        
        tasks = [fetch_rss_async(url) for url in urls]
        results = await asyncio.gather(*tasks)
        return results
    
    # Fetch from all sources
    all_entries = asyncio.run(fetch_all_sources())
    
    # Combine and deduplicate
    seen_titles = set()
    for entries in all_entries:
        if entries:
            for entry in entries:
                title = entry.get('title', '')
                if title and title not in seen_titles:
                    seen_titles.add(title)
                    
                    from bs4 import BeautifulSoup
                    raw_description = entry.get('summary', '')
                    soup = BeautifulSoup(raw_description, 'html.parser')
                    clean_description = soup.get_text(separator=' ', strip=True)
                    
                    articles.append({
                        'title': title,
                        'description': clean_description if clean_description else 'No description',
                        'source': entry.get('source', {}).get('title', 'Unknown'),
                        'link': entry.get('link', ''),
                        'published': entry.get('published', '')
                    })
                    
                    if len(articles) >= max_articles:
                        return articles
    
    return articles
