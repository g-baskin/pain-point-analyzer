from sqlalchemy import Column, Integer, String, Text, Float, Boolean, TIMESTAMP, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from .connection import Base

class RawData(Base):
    """Stores all scraped content before processing."""
    __tablename__ = 'raw_data'

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(50), nullable=False, index=True)
    source_id = Column(String(255), unique=True)
    content = Column(Text, nullable=False)
    author = Column(String(255))
    url = Column(Text)
    subreddit = Column(String(255))
    product_name = Column(String(255))
    source_metadata = Column(JSONB)  # Renamed from 'metadata' to avoid SQLAlchemy conflict
    scraped_at = Column(TIMESTAMP, default=func.now())
    sentiment_score = Column(Float)
    is_negative = Column(Boolean, index=True)
    processed = Column(Boolean, default=False, index=True)
    created_at = Column(TIMESTAMP, default=func.now(), index=True)


class ExtractionSession(Base):
    """Tracks each pain point extraction session for scorecard generation."""
    __tablename__ = 'extraction_sessions'

    id = Column(Integer, primary_key=True, index=True)
    session_name = Column(String(255))  # Auto-generated or user-provided name

    # Session metrics
    items_processed = Column(Integer, default=0)
    pain_points_extracted = Column(Integer, default=0)
    items_skipped = Column(Integer, default=0)

    # Aggregate scores
    avg_opportunity_score = Column(Float)
    high_severity_count = Column(Integer, default=0)
    critical_severity_count = Column(Integer, default=0)

    # Top category breakdown (stored as JSONB)
    category_breakdown = Column(JSONB)  # e.g., {"pricing": 5, "features": 3}
    severity_breakdown = Column(JSONB)  # e.g., {"critical": 2, "high": 5}

    # Timing
    started_at = Column(TIMESTAMP, default=func.now())
    completed_at = Column(TIMESTAMP)
    duration_seconds = Column(Integer)

    # Status
    status = Column(String(20), default='in_progress')  # in_progress, completed, failed
    error_message = Column(Text)

    # Metadata
    created_at = Column(TIMESTAMP, default=func.now(), index=True)


class PainPoint(Base):
    """Extracted, structured pain points."""
    __tablename__ = 'pain_points'

    id = Column(Integer, primary_key=True, index=True)
    raw_data_id = Column(Integer, ForeignKey('raw_data.id'))
    extraction_session_id = Column(Integer, ForeignKey('extraction_sessions.id'), index=True)

    # Core pain point data
    problem_statement = Column(Text, nullable=False)
    category = Column(String(100), index=True)
    severity = Column(String(20), index=True)
    context = Column(Text)

    # Frequency tracking
    mention_count = Column(Integer, default=1)
    first_seen = Column(TIMESTAMP, default=func.now())
    last_seen = Column(TIMESTAMP, default=func.now())

    # Semantic search
    embedding = Column(Vector(1536))

    # Product/market context
    related_product = Column(String(255))
    related_industry = Column(String(100))
    target_audience = Column(String(100))

    # Potential solution
    suggested_solution = Column(Text)
    opportunity_score = Column(Integer, index=True)

    # Metadata
    tags = Column(ARRAY(Text))
    created_at = Column(TIMESTAMP, default=func.now())
    updated_at = Column(TIMESTAMP, default=func.now(), onupdate=func.now())


class SearchQuery(Base):
    """Track what niches/topics to monitor."""
    __tablename__ = 'search_queries'

    id = Column(Integer, primary_key=True, index=True)
    query_text = Column(Text, nullable=False)
    source_type = Column(String(50))
    subreddits = Column(ARRAY(Text))
    keywords = Column(ARRAY(Text))
    is_active = Column(Boolean, default=True)
    last_run = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, default=func.now())


class ScrapeJob(Base):
    """Audit log for scraping runs."""
    __tablename__ = 'scrape_jobs'

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(50))
    query_id = Column(Integer, ForeignKey('search_queries.id'))
    status = Column(String(20))
    items_scraped = Column(Integer, default=0)
    items_negative = Column(Integer, default=0)
    pain_points_extracted = Column(Integer, default=0)
    error_message = Column(Text)
    started_at = Column(TIMESTAMP, default=func.now())
    completed_at = Column(TIMESTAMP)
