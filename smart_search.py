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
            "context_keywords": ["motor", "auto", "vehicle", "drive", "electric", "suv", "sedan", "recall", "launch", "model"]
        },
        "bike": {
            "search_query": "motorcycle industry news OR two-wheeler market OR bike launch",
            "context_keywords": ["motorcycle", "scooter", "ride", "two-wheeler", "engine", "cc", "rider", "launch"]
        },
        "ev": {
            "search_query": "electric vehicle industry OR EV battery news OR tesla byd",
            "context_keywords": ["battery", "range", "charging", "lithium", "electric", "motor", "green"]
        },
        
        # TECH
        "tech": {
            "search_query": "technology sector news OR software companies OR AI startups",
            "context_keywords": ["software", "app", "digital", "ai", "cyber", "data", "cloud", "platform", "user"]
        },
        "ai": {
            "search_query": "artificial intelligence companies OR generative AI news",
            "context_keywords": ["model", "gpt", "bot", "algorithm", "data", "learning", "compute"]
        },
        
        # FINANCE
        "finance": {
            "search_query": "banking sector news OR fintech trends OR stock market",
            "context_keywords": ["bank", "stock", "market", "trade", "invest", "economy", "crypto", "loan"]
        },
        "crypto": {
            "search_query": "cryptocurrency market OR bitcoin news OR blockchain",
            "context_keywords": ["coin", "token", "blockchain", "wallet", "exchange", "btc", "eth"]
        },

        # HEALTH
        "pharma": {
            "search_query": "pharmaceutical industry news OR drug approval OR biotech",
            "context_keywords": ["drug", "medicine", "fda", "trial", "vaccine", "treatment", "clinical", "health"]
        },
        
        # ENERGY
        "energy": {
            "search_query": "energy sector news OR renewable energy projects OR oil gas",
            "context_keywords": ["power", "solar", "wind", "oil", "gas", "grid", "capacity", "green"]
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
            "optimized_query": f"{core_term} industry news OR {core_term} market leaders",
            "context_keywords": [core_term, "market", "sector", "business"],
            "sector_identified": "GENERAL"
        }

    # 3. Default (No expansion)
    return {
        "original": user_query,
        "optimized_query": user_query,
        "context_keywords": [],
        "sector_identified": "NONE"
    }
