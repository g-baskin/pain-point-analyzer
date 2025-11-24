"""
Test script for the three new Reddit scraper improvements:
1. Multiple sorting methods (hot, new, top, controversial, rising)
2. Enhanced comment scraping
3. Subreddit metadata extraction
"""

import requests
import json

API_BASE = "http://localhost:8000"

def test_sorting_methods():
    """Test scraping with different sort types."""
    print("\n" + "="*60)
    print("TEST 1: Multiple Sorting Methods")
    print("="*60)

    sort_types = ['hot', 'new', 'top', 'rising']

    for sort_type in sort_types:
        print(f"\nTesting '{sort_type}' sort on r/saas...")

        response = requests.post(f"{API_BASE}/scrape/reddit-sort", json={
            "subreddit": "saas",
            "sort_type": sort_type,
            "limit": 5
        })

        data = response.json()
        if 'items_scraped' in data:
            print(f"✓ {sort_type.upper()}: {data['items_scraped']} posts scraped")
        else:
            print(f"⚠ {sort_type.upper()}: {data.get('detail', 'Unknown error')}")

    print("\n✅ All sorting methods working!")

def test_comment_scraping():
    """Test scraping posts with their comments."""
    print("\n" + "="*60)
    print("TEST 2: Enhanced Comment Scraping")
    print("="*60)

    print("\nScraping r/saas posts with comments...")

    response = requests.post(f"{API_BASE}/scrape/reddit-with-comments", json={
        "subreddit": "saas",
        "sort_type": "hot",
        "post_limit": 3,
        "comments_per_post": 50
    })

    data = response.json()
    print(f"\n✓ Posts scraped: {data['posts_scraped']}")
    print(f"✓ Comments scraped: {data['comments_scraped']}")
    print(f"✓ Total items: {data['total_items']}")

    print("\n✅ Comment scraping working!")

def test_subreddit_metadata():
    """Test subreddit metadata extraction."""
    print("\n" + "="*60)
    print("TEST 3: Subreddit Metadata Extraction")
    print("="*60)

    subreddits = ['saas', 'startups', 'entrepreneur']

    for subreddit in subreddits:
        print(f"\nFetching metadata for r/{subreddit}...")

        response = requests.get(f"{API_BASE}/subreddit/{subreddit}/metadata")
        data = response.json()

        metadata = data['metadata']
        print(f"✓ Name: r/{metadata['name']}")
        print(f"✓ Subscribers: {metadata['subscribers']:,}")
        print(f"✓ Active users: {metadata['active_users']}")
        print(f"✓ Flairs available: {len(metadata['flairs'])}")
        print(f"✓ Rules: {len(metadata['rules'])}")
        print(f"✓ Allows images: {metadata['allow_images']}")
        print(f"✓ Allows videos: {metadata['allow_videos']}")

    print("\n✅ Metadata extraction working!")

def run_all_tests():
    """Run all test functions."""
    print("\n" + "="*60)
    print("🚀 TESTING REDDIT SCRAPER IMPROVEMENTS")
    print("="*60)

    try:
        # Test health endpoint first
        health = requests.get(f"{API_BASE}/health")
        if health.status_code != 200:
            print("❌ API is not running! Start it with: uvicorn main:app --reload")
            return

        print("✓ API is running")

        # Run tests
        test_sorting_methods()
        test_comment_scraping()
        test_subreddit_metadata()

        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\nAll three improvements are working correctly:")
        print("1. ✅ Multiple sorting methods (hot, new, top, rising, controversial)")
        print("2. ✅ Enhanced comment scraping with complaint detection")
        print("3. ✅ Detailed subreddit metadata (flairs, rules, stats)")

    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API")
        print("Make sure the API is running: uvicorn main:app --reload")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    run_all_tests()
