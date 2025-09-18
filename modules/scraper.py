import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import urllib3
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Update POLICY_KEYWORDS with more variations
POLICY_KEYWORDS = [
    'privacy', 'terms', 'cookie', 'legal', 'policy',
    'disclaimer', 'notice', 'conditions', 'guidelines',
    'copyright', 'accessibility', 'hyperlink', 'help',
    'website policies', 'terms of use', 'terms of service',
    'tos', 'eula', 'agreement', 'service terms',
    'user agreement', 'community guidelines',
    'privacy-policy', 'terms-of-service', 'terms-and-conditions',
    'legal-notice', 'data-protection', 'data-privacy'
]

def find_policy_links(base_url):
    """Scans a website's homepage to find links to policy pages."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
        
        logger.info(f"Fetching page: {base_url}")
        response = requests.get(base_url, timeout=15, verify=False, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        links = set()
        
        # Look for links in common locations
        for element in soup.find_all(['a', 'link', 'footer', 'nav', 'div']):
            href = element.get('href', '')
            if not href or href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                continue
                
            link_text = element.get_text().lower().strip()
            title = element.get('title', '').lower()
            aria_label = element.get('aria-label', '').lower()
            
            # Check all possible indicators
            text_indicators = [link_text, title, aria_label, href.lower()]
            if any(keyword in indicator for indicator in text_indicators 
                  for keyword in POLICY_KEYWORDS):
                try:
                    full_url = urljoin(base_url, href)
                    if urlparse(full_url).netloc == urlparse(base_url).netloc:
                        links.add(full_url)
                        logger.debug(f"Found policy link: {full_url}")
                except Exception as e:
                    logger.error(f"Error processing URL {href}: {e}")
                    continue
        
        return list(links)
    except Exception as e:
        logger.error(f"Error finding policy links for {base_url}: {e}")
        return []

def get_text_from_url(url, timeout=15):
    """Extracts all readable text content from a given URL."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        
        logger.info(f"Fetching content from: {url}")
        response = requests.get(url, timeout=timeout, verify=False, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'iframe', 'noscript']):
            element.decompose()
        
        # First try to find specific policy content
        content_areas = soup.find_all(['main', 'article', 'div', 'section'], 
            class_=lambda x: x and any(term in str(x).lower() 
            for term in ['content', 'policy', 'terms', 'legal', 'agreement']))
        
        if content_areas:
            logger.debug("Found specific policy content areas")
            text = ' '.join(area.get_text() for area in content_areas)
        else:
            logger.debug("No specific policy content found, using main content")
            # Try to find main content area
            main_content = soup.find(['main', 'article', 'div[role="main"]'])
            text = main_content.get_text() if main_content else soup.get_text()
        
        # Clean up the text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Additional cleanup
        text = ' '.join(text.split())
        
        if not text.strip():
            logger.warning(f"No text content found at {url}")
            return None
            
        logger.info(f"Successfully extracted {len(text)} characters of text")
        return text
        
    except Exception as e:
        logger.error(f"Error fetching text from {url}: {e}")
        return None

def validate_url(url):
    """Validates and normalizes URLs."""
    try:
        result = urlparse(url)
        if not result.scheme:
            url = 'https://' + url
            
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.head(url, 
                               allow_redirects=True, 
                               timeout=10, 
                               verify=False, 
                               headers=headers)
        
        if response.status_code == 200:
            return response.url
        else:
            logger.warning(f"URL returned status code {response.status_code}: {url}")
            return None
            
    except Exception as e:
        logger.error(f"URL validation error for {url}: {e}")
        return None
