"""Article Content Scraper (Async) - High Accuracy"""

import aiohttp
import asyncio
from bs4 import BeautifulSoup
import re

async def scrape_article_content_async(session, url, max_sentences=8):
    """Scrape article content and return sufficient lines asynchronously"""
    try:
        # Standard browser headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        
        async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15), allow_redirects=True) as response:
            if response.status != 200:
                return None
            
            html = await response.text()
            soup = BeautifulSoup(html, 'lxml')
            
            # 1. Try Meta-Description first as a high-quality summary fallback
            meta_desc = ""
            og_desc = soup.find("meta", property="og:description")
            if og_desc:
                meta_desc = og_desc.get("content", "")
            
            if len(meta_desc) < 100:
                standard_desc = soup.find("meta", attrs={"name": "description"})
                if standard_desc:
                    meta_desc = standard_desc.get("content", "")

            # 2. Extract Body Content
            for noise in soup(["script", "style", "nav", "header", "footer", "aside", "form", "iframe", "button"]):
                noise.decompose()
            
            # Focus on potential content containers
            paragraphs = []
            
            # Look for long paragraphs first
            potential_containers = soup.find_all(['div', 'article', 'section'])
            best_container = None
            max_p_count = 0
            
            for container in potential_containers:
                p_count = len(container.find_all('p', recursive=False))
                if p_count > max_p_count:
                    max_p_count = p_count
                    best_container = container
            
            target = best_container if best_container else soup.body
            if not target: target = soup
            
            for p in target.find_all('p'):
                text = p.get_text(separator=' ', strip=True)
                if len(text) > 80: # Substantial paragraph
                    paragraphs.append(text)
            
            # 3. Assemble the 5-6 lines (approx 600-800 characters)
            content_text = ""
            if paragraphs:
                content_text = ' '.join(paragraphs[:4]) # Take first 4 paragraphs for sufficient depth
            elif len(meta_desc) > 100:
                content_text = meta_desc
            else:
                return None # Failed to find good content
                
            # Split into sentences and take 6-8 of them to ensure "sufficient data"
            sentences = re.split(r'(?<=[.!?])\s+', content_text)
            sentences = [s.strip() for s in sentences if len(s.strip()) > 15]
            
            if len(sentences) < 3 and len(meta_desc) > 100:
                # If content extraction was poor, use meta description
                return meta_desc if len(meta_desc) > len(content_text) else content_text

            final_summary = ' '.join(sentences[:max_sentences])
            
            # Ensure it's long enough to be "sufficient"
            if len(final_summary) < 250 and len(meta_desc) > len(final_summary):
                return meta_desc
                
            return final_summary if len(final_summary) > 100 else None
    
    except Exception:
        return None

async def enhance_articles_async(articles, limit=15):
    """Enhance top N articles with scraped content in parallel"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for article in articles[:limit]:
            tasks.append(scrape_article_content_async(session, article['link']))
        
        results = await asyncio.gather(*tasks)
        
        for i, content in enumerate(results):
            if content and len(content) > 120:
                # Use the new detailed content
                articles[i]['description'] = content
        
    return articles
