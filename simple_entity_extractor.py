"""Simple NLP-based entity extraction without AI"""
import re
from collections import Counter

def extract_entities_simple(headlines_data: list, query: str) -> dict:
    """Extract entities using simple NLP patterns"""
    
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
        'bad', 'same', 'able', 'india', 'indian', 'us', 'uk', 'china', 'says'
    }
    
    entities = []
    
    for item in headlines_data:
        headline = item.get('headline', '')
        description = item.get('description', '')
        text = f"{headline} {description}"
        
        # Find capitalized words/phrases (likely company names)
        pattern = r'\b[A-Z][A-Za-z]*(?:\s+[A-Z][A-Za-z]*)*\b'
        matches = re.findall(pattern, text)
        
        for match in matches:
            # Filter out single letters and common words
            if len(match) > 2 and match.lower() not in exclude_words:
                entities.append(match.strip())
    
    # Count frequencies
    entity_counts = Counter(entities)
    
    # Get top 10
    top_entities = entity_counts.most_common(10)
    
    # Format output
    result = {
        "keyword": query,
        "sector_interpretation": f"Analysis of {len(headlines_data)} news headlines related to '{query}'",
        "top_agencies_list": []
    }
    
    for rank, (name, count) in enumerate(top_entities, 1):
        # Determine entity type
        entity_type = "company"
        if any(word in name.lower() for word in ['ministry', 'department', 'government', 'agency', 'commission']):
            entity_type = "government_agency"
        elif any(word in name.lower() for word in ['university', 'institute', 'research', 'lab']):
            entity_type = "research_org"
        
        confidence = min(0.95, 0.5 + (count / len(headlines_data)) * 0.5)
        
        result["top_agencies_list"].append({
            "rank": rank,
            "name": name,
            "entity_type": entity_type,
            "reason": f"Mentioned in {count} headline(s)",
            "confidence_score": round(confidence, 2)
        })
    
    return result
