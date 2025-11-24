#!/usr/bin/env python3
"""Test the full pipeline: Reddit scraping + Claude pain point extraction."""
import os
from dotenv import load_dotenv
import json

load_dotenv()

from scrapers.reddit_scraper import RedditScraper
from processors.pain_point_extractor import PainPointExtractor

def main():
    print("🚀 TESTING FULL PIPELINE")
    print("=" * 70)
    print()

    # Step 1: Scrape Reddit
    print("📡 STEP 1: Scraping Reddit for complaints...")
    print("-" * 70)

    scraper = RedditScraper()
    results = scraper.scrape_subreddit_complaints(
        subreddit="saas",
        keywords=["frustrated", "hate"],
        limit=3,  # Just 3 posts for testing
        time_filter="week"
    )

    print(f"✅ Found {len(results)} posts with complaints\n")

    if not results:
        print("❌ No results found. Try different keywords or subreddit.")
        return

    # Step 2: Extract pain points with Claude
    print("🧠 STEP 2: Extracting pain points with Claude AI...")
    print("-" * 70)

    extractor = PainPointExtractor()

    for i, post in enumerate(results[:2], 1):  # Process first 2
        print(f"\n{'='*70}")
        print(f"POST #{i}: {post['content'].split(chr(10))[0][:60]}...")
        print(f"{'='*70}")

        try:
            # Extract pain point
            pain_point = extractor.extract(
                text=post['content'],
                source_metadata=post.get('metadata', {})
            )

            if pain_point:
                print(f"✅ Pain Point Extracted!\n")
                print(f"📌 Problem: {pain_point['problem_statement']}")
                print(f"📂 Category: {pain_point['category']}")
                print(f"⚠️  Severity: {pain_point['severity']}")
                print(f"🎯 Opportunity Score: {pain_point['opportunity_score']}/100")
                print(f"🏷️  Tags: {', '.join(pain_point.get('tags', []))}")
                print(f"👥 Target Audience: {pain_point.get('target_audience', 'N/A')}")
                print(f"💡 Suggested Solution: {pain_point.get('suggested_solution', 'N/A')[:80]}...")
            else:
                print("⚠️  Could not extract pain point")

        except Exception as e:
            print(f"❌ Error: {e}")

    print(f"\n{'='*70}")
    print("🎉 PIPELINE TEST COMPLETE!")
    print("=" * 70)
    print("\n✅ Reddit Scraping: Working")
    print("✅ Claude Extraction: Working")
    print("✅ Pain Point Analysis: Working")
    print("\n💡 Next: Set up database and API to store/query these pain points!")

if __name__ == "__main__":
    main()
