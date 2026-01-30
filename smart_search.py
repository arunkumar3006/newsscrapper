"""Smart Query Processor & Context Manager"""

def expand_query(user_query: str) -> dict:
    """
    Expands simple user terms into professional news search queries
    and defines context keywords for entity filtering.
    """
    q = user_query.lower().strip()
    
    # Sector Knowledge Base
    # format: "trigger_word": {"search_terms": [...], "context_words": [...]}
    sectors = {
        # AUTOMOTIVE
        "car": {
            "search_query": "automotive industry news OR car manufacturers OR vehicle launch",
            "context_keywords": ["automaker", "manufacturer", "motor", "motors", "group", "holdings", "inc", "corp", "ltd"]
        },
        "bike": {
            "search_query": "motorcycle industry news OR two-wheeler market OR bike launch",
            "context_keywords": ["motorcycle", "motors", "corp", "dashboard", "rider", "two-wheeler"]
        },
        "ev": {
            "search_query": "electric vehicle industry OR EV battery news OR tesla byd",
            "context_keywords": ["automaker", "inc", "corp", "ltd", "manufacturing", "plant", "factory", "gigafactory"]
        },
        
        # TECH
        "tech": {
            "search_query": "technology sector news OR software companies OR AI startups",
            "context_keywords": ["inc", "technologies", "tech", "software", "solutions", "systems", "platform", "cloud"]
        },
        "ai": {
            "search_query": "artificial intelligence companies OR generative AI news",
            "context_keywords": ["ai", "lab", "research", "inc", "technologies", "solutions", "startups"]
        },
        
        # FINANCE
        "finance": {
            "search_query": "banking sector news OR fintech trends OR stock market",
            "context_keywords": ["bank", "group", "inc", "capital", "financial", "securities", "holdings", "fund"]
        },
        "crypto": {
            "search_query": "cryptocurrency market OR bitcoin news OR blockchain",
            "context_keywords": ["exchange", "foundation", "protocol", "dao", "venture", "capital", "labs"]
        },

        # HEALTH
        "pharma": {
            "search_query": "pharmaceutical industry news OR drug approval OR biotech",
            "context_keywords": ["pharma", "pharmaceuticals", "laboratories", "inc", "ltd", "biotech", "healthcare", "hospital"]
        },
        
        # ENERGY
        "energy": {
            "search_query": "energy sector news OR renewable energy projects OR oil gas",
            "context_keywords": ["energy", "power", "limited", "petroleum", "resources", "group", "renewables", "solar"]
        }
    }
    
    # 1. Direct Expansion
    for key, data in sectors.items():
        if key in q:
            return {
                "original": user_query,
                "optimized_query": data["search_query"],
                "context_keywords": data["context_keywords"],
                "sector_identified": key.upper()
            }
            
    # 2. Heuristic Expansion (fallback)
    # If query ends in "brands" or "companies", focus on the industry
    if "brand" in q or "company" in q:
        core_term = q.replace("brands", "").replace("brand", "").replace("companies", "").replace("company", "").strip()
        return {
            "original": user_query,
            "optimized_query": f"top {core_term} companies OR {core_term} industry leaders",
            "context_keywords": ["inc", "corp", "ltd", "group", "holdings", "technologies", "solutions"],
            "sector_identified": "GENERAL"
        }

    # 3. Default (No expansion)
    return {
        "original": user_query,
        "optimized_query": user_query,
        "context_keywords": [],
        "sector_identified": "NONE"
    }
