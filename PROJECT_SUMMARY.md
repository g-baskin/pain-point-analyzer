# Project Summary: Autonomous Market Research App

## What Was Built

A **fully functional Python application** that autonomously scrapes the internet for customer pain points and complaints, analyzes sentiment, and extracts structured insights for product ideation.

## Tech Stack

- **Backend**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15+ with pgvector
- **Task Queue**: Celery + Redis
- **AI/ML**:
  - Cloudflare AI (sentiment analysis)
  - Claude API (pain point extraction)
- **Scrapers**: PRAW (Reddit), Snscrape (Twitter), Apify (reviews)
- **Deployment**: Docker + Docker Compose

## Project Structure

```
negative-sentim/
├── scrapers/                    # Web scrapers
│   ├── reddit_scraper.py       # Reddit posts/comments
│   ├── twitter_scraper.py      # Twitter complaints
│   └── apify_scraper.py        # Amazon/Google reviews
│
├── processors/                  # AI processors
│   ├── sentiment_filter.py     # Cloudflare AI sentiment
│   └── pain_point_extractor.py # Claude extraction
│
├── database/                    # Database layer
│   ├── models.py               # SQLAlchemy models
│   └── connection.py           # DB connection
│
├── tasks/                       # Background jobs
│   └── scheduler.py            # Celery tasks
│
├── main.py                      # FastAPI application
├── docker-compose.yml           # All services
├── requirements.txt             # Dependencies
├── README.md                    # Full documentation
├── API_KEYS_SETUP.md           # API key guide
└── QUICKSTART.md               # 10-minute setup
```

## Key Features

✅ **Autonomous Scraping**
- Reddit: Posts/comments from any subreddit
- Twitter: Tweets by keywords
- Reviews: Amazon, Google Maps, Yelp (via Apify)

✅ **AI Processing**
- Sentiment analysis (filters negative only)
- Structured pain point extraction
- Automatic categorization
- Opportunity scoring

✅ **API Endpoints**
- Scraping: `/scrape/reddit`, `/scrape/twitter`
- Processing: `/process/sentiment`, `/extract/pain-points`
- Querying: `/pain-points`, `/stats`

✅ **Scheduled Jobs**
- Daily Reddit scraping (2 AM UTC)
- Hourly sentiment processing
- Hourly pain point extraction

✅ **Database Schema**
- `raw_data`: All scraped content
- `pain_points`: Extracted insights
- `search_queries`: Monitoring queries
- `scrape_jobs`: Audit logs

## What You Need to Do Next

### 1. Get API Keys (Required)

**Essential (15 minutes):**
- Reddit API (free) - [Instructions](./API_KEYS_SETUP.md#1-reddit-api-free-)
- Cloudflare AI (free tier) - [Instructions](./API_KEYS_SETUP.md#2-cloudflare-ai-free-tier-)
- Claude API (paid ~$10/month) - [Instructions](./API_KEYS_SETUP.md#3-anthropic-claude-api-paid-)

**Optional:**
- Apify (free tier) - For product reviews
- OpenAI (paid) - For semantic search

### 2. Configure `.env` File

Edit `/Users/dellcbyerllc/Documents/agent-girl/negative-sentim/.env`:

```bash
# Add your actual API keys here
REDDIT_CLIENT_ID=your_actual_client_id
REDDIT_CLIENT_SECRET=your_actual_secret
CLOUDFLARE_ACCOUNT_ID=your_actual_account_id
CLOUDFLARE_API_TOKEN=your_actual_token
ANTHROPIC_API_KEY=your_actual_key
```

### 3. Start the Application

**Option A: Docker (Recommended)**
```bash
cd /Users/dellcbyerllc/Documents/agent-girl/negative-sentim
docker-compose up -d
```

**Option B: Local Development**
```bash
cd /Users/dellcbyerllc/Documents/agent-girl/negative-sentim
source venv/bin/activate
pip install -r requirements.txt
docker-compose up db redis -d
alembic upgrade head
uvicorn main:app --reload
```

### 4. Test the System

```bash
# Test scraping Reddit
curl -X POST "http://localhost:8000/scrape/reddit" \
  -H "Content-Type: application/json" \
  -d '{"source": "reddit", "subreddit": "saas", "keywords": ["frustrated"], "limit": 10}'

# Process sentiment
curl -X POST "http://localhost:8000/process/sentiment?limit=10"

# Extract pain points
curl -X POST "http://localhost:8000/extract/pain-points?limit=5"

# View results
curl "http://localhost:8000/pain-points?limit=10"
```

## Files Created

| File | Purpose |
|------|---------|
| `main.py` | FastAPI application with all endpoints |
| `database/models.py` | SQLAlchemy database models |
| `scrapers/*.py` | Reddit, Twitter, Apify scrapers |
| `processors/*.py` | Sentiment filter, pain point extractor |
| `tasks/scheduler.py` | Celery background jobs |
| `docker-compose.yml` | All services (DB, Redis, API, workers) |
| `requirements.txt` | All Python dependencies |
| `README.md` | Complete documentation |
| `API_KEYS_SETUP.md` | Step-by-step API key guide |
| `QUICKSTART.md` | 10-minute setup guide |
| `.env.example` | Template for API keys |
| `.gitignore` | Git ignore rules |

## Cost Estimates

**Free Tier (Getting Started):**
- Reddit API: Free ✅
- Cloudflare AI: 10k requests/day free ✅
- Apify: 5 actors/month free ✅
- Claude API: ~$10/month (only paid service)
- **Total: $10/month**

**Production Scale:**
- Hosting (Railway/Render): $7-25/month
- Database: $7-15/month
- Claude API: $10-50/month
- Apify (if needed): $49/month
- **Total: $30-165/month**

## Next Steps & Customization

1. **Add more subreddits**: Edit `tasks/scheduler.py`
2. **Change keywords**: Modify search terms in scheduler
3. **Adjust schedule**: Update Celery beat schedule
4. **Build dashboard**: Create React frontend
5. **Add email alerts**: Notify on high-opportunity pain points
6. **Deploy to production**: Use Railway.app or Render.com

## Documentation

- 📘 [README.md](./README.md) - Complete guide
- 🔑 [API_KEYS_SETUP.md](./API_KEYS_SETUP.md) - Get your API keys
- ⚡ [QUICKSTART.md](./QUICKSTART.md) - Get running in 10 min
- 📖 [Original Blueprint](../problem-finder/AUTONOMOUS_MARKET_RESEARCH_APP.md)

## Testing

```bash
# Run API tests
pytest

# Check Celery workers
celery -A tasks.scheduler inspect active

# View logs
docker-compose logs -f
```

## Deployment Options

1. **Railway.app** (Recommended)
   - One-click deploy
   - Free tier available
   - $5/month for production

2. **Render.com**
   - Free tier for testing
   - $7/month for production

3. **Self-hosted**
   - DigitalOcean: $6/month droplet
   - AWS EC2: ~$8/month

## Support

Issues? Questions?
- Check [README.md](./README.md) troubleshooting section
- Review [API_KEYS_SETUP.md](./API_KEYS_SETUP.md) for key issues
- Test each component individually

---

**Status**: ✅ Project fully initialized and ready to run
**Next Step**: Get API keys and update `.env` file
**Estimated Setup Time**: 15-30 minutes

Built with ❤️ by Agent Girl + Greg
