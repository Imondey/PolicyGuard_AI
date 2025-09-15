import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Keywords to identify policy links
POLICY_KEYWORDS = ['privacy', 'terms', 'cookie', 'legal', 'policy']

def find_policy_links(base_url):
    """
    Scans a website's homepage to find links to policy pages.
    """
    try:
        response = requests.get(base_url, timeout=10)
        response.raise_for_status() # Raise an exception for bad status codes
        soup = BeautifulSoup(response.content, 'html.parser')
        
        links = set()
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            # Check if any keyword is in the link text or the URL itself
            link_text = a_tag.get_text().lower()
            if any(keyword in link_text or keyword in href.lower() for keyword in POLICY_KEYWORDS):
                # Convert relative URLs to absolute URLs
                full_url = urljoin(base_url, href)
                # Ensure the link belongs to the same domain
                if urlparse(full_url).netloc == urlparse(base_url).netloc:
                    links.add(full_url)
        return list(links)
    except requests.RequestException as e:
        print(f"Error finding policy links for {base_url}: {e}")
        return []

def get_text_from_url(url):
    """
    Extracts all readable text content from a given URL.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script_or_style in soup(['script', 'style']):
            script_or_style.decompose()
            
        # Get text and clean it up
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
    except requests.RequestException as e:
        print(f"Error fetching text from {url}: {e}")
        return None
