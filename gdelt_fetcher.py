"""Multi-Source News Fetcher"""

import requests
import feedparser
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict

def fetch_gdelt_simple(keyword: str, days: int = 7, max_articles: int = 1000) -> List[Dict]:
    """Fetch news from multiple global sources"""
    
    articles = []
    
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
        urls = [
            f"https://news.google.com/rss/search?q={keyword}%20when%3A{days}d&hl=en-US&gl=US&ceid=US:en",
            f"https://news.google.com/rss/search?q={keyword}%20when%3A{days}d&hl=en-GB&gl=GB&ceid=GB:en",
            f"https://news.google.com/rss/search?q={keyword}%20when%3A{days}d&hl=en-IN&gl=IN&ceid=IN:en",
            f"https://news.google.com/rss/search?q={keyword}%20when%3A{days}d&hl=en-AU&gl=AU&ceid=AU:en",
        ]
        
        tasks = [fetch_rss_async(url) for url in urls]
        results = await asyncio.gather(*tasks)
        return results
    
    all_entries = asyncio.run(fetch_all_sources())
    
    seen_titles = set()
    for entries in all_entries:
        if entries:
            for entry in entries:
                title = entry.get('title', '')
                if title and title not in seen_titles:
                    seen_titles.add(title)
                    
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
