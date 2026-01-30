"""Multi-Cycle Massive News Fetcher (High Yield)"""

import requests
import feedparser
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict
import random
import time

def fetch_gdelt_simple(keyword: str, days: int = 7, max_articles: int = 5000) -> List[Dict]:
    """
    Fetch news from multiple global sources using Multi-Cycle Aggregation.
    OPTIMIZED for maximum article yield.
    """
    
    articles = []
    
    # Pool of User-Agents to avoid throttling
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    ]
    
    async def fetch_rss_async(url):
        try:
            headers = {'User-Agent': random.choice(user_agents)}
            # Increased timeout to 20s for slow responses
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=20)) as response:
                    if response.status == 200:
                        content = await response.text()
                        feed = feedparser.parse(content)
                        return feed.entries
                    else:
                        return []
        except Exception as e:
            return []
        
    async def fetch_massive_sources():
        base_query = requests.utils.quote(keyword)
        
        # INCREASED VARIETY of queries
        queries = [
            f"{base_query}", 
            f'"{keyword}"', # Exact match
            f"{base_query}%20news", 
            f"{base_query}%20market",
            f"{base_query}%20industry",
            f"{base_query}%20report",
            f"{base_query}%20trends",
            f"{base_query}%20growth", 
            f"{base_query}%20shares",
            f"{base_query}%20review",
        ]
        
        # TARGET ALL KEY REGIONS for volume
        regions = [
            "US:en", "GB:en", "IN:en", "AU:en", "CA:en", "SG:en", "IE:en", "NZ:en"
        ]
        
        urls = []
        # Strategy: Pick 5 random regions for each query to spread load but maximize hits
        for q in queries:
            selected_regions = random.sample(regions, min(len(regions), 4))
            for region in selected_regions: 
                hl = "en-" + region.split(':')[0]
                gl = region.split(':')[0]
                ceid = region
                # Use 'search' endpoint which is broader than 'topics'
                url = f"https://news.google.com/rss/search?q={q}%20when%3A{days}d&hl={hl}&gl={gl}&ceid={ceid}"
                urls.append(url)
        
        # Batch requests to avoid overwhelming local network/DNS
        batch_size = 10
        all_results = []
        for i in range(0, len(urls), batch_size):
            batch = urls[i:i + batch_size]
            tasks = [fetch_rss_async(url) for url in batch]
            results = await asyncio.gather(*tasks)
            all_results.extend(results)
            # Tiny sleep to be polite
            await asyncio.sleep(0.1)
            
        return all_results
    
    # Run fetch
    all_entries_lists = asyncio.run(fetch_massive_sources())
    
    seen_titles = set()
    
    for entries in all_entries_lists:
        if entries:
            for entry in entries:
                title = entry.get('title', '')
                # Less strict deduplication: First 20 chars + last 20 chars
                # This keeps "Toyota launched X" and "Toyota launched Y" as separate
                if len(title) > 20:
                    norm_title = (title[:20] + title[-20:]).lower().replace(" ", "")
                else:
                    norm_title = title.lower().replace(" ", "")
                
                if title and norm_title not in seen_titles:
                    seen_titles.add(norm_title) # Add normalized
                    
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
