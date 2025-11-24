import praw
from datetime import datetime, timedelta
from typing import List, Dict
import os
from loguru import logger

class RedditScraper:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT")
        )

    def _has_complaint_indicators(self, text: str) -> bool:
        """Check if text contains complaint indicators."""
        if not text:
            return False

        text_lower = text.lower()
        complaint_keywords = [
            'hate', 'frustrated', 'annoying', 'terrible',
            'worst', 'awful', 'disappointed', 'wish there was',
            'sucks', 'useless', 'broken', 'doesn\'t work',
            'pain', 'problem', 'issue', 'bug', 'fail'
        ]
        return any(keyword in text_lower for keyword in complaint_keywords)

    def scrape_subreddit_complaints(
        self,
        subreddit: str,
        keywords: List[str],
        limit: int = 100,
        time_filter: str = "week"
    ) -> List[Dict]:
        """
        Scrape Reddit for posts/comments containing complaint keywords.

        Args:
            subreddit: Subreddit name (e.g., 'saas')
            keywords: List of complaint indicators ['frustrated', 'hate', 'wish']
            limit: Max posts to check
            time_filter: 'hour', 'day', 'week', 'month', 'year', 'all'

        Returns:
            List of dicts with post data
        """
        results = []
        sub = self.reddit.subreddit(subreddit)

        # Search for each keyword
        for keyword in keywords:
            try:
                search_results = sub.search(
                    keyword,
                    time_filter=time_filter,
                    limit=limit
                )

                for post in search_results:
                    # Check if negative sentiment indicators
                    content = f"{post.title} {post.selftext}".lower()

                    if any(neg in content for neg in [
                        'hate', 'frustrated', 'annoying', 'terrible',
                        'worst', 'awful', 'disappointed', 'wish there was'
                    ]):
                        results.append({
                            'source': 'reddit',
                            'source_id': post.id,
                            'content': f"{post.title}\n\n{post.selftext}",
                            'author': str(post.author),
                            'url': f"https://reddit.com{post.permalink}",
                            'subreddit': subreddit,
                            'score': post.score,
                            'num_comments': post.num_comments,
                            'created_utc': datetime.fromtimestamp(post.created_utc),
                            'metadata': {
                                'upvote_ratio': post.upvote_ratio,
                                'keyword_matched': keyword
                            }
                        })

                logger.info(f"Found {len(results)} posts for keyword '{keyword}' in r/{subreddit}")

            except Exception as e:
                logger.error(f"Error scraping r/{subreddit} for '{keyword}': {e}")
                continue

        return results

    def scrape_by_sort(
        self,
        subreddit: str,
        sort_type: str = 'hot',
        keywords: List[str] = None,
        limit: int = 100,
        time_filter: str = 'week'
    ) -> List[Dict]:
        """
        Scrape subreddit using different sorting methods.

        Args:
            subreddit: Subreddit name
            sort_type: 'hot', 'new', 'top', 'controversial', 'rising'
            keywords: Optional keywords to filter for (if None, uses complaint detection)
            limit: Max posts to scrape
            time_filter: For 'top' and 'controversial' - 'hour', 'day', 'week', 'month', 'year', 'all'

        Returns:
            List of dicts with post data
        """
        results = []
        sub = self.reddit.subreddit(subreddit)

        try:
            # Get posts based on sort type
            if sort_type == 'hot':
                posts = sub.hot(limit=limit)
            elif sort_type == 'new':
                posts = sub.new(limit=limit)
            elif sort_type == 'top':
                posts = sub.top(limit=limit, time_filter=time_filter)
            elif sort_type == 'controversial':
                posts = sub.controversial(limit=limit, time_filter=time_filter)
            elif sort_type == 'rising':
                posts = sub.rising(limit=limit)
            else:
                logger.error(f"Invalid sort_type: {sort_type}")
                return []

            for post in posts:
                content = f"{post.title} {post.selftext}"

                # Filter by keywords if provided, otherwise use complaint detection
                should_include = False
                matched_keyword = None

                if keywords:
                    content_lower = content.lower()
                    for keyword in keywords:
                        if keyword.lower() in content_lower:
                            should_include = True
                            matched_keyword = keyword
                            break
                else:
                    should_include = self._has_complaint_indicators(content)

                if should_include:
                    results.append({
                        'source': 'reddit',
                        'source_id': post.id,
                        'content': content,
                        'author': str(post.author),
                        'url': f"https://reddit.com{post.permalink}",
                        'subreddit': subreddit,
                        'score': post.score,
                        'num_comments': post.num_comments,
                        'created_utc': datetime.fromtimestamp(post.created_utc),
                        'metadata': {
                            'upvote_ratio': post.upvote_ratio,
                            'sort_type': sort_type,
                            'keyword_matched': matched_keyword
                        }
                    })

            logger.info(f"Scraped {len(results)} posts from r/{subreddit} using sort '{sort_type}'")

        except Exception as e:
            logger.error(f"Error scraping r/{subreddit} with sort '{sort_type}': {e}")

        return results

    def scrape_comments(self, post_id: str, limit: int = 50) -> List[Dict]:
        """Scrape comments from a specific post."""
        try:
            submission = self.reddit.submission(id=post_id)
            submission.comments.replace_more(limit=0)  # Remove MoreComments

            results = []
            for comment in submission.comments.list()[:limit]:
                if hasattr(comment, 'body'):
                    results.append({
                        'source': 'reddit_comment',
                        'source_id': comment.id,
                        'content': comment.body,
                        'author': str(comment.author),
                        'url': f"https://reddit.com{comment.permalink}",
                        'subreddit': submission.subreddit.display_name,
                        'parent_post_id': post_id,
                        'score': comment.score,
                        'created_utc': datetime.fromtimestamp(comment.created_utc)
                    })

            return results

        except Exception as e:
            logger.error(f"Error scraping comments for post {post_id}: {e}")
            return []

    def scrape_post_comments_with_complaints(
        self,
        post_id: str,
        limit: int = 100,
        min_score: int = 1
    ) -> List[Dict]:
        """
        Enhanced comment scraping with pain point detection.

        Args:
            post_id: Reddit post ID
            limit: Max comments to scrape
            min_score: Minimum comment score to include

        Returns:
            List of comments with complaint indicators
        """
        try:
            submission = self.reddit.submission(id=post_id)
            submission.comments.replace_more(limit=0)  # Load all comments

            results = []
            comments_processed = 0

            for comment in submission.comments.list():
                if comments_processed >= limit:
                    break

                if not hasattr(comment, 'body'):
                    continue

                comments_processed += 1

                # Filter for complaints and minimum score
                if comment.score >= min_score and self._has_complaint_indicators(comment.body):
                    results.append({
                        'source': 'reddit_comment',
                        'source_id': comment.id,
                        'content': comment.body,
                        'author': str(comment.author),
                        'url': f"https://reddit.com{comment.permalink}",
                        'subreddit': submission.subreddit.display_name,
                        'parent_post_id': post_id,
                        'parent_post_title': submission.title,
                        'score': comment.score,
                        'created_utc': datetime.fromtimestamp(comment.created_utc),
                        'metadata': {
                            'is_submitter': comment.is_submitter,
                            'depth': comment.depth if hasattr(comment, 'depth') else 0
                        }
                    })

            logger.info(f"Found {len(results)} complaint comments from post {post_id}")
            return results

        except Exception as e:
            logger.error(f"Error scraping comments for post {post_id}: {e}")
            return []

    def scrape_subreddit_with_comments(
        self,
        subreddit: str,
        sort_type: str = 'hot',
        keywords: List[str] = None,
        post_limit: int = 50,
        comments_per_post: int = 100,
        time_filter: str = 'week'
    ) -> Dict[str, List[Dict]]:
        """
        Scrape subreddit posts AND their comments for comprehensive pain point discovery.

        Args:
            subreddit: Subreddit name
            sort_type: Sorting method
            keywords: Optional keywords
            post_limit: Max posts to scrape
            comments_per_post: Max comments per post
            time_filter: Time filter for top/controversial

        Returns:
            Dict with 'posts' and 'comments' lists
        """
        # Get posts
        posts = self.scrape_by_sort(
            subreddit=subreddit,
            sort_type=sort_type,
            keywords=keywords,
            limit=post_limit,
            time_filter=time_filter
        )

        # Get comments from each post
        all_comments = []
        for post in posts[:10]:  # Limit to first 10 posts to avoid rate limits
            post_comments = self.scrape_post_comments_with_complaints(
                post_id=post['source_id'],
                limit=comments_per_post
            )
            all_comments.extend(post_comments)

        logger.info(f"Scraped {len(posts)} posts and {len(all_comments)} complaint comments from r/{subreddit}")

        return {
            'posts': posts,
            'comments': all_comments
        }

    def get_subreddit_metadata(self, subreddit_name: str) -> Dict:
        """
        Get detailed subreddit metadata including flairs and rules.

        Args:
            subreddit_name: Name of the subreddit

        Returns:
            Dict with comprehensive subreddit metadata
        """
        try:
            subreddit = self.reddit.subreddit(subreddit_name)

            # Get link flairs
            flairs = []
            try:
                for flair in subreddit.flair.link_templates:
                    flairs.append({
                        'id': flair.get('id', ''),
                        'text': flair.get('text', ''),
                        'css_class': flair.get('css_class', '')
                    })
            except Exception as e:
                logger.debug(f"Could not fetch flairs for r/{subreddit_name}: {e}")

            # Get subreddit rules
            rules = []
            try:
                for rule in subreddit.rules:
                    rules.append({
                        'short_name': rule.short_name,
                        'description': rule.description if hasattr(rule, 'description') else '',
                        'kind': rule.kind if hasattr(rule, 'kind') else 'all'
                    })
            except Exception as e:
                logger.debug(f"Could not fetch rules for r/{subreddit_name}: {e}")

            # Get basic metadata
            metadata = {
                'name': subreddit.display_name,
                'display_name': subreddit.display_name_prefixed,
                'title': subreddit.title,
                'description': subreddit.public_description,
                'long_description': subreddit.description[:500] if subreddit.description else '',
                'subscribers': subreddit.subscribers or 0,
                'active_users': getattr(subreddit, 'active_user_count', 0) or 0,
                'created_utc': datetime.fromtimestamp(subreddit.created_utc).isoformat(),
                'nsfw': subreddit.over18,
                'url': f"https://reddit.com/r/{subreddit.display_name}",
                'flairs': flairs,
                'rules': rules,
                'submission_type': subreddit.submission_type if hasattr(subreddit, 'submission_type') else 'any',
                'allow_images': subreddit.allow_images if hasattr(subreddit, 'allow_images') else True,
                'allow_videos': subreddit.allow_videos if hasattr(subreddit, 'allow_videos') else True
            }

            logger.info(f"Retrieved metadata for r/{subreddit_name} ({metadata['subscribers']} subscribers, {len(flairs)} flairs, {len(rules)} rules)")
            return metadata

        except Exception as e:
            logger.error(f"Error fetching metadata for r/{subreddit_name}: {e}")
            return {
                'name': subreddit_name,
                'error': str(e)
            }

    def discover_popular_subreddits(self, limit: int = 50) -> List[Dict]:
        """
        Discover popular subreddits from Reddit's popular feed.

        Returns:
            List of dicts with subreddit info
        """
        results = []
        seen_subreddits = set()

        try:
            # Get popular posts to discover active subreddits
            for post in self.reddit.subreddit('all').hot(limit=limit * 3):
                subreddit_name = post.subreddit.display_name

                if subreddit_name not in seen_subreddits:
                    seen_subreddits.add(subreddit_name)

                    try:
                        subreddit = self.reddit.subreddit(subreddit_name)
                        results.append({
                            'name': subreddit_name,
                            'display_name': subreddit.display_name_prefixed,
                            'title': subreddit.title,
                            'description': subreddit.public_description[:200] if subreddit.public_description else '',
                            'subscribers': subreddit.subscribers,
                            'active_users': subreddit.active_user_count or 0,
                            'created_utc': datetime.fromtimestamp(subreddit.created_utc).isoformat(),
                            'nsfw': subreddit.over18,
                            'url': f"https://reddit.com/r/{subreddit_name}"
                        })

                        if len(results) >= limit:
                            break
                    except Exception as e:
                        logger.debug(f"Could not fetch info for r/{subreddit_name}: {e}")
                        continue

            # Sort by subscribers
            results.sort(key=lambda x: x['subscribers'], reverse=True)
            logger.info(f"Discovered {len(results)} popular subreddits")

        except Exception as e:
            logger.error(f"Error discovering popular subreddits: {e}")

        return results

    def discover_subreddits_by_category(self, category: str = 'business') -> List[Dict]:
        """
        Discover subreddits by searching for a category/topic.

        Args:
            category: Category to search for (e.g., 'business', 'saas', 'startup')

        Returns:
            List of subreddit info dicts
        """
        results = []

        try:
            # Search for subreddits matching the category
            for subreddit in self.reddit.subreddits.search(category, limit=30):
                try:
                    results.append({
                        'name': subreddit.display_name,
                        'display_name': subreddit.display_name_prefixed,
                        'title': subreddit.title,
                        'description': subreddit.public_description[:200] if subreddit.public_description else '',
                        'subscribers': subreddit.subscribers,
                        'active_users': subreddit.active_user_count or 0,
                        'created_utc': datetime.fromtimestamp(subreddit.created_utc).isoformat(),
                        'nsfw': subreddit.over18,
                        'url': f"https://reddit.com/r/{subreddit.display_name}",
                        'category': category
                    })
                except Exception as e:
                    logger.debug(f"Could not fetch info for subreddit: {e}")
                    continue

            # Sort by subscribers
            results.sort(key=lambda x: x['subscribers'], reverse=True)
            logger.info(f"Found {len(results)} subreddits for category '{category}'")

        except Exception as e:
            logger.error(f"Error discovering subreddits for category '{category}': {e}")

        return results

    def get_trending_subreddits(self) -> List[Dict]:
        """
        Get currently trending/growing subreddits across multiple categories.

        Returns:
            Curated list of trending subreddits by category
        """
        categories = {
            'SaaS & Startups': ['saas', 'startups', 'entrepreneur', 'SideProject', 'roastmystartup'],
            'Business': ['smallbusiness', 'business', 'Entrepreneur', 'EntrepreneurRideAlong'],
            'Marketing': ['marketing', 'DigitalMarketing', 'socialmedia', 'content_marketing', 'SEO'],
            'Technology': ['webdev', 'programming', 'technology', 'selfhosted', 'homelab'],
            'E-commerce': ['ecommerce', 'shopify', 'FulfillmentByAmazon', 'dropship', 'AmazonSeller'],
            'Freelancing': ['freelance', 'forhire', 'freelanceWriters', 'web_design', 'digitalnomad']
        }

        all_results = []

        for category, subreddit_names in categories.items():
            for sub_name in subreddit_names:
                try:
                    subreddit = self.reddit.subreddit(sub_name)
                    # Try to get active user count, fallback to 0 if not available
                    active_users = getattr(subreddit, 'active_user_count', 0) or 0
                    all_results.append({
                        'name': subreddit.display_name,
                        'display_name': subreddit.display_name_prefixed,
                        'title': subreddit.title,
                        'description': subreddit.public_description[:200] if subreddit.public_description else '',
                        'subscribers': subreddit.subscribers or 0,
                        'active_users': active_users,
                        'nsfw': subreddit.over18,
                        'url': f"https://reddit.com/r/{subreddit.display_name}",
                        'category': category
                    })
                except Exception as e:
                    logger.debug(f"Could not fetch r/{sub_name}: {e}")
                    continue

        # Sort by subscribers (more reliable than active users)
        all_results.sort(key=lambda x: x['subscribers'], reverse=True)
        logger.info(f"Retrieved {len(all_results)} trending subreddits")

        return all_results

# Usage example
if __name__ == "__main__":
    scraper = RedditScraper()

    # Scrape r/saas for complaints
    results = scraper.scrape_subreddit_complaints(
        subreddit="saas",
        keywords=["frustrated", "hate", "worst"],
        limit=100,
        time_filter="week"
    )

    print(f"Found {len(results)} posts with complaints")
