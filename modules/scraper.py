import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import urllib3

# Disable only the single InsecureRequestWarning from urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Update POLICY_KEYWORDS
POLICY_KEYWORDS = [
    'privacy', 'terms', 'cookie', 'legal', 'policy',
    'disclaimer', 'notice', 'conditions', 'guidelines',
    'copyright', 'accessibility', 'hyperlink', 'help',
    'website policies', 'terms of use', 'terms of service',
    'tos', 'eula', 'agreement', 'service terms',
    'user agreement', 'community guidelines'
]

def find_policy_links(base_url):
    """
    Scans a website's homepage to find links to policy pages.
    """
    try:
        # Add user agent to avoid being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(base_url, timeout=15, verify=False, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        links = set()
        # Look for links in common locations
        for element in soup.find_all(['a', 'link', 'footer', 'nav']):
            href = element.get('href', '')
            if not href:
                continue
                
            link_text = element.get_text().lower()
            title = element.get('title', '').lower()
            
            if any(keyword in link_text or keyword in href.lower() or keyword in title 
                  for keyword in POLICY_KEYWORDS):
                try:
                    full_url = urljoin(base_url, href)
                    # Only include links from same domain
                    if urlparse(full_url).netloc == urlparse(base_url).netloc:
                        links.add(full_url)
                except Exception as e:
                    print(f"Error processing URL {href}: {e}")
                    continue
                    
        return list(links)
    except Exception as e:
        print(f"Error finding policy links for {base_url}: {e}")
        return []

def get_text_from_url(url, timeout=15):
    """
    Extracts all readable text content from a given URL.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, timeout=timeout, verify=False, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'iframe']):
            element.decompose()
            
        # Look for content in common policy page containers
        content_areas = soup.find_all(['main', 'article', 'div'], 
                                    class_=lambda x: x and any(term in str(x).lower() 
                                    for term in ['content', 'policy', 'terms', 'legal']))
        
        if content_areas:
            text = ' '.join(area.get_text() for area in content_areas)
        else:
            text = soup.get_text()
        
        # Clean up the text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        return text if text.strip() else None
    except Exception as e:
        print(f"Error fetching text from {url}: {e}")
        return None
