# API Keys Setup Guide

This guide walks you through obtaining all the API keys needed for the Autonomous Market Research App.

## Required API Keys

| Service | Cost | Purpose | Priority |
|---------|------|---------|----------|
| Reddit API | Free | Scraping posts/comments | ⭐ High |
| Cloudflare AI | Free (10k/day) | Sentiment analysis | ⭐ High |
| Anthropic Claude | Paid (~$3/1M tokens) | Pain point extraction | ⭐ High |
| Apify | Free (5 actors/month) | Review scraping | Medium |
| OpenAI | Paid (~$0.10/1M tokens) | Embeddings (optional) | Low |

---

## 1. Reddit API (Free) ⭐

**What you need**: `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`

### Steps:
1. Go to https://www.reddit.com/prefs/apps
2. Scroll to bottom and click **"create another app..."**
3. Fill out the form:
   - **name**: `market-research-bot` (or any name)
   - **App type**: Select **"script"**
   - **description**: `Market research scraper`
   - **about url**: Leave blank
   - **redirect uri**: `http://localhost:8000` (required but not used)
4. Click **"create app"**
5. Copy the credentials:
   - **client_id**: The string under "personal use script" (looks like: `abc123XYZ`)
   - **client_secret**: The "secret" field

### Add to .env:
```bash
REDDIT_CLIENT_ID=abc123XYZ
REDDIT_CLIENT_SECRET=your_secret_here
REDDIT_USER_AGENT=MarketResearchBot/1.0
```

---

## 2. Cloudflare AI (Free Tier) ⭐

**What you need**: `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN`

### Steps:
1. Sign up at https://dash.cloudflare.com/sign-up
2. Go to https://dash.cloudflare.com/
3. Get your Account ID:
   - Look for "Account ID" on the right sidebar
   - Or go to **Workers & Pages** → Copy Account ID
4. Create an API Token:
   - Go to https://dash.cloudflare.com/profile/api-tokens
   - Click **"Create Token"**
   - Choose **"Create Custom Token"**
   - Give it a name: `market-research-ai`
   - Permissions:
     - **Account** → **Workers AI** → **Read**
   - Click **"Continue to summary"** → **"Create Token"**
   - Copy the token (you won't see it again!)

### Add to .env:
```bash
CLOUDFLARE_ACCOUNT_ID=your_account_id
CLOUDFLARE_API_TOKEN=your_api_token
```

### Testing:
```bash
curl -X POST \
  "https://api.cloudflare.com/client/v4/accounts/YOUR_ACCOUNT_ID/ai/run/@cf/huggingface/distilbert-sst-2-int8" \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "This is terrible"}'
```

---

## 3. Anthropic Claude API (Paid) ⭐

**What you need**: `ANTHROPIC_API_KEY`

### Steps:
1. Go to https://console.anthropic.com/
2. Sign up/log in
3. Go to **Settings** → **API Keys**
4. Click **"Create Key"**
5. Give it a name: `market-research`
6. Copy the API key

### Pricing:
- **Claude 3.5 Sonnet**: ~$3 per 1M input tokens, $15 per 1M output tokens
- **Estimated cost**: $10-30/month for moderate usage

### Add to .env:
```bash
ANTHROPIC_API_KEY=sk-ant-api03-...
```

### Testing:
```bash
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: YOUR_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-3-5-sonnet-20241022",
    "max_tokens": 100,
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

---

## 4. Apify (Free Tier)

**What you need**: `APIFY_API_TOKEN`

### Steps:
1. Sign up at https://apify.com/sign-up
2. Go to **Settings** → **Integrations**
3. Find **API Tokens** section
4. Copy your personal API token (or create a new one)

### Free Tier Limits:
- 5 actor runs per month
- Good for testing, upgrade to $49/month for production

### Add to .env:
```bash
APIFY_API_TOKEN=apify_api_...
```

---

## 5. OpenAI (Optional - For Embeddings)

**What you need**: `OPENAI_API_KEY`

Only needed if you want semantic search with embeddings.

### Steps:
1. Go to https://platform.openai.com/signup
2. Add payment method
3. Go to https://platform.openai.com/api-keys
4. Click **"Create new secret key"**
5. Copy the key

### Pricing:
- **text-embedding-3-small**: ~$0.02 per 1M tokens (very cheap)

### Add to .env:
```bash
OPENAI_API_KEY=sk-proj-...
```

---

## Final .env File

Your `.env` should look like this:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/market_research

# Redis
REDIS_URL=redis://localhost:6379/0

# Reddit API
REDDIT_CLIENT_ID=abc123XYZ
REDDIT_CLIENT_SECRET=your_reddit_secret
REDDIT_USER_AGENT=MarketResearchBot/1.0

# Apify
APIFY_API_TOKEN=apify_api_your_token

# Cloudflare AI
CLOUDFLARE_ACCOUNT_ID=your_cloudflare_account_id
CLOUDFLARE_API_TOKEN=your_cloudflare_token

# Claude API
ANTHROPIC_API_KEY=sk-ant-api03-your_key

# OpenAI (Optional)
# OPENAI_API_KEY=sk-proj-your_key

# App Settings
ENVIRONMENT=development
LOG_LEVEL=INFO
```

---

## Testing Your Setup

After adding all keys, test each integration:

```bash
# Activate virtual environment
source venv/bin/activate

# Test Reddit
python -c "from scrapers.reddit_scraper import RedditScraper; s = RedditScraper(); print('Reddit: OK')"

# Test Cloudflare AI
python -c "import asyncio; from processors.sentiment_filter import SentimentFilter; asyncio.run(SentimentFilter().analyze_sentiment('This is bad')); print('Cloudflare: OK')"

# Test Claude
python -c "from processors.pain_point_extractor import PainPointExtractor; PainPointExtractor(); print('Claude: OK')"
```

---

## Cost Management Tips

1. **Start with free tiers**: Use Cloudflare AI (free) instead of paid alternatives
2. **Set spending limits**: In Anthropic/OpenAI dashboards, set monthly spending caps
3. **Monitor usage**: Check usage in each service's dashboard weekly
4. **Batch processing**: Process 100 items at once to reduce API calls
5. **Cache results**: Don't re-analyze the same content

---

## Troubleshooting

### "Invalid API key" errors
- Double-check you copied the entire key (no spaces)
- Make sure `.env` file is in the project root
- Restart your application after changing `.env`

### Reddit rate limiting
- Free tier allows 60 requests/minute
- Add delays between requests if needed
- Use `time_filter='week'` to reduce duplicate scraping

### Cloudflare AI errors
- Free tier: 10,000 requests/day
- Requests reset at midnight UTC
- Use batch processing to stay under limits

---

## Security Best Practices

1. **Never commit .env to git** (already in .gitignore)
2. **Use environment-specific keys** (dev vs production)
3. **Rotate keys regularly** (every 3-6 months)
4. **Set key permissions** (read-only when possible)
5. **Monitor for leaked keys** at https://github.com/settings/security

---

## Need Help?

- **Reddit API**: https://www.reddit.com/dev/api
- **Cloudflare AI**: https://developers.cloudflare.com/workers-ai/
- **Anthropic**: https://docs.anthropic.com/
- **Apify**: https://docs.apify.com/

Happy scraping! 🚀
