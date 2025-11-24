# Automation Setup Guide

This guide shows you how to set up automated daily scraping and add new subreddits to monitor.

## Option 1: Using Celery (Recommended for Production)

### Step 1: Start Redis (if not already running)
```bash
docker-compose up redis -d
```

### Step 2: Start Celery Worker
Open a new terminal window:
```bash
cd /Users/dellcbyerllc/Documents/agent-girl/negative-sentim
source venv/bin/activate
celery -A tasks.scheduler worker --loglevel=info
```

### Step 3: Start Celery Beat (Scheduler)
Open another terminal window:
```bash
cd /Users/dellcbyerllc/Documents/agent-girl/negative-sentim
source venv/bin/activate
celery -A tasks.scheduler beat --loglevel=info
```

### Current Schedule:
- **Daily Reddit Scrape**: 2 AM UTC
- **Sentiment Processing**: Every hour
- **Pain Point Extraction**: Every hour at :30

### Customize the Schedule:

Edit `tasks/scheduler.py` and modify the `app.conf.beat_schedule`:

```python
app.conf.beat_schedule = {
    'daily-reddit-scrape': {
        'task': 'tasks.scheduler.daily_reddit_scrape',
        'schedule': crontab(hour=2, minute=0),  # Change time here
    },
    # Add more schedules...
}
```

**Crontab Examples:**
- Every hour: `crontab(minute=0)`
- Every day at 3 PM: `crontab(hour=15, minute=0)`
- Every Monday at 9 AM: `crontab(day_of_week=1, hour=9, minute=0)`
- Every 6 hours: `crontab(minute=0, hour='*/6')`

---

## Option 2: Using Cron (macOS/Linux)

### Step 1: Create a scraping script

Create `scripts/auto_scrape.sh`:
```bash
#!/bin/bash
cd /Users/dellcbyerllc/Documents/agent-girl/negative-sentim
source venv/bin/activate

# Scrape multiple subreddits
python3 << 'EOF'
import requests

API_BASE = 'http://localhost:8000'
subreddits = ['saas', 'entrepreneur', 'smallbusiness']
keywords = ['frustrated', 'hate', 'terrible', 'wish there was']

for sub in subreddits:
    try:
        response = requests.post(f'{API_BASE}/scrape/reddit', json={
            'source': 'reddit',
            'subreddit': sub,
            'keywords': keywords,
            'limit': 20
        })
        print(f"✅ Scraped {sub}: {response.json()}")
    except Exception as e:
        print(f"❌ Error scraping {sub}: {e}")

# Extract pain points
try:
    response = requests.post(f'{API_BASE}/extract/pain-points?limit=50')
    print(f"🧠 Extracted: {response.json()}")
except Exception as e:
    print(f"❌ Error extracting: {e}")
EOF
```

Make it executable:
```bash
chmod +x scripts/auto_scrape.sh
```

### Step 2: Add to crontab

Open crontab:
```bash
crontab -e
```

Add this line (runs daily at 2 AM):
```
0 2 * * * /Users/dellcbyerllc/Documents/agent-girl/negative-sentim/scripts/auto_scrape.sh >> /Users/dellcbyerllc/Documents/agent-girl/negative-sentim/logs/scrape.log 2>&1
```

**Cron Schedule Examples:**
- Every day at 2 AM: `0 2 * * *`
- Every 6 hours: `0 */6 * * *`
- Every Monday at 9 AM: `0 9 * * 1`
- Twice a day (9 AM & 9 PM): `0 9,21 * * *`

---

## Adding New Subreddits

### Method 1: Edit the Scheduler

Edit `tasks/scheduler.py`:

```python
@app.task
def daily_reddit_scrape():
    """Run daily Reddit scraping."""
    from scrapers.reddit_scraper import RedditScraper
    from database import SessionLocal, RawData

    db = SessionLocal()
    scraper = RedditScraper()

    # ADD YOUR SUBREDDITS HERE
    subreddits = [
        'saas',
        'entrepreneur',
        'smallbusiness',
        'startups',          # NEW
        'marketing',         # NEW
        'freelance'          # NEW
    ]

    # ADD/CHANGE KEYWORDS HERE
    keywords = [
        'frustrated',
        'hate',
        'terrible',
        'wish there was',
        'need a better',    # NEW
        'looking for'       # NEW
    ]

    # Rest of the function...
```

