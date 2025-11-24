from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import os

from database import get_db, RawData, PainPoint, ExtractionSession, SearchQuery, ScrapeJob
from scrapers import RedditScraper, ApifyReviewScraper
# TwitterScraper disabled due to Python 3.12 compatibility
from processors import SentimentFilter, PainPointExtractor
from loguru import logger

# Initialize FastAPI app
app = FastAPI(
    title="Autonomous Market Research API",
    description="API for discovering customer pain points across the internet",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API
class ScrapeRequest(BaseModel):
    source: str  # 'reddit', 'twitter', 'amazon'
    keywords: List[str]
    subreddit: Optional[str] = None
    limit: int = 100

class ScrapeBySort(BaseModel):
    subreddit: str
    sort_type: str = 'hot'  # 'hot', 'new', 'top', 'controversial', 'rising'
    keywords: Optional[List[str]] = None
    limit: int = 100
    time_filter: str = 'week'

class ScrapeWithComments(BaseModel):
    subreddit: str
    sort_type: str = 'hot'
    keywords: Optional[List[str]] = None
    post_limit: int = 50
    comments_per_post: int = 100
    time_filter: str = 'week'

class PainPointResponse(BaseModel):
    id: int
    problem_statement: str
    category: str
    severity: str
    context: str
    opportunity_score: int
    tags: List[str]
    created_at: datetime

    class Config:
        from_attributes = True

class RawDataResponse(BaseModel):
    id: int
    source: str
    source_id: str
    content: str
    author: Optional[str] = None
    url: Optional[str] = None
    subreddit: Optional[str] = None
    source_metadata: Optional[dict] = None
    scraped_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Health check
@app.get("/")
def read_root():
    return {
        "message": "Autonomous Market Research API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Scraping endpoints
@app.post("/scrape/reddit")
async def scrape_reddit(request: ScrapeRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Scrape Reddit for complaints."""
    if not request.subreddit:
        raise HTTPException(status_code=400, detail="subreddit is required for Reddit scraping")

    try:
        scraper = RedditScraper()
        results = scraper.scrape_subreddit_complaints(
            subreddit=request.subreddit,
            keywords=request.keywords,
            limit=request.limit
        )

        # Save raw data to database
        for item in results:
            raw_data = RawData(
                source=item['source'],
                source_id=item['source_id'],
                content=item['content'],
                author=item['author'],
                url=item['url'],
                subreddit=item.get('subreddit'),
                source_metadata=item.get('metadata'),
                scraped_at=item.get('created_utc')
            )
            db.add(raw_data)

        db.commit()

        return {
            "status": "success",
            "items_scraped": len(results),
            "message": f"Scraped {len(results)} posts from r/{request.subreddit}"
        }

    except Exception as e:
        logger.error(f"Error scraping Reddit: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Twitter scraper disabled due to Python 3.12 compatibility
# @app.post("/scrape/twitter")
# async def scrape_twitter(request: ScrapeRequest, db: Session = Depends(get_db)):
#     """Scrape Twitter for complaints."""
#     raise HTTPException(status_code=501, detail="Twitter scraper temporarily disabled due to compatibility issues")

@app.post("/scrape/amazon")
async def scrape_amazon_reviews(
    product_asin: str,
    max_reviews: int = 100,
    db: Session = Depends(get_db)
):
    """
    Scrape Amazon product reviews (1-3 stars only).

    Args:
        product_asin: Amazon product ID (e.g., B08N5WRWNW)
        max_reviews: Maximum reviews to scrape
    """
    try:
        scraper = ApifyReviewScraper()
        results = scraper.scrape_amazon_reviews(
            product_asin=product_asin,
            max_reviews=max_reviews
        )

        # Save raw data to database
        for item in results:
            raw_data = RawData(
                source=item['source'],
                source_id=item['source_id'],
                content=item['content'],
                author=item['author'],
                url=item['url'],
                source_metadata=item.get('metadata'),
                scraped_at=item.get('created_utc')
            )
            db.add(raw_data)

        db.commit()

        return {
            "status": "success",
            "items_scraped": len(results),
            "message": f"Scraped {len(results)} negative reviews for ASIN {product_asin}"
        }

    except Exception as e:
        logger.error(f"Error scraping Amazon reviews: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scrape/google-maps")
async def scrape_google_maps_reviews(
    place_url: str,
    max_reviews: int = 100,
    db: Session = Depends(get_db)
):
    """
    Scrape Google Maps business reviews (1-3 stars only).

    Args:
        place_url: Google Maps place URL
        max_reviews: Maximum reviews to scrape
    """
    try:
        scraper = ApifyReviewScraper()
        results = scraper.scrape_google_maps_reviews(
            place_url=place_url,
            max_reviews=max_reviews
        )

        # Save raw data to database
        for item in results:
            raw_data = RawData(
                source=item['source'],
                source_id=item['source_id'],
                content=item['content'],
                author=item['author'],
                url=item['url'],
                source_metadata=item.get('metadata'),
                scraped_at=item.get('created_utc')
            )
            db.add(raw_data)

        db.commit()

        return {
            "status": "success",
            "items_scraped": len(results),
            "message": f"Scraped {len(results)} negative Google Maps reviews"
        }

    except Exception as e:
        logger.error(f"Error scraping Google Maps reviews: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scrape/reddit-sort")
async def scrape_reddit_by_sort(request: ScrapeBySort, db: Session = Depends(get_db)):
    """
    Scrape Reddit using different sorting methods (hot, new, top, controversial, rising).

    Args:
        subreddit: Subreddit name
        sort_type: 'hot', 'new', 'top', 'controversial', 'rising'
        keywords: Optional keywords to filter
        limit: Max posts to scrape
        time_filter: For top/controversial - 'hour', 'day', 'week', 'month', 'year', 'all'
    """
    try:
        scraper = RedditScraper()
        results = scraper.scrape_by_sort(
            subreddit=request.subreddit,
            sort_type=request.sort_type,
            keywords=request.keywords,
            limit=request.limit,
            time_filter=request.time_filter
        )

        # Save to database with duplicate handling
        items_added = 0
        items_skipped = 0

        for item in results:
            try:
                raw_data = RawData(
                    source=item['source'],
                    source_id=item['source_id'],
                    content=item['content'],
                    author=item['author'],
                    url=item['url'],
                    subreddit=item.get('subreddit'),
                    source_metadata=item.get('metadata'),
                    scraped_at=item.get('created_utc')
                )
                db.add(raw_data)
                db.commit()
                items_added += 1
            except IntegrityError:
                db.rollback()
                items_skipped += 1
                logger.debug(f"Skipping duplicate post: {item['source_id']}")

        return {
            "status": "success",
            "items_scraped": items_added,
            "items_skipped": items_skipped,
            "total_found": len(results),
            "sort_type": request.sort_type,
            "message": f"Scraped {items_added} new posts from r/{request.subreddit} ({items_skipped} duplicates skipped)"
        }

    except Exception as e:
        logger.error(f"Error scraping Reddit with sort: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scrape/reddit-with-comments")
async def scrape_reddit_with_comments(request: ScrapeWithComments, db: Session = Depends(get_db)):
    """
    Scrape Reddit posts AND their comments for comprehensive pain point discovery.

    Args:
        subreddit: Subreddit name
        sort_type: Sorting method
        keywords: Optional keywords
        post_limit: Max posts to scrape
        comments_per_post: Max comments per post
        time_filter: Time filter
    """
    try:
        scraper = RedditScraper()
        results = scraper.scrape_subreddit_with_comments(
            subreddit=request.subreddit,
            sort_type=request.sort_type,
            keywords=request.keywords,
            post_limit=request.post_limit,
            comments_per_post=request.comments_per_post,
            time_filter=request.time_filter
        )

        # Save posts to database with duplicate handling
        posts_saved = 0
        posts_skipped = 0
        for item in results['posts']:
            try:
                raw_data = RawData(
                    source=item['source'],
                    source_id=item['source_id'],
                    content=item['content'],
                    author=item['author'],
                    url=item['url'],
                    subreddit=item.get('subreddit'),
                    source_metadata=item.get('metadata'),
                    scraped_at=item.get('created_utc')
                )
                db.add(raw_data)
                db.commit()
                posts_saved += 1
            except IntegrityError:
                db.rollback()
                posts_skipped += 1
                logger.debug(f"Skipping duplicate post: {item['source_id']}")

        # Save comments to database with duplicate handling
        comments_saved = 0
        comments_skipped = 0
        for item in results['comments']:
            try:
                raw_data = RawData(
                    source=item['source'],
                    source_id=item['source_id'],
                    content=item['content'],
                    author=item['author'],
                    url=item['url'],
                    subreddit=item.get('subreddit'),
                    source_metadata=item.get('metadata'),
                    scraped_at=item.get('created_utc')
                )
                db.add(raw_data)
                db.commit()
                comments_saved += 1
            except IntegrityError:
                db.rollback()
                comments_skipped += 1
                logger.debug(f"Skipping duplicate comment: {item['source_id']}")

        return {
            "status": "success",
            "posts_scraped": posts_saved,
            "posts_skipped": posts_skipped,
            "comments_scraped": comments_saved,
            "comments_skipped": comments_skipped,
            "total_items": posts_saved + comments_saved,
            "message": f"Scraped {posts_saved} new posts and {comments_saved} new comments from r/{request.subreddit} ({posts_skipped + comments_skipped} duplicates skipped)"
        }

    except Exception as e:
        logger.error(f"Error scraping Reddit with comments: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Processing endpoints
@app.post("/process/sentiment")
async def process_sentiment(limit: int = 100, db: Session = Depends(get_db)):
    """Process sentiment for unprocessed items."""
    try:
        # Get unprocessed items
        items = db.query(RawData).filter(
            RawData.processed == False,
            RawData.sentiment_score == None
        ).limit(limit).all()

        if not items:
            return {"status": "success", "message": "No items to process"}

        # Convert to dict format for processor
        items_dict = [
            {
                'id': item.id,
                'content': item.content
            }
            for item in items
        ]

        # Process sentiment
        sentiment_filter = SentimentFilter()
        negative_items = await sentiment_filter.filter_negative(items_dict)

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

        return {
            "status": "success",
            "items_processed": len(items),
            "items_negative": len(negative_items)
        }

    except Exception as e:
        logger.error(f"Error processing sentiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/extract/pain-points")
async def extract_pain_points(limit: int = 50, db: Session = Depends(get_db)):
    """Extract pain points from negative items and create extraction session scorecard."""
    start_time = datetime.now()

    try:
        # Create extraction session
        session_name = f"Analysis {start_time.strftime('%Y-%m-%d %H:%M')}"
        extraction_session = ExtractionSession(
            session_name=session_name,
            started_at=start_time,
            status='in_progress'
        )
        db.add(extraction_session)
        db.commit()
        db.refresh(extraction_session)

        session_id = extraction_session.id
        logger.info(f"Created extraction session {session_id}: {session_name}")

        # Get all raw data IDs that already have pain points
        processed_ids = set(
            db.query(PainPoint.raw_data_id)
            .filter(PainPoint.raw_data_id != None)
            .distinct()
            .all()
        )
        processed_ids = {pid[0] for pid in processed_ids}

        # Get items without pain points
        items = db.query(RawData).filter(
            RawData.content != None,
            ~RawData.id.in_(processed_ids) if processed_ids else True
        ).limit(limit).all()

        if not items:
            extraction_session.status = 'completed'
            extraction_session.completed_at = datetime.now()
            extraction_session.items_processed = 0
            extraction_session.pain_points_extracted = 0
            db.commit()

            return {
                "status": "success",
                "message": "No new items to extract",
                "session_id": session_id,
                "pain_points_extracted": 0,
                "items_processed": 0,
                "items_skipped": 0
            }

        logger.info(f"Extracting pain points from {len(items)} items...")

        # Convert to dict format
        items_dict = [
            {
                'id': item.id,
                'content': item.content,
                'metadata': item.source_metadata or {}
            }
            for item in items
        ]

        # Extract pain points
        extractor = PainPointExtractor()
        pain_points_data = await extractor.batch_extract(items_dict)

        # Save pain points to database and track metrics
        saved_count = 0
        category_counts = {}
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        total_opportunity_score = 0

        for pp_data in pain_points_data:
            try:
                pain_point = PainPoint(
                    raw_data_id=pp_data.get('raw_data_id'),
                    extraction_session_id=session_id,
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
                saved_count += 1

                # Track metrics
                category = pp_data.get('category', 'other')
                category_counts[category] = category_counts.get(category, 0) + 1

                severity = pp_data.get('severity', 'low')
                if severity in severity_counts:
                    severity_counts[severity] += 1

                total_opportunity_score += pp_data.get('opportunity_score', 50)

            except Exception as e:
                logger.error(f"Error saving pain point: {e}")
                continue

        # Calculate session metrics
        avg_opportunity_score = total_opportunity_score / saved_count if saved_count > 0 else 0
        duration_seconds = int((datetime.now() - start_time).total_seconds())

        # Update extraction session with final metrics
        extraction_session.items_processed = len(items)
        extraction_session.pain_points_extracted = saved_count
        extraction_session.items_skipped = len(items) - saved_count
        extraction_session.avg_opportunity_score = avg_opportunity_score
        extraction_session.high_severity_count = severity_counts['high']
        extraction_session.critical_severity_count = severity_counts['critical']
        extraction_session.category_breakdown = category_counts
        extraction_session.severity_breakdown = severity_counts
        extraction_session.completed_at = datetime.now()
        extraction_session.duration_seconds = duration_seconds
        extraction_session.status = 'completed'

        db.commit()

        logger.info(f"Session {session_id}: Extracted {saved_count} pain points in {duration_seconds}s")

        return {
            "status": "success",
            "session_id": session_id,
            "session_name": session_name,
            "pain_points_extracted": saved_count,
            "items_processed": len(items),
            "items_skipped": len(items) - saved_count,
            "duration_seconds": duration_seconds
        }

    except Exception as e:
        # Mark session as failed
        if 'extraction_session' in locals():
            extraction_session.status = 'failed'
            extraction_session.error_message = str(e)
            extraction_session.completed_at = datetime.now()
            db.commit()

        logger.error(f"Error extracting pain points: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Query endpoints
@app.get("/pain-points", response_model=List[PainPointResponse])
def get_pain_points(
    category: Optional[str] = None,
    severity: Optional[str] = None,
    min_score: Optional[int] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get pain points with optional filters."""
    query = db.query(PainPoint)

    if category:
        query = query.filter(PainPoint.category == category)
    if severity:
        query = query.filter(PainPoint.severity == severity)
    if min_score:
        query = query.filter(PainPoint.opportunity_score >= min_score)

    pain_points = query.order_by(PainPoint.opportunity_score.desc()).limit(limit).all()

    return pain_points

@app.get("/raw-data", response_model=List[RawDataResponse])
def get_raw_data(
    source: Optional[str] = None,
    subreddit: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get raw scraped data with optional filters."""
    query = db.query(RawData)

    if source:
        query = query.filter(RawData.source == source)
    if subreddit:
        query = query.filter(RawData.subreddit == subreddit)

    raw_data = query.order_by(RawData.scraped_at.desc()).limit(limit).all()

    return raw_data

@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """Get overall statistics."""
    total_scraped = db.query(RawData).count()
    total_negative = db.query(RawData).filter(RawData.is_negative == True).count()
    total_pain_points = db.query(PainPoint).count()

    # Category breakdown
    categories = db.query(
        PainPoint.category,
        db.func.count(PainPoint.id)
    ).group_by(PainPoint.category).all()

    return {
        "total_items_scraped": total_scraped,
        "total_negative_items": total_negative,
        "total_pain_points": total_pain_points,
        "categories": {cat: count for cat, count in categories}
    }

# Subreddit discovery endpoints
@app.get("/discover/trending")
def discover_trending_subreddits():
    """Get trending subreddits organized by category."""
    try:
        scraper = RedditScraper()
        trending = scraper.get_trending_subreddits()

        # Group by category
        by_category = {}
        for sub in trending:
            category = sub.get('category', 'Other')
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(sub)

        return {
            "status": "success",
            "total_subreddits": len(trending),
            "by_category": by_category,
            "all_subreddits": trending
        }
    except Exception as e:
        logger.error(f"Error discovering trending subreddits: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/discover/popular")
def discover_popular_subreddits(limit: int = 30):
    """Discover currently popular subreddits from Reddit's hot feed."""
    try:
        scraper = RedditScraper()
        popular = scraper.discover_popular_subreddits(limit=limit)

        return {
            "status": "success",
            "total_subreddits": len(popular),
            "subreddits": popular
        }
    except Exception as e:
        logger.error(f"Error discovering popular subreddits: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/discover/category/{category}")
def discover_by_category(category: str):
    """Search for subreddits by category/topic."""
    try:
        scraper = RedditScraper()
        results = scraper.discover_subreddits_by_category(category)

        return {
            "status": "success",
            "category": category,
            "total_subreddits": len(results),
            "subreddits": results
        }
    except Exception as e:
        logger.error(f"Error discovering subreddits for category '{category}': {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/subreddit/{subreddit_name}/metadata")
def get_subreddit_metadata(subreddit_name: str):
    """
    Get detailed subreddit metadata including flairs, rules, and statistics.

    Args:
        subreddit_name: Name of the subreddit (without r/ prefix)

    Returns:
        Comprehensive subreddit metadata including:
        - Basic info (name, title, description, subscribers, active users)
        - Link flairs available
        - Subreddit rules
        - Content settings (images, videos allowed)
    """
    try:
        scraper = RedditScraper()
        metadata = scraper.get_subreddit_metadata(subreddit_name)

        if 'error' in metadata:
            raise HTTPException(status_code=404, detail=f"Subreddit not found: {metadata['error']}")

        return {
            "status": "success",
            "subreddit": subreddit_name,
            "metadata": metadata
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting metadata for r/{subreddit_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Extraction Session / Scorecard endpoints
@app.get("/extraction-sessions")
def get_extraction_sessions(
    limit: int = 50,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get list of all extraction sessions (scorecards).

    Args:
        limit: Max sessions to return
        status: Filter by status ('completed', 'in_progress', 'failed')

    Returns:
        List of extraction sessions with their metrics
    """
    try:
        query = db.query(ExtractionSession)

        if status:
            query = query.filter(ExtractionSession.status == status)

        sessions = query.order_by(ExtractionSession.created_at.desc()).limit(limit).all()

        return {
            "status": "success",
            "total_sessions": len(sessions),
            "sessions": [
                {
                    "id": session.id,
                    "session_name": session.session_name,
                    "items_processed": session.items_processed,
                    "pain_points_extracted": session.pain_points_extracted,
                    "items_skipped": session.items_skipped,
                    "avg_opportunity_score": session.avg_opportunity_score,
                    "high_severity_count": session.high_severity_count,
                    "critical_severity_count": session.critical_severity_count,
                    "category_breakdown": session.category_breakdown,
                    "severity_breakdown": session.severity_breakdown,
                    "started_at": session.started_at,
                    "completed_at": session.completed_at,
                    "duration_seconds": session.duration_seconds,
                    "status": session.status,
                    "error_message": session.error_message
                }
                for session in sessions
            ]
        }
    except Exception as e:
        logger.error(f"Error getting extraction sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/extraction-sessions/{session_id}")
def get_extraction_session_detail(session_id: int, db: Session = Depends(get_db)):
    """
    Get detailed scorecard for a specific extraction session.

    Args:
        session_id: ID of the extraction session

    Returns:
        Full session details including all associated pain points
    """
    try:
        session = db.query(ExtractionSession).filter(ExtractionSession.id == session_id).first()

        if not session:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        # Get all pain points for this session
        pain_points = db.query(PainPoint).filter(
            PainPoint.extraction_session_id == session_id
        ).order_by(PainPoint.opportunity_score.desc()).all()

        return {
            "status": "success",
            "session": {
                "id": session.id,
                "session_name": session.session_name,
                "items_processed": session.items_processed,
                "pain_points_extracted": session.pain_points_extracted,
                "items_skipped": session.items_skipped,
                "avg_opportunity_score": session.avg_opportunity_score,
                "high_severity_count": session.high_severity_count,
                "critical_severity_count": session.critical_severity_count,
                "category_breakdown": session.category_breakdown,
                "severity_breakdown": session.severity_breakdown,
                "started_at": session.started_at,
                "completed_at": session.completed_at,
                "duration_seconds": session.duration_seconds,
                "status": session.status,
                "error_message": session.error_message
            },
            "pain_points": [
                {
                    "id": pp.id,
                    "problem_statement": pp.problem_statement,
                    "category": pp.category,
                    "severity": pp.severity,
                    "context": pp.context,
                    "opportunity_score": pp.opportunity_score,
                    "tags": pp.tags,
                    "target_audience": pp.target_audience,
                    "related_industry": pp.related_industry,
                    "suggested_solution": pp.suggested_solution
                }
                for pp in pain_points
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session {session_id} details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/extraction-sessions/{session_id}/scorecard")
def get_session_scorecard(session_id: int, db: Session = Depends(get_db)):
    """
    Get high-level scorecard summary for an extraction session.

    Args:
        session_id: ID of the extraction session

    Returns:
        Scorecard with key metrics and insights
    """
    try:
        session = db.query(ExtractionSession).filter(ExtractionSession.id == session_id).first()

        if not session:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        # Get top pain points
        top_pain_points = db.query(PainPoint).filter(
            PainPoint.extraction_session_id == session_id
        ).order_by(PainPoint.opportunity_score.desc()).limit(5).all()

        return {
            "status": "success",
            "scorecard": {
                "session_name": session.session_name,
                "date": session.started_at.strftime('%Y-%m-%d %H:%M'),
                "duration": f"{session.duration_seconds}s" if session.duration_seconds else "N/A",

                # Summary metrics
                "total_pain_points": session.pain_points_extracted,
                "items_analyzed": session.items_processed,
                "avg_opportunity_score": round(session.avg_opportunity_score, 1) if session.avg_opportunity_score else 0,

                # Severity breakdown
                "critical_count": session.critical_severity_count,
                "high_count": session.high_severity_count,
                "severity_breakdown": session.severity_breakdown,

                # Category insights
                "top_category": max(session.category_breakdown.items(), key=lambda x: x[1])[0] if session.category_breakdown else None,
                "category_breakdown": session.category_breakdown,

                # Top opportunities
                "top_opportunities": [
                    {
                        "problem": pp.problem_statement,
                        "category": pp.category,
                        "severity": pp.severity,
                        "score": pp.opportunity_score
                    }
                    for pp in top_pain_points
                ],

                "status": session.status
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting scorecard for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
