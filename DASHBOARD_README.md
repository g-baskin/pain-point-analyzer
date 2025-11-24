# 📊 Dashboard Quick Start Guide

## Access Your Dashboard

**Dashboard URL**: http://localhost:3000/index.html
**API URL**: http://localhost:8000
**API Docs**: http://localhost:8000/docs

---

## What's Running:

✅ **PostgreSQL** - localhost:5432
✅ **Redis** - localhost:6379
✅ **FastAPI Backend** - http://localhost:8000
✅ **Dashboard** - http://localhost:3000/index.html

---

## Dashboard Features:

### 📈 Real-Time Visualizations
- **Pain Points Overview**: Total count, severity breakdown
- **Category Charts**: Bar chart showing pain points by category
- **Severity Distribution**: Doughnut chart of critical/high/medium/low
- **Opportunity Scores**: Visual indicators of business potential

### 🕷️ One-Click Scraping
1. Click **"+ Scrape Reddit"** button
2. Enter:
   - Subreddit name (e.g., "saas", "entrepreneur")
   - Keywords (e.g., "frustrated, hate, terrible")
   - Limit (how many posts to scrape)
3. Click **"Start Scraping"**
4. Wait for AI to extract pain points
5. Results appear automatically!

### 🔍 Smart Filtering
- Filter by **Category** (pricing, features, usability, etc.)
- Filter by **Severity** (critical, high, medium, low)
- Combined filters for precise targeting

### 📊 Pain Points Table
- Problem statement with context
- Category and severity badges
- Opportunity score with progress bar
- Relevant tags for each pain point

---

## Quick Start

### Option 1: Use the Dashboard (Easiest)
```bash
# Open in your browser
open http://localhost:3000/index.html
```

### Option 2: Command Line
```bash
# Scrape a subreddit
curl -X POST http://localhost:8000/scrape/reddit \
  -H "Content-Type: application/json" \
  -d '{"subreddit": "saas", "keywords": ["frustrated"], "limit": 10}'

# Extract pain points
curl -X POST http://localhost:8000/extract/pain-points?limit=10

# View results
curl http://localhost:8000/pain-points
```

---

## Recommended Subreddits to Scrape:

### High-Value Targets:
1. **r/saas** - SaaS product discussions
2. **r/entrepreneur** - Business problems
3. **r/startups** - Startup challenges
4. **r/smallbusiness** - Small business pain points
5. **r/freelance** - Freelancer frustrations

### Niche Communities:
- **r/marketing** - Marketing challenges
- **r/webdev** - Developer problems
- **r/ecommerce** - E-commerce issues
- **r/shopify** - Shopify store problems
- **r/DigitalMarketing** - Digital marketing pain

### Example Keywords:
```
frustrated, hate, terrible, worst, awful
disappointed, annoying, wish there was
need a better, looking for, can't find
struggling with, difficult to, impossible to
```

---

##Automation Setup

See [AUTOMATION_GUIDE.md](./AUTOMATION_GUIDE.md) for detailed instructions on:
- Setting up daily/hourly automated scraping
- Using Celery or Cron
- Adding new subreddits
- Customizing schedules
- Monitoring and troubleshooting

---

## Stopping/Starting Services:

### Stop Everything:
```bash
# Stop API
pkill -f uvicorn

# Stop Dashboard
pkill -f "http.server 3000"

# Stop Docker containers
docker-compose down
```

### Start Everything:
```bash
# Start database & Redis
docker-compose up db redis -d

# Start API (in background)
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &

# Start Dashboard (in background)
python3 -m http.server 3000 --directory dashboard &

# Open dashboard
open http://localhost:3000/index.html
```

---

## Tips & Best Practices:

### 1. Start Small
- Begin with 2-3 subreddits
- Use 3-5 keywords
- Limit to 10-20 posts initially

### 2. Quality Over Quantity
- Focus on active subreddits (50k+ members)
- Use specific keywords for your niche
- Review extracted pain points regularly

### 3. Iterate & Improve
- Monitor which keywords find the best pain points
- Add successful subreddits to automation
- Remove noisy sources

### 4. Act on Insights
- Look for patterns (multiple people with same problem)
- High opportunity scores = potential products
- Critical severity = urgent needs

---

## Troubleshooting:

### Dashboard not loading?
```bash
# Check if server is running
curl http://localhost:3000/index.html

# Restart server
python3 -m http.server 3000 --directory dashboard &
```

### API errors?
```bash
# Check API health
curl http://localhost:8000/health

# View API logs
docker-compose logs api
```

### No data showing?
1. Scrape some data first using the dashboard
2. Make sure API is running
3. Check browser console for errors (F12)

---

## Next Steps:

1. ✅ **Scrape Data**: Use dashboard to scrape 3-5 subreddits
2. ✅ **Review Pain Points**: Look for patterns and opportunities
3. ✅ **Set Up Automation**: Follow AUTOMATION_GUIDE.md
4. ✅ **Add More Sources**: Expand to 10-15 subreddits
5. ✅ **Build Products**: Turn pain points into solutions!

---

**Happy Product Hunting!** 🚀

Built by Agent Girl + Greg