### Method 2: Use the API Directly

Scrape any subreddit on-demand:

```bash
curl -X POST http://localhost:8000/scrape/reddit \
  -H "Content-Type: application/json" \
  -d '{
    "subreddit": "YOUR_SUBREDDIT_HERE",
    "keywords": ["frustrated", "hate"],
    "limit": 20
  }'
```

### Method 3: Use the Dashboard

1. Open http://localhost:3000 (or wherever dashboard is served)
2. Click **"+ Scrape Reddit"** button
3. Enter subreddit name and keywords
4. Click **"Start Scraping"**

---

## Discovering New Subreddits

### Popular Subreddits by Industry:

**SaaS & Startups:**
- r/saas - SaaS discussions
- r/startups - Startup community
- r/entrepreneur - Entrepreneurs
- r/SideProject - Side projects
- r/roastmystartup - Startup feedback

**Business & Marketing:**
- r/smallbusiness - Small business owners
- r/marketing - Marketing professionals
- r/DigitalMarketing - Digital marketing
- r/socialmedia - Social media marketing
- r/content_marketing - Content marketing

**Technology:**
- r/webdev - Web development
- r/programming - Programming
- r/technology - General tech
- r/selfhosted - Self-hosting
- r/homelab - Home lab enthusiasts

**E-commerce:**
- r/ecommerce - E-commerce discussions
- r/shopify - Shopify store owners
- r/FulfillmentByAmazon - Amazon sellers
- r/dropship - Dropshipping

**Freelancing:**
- r/freelance - Freelancers
- r/forhire - Job postings
- r/freelanceWriters - Freelance writers
- r/web_design - Web designers

### How to Find More:

1. **Search Reddit**: https://www.reddit.com/subreddits/search
2. **Related subreddits**: Check sidebar of subreddits you already monitor
3. **Reddit Metrics**: https://redditmetrics.com/
4. **Subreddit Stats**: https://subredditstats.com/

---

## Best Practices

### Keywords to Use:

**Problem Discovery:**
- "frustrated", "hate", "annoying"
- "terrible", "worst", "awful"
- "disappointed", "doesn't work"
- "wish there was", "need a better"
- "looking for", "struggling with"
- "can't find", "is there a"

### Optimal Scraping:

1. **Frequency**: Daily is usually enough
2. **Limit**: 20-50 posts per subreddit
3. **Time Filter**: "week" or "day"
4. **Multiple subreddits**: 5-10 related subs

### Monitoring:

```bash
# Check Celery tasks
celery -A tasks.scheduler inspect active

# View logs
tail -f logs/scrape.log

# Check database
docker-compose exec db psql -U user -d market_research -c "SELECT COUNT(*) FROM pain_points;"
```

---

## Troubleshooting

### Celery not running tasks:
```bash
# Check if Redis is running
docker-compose ps redis

# Restart Celery
pkill -f celery
celery -A tasks.scheduler worker --loglevel=info &
celery -A tasks.scheduler beat --loglevel=info &
```

### API not responding:
```bash
# Check if API is running
curl http://localhost:8000/health

# Restart API
pkill -f uvicorn
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
```

### Database full:
```bash
# Clean old data (keep last 30 days)
docker-compose exec db psql -U user -d market_research -c "
DELETE FROM raw_data WHERE created_at < NOW() - INTERVAL '30 days';
"
```

---

## Next Steps

1. ✅ Start with 3-5 subreddits
2. ✅ Run daily scraping
3. ✅ Monitor for a week
4. ✅ Adjust keywords based on results
5. ✅ Add more subreddits gradually
6. ✅ Review pain points weekly
7. ✅ Identify product opportunities!

**Happy pain point hunting!** 🎯
