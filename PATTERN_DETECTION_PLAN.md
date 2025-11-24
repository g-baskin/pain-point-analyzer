# Pattern Detection & Signal Engine Implementation Plan

## Overview
Transform the pain point analyzer into a "signal engine" that detects patterns across subreddits and provides early warnings about emerging trends before they appear in Google Trends.

## Core Features to Build

### 1. **Pattern Detection System**
**What it does:** Identifies recurring phrases, complaints, and blockers across multiple subreddits

**Technical Implementation:**
- Extract key phrases from all pain points using NLP (spaCy)
- Track phrase frequency across time and subreddits
- Identify phrases that appear in 3+ different subreddits
- Score patterns by: frequency, spread (# subreddits), recency

**Database Tables:**
```sql
-- Store extracted patterns
CREATE TABLE patterns (
    id SERIAL PRIMARY KEY,
    phrase TEXT NOT NULL,
    first_seen TIMESTAMP,
    last_seen TIMESTAMP,
    total_mentions INT,
    subreddit_count INT,  -- How many subreddits mentioned this
    trend_score FLOAT,     -- Calculated score for trending
    category VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Link patterns to pain points
CREATE TABLE pattern_occurrences (
    id SERIAL PRIMARY KEY,
    pattern_id INT REFERENCES patterns(id),
    pain_point_id INT REFERENCES pain_points(id),
    raw_data_id INT REFERENCES raw_data(id),
    subreddit VARCHAR(255),
    mentioned_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 2. **Semantic Clustering**
**What it does:** Groups similar pain points even if they use different words

**Technical Implementation:**
- Use sentence-transformers to create embeddings for each pain point
- Cluster similar pain points using DBSCAN or HDBSCAN
- Identify cluster themes (product issues, pricing complaints, feature requests)
- Track which clusters are growing vs shrinking

**Database Tables:**
```sql
CREATE TABLE pain_point_clusters (
    id SERIAL PRIMARY KEY,
    cluster_name VARCHAR(255),
    description TEXT,
    pain_point_count INT,
    subreddit_spread INT,
    avg_severity VARCHAR(20),
    first_appeared TIMESTAMP,
    last_updated TIMESTAMP,
    growth_rate FLOAT,  -- How fast this cluster is growing
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE cluster_members (
    id SERIAL PRIMARY KEY,
    cluster_id INT REFERENCES pain_point_clusters(id),
    pain_point_id INT REFERENCES pain_points(id),
    similarity_score FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 3. **Trend Timeline**
**What it does:** Shows when patterns emerged and tracks their growth over time

**Features:**
- Timeline visualization of pattern emergence
- "Days since first detection" metric
- Growth velocity (mentions per week)
- Peak detection (when did it explode?)
- Early warning alerts (pattern appearing in 2+ subs within 7 days)

**Database Tables:**
```sql
CREATE TABLE trend_snapshots (
    id SERIAL PRIMARY KEY,
    pattern_id INT REFERENCES patterns(id),
    snapshot_date DATE,
    mention_count INT,
    subreddit_count INT,
    avg_sentiment FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 4. **Cross-Subreddit Analysis**
**What it does:** Identifies which complaints are universal vs niche

**Features:**
- Heatmap: Which subreddits share the same pain points?
- "Spreading" patterns: Started in r/saas, now appearing in r/entrepreneur
- Subreddit-specific vs universal complaints
- Community overlap analysis

**Queries:**
```sql
-- Find patterns appearing in multiple subreddits
SELECT
    p.phrase,
    COUNT(DISTINCT po.subreddit) as subreddit_count,
    ARRAY_AGG(DISTINCT po.subreddit) as subreddits,
    COUNT(*) as total_mentions
FROM patterns p
JOIN pattern_occurrences po ON p.id = po.pattern_id
GROUP BY p.id, p.phrase
HAVING COUNT(DISTINCT po.subreddit) >= 3
ORDER BY subreddit_count DESC, total_mentions DESC;
```

### 5. **Google Trends Integration**
**What it does:** Compare your detection timing vs when it hit mainstream

**Implementation:**
- Use `pytrends` library to query Google Trends
- For each pattern, check when it trended on Google
- Calculate "early detection advantage" (days before Google Trends peak)
- Show "You detected this X days before it went mainstream"

**API Endpoints:**
```python
@app.post("/patterns/compare-trends")
async def compare_with_google_trends(pattern_id: int):
    """Compare pattern detection date with Google Trends"""
    # Get pattern first seen date
    # Query Google Trends for the phrase
    # Calculate time delta
    # Return competitive advantage metrics
```

### 6. **Insights Generator**
**What it does:** AI-powered recommendations for product, copy, and onboarding

**Features:**
- **Product Insights:** "5 pain points detected across 3 subreddits suggest demand for X feature"
- **Copy Insights:** "Most common phrases: 'wish there was', 'frustrated with' - use this language"
- **Onboarding Insights:** "Users consistently struggle with Y - simplify onboarding step 3"
- **Timing Insights:** "This pattern is accelerating - act now before competitors notice"

**Implementation:**
```python
@app.get("/insights/generate")
async def generate_insights(time_period: str = "30d"):
    """Use Claude API to analyze patterns and generate insights"""
    # Get top patterns from last 30 days
    # Get cross-subreddit analysis
    # Get trending clusters
    # Send to Claude with prompt:
    # "Analyze these pain point patterns and provide:
    #  1. Top 3 product opportunities
    #  2. Landing page copy suggestions
    #  3. Onboarding improvement recommendations"
```

### 7. **Pattern Detection Dashboard**
**What it does:** Visualization hub for all pattern insights

**Components:**
- **Trending Patterns Card:** Real-time view of emerging patterns
- **Cross-Subreddit Heatmap:** Which subs share pain points
- **Timeline Chart:** When patterns emerged
- **Early Warning Alerts:** New patterns detected this week
- **Competitive Advantage Metrics:** Days ahead of Google Trends
- **Insight Feed:** AI-generated recommendations

## Implementation Phases

### Phase 1: Foundation (Week 1)
1. Add new database tables
2. Install NLP libraries (`sentence-transformers`, `spacy`, `sklearn`)
3. Create pattern extraction service
4. Build basic API endpoints

### Phase 2: Pattern Detection (Week 2)
1. Implement phrase extraction from pain points
2. Build cross-subreddit tracking
3. Create Pattern Detection Dashboard UI
4. Add pattern frequency analysis

### Phase 3: Advanced Features (Week 3)
1. Implement semantic clustering
2. Add Google Trends integration
3. Build trend timeline visualization
4. Create insight generator with Claude API

### Phase 4: Polish & Optimization (Week 4)
1. Add caching for expensive NLP operations
2. Optimize database queries
3. Create automated pattern detection (run daily)
4. Add email alerts for important patterns

## Open Source Tools to Integrate

### Recommended Libraries:
1. **sentence-transformers** - Best for semantic similarity
2. **spacy** - Industrial-strength NLP
3. **pytrends** - Google Trends API (unofficial but works)
4. **scikit-learn** - Clustering algorithms
5. **plotly** - Interactive visualizations
6. **schedule** - Automated pattern detection runs

### Optional Advanced Tools:
1. **BERTopic** - State-of-the-art topic modeling
2. **UMAP** - Better visualization than t-SNE
3. **KeyBERT** - Keyword extraction
4. **Gensim** - Topic modeling and similarity

## Example Insights Output

```json
{
  "insights": {
    "product_opportunities": [
      {
        "opportunity": "API rate limiting solution",
        "evidence": "Mentioned 47 times across r/webdev, r/SaaS, r/programming",
        "trend": "Growing 23% week-over-week",
        "urgency": "HIGH - Detected 83 days before Google Trends peak",
        "recommendation": "Build API rate limit dashboard feature"
      }
    ],
    "copy_suggestions": [
      {
        "phrase": "frustrated with complicated setup",
        "frequency": 34,
        "usage": "Use in hero copy: 'No complicated setup - start in 60 seconds'"
      }
    ],
    "onboarding_fixes": [
      {
        "issue": "API key confusion",
        "mentions": 28,
        "subreddits": ["r/SaaS", "r/webdev"],
        "fix": "Add video tutorial for API key setup step"
      }
    ]
  }
}
```

## Success Metrics

1. **Pattern Detection Accuracy**: % of patterns that actually become mainstream trends
2. **Early Detection Time**: Average days before Google Trends peak
3. **Cross-Subreddit Coverage**: % of patterns found in 3+ subreddits
4. **Insight Quality**: User feedback on AI-generated recommendations
5. **Competitive Advantage**: Features built before competitors

## Next Steps

1. Review and approve this plan
2. Install required dependencies
3. Create database migrations
4. Start with Phase 1 implementation

---

**Estimated Timeline:** 4 weeks for full implementation
**Estimated Effort:** 80-100 hours
**Key Dependencies:** Claude API, PostgreSQL, sentence-transformers
