# Autonomous Market Research App

Autonomous web scraping system to discover customer pain points, problems, and frustrations across the internet for product/service ideation.

## Features

- **Autonomous Scraping**: Reddit, Twitter, product reviews, forums
- **Sentiment Analysis**: Filters for negative sentiment (complaints, frustrations)
- **AI Extraction**: Structured pain points using Claude API
- **Categorization**: Automatic categorization by theme (pricing, usability, features, etc.)
- **Searchable Database**: PostgreSQL with pgvector for semantic search
- **Scheduled Jobs**: Runs automatically via Celery

## Quick Start

### Prerequisites

1. **API Keys Required** (see [API_KEYS_SETUP.md](./API_KEYS_SETUP.md) for detailed instructions):
   - Reddit API credentials (free)
   - Cloudflare AI API (free tier)
   - Anthropic Claude API (paid)
   - Apify API (free tier)

2. **System Requirements**:
   - Python 3.11+
   - Docker & Docker Compose
   - PostgreSQL 15+ with pgvector

### Installation

1. **Clone and setup**:
```bash
cd negative-sentim

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

2. **Configure environment variables**:
```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your API keys
nano .env
```

3. **Start services with Docker**:
```bash
# Start PostgreSQL and Redis
docker-compose up db redis -d

# Run database migrations
alembic upgrade head
```

4. **Start the API**:
```bash
# Development
uvicorn main:app --reload

# Production
uvicorn main:app --host 0.0.0.0 --port 8000
```

5. **Start background workers** (in separate terminals):
```bash
# Start Celery worker
celery -A tasks.scheduler worker --loglevel=info

# Start Celery beat scheduler
celery -A tasks.scheduler beat --loglevel=info
```

### Docker Compose (All-in-One)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

## API Endpoints

### Scraping
- `POST /scrape/reddit` - Scrape Reddit for complaints
- `POST /scrape/twitter` - Scrape Twitter for complaints

### Processing
- `POST /process/sentiment` - Analyze sentiment of scraped data
- `POST /extract/pain-points` - Extract structured pain points

### Querying
- `GET /pain-points` - Get pain points (with filters)
- `GET /stats` - Get overall statistics

### Example Usage

```bash
# Scrape Reddit
curl -X POST "http://localhost:8000/scrape/reddit" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "reddit",
    "subreddit": "saas",
    "keywords": ["frustrated", "hate", "worst"],
    "limit": 100
  }'

# Process sentiment
curl -X POST "http://localhost:8000/process/sentiment?limit=100"

# Extract pain points
curl -X POST "http://localhost:8000/extract/pain-points?limit=50"

# Get pain points
curl "http://localhost:8000/pain-points?category=pricing&min_score=70"
```

## Project Structure

```
negative-sentim/
├── alembic/              # Database migrations
├── database/             # SQLAlchemy models
│   ├── models.py
│   └── connection.py
├── scrapers/             # Web scrapers
│   ├── reddit_scraper.py
│   ├── twitter_scraper.py
│   └── apify_scraper.py
├── processors/           # AI processors
│   ├── sentiment_filter.py
│   └── pain_point_extractor.py
├── tasks/                # Celery tasks
│   └── scheduler.py
├── main.py               # FastAPI application
├── requirements.txt      # Python dependencies
├── docker-compose.yml    # Docker services
└── README.md
```

## Scheduled Jobs

The following jobs run automatically:
- **Daily Reddit Scrape**: 2 AM UTC (r/saas, r/entrepreneur, r/smallbusiness)
- **Sentiment Processing**: Every hour
- **Pain Point Extraction**: Every hour at :30

Configure schedules in `tasks/scheduler.py`.

## Database Schema

- **raw_data**: All scraped content
- **pain_points**: Extracted, structured pain points
- **search_queries**: Monitoring queries
- **scrape_jobs**: Audit log

## Development

### Run tests
```bash
pytest
```

### Create database migration
```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### Manual scraping
```bash
python -m scrapers.reddit_scraper
python -m scrapers.twitter_scraper
```

## Cost Estimates

### Free Tier (Getting Started)
- Reddit API: Free ✅
- Cloudflare AI: 10k requests/day free ✅
- Apify: 5 actors/month free ✅
- **Total: $0-10/month** (Claude API only)

### Production Scale
- Hosting: $7-25/month (Railway/Render)
- Database: $7-15/month
- Claude API: $10-50/month
- **Total: $30-165/month**

## Troubleshooting

### Database connection errors
```bash
# Check PostgreSQL is running
docker-compose ps

# Check connection
docker-compose exec db psql -U user -d market_research
```

### Celery not running
```bash
# Check Redis connection
redis-cli ping

# Check Celery workers
celery -A tasks.scheduler inspect active
```

## Documentation

- [API Keys Setup Guide](./API_KEYS_SETUP.md)
- [Technical Blueprint](../problem-finder/AUTONOMOUS_MARKET_RESEARCH_APP.md)

## License

MIT License - Use however you want!

**Built by Agent Girl + Greg** 🚀
