import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import urllib3

# Disable only the single InsecureRequestWarning from urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Keywords to identify policy links
POLICY_KEYWORDS = [
    'privacy', 'terms', 'cookie', 'legal', 'policy',
    'disclaimer', 'notice', 'conditions', 'guidelines',
    'copyright', 'accessibility', 'hyperlink', 'help',
    'website policies', 'terms of use'
]

def find_policy_links(base_url):
    """
    Scans a website's homepage to find links to policy pages.
    """
    try:
        # Disable SSL verification for government sites that might have certificate issues
        response = requests.get(base_url, timeout=10, verify=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        links = set()
        # Look for both <a> tags and footer links (common in govt sites)
        elements = soup.find_all(['a', 'footer'], href=True)
        
        for element in elements:
            href = element.get('href', '')
            # Check if any keyword is in the link text, URL, or title attribute
            link_text = element.get_text().lower()
            title = element.get('title', '').lower()
            
            if any(keyword in link_text or keyword in href.lower() or keyword in title 
                  for keyword in POLICY_KEYWORDS):
                full_url = urljoin(base_url, href)
                if urlparse(full_url).netloc == urlparse(base_url).netloc:
                    links.add(full_url)
        return list(links)
    except requests.RequestException as e:
        print(f"Error finding policy links for {base_url}: {e}")
        return []

def get_text_from_url(url, timeout=10):
    """
    Extracts all readable text content from a given URL.
    """
    try:
        response = requests.get(url, timeout=timeout, verify=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header']):
            element.decompose()
            
        # Look specifically for main content areas
        main_content = soup.find(['main', 'article', 'div[role="main"]'])
        if main_content:
            text = main_content.get_text()
        else:
            text = soup.get_text()
            
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
    except requests.Timeout:
        print(f"Request timed out for {url}")
        return None
    except requests.RequestException as e:
        print(f"Error fetching text from {url}: {e}")
        return None
