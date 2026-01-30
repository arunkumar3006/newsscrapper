"""
Enhanced Entity Extractor with Cross-Source Validation
Improved accuracy through larger sample sizes and multi-source consensus
"""

import re
from collections import Counter, defaultdict
from typing import List, Dict

def extract_entities_enhanced(articles: List[Dict], query: str) -> dict:
    """
    Extract entities with cross-source validation
    
    Improvements over simple extraction:
    1. Larger sample size (100+ articles vs 10-20)
    2. Cross-source validation (entities in multiple sources = higher confidence)
    3. Source diversity scoring
    4. Statistical significance filtering
    """
    
    if not articles:
        return {"error": "No articles found"}
    
    # Common words to exclude
    exclude_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
        'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that',
        'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
        'what', 'which', 'who', 'when', 'where', 'why', 'how', 'all', 'each',
        'every', 'both', 'few', 'more', 'most', 'other', 'some', 'such',
        'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too',
        'very', 'just', 'now', 'new', 'first', 'last', 'long', 'great',
        'little', 'own', 'other', 'old', 'right', 'big', 'high', 'different',
        'small', 'large', 'next', 'early', 'young', 'important', 'public',
        'bad', 'same', 'able', 'india', 'indian', 'us', 'uk', 'china', 'says',
        'according', 'report', 'reports', 'news', 'today', 'yesterday',
        'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'
    }
    
    # Track entities and their sources
    entity_mentions = defaultdict(int)
    entity_sources = defaultdict(set)
    entity_api_sources = defaultdict(set)
    
    for article in articles:
        headline = article.get('headline', '')
        description = article.get('description', '')
        source = article.get('source', 'Unknown')
        api_source = article.get('api_source', 'Unknown')
        
        text = f"{headline} {description}"
        
        # Find capitalized words/phrases (likely company names)
        # Pattern: One or more capitalized words (2+ chars each)
        pattern = r'\b[A-Z][A-Za-z]{1,}(?:\s+[A-Z][A-Za-z]{1,})*\b'
        matches = re.findall(pattern, text)
        
        for match in matches:
            # Filter out single letters and common words
            if len(match) > 2 and match.lower() not in exclude_words:
                entity = match.strip()
                entity_mentions[entity] += 1
                entity_sources[entity].add(source)
                entity_api_sources[entity].add(api_source)
    
    # Calculate scores with cross-source validation
    entity_scores = []
    total_articles = len(articles)
    total_api_sources = len(set(a.get('api_source', 'Unknown') for a in articles))
    
    for entity, count in entity_mentions.items():
        # Skip entities with very low mentions (noise filter)
        if count < 2:
            continue
        
        # Calculate frequency score
        frequency_score = count / total_articles
        
        # Calculate source diversity score
        num_sources = len(entity_sources[entity])
        num_api_sources = len(entity_api_sources[entity])
        source_diversity_score = num_api_sources / max(total_api_sources, 1)
        
        # Combined confidence score
        # 60% weight on frequency, 40% weight on source diversity
        confidence = min(0.95, (frequency_score * 0.6) + (source_diversity_score * 0.4))
        
        # Determine entity type
        entity_type = "company"
        entity_lower = entity.lower()
        if any(word in entity_lower for word in ['ministry', 'department', 'government', 'agency', 'commission', 'bureau']):
            entity_type = "government_agency"
        elif any(word in entity_lower for word in ['university', 'institute', 'research', 'lab', 'college']):
            entity_type = "research_org"
        
        entity_scores.append({
            "entity": entity,
            "count": count,
            "confidence": confidence,
            "num_sources": num_sources,
            "num_api_sources": num_api_sources,
            "entity_type": entity_type
        })
    
    # Sort by confidence score (descending)
    entity_scores.sort(key=lambda x: x['confidence'], reverse=True)
    
    # Get top 10
    top_entities = entity_scores[:10]
    
    # Format output
    result = {
        "keyword": query,
        "sector_interpretation": f"Analysis of {total_articles} news articles from {total_api_sources} sources related to '{query}'",
        "data_quality_metrics": {
            "total_articles_analyzed": total_articles,
            "unique_api_sources": total_api_sources,
            "unique_entities_found": len(entity_mentions),
            "high_confidence_entities": len([e for e in entity_scores if e['confidence'] > 0.7])
        },
        "top_agencies_list": []
    }
    
    for rank, entity_data in enumerate(top_entities, 1):
        result["top_agencies_list"].append({
            "rank": rank,
            "name": entity_data["entity"],
            "entity_type": entity_data["entity_type"],
            "reason": f"Mentioned in {entity_data['count']} articles across {entity_data['num_api_sources']} news sources",
            "confidence_score": round(entity_data["confidence"], 2),
            "mention_count": entity_data["count"],
            "source_diversity": entity_data["num_api_sources"]
        })
    
    return result


def extract_entities_simple(headlines_data: List[Dict], query: str) -> dict:
    """
    Wrapper for backward compatibility
    Calls the enhanced extractor
    """
    return extract_entities_enhanced(headlines_data, query)
