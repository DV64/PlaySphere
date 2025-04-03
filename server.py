from flask import Flask, jsonify, request, send_file, current_app, session
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from flask_compress import Compress
import requests
from bs4 import BeautifulSoup
import re
import os
import time
import urllib.parse
import logging
import random
import argparse
from requests.adapters import HTTPAdapter
import urllib3
from urllib3.util import Retry
import concurrent.futures
import hashlib
from datetime import datetime, timedelta
import gzip
import functools
from werkzeug.middleware.proxy_fix import ProxyFix
import sys
from translations_ar import TRANSLATIONS as AR_TRANSLATIONS
from translations_en import TRANSLATIONS as EN_TRANSLATIONS

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__, static_folder='assets')
CORS(app, resources={r"/*": {"origins": "*"}})
Compress(app)  # Enable compression

# Configure proxy support
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Configure Flask-Limiter with Redis backend
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"  
)

# Configure Flask-Caching with improved settings
cache_config = {
    "CACHE_TYPE": "null",  # Disable caching
    "CACHE_DEFAULT_TIMEOUT": 7200
}
cache = Cache(app, config=cache_config)

# Configure session with enhanced retry strategy
retry_strategy = Retry(
    total=5,  # زيادة عدد المحاولات
    backoff_factor=0.2,  # تحسين وقت الانتظار بين المحاولات
    status_forcelist=[429, 500, 502, 503, 504, 404, 403],
    allowed_methods=frozenset(['GET', 'POST', 'HEAD', 'PUT', 'DELETE', 'OPTIONS', 'TRACE']),
    raise_on_redirect=False,
    raise_on_status=False
)

# Configure connection pooling with improved settings
adapter = HTTPAdapter(
    max_retries=retry_strategy,
    pool_connections=300,  
    pool_maxsize=300,  
    pool_block=False
)

# Configure global session
http = requests.Session()
http.mount("http://", adapter)
http.mount("https://", adapter)
http.verify = False
http.timeout = 15  # Set timeout to 15 seconds
http.headers.update({
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Connection': 'keep-alive',
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
})

# Enhanced User Agents list with modern browsers
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
]

def get_random_user_agent():
    return random.choice(USER_AGENTS)

