import httpx
import os
from typing import Dict, List
from loguru import logger

class SentimentFilter:
    def __init__(self):
        self.account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
        self.api_token = os.getenv("CLOUDFLARE_API_TOKEN")
        self.model = "@cf/huggingface/distilbert-sst-2-int8"
        self.base_url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/ai/run/{self.model}"

    async def analyze_sentiment(self, text: str) -> Dict:
        """
        Analyze sentiment using Cloudflare AI.

        Returns:
            {
                'label': 'NEGATIVE' | 'POSITIVE',
                'score': 0.0-1.0
            }
        """
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

        data = {"text": text[:1000]}  # Limit to 1000 chars

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.base_url,
                    headers=headers,
                    json=data,
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()

                return result['result'][0]

            except Exception as e:
                logger.error(f"Error analyzing sentiment: {e}")
                # Return neutral sentiment on error
                return {'label': 'NEUTRAL', 'score': 0.5}

    async def filter_negative(self, items: List[Dict]) -> List[Dict]:
        """
        Filter list of items, keeping only negative sentiment.

        Args:
            items: List of dicts with 'content' key

        Returns:
            Filtered list with sentiment_score added
        """
        filtered = []

        for item in items:
            sentiment = await self.analyze_sentiment(item['content'])

            # Keep if negative and high confidence
            if sentiment['label'] == 'NEGATIVE' and sentiment['score'] > 0.7:
                item['sentiment_score'] = -sentiment['score']  # Store as negative value
                item['is_negative'] = True
                filtered.append(item)

        logger.info(f"Filtered {len(items)} items down to {len(filtered)} negative items")
        return filtered

# Usage
if __name__ == "__main__":
    import asyncio

    filter = SentimentFilter()

    test_data = [
        {'content': 'This product is absolutely terrible and waste of money'},
        {'content': 'I love this product, works great!'},
        {'content': 'Frustrated with the slow loading times'}
    ]

    results = asyncio.run(filter.filter_negative(test_data))
    print(f"Filtered to {len(results)} negative items")
