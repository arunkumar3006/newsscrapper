"""Enhanced Entity Extractor for News Analysis"""

import re
from collections import Counter, defaultdict
from typing import List, Dict

def extract_top_agencies_enhanced(articles: List[Dict], query: str, min_mentions: int = 2) -> List[Dict]:
    """Extract top agencies/companies with enhanced accuracy"""
    
    exclude_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
        'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that',
        'these', 'those', 'what', 'which', 'who', 'when', 'where', 'why', 
        'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other',
        'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than',
        'too', 'very', 'just', 'now', 'new', 'first', 'last', 'long', 'great',
        'india', 'indian', 'us', 'uk', 'china', 'chinese', 'american', 'british',
        'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
        'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august',
        'september', 'october', 'november', 'december', 'today', 'yesterday', 'tomorrow',
        'says', 'said', 'news', 'report', 'reports', 'reported', 'according',
        'sources', 'source', 'official', 'officials', 'statement', 'announced',
        'announces', 'announcement', 'press', 'release', 'update', 'updates',
        'company', 'companies', 'corporation', 'inc', 'ltd', 'llc', 'group',
        'industry', 'industries', 'market', 'markets', 'sector', 'sectors',
        'business', 'businesses', 'firm', 'firms', 'agency', 'agencies'
    }
    
    company_suffixes = {
        'inc', 'corp', 'corporation', 'ltd', 'limited', 'llc', 'plc',
        'group', 'holdings', 'industries', 'technologies', 'tech',
        'systems', 'solutions', 'services', 'motors', 'energy',
        'pharmaceuticals', 'pharma', 'labs', 'laboratories'
    }
    
    entity_counts = Counter()
    entity_contexts = defaultdict(list)
    
    for article in articles:
        headline = article.get('title', '') + ' ' + article.get('description', '')
        
        pattern1 = r'\b[A-Z][A-Za-z]{1,}(?:\s+[A-Z][A-Za-z]{1,}){0,3}\b'
        matches1 = re.findall(pattern1, headline)
        
        pattern2 = r'\b[A-Z]{2,6}\b'
        matches2 = re.findall(pattern2, headline)
        
        all_matches = matches1 + matches2
        
        for match in all_matches:
            match = match.strip()
            match_lower = match.lower()
            
            if len(match) <= 2 or match_lower in exclude_words:
                continue
            
            words = match.split()
            if len(words) == 1 and match_lower in exclude_words:
                continue
            
            if all(word.lower() in exclude_words for word in words):
                continue
            
            is_likely_company = any(suffix in match_lower for suffix in company_suffixes)
            is_acronym = len(match) <= 6 and match.isupper()
            
            weight = 1
            if is_likely_company:
                weight = 1.5
            if is_acronym and len(match) >= 3:
                weight = 1.3
                
            entity_counts[match] += weight
            entity_contexts[match].append(headline[:100])
    
    filtered_entities = {k: v for k, v in entity_counts.items() if v >= min_mentions}
    sorted_entities = sorted(filtered_entities.items(), key=lambda x: x[1], reverse=True)
    top_entities = sorted_entities[:10]
    
    results = []
    total_articles = len(articles)
    
    for rank, (name, count) in enumerate(top_entities, 1):
        name_lower = name.lower()
        
        if any(word in name_lower for word in ['ministry', 'department', 'government', 'bureau', 'commission', 'authority']):
            entity_type = "government_agency"
        elif any(word in name_lower for word in ['university', 'institute', 'college', 'school', 'research', 'lab']):
            entity_type = "research_org"
        elif len(name) <= 6 and name.isupper():
            entity_type = "company (acronym)"
        else:
            entity_type = "company"
        
        frequency_pct = (count / total_articles) * 100
        context_diversity = len(set(entity_contexts[name]))
        confidence = min(95, (frequency_pct * 0.7) + (context_diversity / total_articles * 100 * 0.3))
        
        results.append({
            "rank": rank,
            "name": name,
            "mentions": int(count),
            "percentage": round(frequency_pct, 1),
            "confidence": round(confidence, 1),
            "entity_type": entity_type,
            "context_diversity": context_diversity
        })
    
    return results
