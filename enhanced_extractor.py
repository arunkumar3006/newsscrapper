"""Enhanced Entity Extractor for News Analysis"""

import re
from collections import Counter, defaultdict
from typing import List, Dict

def extract_top_agencies_enhanced(articles: List[Dict], query: str, min_mentions: int = 2, context_keywords: List[str] = None) -> List[Dict]:
    """Extract top agencies/companies with enhanced accuracy and context awareness"""
    
    # Common words to ignore
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
        'business', 'businesses', 'firm', 'firms', 'agency', 'agencies', 
        'global', 'international', 'national', 'local', 'world', 'top', 'best'
    }
    
    # Suffixes that strongly indicate a company
    company_suffixes = {
        'inc', 'corp', 'corporation', 'ltd', 'limited', 'llc', 'plc',
        'group', 'holdings', 'industries', 'technologies', 'tech',
        'systems', 'solutions', 'services', 'motors', 'energy',
        'pharmaceuticals', 'pharma', 'labs', 'laboratories', 'auto', 'automotive'
    }
    
    entity_counts = Counter()
    entity_contexts = defaultdict(list)
    
    # Normalize context keywords for fuzzy matching
    context_keywords = [k.lower() for k in (context_keywords or [])]
    
    for article in articles:
        # Include description for broader context
        headline = article.get('title', '') + ' ' + article.get('description', '')
        headline_lower = headline.lower()
        
        # Regex for capitalized phrases (Entities)
        pattern1 = r'\b[A-Z][A-Za-z]{1,}(?:\s+[A-Z][A-Za-z]{1,}){0,3}\b'
        matches1 = re.findall(pattern1, headline)
        
        # Regex for Acronyms (e.g. BMW, IBM)
        pattern2 = r'\b[A-Z]{2,6}\b'
        matches2 = re.findall(pattern2, headline)
        
        all_matches = matches1 + matches2
        
        for match in all_matches:
            match = match.strip()
            match_lower = match.lower()
            
            # Filtering noise
            if len(match) <= 2 or match_lower in exclude_words:
                continue
            
            words = match.split()
            if len(words) == 1 and match_lower in exclude_words:
                continue
                
            if all(word.lower() in exclude_words for word in words):
                continue
            
            # SCORING LOGIC
            weight = 1.0
            
            # Boost if context keywords are present nearby or in the same headline
            # This is key for "Accuracy" - if we search for cars, "Toyota" is boosted if "motor" is in text
            if context_keywords:
                for ctx in context_keywords:
                    if ctx in headline_lower:
                        weight += 1.0 # Significant boost for relevant context
                        break
            
            # Boost for explicit company suffixes
            if any(suffix in match_lower for suffix in company_suffixes):
                weight += 0.5
            
            # Boost for acronyms (likely major tickers/companies)
            if len(match) <= 5 and match.isupper() and len(match) >= 3:
                weight += 0.3
                
            entity_counts[match] += weight
            entity_contexts[match].append(headline[:150])
    
    # Filter and Sort
    filtered_entities = {k: v for k, v in entity_counts.items() if v >= min_mentions}
    sorted_entities = sorted(filtered_entities.items(), key=lambda x: x[1], reverse=True)
    top_entities = sorted_entities[:15] # Return slightly more for better visibility
    
    results = []
    total_articles = max(1, len(articles))
    
    for rank, (name, count) in enumerate(top_entities, 1):
        name_lower = name.lower()
        
        # Determine Type
        if any(word in name_lower for word in ['ministry', 'department', 'government', 'bureau', 'commission', 'authority']):
            entity_type = "government_agency"
        elif any(word in name_lower for word in ['university', 'institute', 'college', 'school', 'research', 'lab']):
            entity_type = "research_org"
        elif len(name) <= 5 and name.isupper():
            entity_type = "company (acronym)"
        else:
            entity_type = "company"
        
        # Confidence Calculation
        # Context presence boosts confidence
        has_context = False
        if context_keywords:
            for ctx in context_keywords:
                if any(ctx in text.lower() for text in entity_contexts[name]):
                    has_context = True
                    break
        
        frequency_pct = (count / total_articles) * 100
        context_diversity = len(set(entity_contexts[name]))
        
        # Base confidence
        confidence = (frequency_pct * 0.5) + (context_diversity / total_articles * 100 * 0.3)
        if has_context:
            confidence += 15 # Bonus confidence for matching sector context
            
        results.append({
            "rank": rank,
            "name": name,
            "mentions": int(count), # Round down for display
            "percentage": round(frequency_pct, 1),
            "confidence": min(98, round(confidence, 1)),
            "entity_type": entity_type,
            "context_diversity": context_diversity
        })
    
    return results
