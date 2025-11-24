from celery import Celery
from celery.schedules import crontab
import os
import asyncio
from loguru import logger

app = Celery('market_research')
app.config_from_object('celeryconfig')

@app.task
def daily_reddit_scrape():
    """Run daily Reddit scraping."""
    from scrapers.reddit_scraper import RedditScraper
    from database import SessionLocal, RawData

    db = SessionLocal()
    scraper = RedditScraper()

    # Scrape multiple subreddits
    subreddits = ['saas', 'entrepreneur', 'smallbusiness']
    keywords = ['frustrated', 'hate', 'terrible', 'wish there was']

    all_results = []
    for sub in subreddits:
        try:
            results = scraper.scrape_subreddit_complaints(
                subreddit=sub,
                keywords=keywords,
                limit=50,
                time_filter='day'
            )
            all_results.extend(results)
        except Exception as e:
            logger.error(f"Error scraping r/{sub}: {e}")
            continue

    # Save to database
    for item in all_results:
        raw_data = RawData(
            source=item['source'],
            source_id=item['source_id'],
            content=item['content'],
            author=item['author'],
            url=item['url'],
            subreddit=item.get('subreddit'),
            metadata=item.get('metadata'),
            scraped_at=item.get('created_utc')
        )
        db.add(raw_data)

    db.commit()
    db.close()

    logger.info(f"Scraped {len(all_results)} posts")
    return f"Scraped {len(all_results)} posts"

@app.task
def process_sentiment():
    """Process sentiment for unprocessed items."""
    from processors.sentiment_filter import SentimentFilter
    from database import SessionLocal, RawData

    db = SessionLocal()

    # Get unprocessed items
    items = db.query(RawData).filter(
        RawData.processed == False,
        RawData.sentiment_score == None
    ).limit(100).all()

    if not items:
        logger.info("No items to process")
        db.close()
        return "No items to process"

    items_dict = [{'id': item.id, 'content': item.content} for item in items]

    sentiment_filter = SentimentFilter()
    negative_items = asyncio.run(sentiment_filter.filter_negative(items_dict))

    # Update database
    negative_ids = {item['id'] for item in negative_items}
    for item in items:
        if item.id in negative_ids:
            item.is_negative = True
            item.sentiment_score = next(
                i['sentiment_score'] for i in negative_items if i['id'] == item.id
            )
        item.processed = True

    db.commit()
    db.close()

    logger.info(f"Processed {len(items)}, found {len(negative_items)} negative")
    return f"Processed {len(items)}, found {len(negative_items)} negative"

@app.task
def extract_pain_points():
    """Extract pain points from negative items."""
    from processors.pain_point_extractor import PainPointExtractor
    from database import SessionLocal, RawData, PainPoint

    db = SessionLocal()

    items = db.query(RawData).filter(
        RawData.is_negative == True
    ).limit(50).all()

    if not items:
        logger.info("No negative items to extract")
        db.close()
        return "No items to extract"

    items_dict = [
        {
            'id': item.id,
            'content': item.content,
            'metadata': item.metadata or {}
        }
        for item in items
    ]

    extractor = PainPointExtractor()
    pain_points_data = asyncio.run(extractor.batch_extract(items_dict))

    # Save to database
    for pp_data in pain_points_data:
        pain_point = PainPoint(
            raw_data_id=pp_data.get('raw_data_id'),
            problem_statement=pp_data['problem_statement'],
            category=pp_data['category'],
            severity=pp_data['severity'],
            context=pp_data.get('context'),
            suggested_solution=pp_data.get('suggested_solution'),
            tags=pp_data.get('tags', []),
            target_audience=pp_data.get('target_audience'),
            related_industry=pp_data.get('related_industry'),
            opportunity_score=pp_data.get('opportunity_score', 50)
        )
        db.add(pain_point)

    db.commit()
    db.close()

    logger.info(f"Extracted {len(pain_points_data)} pain points")
    return f"Extracted {len(pain_points_data)} pain points"

# Schedule
app.conf.beat_schedule = {
    'daily-reddit-scrape': {
        'task': 'tasks.scheduler.daily_reddit_scrape',
        'schedule': crontab(hour=2, minute=0),  # 2 AM daily
    },
    'process-sentiment-hourly': {
        'task': 'tasks.scheduler.process_sentiment',
        'schedule': crontab(minute=0),  # Every hour
    },
    'extract-pain-points-hourly': {
        'task': 'tasks.scheduler.extract_pain_points',
        'schedule': crontab(minute=30),  # Every hour at :30
    }
}
