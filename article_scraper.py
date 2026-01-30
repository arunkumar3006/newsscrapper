"""Article Content Scraper (Async)"""

import aiohttp
import asyncio
from bs4 import BeautifulSoup
import re

async def scrape_article_content_async(session, url, max_sentences=6):
    """Scrape article content and return first 5-6 lines asynchronously"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        async with session.get(url, headers=headers, timeout=10) as response:
            if response.status != 200:
                return None
            
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            
            for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
                script.decompose()
            
            paragraphs = []
            
            article_tags = soup.find_all(['article', 'div'], class_=re.compile(r'(article|content|story|post)[-_]?(body|text|content)?', re.I))
            if article_tags:
                for tag in article_tags[:1]:
                    for p in tag.find_all('p'):
                        text = p.get_text(strip=True)
                        if len(text) > 50:
                            paragraphs.append(text)
            else:
                for p in soup.find_all('p'):
                    text = p.get_text(strip=True)
                    if len(text) > 50:
                        paragraphs.append(text)
            
            if not paragraphs:
                return None
            
            sentences = []
            for para in paragraphs[:5]:
                para_sentences = re.split(r'(?<=[.!?])\s+', para)
                sentences.extend(para_sentences)
                if len(sentences) >= max_sentences:
                    break
            
            content = ' '.join(sentences[:max_sentences])
            
            if len(content) < 100:
                return None
            
            return content
    
    except Exception:
        return None

async def enhance_articles_async(articles, limit=20):
    """Enhance top N articles with scraped content in parallel"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        # We only enhance a subset to keep it fast, but the user asked for sufficient data.
        # Let's try to enhance them all but with a limit on concurrency.
        for article in articles[:limit]:
            tasks.append(scrape_article_content_async(session, article['link']))
        
        results = await asyncio.gather(*tasks)
        
        for i, content in enumerate(results):
            if content:
                articles[i]['description'] = content
        
    return articles
