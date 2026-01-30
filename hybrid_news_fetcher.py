"""
Hybrid Multi-Source News Fetcher
Combines NewsAPI.org, GNews, and NewsData.io for maximum coverage
"""

import asyncio
import aiohttp
import requests
from typing import List, Dict
from fuzzywuzzy import fuzz
from collections import Counter
import hashlib

# API Keys - Get free keys from:
# NewsAPI: https://newsapi.org/register
# GNews: https://gnews.io/
# NewsData: https://newsdata.io/register

NEWSAPI_KEY = "YOUR_NEWSAPI_KEY_HERE"  # Free: 100 requests/day, 100 articles each
GNEWS_KEY = "YOUR_GNEWS_KEY_HERE"      # Free: 100 requests/day, 10 articles each
NEWSDATA_KEY = "YOUR_NEWSDATA_KEY_HERE"  # Free: 200 requests/day, 10 articles each


class HybridNewsFetcher:
    """Fetches news from multiple sources and deduplicates"""
    
    def __init__(self):
        self.newsapi_key = NEWSAPI_KEY
        self.gnews_key = GNEWS_KEY
        self.newsdata_key = NEWSDATA_KEY
        
    async def fetch_newsapi(self, query: str, max_articles: int = 100) -> List[Dict]:
        """Fetch from NewsAPI.org - PRIMARY SOURCE"""
        if not self.newsapi_key or self.newsapi_key == "YOUR_NEWSAPI_KEY_HERE":
            print("NewsAPI key not configured, skipping...")
            return []
        
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "apiKey": self.newsapi_key,
            "pageSize": min(max_articles, 100),
            "language": "en",
            "sortBy": "publishedAt"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        articles = []
                        for article in data.get("articles", []):
                            articles.append({
                                "headline": article.get("title", ""),
                                "description": article.get("description", ""),
                                "source": article.get("source", {}).get("name", "Unknown"),
                                "url": article.get("url", ""),
                                "published": article.get("publishedAt", ""),
                                "api_source": "NewsAPI"
                            })
                        print(f"NewsAPI: Fetched {len(articles)} articles")
                        return articles
                    else:
                        print(f"NewsAPI error: {response.status}")
                        return []
        except Exception as e:
            print(f"NewsAPI fetch error: {e}")
            return []
    
    async def fetch_gnews(self, query: str, max_articles: int = 10) -> List[Dict]:
        """Fetch from GNews API - SECONDARY SOURCE"""
        if not self.gnews_key or self.gnews_key == "YOUR_GNEWS_KEY_HERE":
            print("GNews key not configured, skipping...")
            return []
        
        url = "https://gnews.io/api/v4/search"
        params = {
            "q": query,
            "token": self.gnews_key,
            "max": min(max_articles, 10),
            "lang": "en"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        articles = []
                        for article in data.get("articles", []):
                            articles.append({
                                "headline": article.get("title", ""),
                                "description": article.get("description", ""),
                                "source": article.get("source", {}).get("name", "Unknown"),
                                "url": article.get("url", ""),
                                "published": article.get("publishedAt", ""),
                                "api_source": "GNews"
                            })
                        print(f"GNews: Fetched {len(articles)} articles")
                        return articles
                    else:
                        print(f"GNews error: {response.status}")
                        return []
        except Exception as e:
            print(f"GNews fetch error: {e}")
            return []
    
    async def fetch_newsdata(self, query: str, max_articles: int = 10) -> List[Dict]:
        """Fetch from NewsData.io - TERTIARY SOURCE"""
        if not self.newsdata_key or self.newsdata_key == "YOUR_NEWSDATA_KEY_HERE":
            print("NewsData key not configured, skipping...")
            return []
        
        url = "https://newsdata.io/api/1/news"
        params = {
            "q": query,
            "apikey": self.newsdata_key,
            "language": "en"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        articles = []
                        for article in data.get("results", []):
                            articles.append({
                                "headline": article.get("title", ""),
                                "description": article.get("description", ""),
                                "source": article.get("source_id", "Unknown"),
                                "url": article.get("link", ""),
                                "published": article.get("pubDate", ""),
                                "api_source": "NewsData"
                            })
                        print(f"NewsData: Fetched {len(articles)} articles")
                        return articles
                    else:
                        print(f"NewsData error: {response.status}")
                        return []
        except Exception as e:
            print(f"NewsData fetch error: {e}")
            return []
    
    def deduplicate_articles(self, articles: List[Dict], similarity_threshold: int = 85) -> List[Dict]:
        """Remove duplicate articles using fuzzy matching"""
        if not articles:
            return []
        
        unique_articles = []
        seen_hashes = set()
        
        for article in articles:
            headline = article.get("headline", "").lower().strip()
            if not headline:
                continue
            
            # Check against existing articles
            is_duplicate = False
            for unique in unique_articles:
                unique_headline = unique.get("headline", "").lower().strip()
                similarity = fuzz.ratio(headline, unique_headline)
                
                if similarity >= similarity_threshold:
                    is_duplicate = True
                    # Keep the one from the more reliable source
                    if article.get("api_source") == "NewsAPI" and unique.get("api_source") != "NewsAPI":
                        # Replace with NewsAPI version (higher quality)
                        unique_articles.remove(unique)
                        unique_articles.append(article)
                    break
            
            if not is_duplicate:
                unique_articles.append(article)
        
        print(f"Deduplication: {len(articles)} -> {len(unique_articles)} articles (removed {len(articles) - len(unique_articles)} duplicates)")
        return unique_articles
    
    async def fetch_all_sources(self, query: str) -> List[Dict]:
        """Fetch from all sources in parallel and deduplicate"""
        print(f"\n=== Fetching news for: {query} ===")
        
        # Fetch from all sources in parallel
        tasks = [
            self.fetch_newsapi(query, max_articles=100),
            self.fetch_gnews(query, max_articles=10),
            self.fetch_newsdata(query, max_articles=10)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Combine all articles
        all_articles = []
        for article_list in results:
            all_articles.extend(article_list)
        
        print(f"Total articles before deduplication: {len(all_articles)}")
        
        # Deduplicate
        unique_articles = self.deduplicate_articles(all_articles)
        
        # Calculate source diversity for each article
        source_counts = Counter([a.get("api_source") for a in unique_articles])
        for article in unique_articles:
            article["source_diversity"] = len(source_counts)
        
        return unique_articles


def fetch_hybrid_news(query: str, duration: int = 1) -> List[Dict]:
    """Main function to fetch news from hybrid sources"""
    fetcher = HybridNewsFetcher()
    articles = asyncio.run(fetcher.fetch_all_sources(query))
    return articles
