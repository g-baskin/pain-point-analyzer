from anthropic import Anthropic
import os
import json
from typing import Dict, List
from loguru import logger

class PainPointExtractor:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def extract(self, text: str, source_metadata: Dict = None) -> Dict:
        """
        Extract structured pain point from complaint text.

        Returns:
            {
                'problem_statement': str,
                'category': str,
                'severity': str,
                'context': str,
                'suggested_solution': str,
                'tags': List[str]
            }
        """
        prompt = f"""Analyze this customer complaint and extract the pain point in structured format.

COMPLAINT:
{text}

Extract the following:
1. problem_statement: One clear sentence describing the core problem
2. category: One of [pricing, performance, usability, features, support, reliability, integration, documentation, onboarding, other]
3. severity: One of [critical, high, medium, low]
4. context: Additional context about when/why this is a problem
5. suggested_solution: What would solve this problem
6. tags: 2-5 relevant keywords
7. target_audience: Who experiences this (e.g., "small business owners", "developers")
8. related_industry: What industry/niche (e.g., "SaaS", "e-commerce")

Respond ONLY with valid JSON matching this structure:
{{
    "problem_statement": "...",
    "category": "...",
    "severity": "...",
    "context": "...",
    "suggested_solution": "...",
    "tags": ["...", "..."],
    "target_audience": "...",
    "related_industry": "..."
}}"""

        try:
            message = self.client.messages.create(
                model="claude-3-opus-20240229",  # Using Claude 3 Opus
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse JSON response
            response_text = message.content[0].text

            # Try to extract JSON from response (in case there's extra text)
            try:
                pain_point = json.loads(response_text)
            except json.JSONDecodeError:
                # Try to find JSON in the response
                import re
                json_match = re.search(r'\{[^{}]*\{[^}]*\}[^{}]*\}|\{[^}]*\}', response_text, re.DOTALL)
                if json_match:
                    pain_point = json.loads(json_match.group())
                else:
                    raise ValueError(f"Could not parse JSON from response: {response_text[:100]}")

            # Calculate opportunity score
            pain_point['opportunity_score'] = self._calculate_opportunity(
                pain_point,
                source_metadata
            )

            return pain_point

        except Exception as e:
            logger.error(f"Error extracting pain point: {e}")
            return None

    def _calculate_opportunity(self, pain_point: Dict, metadata: Dict) -> int:
        """Calculate opportunity score 1-100."""
        score = 50  # Base score

        # Severity bonus
        severity_scores = {'critical': 30, 'high': 20, 'medium': 10, 'low': 5}
        score += severity_scores.get(pain_point['severity'], 0)

        # Social proof bonus (if from Reddit/Twitter)
        if metadata:
            score += min(metadata.get('score', 0) // 10, 15)  # Max +15
            score += min(metadata.get('num_comments', 0) // 5, 10)  # Max +10

        return min(score, 100)

    async def batch_extract(self, items: List[Dict]) -> List[Dict]:
        """Extract pain points from multiple items."""
        results = []

        for item in items:
            try:
                pain_point = self.extract(
                    text=item['content'],
                    source_metadata=item.get('metadata', {})
                )
                if pain_point:
                    pain_point['raw_data_id'] = item.get('id')
                    results.append(pain_point)
            except Exception as e:
                logger.error(f"Error extracting from item {item.get('id')}: {e}")
                continue

        logger.info(f"Extracted {len(results)} pain points from {len(items)} items")
        return results

# Usage
if __name__ == "__main__":
    extractor = PainPointExtractor()

    complaint = """
    I'm so frustrated with my project management tool.
    Every time I try to export a report, it takes 5+ minutes to load
    and half the time it crashes. I've complained to support multiple
    times but they just say "we're working on it". This is costing
    me hours every week.
    """

    pain_point = extractor.extract(complaint)
    print(json.dumps(pain_point, indent=2))
