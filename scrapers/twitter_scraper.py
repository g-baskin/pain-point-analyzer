import snscrape.modules.twitter as sntwitter
from datetime import datetime, timedelta
from typing import List, Dict
from loguru import logger

class TwitterScraper:
    def scrape_by_keywords(
        self,
        keywords: List[str],
        max_tweets: int = 100,
        since_days: int = 7
    ) -> List[Dict]:
        """
        Scrape tweets containing complaint keywords.

        Args:
            keywords: Search terms (e.g., ['frustrated with', 'hate when'])
            max_tweets: Max tweets to retrieve per keyword
            since_days: Look back N days

        Returns:
            List of tweet data dicts
        """
        results = []
        since_date = (datetime.now() - timedelta(days=since_days)).strftime('%Y-%m-%d')

        for keyword in keywords:
            query = f'"{keyword}" lang:en since:{since_date} -filter:retweets'

            try:
                tweets = sntwitter.TwitterSearchScraper(query).get_items()

                count = 0
                for tweet in tweets:
                    if count >= max_tweets:
                        break

                    # Filter for negative sentiment
                    content = tweet.rawContent.lower()
                    if any(neg in content for neg in [
                        'hate', 'frustrated', 'annoying', 'terrible',
                        'worst', 'awful', 'disappointed'
                    ]):
                        results.append({
                            'source': 'twitter',
                            'source_id': str(tweet.id),
                            'content': tweet.rawContent,
                            'author': tweet.user.username,
                            'url': tweet.url,
                            'metadata': {
                                'retweet_count': tweet.retweetCount,
                                'like_count': tweet.likeCount,
                                'reply_count': tweet.replyCount,
                                'keyword_matched': keyword,
                                'hashtags': tweet.hashtags if hasattr(tweet, 'hashtags') else []
                            },
                            'created_utc': tweet.date
                        })
                        count += 1

                logger.info(f"Found {count} tweets for keyword '{keyword}'")

            except Exception as e:
                logger.error(f"Error scraping Twitter for '{keyword}': {e}")
                continue

        return results

# Usage
if __name__ == "__main__":
    scraper = TwitterScraper()

    results = scraper.scrape_by_keywords(
        keywords=[
            "frustrated with my CRM",
            "hate using",
            "worst customer service"
        ],
        max_tweets=50,
        since_days=7
    )

    print(f"Found {len(results)} complaint tweets")
