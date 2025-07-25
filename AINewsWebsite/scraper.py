#!/usr/bin/env python3
"""
AI News Scraper - Fetches the latest AI news from multiple sources
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time
import random
import logging
from datetime import datetime
from urllib.parse import urljoin, urlparse
import feedparser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ai_news_scraper")

# User agent rotation to avoid being blocked
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
]

def get_random_user_agent():
    """Return a random user agent from the list"""
    return random.choice(USER_AGENTS)

def get_soup(url, headers=None, timeout=10, max_retries=3):
    """
    Fetch a URL and return a BeautifulSoup object
    
    Args:
        url: URL to fetch
        headers: Optional headers to send with the request
        timeout: Request timeout in seconds
        max_retries: Maximum number of retries on failure
        
    Returns:
        BeautifulSoup object or None if failed
    """
    if headers is None:
        headers = {'User-Agent': get_random_user_agent()}
    
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.RequestException as e:
            logger.warning(f"Error fetching {url}: {e}")
            retries += 1
            if retries < max_retries:
                sleep_time = 2 ** retries  # Exponential backoff
                logger.info(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
            else:
                logger.error(f"Failed to fetch {url} after {max_retries} attempts")
                return None

def clean_text(text):
    """Clean up text by removing extra whitespace and normalizing"""
    if not text:
        return ""
    # Replace multiple whitespace with a single space
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespace
    return text.strip()

def is_relevant(title, content, keywords=None):
    """
    Check if an article is relevant to AI news based on keywords
    
    Args:
        title: Article title
        content: Article content
        keywords: List of keywords to check for relevance
        
    Returns:
        Boolean indicating if the article is relevant
    """
    if keywords is None:
        keywords = [
            'ai', 'artificial intelligence', 'machine learning', 'deep learning', 
            'neural network', 'llm', 'large language model', 'gpt', 'chatgpt',
            'openai', 'deepmind', 'anthropic', 'claude', 'gemini', 'mistral',
            'transformer', 'diffusion', 'stable diffusion', 'midjourney',
            'computer vision', 'nlp', 'natural language processing',
            'reinforcement learning', 'generative ai', 'foundation model',
            'multimodal', 'embedding', 'vector database', 'rag',
            'ai safety', 'ai ethics', 'ai regulation', 'ai policy',
            'ai security', 'ai defense', 'ai cybersecurity'
        ]
    
    combined_text = (title + " " + content).lower()
    
    # Check if any keyword is in the combined text
    for keyword in keywords:
        if keyword.lower() in combined_text:
            return True
    
    return False

def categorize_article(title, content):
    """
    Categorize an article as general AI news, defense/security, or tools/innovations
    
    Args:
        title: Article title
        content: Article content
        
    Returns:
        Category string: "general", "defense_security", or "tools_innovations"
    """
    combined_text = (title + " " + content).lower()
    
    # Defense and security keywords
    defense_keywords = [
        'security', 'defense', 'defence', 'military', 'cyber', 'cybersecurity',
        'threat', 'attack', 'vulnerability', 'exploit', 'malware', 'ransomware',
        'phishing', 'hacking', 'privacy', 'surveillance', 'encryption', 'classified',
        'national security', 'intelligence', 'counterintelligence', 'warfare',
        'weapon', 'missile', 'drone', 'uav', 'autonomous weapon', 'darpa',
        'pentagon', 'nato', 'protection', 'safeguard', 'risk', 'threat detection'
    ]
    
    # Tools and innovations keywords
    tools_keywords = [
        'tool', 'innovation', 'breakthrough', 'release', 'launch', 'announce',
        'new model', 'new feature', 'update', 'upgrade', 'version', 'api',
        'library', 'framework', 'platform', 'software', 'hardware', 'chip',
        'processor', 'gpu', 'tpu', 'accelerator', 'infrastructure', 'cloud',
        'edge', 'mobile', 'app', 'application', 'product', 'service', 'solution',
        'startup', 'funding', 'investment', 'acquisition', 'partnership'
    ]
    
    # Check for defense and security keywords
    for keyword in defense_keywords:
        if keyword in combined_text:
            return "defense_security"
    
    # Check for tools and innovations keywords
    for keyword in tools_keywords:
        if keyword in combined_text:
            return "tools_innovations"
    
    # Default to general AI news
    return "general"

class ArticleInfo:
    """Class to store article information"""
    def __init__(self, title, content, url, source, date=None, category=None):
        self.title = clean_text(title)
        self.content = clean_text(content)
        self.url = url
        self.source = source
        self.date = date if date else datetime.now().strftime("%Y-%m-%d")
        
        # Auto-categorize if category not provided
        if category is None:
            self.category = categorize_article(self.title, self.content)
        else:
            self.category = category
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "title": self.title,
            "content": self.content,
            "url": self.url,
            "source": self.source,
            "date": self.date,
            "category": self.category
        }
    
    def __str__(self):
        """String representation of the article"""
        return f"{self.title} - {self.source} ({self.date}) [{self.category}]"

class MITTechnologyReviewScraper:
    """Scraper for MIT Technology Review AI section"""
    
    def __init__(self):
        self.base_url = "https://www.technologyreview.com/topic/artificial-intelligence/"
        self.source_name = "MIT Technology Review"
    
    def scrape_articles(self, limit=5):
        """
        Scrape articles from MIT Technology Review AI section
        
        Args:
            limit: Maximum number of articles to scrape
            
        Returns:
            List of ArticleInfo objects
        """
        logger.info(f"Scraping {self.source_name}...")
        articles = []
        
        try:
            soup = get_soup(self.base_url)
            if not soup:
                return articles
            
            # Find article cards on the main page
            article_cards = soup.select("div.cardGroup__card")
            
            count = 0
            for card in article_cards:
                if count >= limit:
                    break
                
                try:
                    # Extract article URL
                    link_elem = card.select_one("a.cardItem__title")
                    if not link_elem:
                        continue
                    
                    article_url = urljoin(self.base_url, link_elem.get("href"))
                    
                    # Extract title
                    title = link_elem.get_text()
                    
                    # Extract preview content
                    preview = card.select_one("p.cardItem__excerpt")
                    preview_text = preview.get_text() if preview else ""
                    
                    # Get full article content
                    article_soup = get_soup(article_url)
                    if not article_soup:
                        continue
                    
                    # Extract date
                    date_elem = article_soup.select_one("time")
                    date = date_elem.get("datetime").split("T")[0] if date_elem else None
                    
                    # Extract full content
                    content_elems = article_soup.select("div.contentArticle__content p")
                    content = " ".join([p.get_text() for p in content_elems])
                    
                    # Check if article is relevant to AI
                    if not is_relevant(title, content):
                        continue
                    
                    # Create article object
                    article = ArticleInfo(
                        title=title,
                        content=content if content else preview_text,
                        url=article_url,
                        source=self.source_name,
                        date=date
                    )
                    
                    articles.append(article)
                    count += 1
                    logger.info(f"Scraped article: {article.title}")
                    
                    # Be nice to the server
                    time.sleep(random.uniform(1, 3))
                    
                except Exception as e:
                    logger.error(f"Error scraping article: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error scraping {self.source_name}: {e}")
        
        return articles

class DeepMindBlogScraper:
    """Scraper for Google DeepMind blog"""
    
    def __init__(self):
        self.base_url = "https://deepmind.google/discover/blog/"
        self.source_name = "Google DeepMind"
    
    def scrape_articles(self, limit=5):
        """
        Scrape articles from Google DeepMind blog
        
        Args:
            limit: Maximum number of articles to scrape
            
        Returns:
            List of ArticleInfo objects
        """
        logger.info(f"Scraping {self.source_name}...")
        articles = []
        
        try:
            soup = get_soup(self.base_url)
            if not soup:
                return articles
            
            # Find article cards on the main page
            article_cards = soup.select("a.card-link")
            
            count = 0
            for card in article_cards:
                if count >= limit:
                    break
                
                try:
                    # Extract article URL
                    article_url = urljoin(self.base_url, card.get("href"))
                    
                    # Get article page
                    article_soup = get_soup(article_url)
                    if not article_soup:
                        continue
                    
                    # Extract title
                    title_elem = article_soup.select_one("h1")
                    title = title_elem.get_text() if title_elem else ""
                    
                    # Extract date
                    date_elem = article_soup.select_one("time")
                    date = date_elem.get("datetime").split("T")[0] if date_elem else None
                    
                    # Extract content
                    content_elems = article_soup.select("div.rich-text p")
                    content = " ".join([p.get_text() for p in content_elems])
                    
                    # Check if article is relevant to AI
                    if not is_relevant(title, content):
                        continue
                    
                    # Create article object
                    article = ArticleInfo(
                        title=title,
                        content=content,
                        url=article_url,
                        source=self.source_name,
                        date=date
                    )
                    
                    articles.append(article)
                    count += 1
                    logger.info(f"Scraped article: {article.title}")
                    
                    # Be nice to the server
                    time.sleep(random.uniform(1, 3))
                    
                except Exception as e:
                    logger.error(f"Error scraping article: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error scraping {self.source_name}: {e}")
        
        return articles

class OpenAIBlogScraper:
    """Scraper for OpenAI blog"""
    
    def __init__(self):
        self.base_url = "https://openai.com/blog"
        self.source_name = "OpenAI"
    
    def scrape_articles(self, limit=5):
        """
        Scrape articles from OpenAI blog
        
        Args:
            limit: Maximum number of articles to scrape
            
        Returns:
            List of ArticleInfo objects
        """
        logger.info(f"Scraping {self.source_name}...")
        articles = []
        
        try:
            soup = get_soup(self.base_url)
            if not soup:
                return articles
            
            # Find article links on the main page
            article_links = soup.select("a.ui-link")
            
            count = 0
            for link in article_links:
                if count >= limit:
                    break
                
                try:
                    # Extract article URL
                    article_url = urljoin(self.base_url, link.get("href"))
                    
                    # Skip non-blog URLs
                    if "/blog/" not in article_url:
                        continue
                    
                    # Get article page
                    article_soup = get_soup(article_url)
                    if not article_soup:
                        continue
                    
                    # Extract title
                    title_elem = article_soup.select_one("h1")
                    title = title_elem.get_text() if title_elem else ""
                    
                    # Extract date
                    date_elem = article_soup.select_one("time")
                    date = date_elem.get("datetime").split("T")[0] if date_elem else None
                    
                    # Extract content
                    content_elems = article_soup.select("div.post-content p")
                    content = " ".join([p.get_text() for p in content_elems])
                    
                    # Check if article is relevant to AI
                    if not is_relevant(title, content):
                        continue
                    
                    # Create article object
                    article = ArticleInfo(
                        title=title,
                        content=content,
                        url=article_url,
                        source=self.source_name,
                        date=date
                    )
                    
                    articles.append(article)
                    count += 1
                    logger.info(f"Scraped article: {article.title}")
                    
                    # Be nice to the server
                    time.sleep(random.uniform(1, 3))
                    
                except Exception as e:
                    logger.error(f"Error scraping article: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error scraping {self.source_name}: {e}")
        
        return articles

class HuggingFaceBlogScraper:
    """Scraper for Hugging Face blog"""
    
    def __init__(self):
        self.base_url = "https://huggingface.co/blog"
        self.source_name = "Hugging Face"
    
    def scrape_articles(self, limit=5):
        """
        Scrape articles from Hugging Face blog
        
        Args:
            limit: Maximum number of articles to scrape
            
        Returns:
            List of ArticleInfo objects
        """
        logger.info(f"Scraping {self.source_name}...")
        articles = []
        
        try:
            soup = get_soup(self.base_url)
            if not soup:
                return articles
            
            # Find article cards on the main page
            article_cards = soup.select("a.group")
            
            count = 0
            for card in article_cards:
                if count >= limit:
                    break
                
                try:
                    # Extract article URL
                    article_url = urljoin(self.base_url, card.get("href"))
                    
                    # Get article page
                    article_soup = get_soup(article_url)
                    if not article_soup:
                        continue
                    
                    # Extract title
                    title_elem = article_soup.select_one("h1")
                    title = title_elem.get_text() if title_elem else ""
                    
                    # Extract date
                    date_elem = article_soup.select_one("time")
                    date = date_elem.get("datetime").split("T")[0] if date_elem else None
                    
                    # Extract content
                    content_elems = article_soup.select("div.prose p")
                    content = " ".join([p.get_text() for p in content_elems])
                    
                    # Check if article is relevant to AI
                    if not is_relevant(title, content):
                        continue
                    
                    # Create article object
                    article = ArticleInfo(
                        title=title,
                        content=content,
                        url=article_url,
                        source=self.source_name,
                        date=date
                    )
                    
                    articles.append(article)
                    count += 1
                    logger.info(f"Scraped article: {article.title}")
                    
                    # Be nice to the server
                    time.sleep(random.uniform(1, 3))
                    
                except Exception as e:
                    logger.error(f"Error scraping article: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error scraping {self.source_name}: {e}")
        
        return articles

class VentureBeatAIScraper:
    """Scraper for VentureBeat AI section"""
    
    def __init__(self):
        self.base_url = "https://venturebeat.com/category/ai/"
        self.source_name = "VentureBeat"
    
    def scrape_articles(self, limit=5):
        """
        Scrape articles from VentureBeat AI section
        
        Args:
            limit: Maximum number of articles to scrape
            
        Returns:
            List of ArticleInfo objects
        """
        logger.info(f"Scraping {self.source_name}...")
        articles = []
        
        try:
            soup = get_soup(self.base_url)
            if not soup:
                return articles
            
            # Find article cards on the main page
            article_cards = soup.select("article.ArticleListing")
            
            count = 0
            for card in article_cards:
                if count >= limit:
                    break
                
                try:
                    # Extract article URL
                    link_elem = card.select_one("a.ArticleListing__title-link")
                    if not link_elem:
                        continue
                    
                    article_url = link_elem.get("href")
                    
                    # Get article page
                    article_soup = get_soup(article_url)
                    if not article_soup:
                        continue
                    
                    # Extract title
                    title_elem = article_soup.select_one("h1.article-title")
                    title = title_elem.get_text() if title_elem else ""
                    
                    # Extract date
                    date_elem = article_soup.select_one("time")
                    date = date_elem.get("datetime").split("T")[0] if date_elem else None
                    
                    # Extract content
                    content_elems = article_soup.select("div.article-content p")
                    content = " ".join([p.get_text() for p in content_elems])
                    
                    # Check if article is relevant to AI
                    if not is_relevant(title, content):
                        continue
                    
                    # Create article object
                    article = ArticleInfo(
                        title=title,
                        content=content,
                        url=article_url,
                        source=self.source_name,
                        date=date
                    )
                    
                    articles.append(article)
                    count += 1
                    logger.info(f"Scraped article: {article.title}")
                    
                    # Be nice to the server
                    time.sleep(random.uniform(1, 3))
                    
                except Exception as e:
                    logger.error(f"Error scraping article: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error scraping {self.source_name}: {e}")
        
        return articles

class RSSFeedScraper:
    """Generic RSS feed scraper"""
    
    def __init__(self, feed_url, source_name):
        self.feed_url = feed_url
        self.source_name = source_name
    
    def scrape_articles(self, limit=5):
        """
        Scrape articles from an RSS feed
        
        Args:
            limit: Maximum number of articles to scrape
            
        Returns:
            List of ArticleInfo objects
        """
        logger.info(f"Scraping {self.source_name} RSS feed...")
        articles = []
        
        try:
            feed = feedparser.parse(self.feed_url)
            
            count = 0
            for entry in feed.entries:
                if count >= limit:
                    break
                
                try:
                    # Extract article information
                    title = entry.title
                    
                    # Extract content
                    content = ""
                    if 'content' in entry:
                        content = " ".join([c.value for c in entry.content])
                    elif 'summary' in entry:
                        content = entry.summary
                    
                    # Clean HTML from content
                    soup = BeautifulSoup(content, 'html.parser')
                    content = soup.get_text()
                    
                    # Extract URL
                    url = entry.link
                    
                    # Extract date
                    date = None
                    if 'published_parsed' in entry:
                        date_tuple = entry.published_parsed
                        date = time.strftime("%Y-%m-%d", date_tuple)
                    
                    # Check if article is relevant to AI
                    if not is_relevant(title, content):
                        continue
                    
                    # Create article object
                    article = ArticleInfo(
                        title=title,
                        content=content,
                        url=url,
                        source=self.source_name,
                        date=date
                    )
                    
                    articles.append(article)
                    count += 1
                    logger.info(f"Scraped article: {article.title}")
                    
                except Exception as e:
                    logger.error(f"Error scraping RSS entry: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error scraping {self.source_name} RSS feed: {e}")
        
        return articles

def scrape_all_sources(articles_per_source=3):
    """
    Scrape articles from all sources
    
    Args:
        articles_per_source: Number of articles to scrape from each source
        
    Returns:
        Dictionary with articles categorized by type
    """
    all_articles = []
    
    # Initialize scrapers
    scrapers = [
        MITTechnologyReviewScraper(),
        DeepMindBlogScraper(),
        OpenAIBlogScraper(),
        HuggingFaceBlogScraper(),
        VentureBeatAIScraper(),
        RSSFeedScraper("https://www.deeplearning.ai/feed/", "DeepLearning.AI"),
        RSSFeedScraper("https://aiweekly.co/issues.rss", "AI Weekly"),
        RSSFeedScraper("https://thegradient.pub/rss/", "The Gradient"),
        RSSFeedScraper("https://www.topbots.com/feed/", "TopBots"),
        RSSFeedScraper("https://syncedreview.com/feed/", "Synced Review"),
        RSSFeedScraper("https://towardsdatascience.com/feed", "Towards Data Science"),
        RSSFeedScraper("https://www.allenai.org/blog/rss.xml", "Allen AI"),
        RSSFeedScraper("https://spectrum.ieee.org/feeds/topic/artificial-intelligence.rss", "IEEE Spectrum"),
        RSSFeedScraper("https://techcrunch.com/tag/artificial-intelligence/feed/", "TechCrunch")
    ]
    
    # Scrape articles from each source
    for scraper in scrapers:
        articles = scraper.scrape_articles(limit=articles_per_source)
        all_articles.extend(articles)
        
        # Be nice to servers between different sources
        time.sleep(random.uniform(2, 5))
    
    # Categorize articles
    categorized_articles = {
        "general": [],
        "defense_security": [],
        "tools_innovations": []
    }
    
    for article in all_articles:
        categorized_articles[article.category].append(article.to_dict())
    
    return categorized_articles

def save_articles_to_json(articles, filename="ai_news_articles.json"):
    """Save articles to a JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    logger.info(f"Saved {sum(len(v) for v in articles.values())} articles to {filename}")