def retry_on_failure(retries=3, delay=0.1):
    """Decorator for retrying functions on failure"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if i == retries - 1:
                        raise
                    logger.warning(f"Retry {i+1}/{retries} failed: {str(e)}")
                    time.sleep(delay * (i + 1))
            return None
        return wrapper
    return decorator

@retry_on_failure(retries=3, delay=0.1)
@cache.memoize(timeout=7200)
def get_page_content(url, headers):
    try:
        logger.info(f"Fetching URL: {url}")
        
        # Try normal request first
        try:
            response = http.get(
                url,
                headers=headers,
                timeout=15,
                allow_redirects=True,
                stream=True,
                verify=False
            )
            if response.status_code == 200:
                content = handle_response_content(response)
                return BeautifulSoup(content, 'html.parser')
        except Exception as e:
            logger.warning(f"Normal request failed, trying protection bypass: {str(e)}")
        
        # Try cloudscraper
        try:
            import cloudscraper
            scraper = cloudscraper.create_scraper()
            response = scraper.get(url)
            if response.status_code == 200:
                return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            logger.warning(f"Cloudscraper failed: {str(e)}")
            
        # Try undetected-chromedriver as last resort
        try:
            import undetected_chromedriver as uc
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            options = uc.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            driver = uc.Chrome(options=options)
            driver.get(url)
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            content = driver.page_source
            driver.quit()
            return BeautifulSoup(content, 'html.parser')
            
        except Exception as e:
            logger.error(f"All bypass attempts failed: {str(e)}")
            return None
            
    except Exception as e:
        logger.error(f"Error fetching {url}: {str(e)}")
        return None

def handle_response_content(response):
    """Handle compressed content"""
    try:
        content_encoding = response.headers.get('Content-Encoding', '').lower()
        if 'gzip' in content_encoding:
            try:
                content = gzip.decompress(response.content).decode('utf-8', errors='ignore')
            except Exception:
                content = response.text
        elif 'br' in content_encoding:
            try:
                import brotli
                content = brotli.decompress(response.content).decode('utf-8', errors='ignore')
            except Exception:
                content = response.text
        elif 'deflate' in content_encoding:
            try:
                import zlib
                content = zlib.decompress(response.content).decode('utf-8', errors='ignore')
            except Exception:
                content = response.text
        else:
            content = response.text
        return content
    except Exception as e:
        logger.error(f"Error handling response content: {str(e)}")
        return response.text

def clean_text(text):
    if not text:
        return ""
        
    # Convert text to Unicode if it's not already
    if not isinstance(text, str):
        text = str(text)
    
    # Remove Arabic diacritics
    arabic_diacritics = re.compile("""
        ّ    | # Tashdid
        َ    | # Fatha
        ً    | # Tanwin Fath
        ُ    | # Damma
        ٌ    | # Tanwin Damm
        ِ    | # Kasra
        ٍ    | # Tanwin Kasr
        ْ    | # Sukun
        ـ     # Tatwil/Kashida
    """, re.VERBOSE)
    text = re.sub(arabic_diacritics, '', text)
    
    # Standardize Alef forms
    text = re.sub('[إأآا]', 'ا', text)
    
    # Standardize Yaa and Alef Maksura
    text = re.sub('[يى]', 'ي', text)
    
    # Standardize Taa Marbouta and Haa
    text = re.sub('ة', 'ه', text)
    
    # Remove special characters and numbers
    text = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', text)
    
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Convert text to lowercase (for English words)
    text = text.lower()
    
    return text.strip()

def is_relevant_result(query, title):
    """Check the relevance of search result to the query"""
    query_terms = set(clean_text(query).split())
    title_terms = set(clean_text(title).split())
    
    # Calculate word match ratio
    matching_words = query_terms.intersection(title_terms)
    
    # Calculate match ratio for Arabic and English words
    match_ratio = len(matching_words) / len(query_terms) if query_terms else 0
    
    # Title should contain at least 25% of query words
    # Reduced threshold to improve Arabic language results
    return match_ratio >= 0.25

def fix_image_url(image_url, base_url):
    if not image_url:
        return None
    try:
        # Enhanced URL handling
        image_url = image_url.strip()
        if image_url.startswith('data:'):
            return image_url
        if image_url.startswith('//'):
            return 'https:' + image_url
        if image_url.startswith('/'):
            return urllib.parse.urljoin(base_url, image_url)
        if not image_url.startswith(('http://', 'https://')):
            return urllib.parse.urljoin(base_url, image_url)
        return image_url
    except Exception as e:
        logger.error(f"Error fixing image URL: {str(e)}")
        return None

def generate_cache_key(*args, **kwargs):
    """Generate a unique cache key based on the arguments"""
    key = hashlib.md5(str(args).encode() + str(kwargs).encode()).hexdigest()
    return f"search_{key}"

def search_game_site(query, site):
    headers = {
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ar,en-US;q=0.9,en;q=0.8',  # Add Arabic language support
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0'
    }
    
    # Convert query to URL-safe format with Unicode support
    encoded_query = urllib.parse.quote(query)
    
    results = []
    cache_key = generate_cache_key(query, site)
    
    # Try to retrieve cached results
    cached_results = cache.get(cache_key)
    if cached_results is not None:
        logger.info(f"Returning cached results for {site}")
        return cached_results
    
    try:
        if site == 'fitgirl':
            base_url = 'https://fitgirl-repacks.site'
            for page in range(1, 5):
                if page == 1:
                    url = f'{base_url}/?s={urllib.parse.quote(query)}'
                else:
                    url = f'{base_url}/page/{page}/?s={urllib.parse.quote(query)}'
                
                logger.info(f"Searching FitGirl page {page}: {url}")
                soup = get_page_content(url, headers)
                
                if soup:
                    games = (
                        soup.select('article.post') or 
                        soup.select('article') or 
                        soup.select('.post') or 
                        soup.select('.type-post')
                    )
                    
                    logger.info(f"Found {len(games)} games on FitGirl page {page}")
                    
                    for game in games:
                        try:
                            title_elem = (
                                game.select_one('h1.entry-title a') or 
                                game.select_one('h2.entry-title a') or
                                game.select_one('.entry-title a') or
                                game.select_one('a')
                            )
                            
                            if title_elem:
                                title = clean_text(title_elem.text)
                                url = title_elem.get('href', '')
                                
                                img_elem = (
                                    game.select_one('.entry-content img') or
                                    game.select_one('img') or
                                    game.select_one('a img')
                                )
                                
                                image = img_elem.get('src') if img_elem else None
                                image = fix_image_url(image, base_url)
                                
                                if title and url:
                                    results.append({
                                        'title': title,
                                        'url': url,
                                        'image': image or 'https://via.placeholder.com/120x120',
                                        'source': 'FitGirl Repacks'
                                    })
                        except Exception as e:
                            logger.error(f"Error parsing game from FitGirl: {str(e)}")
                            continue
                
                time.sleep(1)  # Delay between page requests

        elif site == 'gametrex':
            base_url = 'https://gametrex.com'
            url = f'{base_url}/?s={urllib.parse.quote(query)}'
            logger.info(f"Searching GameTrex: {url}")
            soup = get_page_content(url, headers)
            
            if soup:
                games = soup.select('article') or soup.select('.post')
                logger.info(f"Found {len(games)} games on GameTrex")
                
                for game in games:
                    try:
                        title_elem = (
                            game.select_one('h2.entry-title a') or
                            game.select_one('h2 a') or
                            game.select_one('a')
                        )
                        
                        if title_elem:
                            title = clean_text(title_elem.text)
                            url = title_elem.get('href', '')
                            
                            img_elem = game.select_one('img')
                            image = img_elem.get('src') if img_elem else None
                            image = fix_image_url(image, base_url)
                            
                            if title and url:
                                results.append({
                                    'title': title,
                                    'url': url,
                                    'image': image or 'https://via.placeholder.com/120x120',
                                    'source': 'GameTrex'
                                })
                    except Exception as e:
                        logger.error(f"Error parsing game from GameTrex: {str(e)}")
                        continue

        elif site == 'igg':
            base_url = 'https://igg-games.com'
            url = f'{base_url}/search/{urllib.parse.quote(query)}'
            logger.info(f"Searching IGG Games: {url}")
            soup = get_page_content(url, headers)
            
            if soup:
                games = soup.select('.post') or soup.select('article')
                logger.info(f"Found {len(games)} games on IGG Games")
                
                for game in games:
                    try:
                        title_elem = (
                            game.select_one('h2 a') or
                            game.select_one('a')
                        )
                        
                        if title_elem:
                            title = clean_text(title_elem.text)
                            url = title_elem.get('href', '')
                            
                            img_elem = game.select_one('img')
                            image = img_elem.get('src') if img_elem else None
                            image = fix_image_url(image, base_url)
                            
                            if title and url:
                                results.append({
                                    'title': title,
                                    'url': url,
                                    'image': image or 'https://via.placeholder.com/120x120',
                                    'source': 'IGG Games'
                                })
                    except Exception as e:
                        logger.error(f"Error parsing game from IGG Games: {str(e)}")
                        continue

        elif site == 'oceanofgames':
            base_url = 'https://oceanofgames.com'
            url = f'{base_url}/?s={urllib.parse.quote(query)}'
            logger.info(f"Searching Ocean of Games: {url}")
            soup = get_page_content(url, headers)
            
            if soup:
                games = soup.select('article') or soup.select('.post')
                logger.info(f"Found {len(games)} games on Ocean of Games")
                
                for game in games:
                    try:
                        title_elem = (
                            game.select_one('h1 a') or
                            game.select_one('h2 a') or
                            game.select_one('a')
                        )
                        
                        if title_elem:
                            title = clean_text(title_elem.text)
                            url = title_elem.get('href', '')
                            
                            img_elem = game.select_one('img')
                            image = img_elem.get('src') if img_elem else None
                            image = fix_image_url(image, base_url)
                            
                            if title and url:
                                results.append({
                                    'title': title,
                                    'url': url,
                                    'image': image or 'https://via.placeholder.com/120x120',
                                    'source': 'Ocean of Games'
                                })
                    except Exception as e:
                        logger.error(f"Error parsing game from Ocean of Games: {str(e)}")
                        continue

        elif site == 'mechanics':
            base_url = 'https://repack-mechanics.com'
            url = f'{base_url}/?s={urllib.parse.quote(query)}'
            logger.info(f"Searching Mechanics Repacks: {url}")
            soup = get_page_content(url, headers)
            
            if soup:
                games = soup.select('article') or soup.select('.post')
                logger.info(f"Found {len(games)} games on Mechanics Repacks")
                
                for game in games:
                    try:
                        title_elem = (
                            game.select_one('h2 a') or
                            game.select_one('a')
                        )
                        
                        if title_elem:
                            title = clean_text(title_elem.text)
                            url = title_elem.get('href', '')
                            
                            img_elem = game.select_one('img')
                            image = img_elem.get('src') if img_elem else None
                            image = fix_image_url(image, base_url)
                            
                            if title and url:
                                results.append({
                                    'title': title,
                                    'url': url,
                                    'image': image or 'https://via.placeholder.com/120x120',
                                    'source': 'Mechanics Repacks'
                                })
                    except Exception as e:
                        logger.error(f"Error parsing game from Mechanics: {str(e)}")
                        continue

        elif site == 'pcgamestorrents':
            base_url = 'https://pcgamestorrents.org'
            url = f'{base_url}/?s={urllib.parse.quote(query)}'
            logger.info(f"Searching PC Games Torrents: {url}")
            soup = get_page_content(url, headers)
            
            if soup:
                games = soup.select('article') or soup.select('.post')
                logger.info(f"Found {len(games)} games on PC Games Torrents")
                
                for game in games:
                    try:
                        title_elem = (
                            game.select_one('h2 a') or
                            game.select_one('a')
                        )
                        
                        if title_elem:
                            title = clean_text(title_elem.text)
                            url = title_elem.get('href', '')
                            
                            img_elem = game.select_one('img')
                            image = img_elem.get('src') if img_elem else None
                            image = fix_image_url(image, base_url)
                            
                            if title and url:
                                results.append({
                                    'title': title,
                                    'url': url,
                                    'image': image or 'https://via.placeholder.com/120x120',
                                    'source': 'PC Games Torrents'
                                })
                    except Exception as e:
                        logger.error(f"Error parsing game from PC Games Torrents: {str(e)}")
                        continue

        elif site == 'skidrow':
            base_url = 'https://www.skidrowreloaded.com'
            url = f'{base_url}/?s={urllib.parse.quote(query)}'
            logger.info(f"Searching Skidrow Reloaded: {url}")
            soup = get_page_content(url, headers)
            
            if soup:
                games = soup.select('article') or soup.select('.post')
                logger.info(f"Found {len(games)} games on Skidrow Reloaded")
                
                for game in games:
                    try:
                        title_elem = (
                            game.select_one('h2.entry-title a') or
                            game.select_one('h2 a') or
                            game.select_one('a')
                        )
                        
                        if title_elem:
                            title = clean_text(title_elem.text)
                            url = title_elem.get('href', '')
                            
                            img_elem = game.select_one('img')
                            image = img_elem.get('src') if img_elem else None
                            image = fix_image_url(image, base_url)
                            
                            if title and url:
                                results.append({
                                    'title': title,
                                    'url': url,
                                    'image': image or 'https://via.placeholder.com/120x120',
                                    'source': 'Skidrow Reloaded'
                                })
                    except Exception as e:
                        logger.error(f"Error parsing game from Skidrow: {str(e)}")
                        continue

        elif site == 'myabandonware':
            base_url = 'https://www.myabandonware.com'
            url = f'{base_url}/search/q/{urllib.parse.quote(query)}'
            logger.info(f"Searching My Abandonware: {url}")
            soup = get_page_content(url, headers)
            
            if soup:
                games = soup.select('.game') or soup.select('.game-list-item')
                logger.info(f"Found {len(games)} games on My Abandonware")
                
                for game in games:
                    try:
                        title_elem = (
                            game.select_one('h2 a') or
                            game.select_one('h3 a') or
                            game.select_one('a')
                        )
                        
                        if title_elem:
                            title = clean_text(title_elem.text)
                            url = title_elem.get('href', '')
                            
                            img_elem = game.select_one('img')
                            image = img_elem.get('src') if img_elem else None
                            image = fix_image_url(image, base_url)
                            
                            if title and url:
                                results.append({
                                    'title': title,
                                    'url': url,
                                    'image': image or 'https://via.placeholder.com/120x120',
                                    'source': 'My Abandonware'
                                })
                    except Exception as e:
                        logger.error(f"Error parsing game from My Abandonware: {str(e)}")
                        continue

        elif site == 'megagames':
            base_url = 'https://megagames.com'
            url = f'{base_url}/results?titles={urllib.parse.quote(query)}'
            logger.info(f"Searching MegaGames: {url}")
            soup = get_page_content(url, headers)
            
            if soup:
                games = soup.select('.content-item') or soup.select('.search-result')
                logger.info(f"Found {len(games)} games on MegaGames")
                
                for game in games:
                    try:
                        title_elem = (
                            game.select_one('h3 a') or
                            game.select_one('h2 a') or
                            game.select_one('a')
                        )
                        
                        if title_elem:
                            title = clean_text(title_elem.text)
                            url = title_elem.get('href', '')
                            
                            img_elem = game.select_one('img')
                            image = img_elem.get('src') if img_elem else None
                            image = fix_image_url(image, base_url)
                            
                            if title and url:
                                results.append({
                                    'title': title,
                                    'url': url,
                                    'image': image or 'https://via.placeholder.com/120x120',
                                    'source': 'MegaGames'
                                })
                    except Exception as e:
                        logger.error(f"Error parsing game from MegaGames: {str(e)}")
                        continue

        elif site == 'apunkagames':
            base_url = 'https://apunkagames.biz'
            url = f'{base_url}/?s={urllib.parse.quote(query)}'
            logger.info(f"Searching ApunKaGames: {url}")
            soup = get_page_content(url, headers)
            
            if soup:
                games = soup.select('.post') or soup.select('article')
                logger.info(f"Found {len(games)} games on ApunKaGames")
                
                for game in games:
                    try:
                        title_elem = (
                            game.select_one('.post-title a') or
                            game.select_one('h2 a') or
                            game.select_one('a')
                        )
                        
                        if title_elem:
                            title = clean_text(title_elem.text)
                            url = title_elem.get('href', '')
                            
                            img_elem = game.select_one('img')
                            image = img_elem.get('src') if img_elem else None
                            image = fix_image_url(image, base_url)
                            
                            if title and url:
                                results.append({
                                    'title': title,
                                    'url': url,
                                    'image': image or 'https://via.placeholder.com/120x120',
                                    'source': 'ApunKaGames'
                                })
                    except Exception as e:
                        logger.error(f"Error parsing game from ApunKaGames: {str(e)}")
                        continue

        elif site == 'blackbox':
            base_url = 'https://blackboxrepack.com'
            url = f'{base_url}/?s={urllib.parse.quote(query)}'
            logger.info(f"Searching BlackBox Repack: {url}")
            soup = get_page_content(url, headers)
            
            if soup:
                games = soup.select('article') or soup.select('.repack-item')
                logger.info(f"Found {len(games)} games on BlackBox Repack")
                
                for game in games:
                    try:
                        title_elem = (
                            game.select_one('h2.entry-title a') or
                            game.select_one('h2 a') or
                            game.select_one('a')
                        )
                        
                        if title_elem:
                            title = clean_text(title_elem.text)
                            url = title_elem.get('href', '')
                            
                            img_elem = game.select_one('img')
                            image = img_elem.get('src') if img_elem else None
                            image = fix_image_url(image, base_url)
                            
                            if title and url:
                                results.append({
                                    'title': title,
                                    'url': url,
                                    'image': image or 'https://via.placeholder.com/120x120',
                                    'source': 'BlackBox Repack'
                                })
                    except Exception as e:
                        logger.error(f"Error parsing game from BlackBox: {str(e)}")
                        continue

        elif site == 'directforgames':
            base_url = 'https://www.directforgames.com'
            url = f'{base_url}/?s={urllib.parse.quote(query)}'
            logger.info(f"Searching Direct For Games: {url}")
            soup = get_page_content(url, headers)
            
            if soup:
                games = soup.select('article') or soup.select('.post-item') or soup.select('.game-item')
                logger.info(f"Found {len(games)} games on Direct For Games")
                
                for game in games:
                    try:
                        title_elem = (
                            game.select_one('h2 a') or
                            game.select_one('h3 a') or
                            game.select_one('.post-title a') or
                            game.select_one('a')
                        )
                        
                        if title_elem:
                            title = clean_text(title_elem.text)
                            url = title_elem.get('href', '')
                            
                            img_elem = game.select_one('img')
                            image = img_elem.get('src') if img_elem else None
                            image = fix_image_url(image, base_url)
                            
                            if title and url:
                                results.append({
                                    'title': title,
                                    'url': url,
                                    'image': image or 'https://via.placeholder.com/120x120',
                                    'source': 'Direct For Games'
                                })
                    except Exception as e:
                        logger.error(f"Error parsing game from Direct For Games: {str(e)}")
                        continue

        elif site == 'wifi4games':
            base_url = 'https://www.wifi4games.com'
            url = f'{base_url}/search/{urllib.parse.quote(query)}'
            logger.info(f"Searching WIFI4Games: {url}")
            soup = get_page_content(url, headers)
            
            if soup:
                games = soup.select('.game-item') or soup.select('.post') or soup.select('article')
                logger.info(f"Found {len(games)} games on WIFI4Games")
                
                for game in games:
                    try:
                        title_elem = (
                            game.select_one('h2 a') or
                            game.select_one('h3 a') or
                            game.select_one('.game-title a') or
                            game.select_one('a')
                        )
                        
                        if title_elem:
                            title = clean_text(title_elem.text)
                            url = title_elem.get('href', '')
                            
                            img_elem = game.select_one('img')
                            image = img_elem.get('src') if img_elem else None
                            image = fix_image_url(image, base_url)
                            
                            if title and url:
                                results.append({
                                    'title': title,
                                    'url': url,
                                    'image': image or 'https://via.placeholder.com/120x120',
                                    'source': 'WIFI4Games'
                                })
                    except Exception as e:
                        logger.error(f"Error parsing game from WIFI4Games: {str(e)}")
                        continue

        elif site == 'downloadcomputergames':
            base_url = 'https://www.downloadcomputergames.net'
            url = f'{base_url}/?s={urllib.parse.quote(query)}'
            logger.info(f"Searching Download Computer Games: {url}")
            soup = get_page_content(url, headers)
            
            if soup:
                games = soup.select('.posts-container .post-item') or soup.select('.post') or soup.select('article')
                logger.info(f"Found {len(games)} games on Download Computer Games")
                
                for game in games:
                    try:
                        title_elem = (
                            game.select_one('h2 a') or
                            game.select_one('h3 a') or
                            game.select_one('.post-title a') or
                            game.select_one('a')
                        )
                        
                        if title_elem:
                            title = clean_text(title_elem.text)
                            url = title_elem.get('href', '')
                            
                            img_elem = game.select_one('img[src]')
                            image = img_elem['src'] if img_elem else None
                            image = fix_image_url(image, base_url)
                            
                            if title and url:
                                results.append({
                                    'title': title,
                                    'url': url,
                                    'image': image or 'https://via.placeholder.com/120x120',
                                    'source': 'Download Computer Games'
                                })
                    except Exception as e:
                        logger.error(f"Error parsing game from Download Computer Games: {str(e)}")
                        continue

        # Cache the results before returning
        cache.set(cache_key, results)
        return results
        
    except Exception as e:
        logger.error(f"Error searching {site}: {str(e)}")
        return []

# Add language detection and session handling
app.secret_key = os.urandom(24)  # For session handling

def get_user_language():
    """Get user's preferred language from various sources"""
    # Check if language is set in session
    if 'language' in session:
        return session['language']
    
    # Check if language is set in query parameters
    lang = request.args.get('lang')
    if lang in ['ar', 'en']:
        session['language'] = lang
        return lang
    
    # Check Accept-Language header
    accept_languages = request.headers.get('Accept-Language', '')
    if accept_languages:
        # Parse the Accept-Language header
        languages = accept_languages.split(',')
        for language in languages:
            lang_code = language.split(';')[0].strip().lower()
            if 'ar' in lang_code:
                session['language'] = 'ar'
                return 'ar'
            elif 'en' in lang_code:
                session['language'] = 'en'
                return 'en'
    
    # Default to English
    session['language'] = 'en'
    return 'en'

