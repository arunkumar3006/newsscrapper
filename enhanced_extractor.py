"""Strict Entity Extractor for Brand/Company Precision"""

import re
from collections import Counter, defaultdict
from typing import List, Dict

def extract_top_agencies_enhanced(articles: List[Dict], query: str, min_mentions: int = 2, context_keywords: List[str] = None) -> List[Dict]:
    """Extract top agencies/companies with STRICT brand filtering"""
    
    # 1. AGGRESSIVE STOPWORD LIST (Industry buzzwords that mimic brands)
    exclude_words = {
        # Common Stopwords
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
        'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that',
        'these', 'those', 'what', 'which', 'who', 'when', 'where', 'why', 
        'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other',
        'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than',
        'too', 'very', 'just', 'now', 'new', 'first', 'last', 'long', 'great',
        
        # Geographic/Time
        'india', 'indian', 'us', 'uk', 'china', 'chinese', 'american', 'british',
        'japan', 'japanese', 'german', 'germany', 'france', 'french',
        'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
        'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august',
        'september', 'october', 'november', 'december', 'today', 'yesterday', 'tomorrow',
        'year', 'years', 'month', 'months', 'week', 'weeks', 'day', 'days',
        
        # Generic News Terms
        'says', 'said', 'news', 'report', 'reports', 'reported', 'according',
        'sources', 'source', 'official', 'officials', 'statement', 'announced',
        'announces', 'announcement', 'press', 'release', 'update', 'updates',
        'breaking', 'exclusive', 'analysis', 'opinion', 'review', 'top', 'best',
        
        # Industry Nouns (The problem words!)
        'car', 'cars', 'vehicle', 'vehicles', 'automobile', 'automotive',
        'electric', 'ev', 'evs', 'battery', 'batteries', 'charging',
        'sedan', 'suv', 'truck', 'trucks', 'bike', 'bikes', 'motorcycle',
        'engine', 'motor', 'motors', 'drive', 'driver', 'driving',
        'launch', 'launches', 'launched', 'model', 'models', 'variant',
        'price', 'prices', 'cost', 'sales', 'sale', 'market', 'markets',
        'industry', 'sector', 'business', 'economy', 'growth', 'profit',
        'revenue', 'share', 'shares', 'stock', 'stocks', 'trade', 'trading',
        'global', 'international', 'national', 'local', 'world',
        'company', 'companies', 'corporation', 'firm', 'firms', 'brand', 'brands',
        'agency', 'agencies', 'group', 'groups', 'ltd', 'inc', 'corp',
        'technology', 'tech', 'software', 'hardware', 'app', 'apps',
        'digital', 'data', 'cloud', 'ai', 'artificial', 'intelligence',
        'smart', 'phone', 'mobile', 'device', 'devices', 'system', 'systems'
    }
    
    # 2. KNOWN BRANDS DATABASE (To guarantee recognition)
    known_brands = {
        # Cars
        'toyota', 'volkswagen', 'vw', 'ford', 'honda', 'nissan', 'hyundai', 'kia',
        'suzuki', 'maruti', 'tata', 'mahindra', 'bmw', 'mercedes', 'benz', 'audi',
        'tesla', 'byd', 'chevrolet', 'gm', 'general motors', 'stellantis', 'jeep',
        'volvo', 'renault', 'porsche', 'ferrari', 'lamborghini', 'fiat', 'jaguar',
        'land rover', 'mg', 'skoda', 'lexus', 'mazda', 'subaru', 'mitsubishi',
        
        # Tech
        'apple', 'google', 'microsoft', 'amazon', 'meta', 'facebook', 'nvidia',
        'intel', 'amd', 'samsung', 'sony', 'lg', 'dell', 'hp', 'lenovo', 'asus',
        'acer', 'cisco', 'oracle', 'ibm', 'salesforce', 'adobe', 'netflix',
        'uber', 'airbnb', 'spotify', 'twitter', 'x', 'linkedin', 'snapchat',
        'openai', 'anthropic', 'midjourney', 'stability', 'infur',
        
        # Bikes
        'honda', 'hero', 'bajaj', 'tvs', 'royal enfield', 'yamaha', 'suzuki',
        'ktm', 'kawasaki', 'harley', 'davidson', 'triumph', 'ducati', 'bmw motorrad',
        'ather', 'ola', 'ola electric', 'revolt', 'ultraviolette',
        
        # Finance
        'jpmorgan', 'chase', 'goldman sachs', 'morgan stanley', 'citi', 'citigroup',
        'bank of america', 'wells fargo', 'hsbc', 'barclays', 'ubs', 'credit suisse',
        'hdfc', 'icici', 'sbi', 'axis', 'kotak', 'paytm', 'phonepe', 'gpay',
        
        # Pharma/Health
        'pfizer', 'moderna', 'astrazeneca', 'johnson & johnson', 'novartis', 'roche',
        'merck', 'gsk', 'sanofi', 'abbvie', 'bayer', 'sun pharma', 'cipla', 'dr reddy',
        'apollo', 'fortis', 'max'
    }
    
    # Suffixes that confirm it's a company
    company_suffixes = {
        'inc', 'corp', 'corporation', 'ltd', 'limited', 'llc', 'plc',
        'group', 'holdings', 'industries', 'technologies', 'motors', 'automotive',
        'labs', 'pharmaceuticals', 'energy', 'systems', 'solution', 'solutions'
    }
    
    entity_counts = Counter()
    entity_contexts = defaultdict(list)
    
    # Pre-process context keywords
    context_keywords = [k.lower() for k in (context_keywords or [])]
    
    for article in articles:
        # Scan Titles primarily (Headlines are most precise)
        text = article.get('title', '')
        # Only use description if title is short
        if len(text) < 50:
            text += ' ' + article.get('description', '')
            
        # Clean text
        text = text.replace("'s", "").replace("’s", "")
        
        # 1. Regex for capitalized phrases (Potential Entities)
        # Matches: "Tesla", "General Motors", "Tata Motors"
        pattern = r'\b[A-Z][A-Za-z0-9&]{1,}(?:\s+[A-Z][A-Za-z0-9&]{1,})*\b'
        matches = re.findall(pattern, text)
        
        for match in matches:
            original_match = match
            match = match.strip()
            match_lower = match.lower()
            
            # --- FILTERING ---
            
            # Skip if common word
            if match_lower in exclude_words:
                continue
            
            # Skip if all parts are common words
            words = match_lower.split()
            if all(w in exclude_words for w in words):
                continue
                
            # Skip if 2 chars or less (unless it's a known brand like "VW", "GM", "HP")
            if len(match) <= 2 and match_lower not in known_brands:
                continue
            
            # --- SCORING ---
            
            score = 0
            
            # Critical Check: Is it a KNOWN brand?
            if match_lower in known_brands:
                score += 5.0 # Huge boost for known brands
            
            # Check: Does it have a company suffix?
            elif any(suffix in match_lower for suffix in company_suffixes):
                score += 3.0 # Strong boost for explicit companies
                
            # Check: Is it an Acronym? (IBM, BMW)
            elif match.isupper() and len(match) >= 3 and len(match) <= 5:
                score += 2.0
            
            # Context Check: Is it near sector keywords?
            # (Only applies if it passed one of the above or is a strong candidate)
            has_context = False
            if context_keywords:
                for ctx in context_keywords:
                    if ctx in text.lower():
                        has_context = True
                        break
            
            if has_context:
                score += 1.0
            
            # Final threshold: Must have some "brand-ness" score
            # Pure capitalized words get score 0 + 1 (context) = 1.
            # Brands get 5 or 3.
            
            # HEURISTIC: If score is low (just a capitalized word), 
            # we only count it if it APPEARS repeatedly across many articles.
            # But for "Top Agencies", we prefer high scores.
            
            if score >= 1.0:
                 entity_counts[original_match] += score
                 entity_contexts[original_match].append(text)

    # Consolidate duplicates (e.g. "Tesla" and "Tesla Inc")
    # Simple fuzzy merge
    final_counts = Counter()
    for name, score in entity_counts.items():
        # Check if a longer version exists
        extracted = False
        for existing in final_counts:
            if name in existing or existing in name:
                # Keep the longer one usually, or the one with higher count
                final_counts[existing] += score
                extracted = True
                break
        if not extracted:
            final_counts[name] = score

    # Filter by mentions
    filtered_entities = {k: v for k, v in final_counts.items() if v >= min_mentions}
    
    # Sort by Score (high confidence brands first)
    sorted_entities = sorted(filtered_entities.items(), key=lambda x: x[1], reverse=True)
    top_entities = sorted_entities[:15]
    
    results = []
    total_score_sum = sum(final_counts.values()) or 1
    
    for rank, (name, score) in enumerate(top_entities, 1):
        name_lower = name.lower()
        
        # Determine Type
        entity_type = "company"
        if any(w in name_lower for w in ['ministry', 'govt', 'government']): entity_type = "government_agency"
        elif any(w in name_lower for w in ['university', 'research']): entity_type = "research_org"
        elif len(name) <= 5 and name.isupper(): entity_type = "company (acronym)"
        
        # Calculate Mock Mentions (reverse engineer from score)
        # Assuming avg score per mention is ~3 for brands
        est_mentions = max(1, int(score / 3))
        
        results.append({
            "rank": rank,
            "name": name,
            "mentions": est_mentions,
            "percentage": round((score / total_score_sum) * 100, 1),
            "confidence": 95 if name_lower in known_brands else 80,
            "entity_type": entity_type,
            "context_diversity": len(set(entity_contexts[name]))
        })
    
    return results
