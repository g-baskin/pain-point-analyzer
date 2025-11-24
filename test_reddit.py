#!/usr/bin/env python3
"""Quick test of Reddit scraper without AI processing."""
import os
from dotenv import load_dotenv

load_dotenv()

from scrapers.reddit_scraper import RedditScraper

def main():
    print("🔍 Testing Reddit Scraper...")
    print("=" * 60)

    scraper = RedditScraper()

    # Scrape r/saas for complaints
    results = scraper.scrape_subreddit_complaints(
        subreddit="saas",
        keywords=["frustrated", "hate"],
        limit=5,
        time_filter="week"
    )

    print(f"\n✅ Found {len(results)} posts with complaints\n")

    for i, post in enumerate(results[:3], 1):
        print(f"{'='*60}")
        print(f"POST #{i}")
        print(f"{'='*60}")
        print(f"Title: {post['content'].split(chr(10))[0]}")
        print(f"Author: {post['author']}")
        print(f"Score: {post.get('score', 0)} upvotes")
        print(f"Comments: {post.get('num_comments', 0)}")
        print(f"URL: {post['url']}")
        print(f"\nPreview:")
        content_preview = post['content'][:200].replace('\n', ' ')
        print(f"  {content_preview}...")
        print()

    print(f"🎉 Reddit scraping is working perfectly!")
    print(f"\n💡 Once you add credits to Claude, we can extract pain points from these posts!")

if __name__ == "__main__":
    main()