@app.route('/translations')
def get_translations():
    """Get translations based on user's language"""
    lang = request.args.get('lang') or get_user_language()
    if lang == 'ar':
        return jsonify(AR_TRANSLATIONS)
    return jsonify(EN_TRANSLATIONS)

@app.route('/set_language')
def set_language():
    """Set user's preferred language"""
    lang = request.args.get('lang', 'en')
    if lang in ['ar', 'en']:
        session['language'] = lang
        return jsonify({'status': 'success', 'language': lang})
    return jsonify({'status': 'error', 'message': 'Invalid language'}), 400

@app.route('/')
@limiter.limit("60 per minute")
def home():
    return send_file('index.html')

@app.route('/search')
@limiter.limit("30 per minute")
def search():
    start_time = time.time()
    query = request.args.get('q', '').strip()
    sources = request.args.get('sources', '').split(',')
    
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    logger.info(f"Searching for: {query} in sources: {sources}")
    
    # تحديد المواقع المتاحة
    available_sites = {
        'fitgirl': 'fitgirl',
        'gametrex': 'gametrex',
        'igg': 'igg',
        'ocean': 'oceanofgames',
        'mechanics': 'mechanics',
        'pcgames': 'pcgamestorrents',
        'skidrow': 'skidrow',
        'myabandonware': 'myabandonware',
        'megagames': 'megagames',
        'apunkagames': 'apunkagames',
        'blackbox': 'blackbox',
        'directforgames': 'directforgames',
        'wifi4games': 'wifi4games',
        'downloadcomputergames': 'downloadcomputergames'
    }
    
    # تحديد المواقع للبحث
    if not sources or sources[0] == '':
        sites_to_search = list(available_sites.values())
    else:
        sites_to_search = [
            available_sites[source] for source in sources 
            if source in available_sites
        ]
    
    all_results = []
    total_available = 0
    failed_sites = []
    successful_sites = []
    
    # تحسين البحث المتوازي مع زيادة عدد العمال
    max_workers = min(len(sites_to_search) * 3, 30)  # زيادة عدد العمال إلى 30 كحد أقصى
    
    # تحسين إدارة الذاكرة
    chunk_size = 50  # معالجة النتائج في مجموعات
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_site = {
            executor.submit(search_game_site, query, site): site 
            for site in sites_to_search
        }
        
        # تحسين معالجة النتائج المتوازية
        completed_futures = []
        current_chunk = []
        
        try:
            for future in concurrent.futures.as_completed(future_to_site):
                completed_futures.append(future)
                site = future_to_site[future]
                try:
                    results = future.result(timeout=15)
                    if results:
                        # Filter results for relevance
                        relevant_results = [
                            result for result in results 
                            if is_relevant_result(query, result['title'])
                        ]
                        total_available += len(relevant_results)
                        current_chunk.extend(relevant_results)
                        successful_sites.append(site)
                        logger.info(f"Found {len(relevant_results)} relevant results from {site}")
                        
                        # Process results in chunks for better performance
                        if len(current_chunk) >= chunk_size:
                            all_results.extend(sorted(current_chunk, key=lambda x: x['title'].lower()))
                            current_chunk = []
                    else:
                        failed_sites.append(site)
                except Exception as e:
                    logger.error(f"Error processing results from {site}: {str(e)}")
                    failed_sites.append(site)
                    
        except concurrent.futures.TimeoutError:
            logger.warning("Some searches timed out")
        finally:
            # إضافة النتائج المتبقية
            if current_chunk:
                all_results.extend(sorted(current_chunk, key=lambda x: x['title'].lower()))
            
            # إلغاء المهام غير المكتملة
            for future in future_to_site:
                if future not in completed_futures:
                    future.cancel()
    
    # تحسين الفرز والترتيب باستخدام خوارزمية أكثر كفاءة
    all_results = sorted(
        all_results,
        key=lambda x: (x['title'].lower(), x['source']),
        reverse=False
    )
    
    # زيادة عدد النتائج إلى 200
    final_results = all_results[:200] if len(all_results) > 200 else all_results
    
    execution_time = time.time() - start_time
    response = {
        'results': final_results,
        'total_available': total_available,
        'displayed_results': len(final_results),
        'has_more': total_available > len(final_results),
        'execution_time': f"{execution_time:.2f} seconds",
        'sources_searched': sites_to_search,
        'failed_sites': failed_sites,
        'successful_sites': successful_sites,
        'success_rate': f"{(len(successful_sites) / len(sites_to_search)) * 100:.1f}%"
    }
    
    logger.info(f"Search completed in {response['execution_time']}")
    logger.info(f"Total results found: {total_available}")
    logger.info(f"Displayed results: {len(final_results)}")
    logger.info(f"Success rate: {response['success_rate']}")
    
    return jsonify(response)

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify(error="Rate limit exceeded. Please try again later."), 429

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Internal server error: {str(e)}")
    return jsonify(error="An internal server error occurred."), 500

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5000, help='Port to run the server on')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--workers', type=int, default=12, help='Number of worker processes')
    args = parser.parse_args()
    
    app.config['JSON_SORT_KEYS'] = False
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
    app.config['COMPRESS_ALGORITHM'] = ['gzip', 'br', 'deflate']
    app.config['COMPRESS_LEVEL'] = 6
    app.config['COMPRESS_MIN_SIZE'] = 500
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
    
    if not args.debug:
        from waitress import serve
        logger.info(f"Starting production server on port {args.port}")
        serve(
            app,
            host='0.0.0.0',
            port=args.port,
            threads=args.workers,
            url_scheme='http',
            channel_timeout=60,
            cleanup_interval=30,
            max_request_body_size=52428800,
            connection_limit=1000,
            asyncore_use_poll=True,
            outbuf_overflow=1048576,
            inbuf_overflow=1048576
        )
    else:
        app.run(
            host='0.0.0.0',
            port=args.port,
            debug=True,
            threaded=True
        )