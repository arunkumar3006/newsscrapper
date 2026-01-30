"""
Enhanced Entity Extractor with Better Accuracy
Focuses on company/agency names with improved filtering
"""

import re
from collections import Counter, defaultdict
from typing import List, Dict

def extract_top_agencies_enhanced(articles: List[Dict], query: str, min_mentions: int = 2) -> List[Dict]:
    """
    Enhanced entity extraction with better accuracy for company/agency names
    
    Improvements:
    - Better filtering of non-entities
    - Multi-word company name detection
    - Industry-specific patterns
    - Noise reduction
    """
    
    # Expanded exclude list with common non-entity words
    exclude_words = {
        # Articles, conjunctions, prepositions
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
        'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that',
        'these', 'those', 'what', 'which', 'who', 'when', 'where', 'why', 
        'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other',
        'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than',
        'too', 'very', 'just', 'now', 'new', 'first', 'last', 'long', 'great',
        
        # Geographic/temporal
        'india', 'indian', 'us', 'uk', 'china', 'chinese', 'american', 'british',
        'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
        'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august',
        'september', 'october', 'november', 'december', 'today', 'yesterday', 'tomorrow',
        
        # Common news words
        'says', 'said', 'news', 'report', 'reports', 'reported', 'according',
        'sources', 'source', 'official', 'officials', 'statement', 'announced',
        'announces', 'announcement', 'press', 'release', 'update', 'updates',
        
        # Generic terms
        'company', 'companies', 'corporation', 'inc', 'ltd', 'llc', 'group',
        'industry', 'industries', 'market', 'markets', 'sector', 'sectors',
        'business', 'businesses', 'firm', 'firms', 'agency', 'agencies'
    }
    
    # Company suffixes to help identify companies
    company_suffixes = {
        'inc', 'corp', 'corporation', 'ltd', 'limited', 'llc', 'plc',
        'group', 'holdings', 'industries', 'technologies', 'tech',
        'systems', 'solutions', 'services', 'motors', 'energy',
        'pharmaceuticals', 'pharma', 'labs', 'laboratories'
    }
    
    entity_counts = Counter()
    entity_contexts = defaultdict(list)  # Store contexts for validation
    
    for article in articles:
        headline = article.get('title', '') + ' ' + article.get('description', '')
        
        # Pattern 1: Standard capitalized entities (1-4 words)
        pattern1 = r'\b[A-Z][A-Za-z]{1,}(?:\s+[A-Z][A-Za-z]{1,}){0,3}\b'
        matches1 = re.findall(pattern1, headline)
        
        # Pattern 2: Acronyms (2-6 capital letters)
        pattern2 = r'\b[A-Z]{2,6}\b'
        matches2 = re.findall(pattern2, headline)
        
        all_matches = matches1 + matches2
        
        for match in all_matches:
            match = match.strip()
            match_lower = match.lower()
            
            # Skip if too short or in exclude list
            if len(match) <= 2 or match_lower in exclude_words:
                continue
            
            # Skip if it's just a single common word
            words = match.split()
            if len(words) == 1 and match_lower in exclude_words:
                continue
            
            # Skip if all words are in exclude list
            if all(word.lower() in exclude_words for word in words):
                continue
            
            # Boost score if it has company suffix
            is_likely_company = any(suffix in match_lower for suffix in company_suffixes)
            
            # Boost score if it's an acronym (likely a company)
            is_acronym = len(match) <= 6 and match.isupper()
            
            # Add to counter
            weight = 1
            if is_likely_company:
                weight = 1.5
            if is_acronym and len(match) >= 3:
                weight = 1.3
                
            entity_counts[match] += weight
            entity_contexts[match].append(headline[:100])  # Store context
    
    # Filter entities with minimum mentions
    filtered_entities = {k: v for k, v in entity_counts.items() if v >= min_mentions}
    
    # Sort by count
    sorted_entities = sorted(filtered_entities.items(), key=lambda x: x[1], reverse=True)
    
    # Get top 10
    top_entities = sorted_entities[:10]
    
    results = []
    total_articles = len(articles)
    
    for rank, (name, count) in enumerate(top_entities, 1):
        # Determine entity type with better heuristics
        name_lower = name.lower()
        
        if any(word in name_lower for word in ['ministry', 'department', 'government', 'bureau', 'commission', 'authority']):
            entity_type = "government_agency"
        elif any(word in name_lower for word in ['university', 'institute', 'college', 'school', 'research', 'lab']):
            entity_type = "research_org"
        elif len(name) <= 6 and name.isupper():
            entity_type = "company (acronym)"
        else:
            entity_type = "company"
        
        # Calculate confidence based on frequency and context diversity
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
