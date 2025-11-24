# Quick Start Guide

Get the Autonomous Market Research App running in 10 minutes.

## Prerequisites Check

```bash
# Check Python version (need 3.11+)
python3 --version

# Check Docker
docker --version
docker-compose --version
```

## Step 1: Get API Keys (15 minutes)

You need **3 essential API keys** to start:

1. **Reddit API** (free, 5 min) → [Guide](./API_KEYS_SETUP.md#1-reddit-api-free-)
2. **Cloudflare AI** (free, 5 min) → [Guide](./API_KEYS_SETUP.md#2-cloudflare-ai-free-tier-)
3. **Claude API** (paid, 5 min) → [Guide](./API_KEYS_SETUP.md#3-anthropic-claude-api-paid-)

Optional: Apify (for product reviews)

## Step 2: Configure Environment

```bash
# Edit .env file with your API keys
nano .env

# Or use your favorite editor
code .env
```

**Minimum required in .env:**
```bash
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
CLOUDFLARE_ACCOUNT_ID=your_account_id
CLOUDFLARE_API_TOKEN=your_api_token
ANTHROPIC_API_KEY=your_anthropic_key
```

## Step 3: Start with Docker (Recommended)

```bash
# Start all services (database, Redis, API, workers)
docker-compose up -d

# Check logs
docker-compose logs -f

# Access API at http://localhost:8000
```

**That's it!** Skip to [Testing](#step-5-test-it-out) below.

---

## Step 3 (Alternative): Local Development Setup

If you prefer running locally without Docker:

```bash
# 1. Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start PostgreSQL & Redis with Docker
docker-compose up db redis -d

# 4. Run migrations
alembic upgrade head

# 5. Start API (in terminal 1)
uvicorn main:app --reload

# 6. Start Celery worker (in terminal 2)
celery -A tasks.scheduler worker --loglevel=info

# 7. Start Celery beat scheduler (in terminal 3)
celery -A tasks.scheduler beat --loglevel=info
```

## Step 4: Initialize Database

```bash
# Run migrations (creates tables)
docker-compose exec api alembic upgrade head

# Or locally:
alembic upgrade head
```

## Step 5: Test It Out

### Test 1: Scrape Reddit
```bash
curl -X POST "http://localhost:8000/scrape/reddit" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "reddit",
    "subreddit": "saas",
    "keywords": ["frustrated", "hate"],
    "limit": 10
  }'
```

### Test 2: Process Sentiment
```bash
curl -X POST "http://localhost:8000/process/sentiment?limit=10"
```

### Test 3: Extract Pain Points
```bash
curl -X POST "http://localhost:8000/extract/pain-points?limit=5"
```

### Test 4: View Results
```bash
# Get pain points
curl "http://localhost:8000/pain-points?limit=10"

# Get stats
curl "http://localhost:8000/stats"
```

## Step 6: View API Documentation

Open in browser:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Common Issues

### "Connection refused" errors
```bash
# Check services are running
docker-compose ps

# Restart services
docker-compose restart
```

### "Invalid API key" errors
- Double-check API keys in `.env`
- Make sure no spaces or quotes around values
- Restart containers: `docker-compose restart`

### Database migration errors
```bash
# Reset database (⚠️ deletes all data)
docker-compose down -v
docker-compose up -d
alembic upgrade head
```

## Next Steps

1. **Customize scrapers**: Edit `tasks/scheduler.py` to change:
   - Subreddits to monitor
   - Keywords to search
   - Schedule frequency

2. **Add more sources**: Enable Twitter, Apify scrapers

3. **Build a dashboard**: Create a frontend (React + Tailwind)

4. **Set up alerts**: Get notified of high-opportunity pain points

## Monitoring

```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f api
docker-compose logs -f celery_worker

# Check Celery tasks
docker-compose exec celery_worker celery -A tasks.scheduler inspect active
```

## Stopping the App

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (⚠️ deletes database)
docker-compose down -v
```

## Cost Reminder

- **Free tier**: ~$0-10/month (just Claude API)
- **Production**: ~$30-165/month

Set spending limits in:
- Anthropic console: https://console.anthropic.com/settings/limits
- OpenAI: https://platform.openai.com/account/billing/limits

---

**Questions?** Check [README.md](./README.md) or [API_KEYS_SETUP.md](./API_KEYS_SETUP.md)

Happy pain point hunting! 🎯