def generate_markdown_report(articles, filename="daily_ai_news_report.md"):
    """
    Generate a markdown report from the scraped articles
    
    Args:
        articles: Dictionary with articles categorized by type
        filename: Output filename for the markdown report
    """
    today = datetime.now().strftime("%B %d, %Y")
    
    with open(filename, 'w', encoding='utf-8') as f:
        # Write header
        f.write(f"# Daily AI News Report\n\n")
        f.write(f"## Date: {today}\n\n")
        
        # Write general AI news
        f.write(f"### General AI News\n\n")
        for i, article in enumerate(articles["general"], 1):
            f.write(f"{i}. **{article['title']}** - {article['content'][:200]}... (Source: {article['source']}) [Ref{i}]\n\n")
        
        # Write defense and security news
        f.write(f"### AI in Defense and Security\n\n")
        for i, article in enumerate(articles["defense_security"], 1):
            f.write(f"{i}. **{article['title']}** - {article['content'][:200]}... (Source: {article['source']}) [Ref{i+len(articles['general'])}]\n\n")
        
        # Write tools and innovations news
        f.write(f"### Important Tools and Innovations\n\n")
        for i, article in enumerate(articles["tools_innovations"], 1):
            f.write(f"{i}. **{article['title']}** - {article['content'][:200]}... (Source: {article['source']}) [Ref{i+len(articles['general'])+len(articles['defense_security'])}]\n\n")
        
        # Write references
        f.write(f"## References\n\n")
        ref_count = 1
        
        for category in ["general", "defense_security", "tools_innovations"]:
            for article in articles[category]:
                f.write(f"[Ref{ref_count}] {article['url']}\n")
                ref_count += 1
    
    logger.info(f"Generated markdown report: {filename}")

if __name__ == "__main__":
    # Scrape articles from all sources
    articles = scrape_all_sources(articles_per_source=5)
    
    # Save articles to JSON
    save_articles_to_json(articles)
    
    # Generate markdown report
    generate_markdown_report(articles)

