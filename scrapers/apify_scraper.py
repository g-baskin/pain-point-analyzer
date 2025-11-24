from apify_client import ApifyClient
import os
from typing import List, Dict
from loguru import logger

class ApifyReviewScraper:
    def __init__(self):
        self.client = ApifyClient(os.getenv("APIFY_API_TOKEN"))

    def scrape_amazon_reviews(
        self,
        product_asin: str,
        max_reviews: int = 100
    ) -> List[Dict]:
        """
        Scrape Amazon product reviews.

        Args:
            product_asin: Amazon product ID
            max_reviews: Max reviews to scrape
        """
        run_input = {
            "asins": [product_asin],
            "maxReviews": max_reviews,
            "scrapeReviewerInfo": True
        }

        try:
            # Run Amazon Reviews Scraper actor
            run = self.client.actor("junglee/amazon-reviews-scraper").call(
                run_input=run_input
            )

            results = []
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                # Filter for low ratings (pain points)
                if item.get('stars', 5) <= 3:
                    results.append({
                        'source': 'amazon_review',
                        'source_id': item.get('id'),
                        'content': f"{item.get('title', '')} {item.get('text', '')}",
                        'author': item.get('reviewerName', 'Anonymous'),
                        'url': item.get('url'),
                        'product_name': item.get('productTitle'),
                        'metadata': {
                            'rating': item.get('stars'),
                            'verified_purchase': item.get('verifiedPurchase'),
                            'helpful_votes': item.get('helpfulVotes')
                        },
                        'created_utc': item.get('date')
                    })

            logger.info(f"Scraped {len(results)} negative Amazon reviews for {product_asin}")
            return results

        except Exception as e:
            logger.error(f"Error scraping Amazon reviews: {e}")
            return []

    def scrape_google_maps_reviews(
        self,
        place_url: str,
        max_reviews: int = 100
    ) -> List[Dict]:
        """Scrape Google Maps reviews for a business."""
        run_input = {
            "searchStringsArray": [place_url],
            "maxReviews": max_reviews,
            "reviewsSort": "newest"
        }

        try:
            run = self.client.actor("compass/google-maps-reviews-scraper").call(
                run_input=run_input
            )

            results = []
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                # Filter for low ratings
                if item.get('stars', 5) <= 3:
                    results.append({
                        'source': 'google_maps_review',
                        'source_id': item.get('reviewId'),
                        'content': item.get('text', ''),
                        'author': item.get('name'),
                        'url': item.get('reviewUrl'),
                        'metadata': {
                            'rating': item.get('stars'),
                            'likes': item.get('likes'),
                            'response_from_owner': item.get('responseFromOwnerText')
                        },
                        'created_utc': item.get('publishedAtDate')
                    })

            logger.info(f"Scraped {len(results)} negative Google Maps reviews")
            return results

        except Exception as e:
            logger.error(f"Error scraping Google Maps reviews: {e}")
            return []

# Usage
if __name__ == "__main__":
    scraper = ApifyReviewScraper()

    # Scrape reviews for a product
    reviews = scraper.scrape_amazon_reviews(
        product_asin="B08N5WRWNW",  # Example ASIN
        max_reviews=50
    )

    print(f"Found {len(reviews)} negative reviews")
