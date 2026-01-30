# Hybrid Multi-Source News Intelligence System - Setup Guide

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Get FREE API Keys

You need at least ONE of these free API keys (NewsAPI recommended):

#### **NewsAPI.org** (RECOMMENDED - Best Coverage)
1. Go to: https://newsapi.org/register
2. Sign up for free account
3. Get your API key (100 requests/day, 100 articles each = 10,000 articles/day)
4. **This is the most important key to get!**

#### **GNews.io** (Optional - Google News)
1. Go to: https://gnews.io/
2. Sign up for free account
3. Get your API key (100 requests/day, 10 articles each = 1,000 articles/day)

#### **NewsData.io** (Optional - Real-time News)
1. Go to: https://newsdata.io/register
2. Sign up for free account
3. Get your API key (200 requests/day, 10 articles each = 2,000 articles/day)

### Step 3: Run the Application

```bash
streamlit run app2.py
```

### Step 4: Use the Hybrid Mode

1. Open the app in your browser
2. Scroll to **"🚀 Hybrid Multi-Source Analysis (RECOMMENDED)"**
3. Click **"⚙️ Configure API Keys"** expander
4. Enter your API key(s)
5. Click **"🚀 Hybrid Fetch - Show Top Entities"**

---

## 📊 What You Get

### With Hybrid Mode (vs RSS Only):

| Feature | RSS Only | Hybrid Mode | Improvement |
|---------|----------|-------------|-------------|
| Articles per query | 10-20 | 100+ | **10x** |
| Data sources | 1 | 3 | **3x** |
| Entity accuracy | Low | High | **Dramatic** |
| False positives | High | Low | **Major reduction** |
| Confidence scoring | Basic | Advanced | **Cross-validated** |

### Features:

✅ **Multi-Source Fetching**: Combines NewsAPI, GNews, and NewsData.io  
✅ **Automatic Deduplication**: Removes duplicate articles using fuzzy matching  
✅ **Cross-Source Validation**: Entities in multiple sources = higher confidence  
✅ **Enhanced Confidence Scoring**: Weighted by frequency + source diversity  
✅ **Data Quality Metrics**: See exactly how many articles and sources were analyzed  
✅ **Color-Coded Results**: 🟢 High confidence, 🟡 Medium, 🟠 Low  

---

## 🎯 Usage Tips

### For Best Results:

1. **Use NewsAPI.org** - It provides 100 articles per request (vs 10 for others)
2. **Combine Multiple Sources** - More sources = better validation
3. **Use Specific Keywords** - "Tesla Motors" better than "cars"
4. **Check Confidence Scores** - Focus on entities with 70%+ confidence

### Free Tier Limits:

- **NewsAPI**: 100 requests/day = 10,000 articles/day
- **GNews**: 100 requests/day = 1,000 articles/day
- **NewsData**: 200 requests/day = 2,000 articles/day

**Total**: Up to 13,000 articles per day across all sources!

---

## 🔧 Troubleshooting

### "No articles found"
- Check your API keys are correct
- Make sure you've entered at least one key
- Try a different keyword

### "API error 429"
- You've hit the daily rate limit
- Wait 24 hours or use a different API

### "Hybrid fetch failed"
- Check your internet connection
- Verify API keys are valid
- Try with just NewsAPI first

---

## 📈 How It Works

### 1. Multi-Source Fetch
```
NewsAPI.org (100 articles)
    +
GNews.io (10 articles)
    +
NewsData.io (10 articles)
    =
120 total articles
```

### 2. Deduplication
```
120 articles → Fuzzy matching → ~100 unique articles
(Removes syndicated duplicates)
```

### 3. Entity Extraction
```
Extract capitalized entities from headlines
Filter common words
Count frequencies
```

### 4. Cross-Source Validation
```
Confidence = (Frequency × 0.6) + (Source Diversity × 0.4)

Example:
- Entity appears 15 times in 100 articles = 15% frequency
- Entity appears in 3 different sources = 100% diversity
- Confidence = (0.15 × 0.6) + (1.0 × 0.4) = 0.49 = 49%
```

### 5. Ranking
```
Sort by confidence score
Return top 10 entities
```

---

## 🆚 Comparison: RSS vs Hybrid

### RSS Only Mode:
- ✅ No API key required
- ✅ Instant setup
- ❌ Only 10-20 articles
- ❌ Low accuracy
- ❌ High false positives

### Hybrid Mode:
- ✅ 100+ articles
- ✅ High accuracy
- ✅ Cross-validated results
- ✅ Data quality metrics
- ⚠️ Requires free API key(s)

---

## 💡 Pro Tips

1. **Start with NewsAPI** - Get the biggest improvement with one key
2. **Cache Results** - Results are cached in session, no need to re-fetch
3. **Download Data** - Use the download buttons to export results
4. **Monitor Limits** - Keep track of your daily API usage

---

## 🎓 Understanding Confidence Scores

### 🟢 High Confidence (70%+)
- Mentioned frequently (10+ times)
- Appears in multiple sources
- **Highly reliable entity**

### 🟡 Medium Confidence (50-70%)
- Moderate mentions (5-10 times)
- May appear in 1-2 sources
- **Likely relevant**

### 🟠 Low Confidence (<50%)
- Few mentions (<5 times)
- Single source only
- **Possible noise**

---

## 📞 Support

For issues or questions:
1. Check this guide first
2. Verify API keys are correct
3. Try with a simpler keyword
4. Check the terminal for error messages

---

## 🚀 Next Steps

After setup:
1. Try the Hybrid mode with your keyword
2. Compare results with RSS-only mode
3. Experiment with different keywords
4. Export results for further analysis

**Enjoy 10x better entity extraction!** 🎉
