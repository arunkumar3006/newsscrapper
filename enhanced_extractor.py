"""Strict Entity Extractor for Massive Data (High Min Mentions)"""

import re
from collections import Counter, defaultdict
from typing import List, Dict

def extract_top_agencies_enhanced(articles: List[Dict], query: str, min_mentions: int = 4, context_keywords: List[str] = None) -> List[Dict]:
    """Extract top agencies with high minimum mentions threshold for accuracy"""
    
    # 1. Standard Exclude Words
    exclude_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from',
        'is', 'was', 'are', 'were', 'be', 'been', 'has', 'have', 'had', 'do', 'does', 'did',
        'will', 'would', 'shall', 'should', 'may', 'might', 'must', 'can', 'could',
        'this', 'that', 'these', 'those', 'it', 'its', 'he', 'she', 'they', 'them', 'their',
        'what', 'which', 'who', 'whom', 'whose', 'when', 'where', 'why', 'how',
        'india', 'indian', 'us', 'uk', 'china', 'chinese', 'american', 'british', 'japan', 'japanese',
        'german', 'germany', 'france', 'french', 'russia', 'russian', 'european', 'europe',
        'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
        'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august',
        'september', 'october', 'november', 'december', 'today', 'yesterday', 'tomorrow',
        'year', 'years', 'month', 'months', 'week', 'weeks', 'day', 'days',
        'says', 'said', 'news', 'report', 'reports', 'reported', 'according', 'sources', 'source',
        'official', 'officials', 'statement', 'announced', 'announces', 'announcement',
        'press', 'release', 'update', 'updates', 'breaking', 'exclusive', 'analysis', 'opinion',
        'review', 'top', 'best', 'key', 'major', 'new', 'latest', 'live',
        'car', 'cars', 'vehicle', 'vehicles', 'automobile', 'automotive', 'electric', 'ev', 'evs',
        'battery', 'batteries', 'charging', 'sedan', 'suv', 'truck', 'trucks', 'bike', 'bikes',
        'motorcycle', 'engine', 'motor', 'motors', 'drive', 'driver', 'driving', 'launch',
        'launches', 'launched', 'model', 'models', 'variant', 'price', 'prices', 'cost',
        'sales', 'sale', 'market', 'markets', 'industry', 'sector', 'business', 'economy',
        'growth', 'profit', 'revenue', 'share', 'shares', 'stock', 'stocks', 'trade', 'trading',
        'global', 'international', 'national', 'local', 'world', 'company', 'companies',
        'corporation', 'firm', 'firms', 'brand', 'brands', 'agency', 'agencies', 'group', 'groups',
        'ltd', 'inc', 'corp', 'technology', 'tech', 'software', 'hardware', 'app', 'apps',
        'digital', 'data', 'cloud', 'ai', 'artificial', 'intelligence', 'smart', 'phone',
        'mobile', 'device', 'devices', 'system', 'systems'
    }
    
    # 2. Known Brands (Same as before)
    known_brands = {
        'toyota', 'volkswagen', 'vw', 'ford', 'honda', 'nissan', 'hyundai', 'kia',
        'suzuki', 'maruti', 'tata', 'mahindra', 'bmw', 'mercedes', 'benz', 'audi',
        'tesla', 'byd', 'chevrolet', 'gm', 'general motors', 'stellantis', 'jeep',
        'volvo', 'renault', 'porsche', 'ferrari', 'lamborghini', 'fiat', 'jaguar',
        'land rover', 'mg', 'skoda', 'lexus', 'mazda', 'subaru', 'mitsubishi',
        'apple', 'google', 'microsoft', 'amazon', 'meta', 'facebook', 'nvidia',
        'intel', 'amd', 'samsung', 'sony', 'lg', 'dell', 'hp', 'lenovo', 'asus',
        'acer', 'cisco', 'oracle', 'ibm', 'salesforce', 'adobe', 'netflix',
        'uber', 'airbnb', 'spotify', 'twitter', 'x', 'linkedin', 'snapchat',
        'openai', 'anthropic', 'midjourney', 'stability',
        'honda', 'hero', 'bajaj', 'tvs', 'royal enfield', 'yamaha',
        'ktm', 'kawasaki', 'harley', 'davidson', 'triumph', 'ducati',
        'ather', 'ola', 'revolt', 'ultraviolette',
        'jpmorgan', 'chase', 'goldman sachs', 'morgan stanley', 'citi',
        'bank of america', 'wells fargo', 'hsbc', 'barclays', 'ubs',
        'hdfc', 'icici', 'sbi', 'axis', 'kotak', 'paytm', 'phonepe',
        'pfizer', 'moderna', 'astrazeneca', 'johnson & johnson', 'novartis', 'roche',
        'merck', 'gsk', 'sanofi', 'abbvie', 'bayer', 'sun pharma', 'cipla', 'dr reddy'
    }
    
    company_suffixes = {
        'inc', 'corp', 'corporation', 'ltd', 'limited', 'llc', 'plc',
        'group', 'holdings', 'industries', 'technologies', 'motors', 'automotive',
        'labs', 'pharmaceuticals', 'energy', 'systems', 'solution', 'solutions'
    }
    
    entity_counts = Counter()
    entity_contexts = defaultdict(list)
    context_keywords = [k.lower() for k in (context_keywords or [])]
    
    for article in articles:
        text = article.get('title', '')
        if len(text) < 50: text += ' ' + article.get('description', '')
        text = text.replace("'s", "").replace("’s", "")
        
        pattern = r'\b[A-Z][A-Za-z0-9&]{1,}(?:\s+[A-Z][A-Za-z0-9&]{1,})*\b'
        matches = re.findall(pattern, text)
        
        for match in matches:
            original_match = match
            match = match.strip()
            match_lower = match.lower()
            
            if match_lower in exclude_words: continue
            words = match_lower.split()
            if all(w in exclude_words for w in words): continue
            
            # --- Strict Scoring ---
            score = 0
            is_valid = False

            if len(match) > 2:
                # 1. High value match
                if match_lower in known_brands:
                    score += 5.0
                    is_valid = True
                elif any(suffix in match_lower for suffix in company_suffixes):
                    score += 3.0
                    is_valid = True
                elif match.isupper() and 3 <= len(match) <= 5: 
                    score += 2.0
                    is_valid = True
                # 2. Context Match
                elif any(ctx in text.lower() for ctx in context_keywords if ctx):
                    score += 1.0
                    is_valid = True
                
                # Loose match (backup) only if score > 0 effectively (meaning it has SOME validation)
                # But to reach "efficiency", we want frequent mentions.
                # So we count ALL capitalized words, but filter by frequency later.
                score += 1.0 # Base count
            
            if score > 0:
                entity_counts[original_match] += score
                entity_contexts[original_match].append(text)

    # Simple Merge
    final_counts = Counter()
    for name, score in entity_counts.items():
        extracted = False
        for existing in final_counts:
            if name in existing or existing in name:
                final_counts[existing] += score
                extracted = True
                break
        if not extracted:
            final_counts[name] = score

    # FILTER: Use the provided min_mentions (now higher, e.g. 4)
    filtered_entities = {k: v for k, v in final_counts.items() if (v / 5.0) >= 1 or v >= (min_mentions * 2)} 
    # Logic: Score includes weight (5.0 for brands). So score/5 >= 1 means at least 1 mention of a Known Brand.
    # OR total score >= min_mentions * 2 (approx 2 mentions of an unknown entity).

    sorted_entities = sorted(filtered_entities.items(), key=lambda x: x[1], reverse=True)
    top_entities = sorted_entities[:15]
    
    results = []
    total_score = sum(final_counts.values()) or 1
    
    for rank, (name, score) in enumerate(top_entities, 1):
        name_lower = name.lower()
        entity_type = "company"
        if any(w in name_lower for w in ['ministry', 'govt']): entity_type = "government_agency"
        elif any(w in name_lower for w in ['university', 'research']): entity_type = "research_org"
        elif len(name) <= 5 and name.isupper(): entity_type = "company (acronym)"
        
        # Calculate Real Mentions from Weighted Score
        # Approx: If known brand, score per mention is ~6. If unknown, ~2.
        # This is an estimate for display purposes.
        est_mentions = max(1, int(score / 5)) if name_lower in known_brands else max(1, int(score / 2))
        
        results.append({
            "rank": rank,
            "name": name,
            "mentions": est_mentions,
            "percentage": round((score / total_score) * 100, 1),
            "confidence": 95 if name_lower in known_brands else 75,
            "entity_type": entity_type,
            "context_diversity": len(set(entity_contexts[name]))
        })
    
    return results
