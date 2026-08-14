import re
import requests
import os
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from urllib.parse import urlparse

class DOHParser:
    SOURCE_NAME = "curl"
    
    @classmethod
    def fetch(cls) -> List[Dict[str, Any]]:
        try:
            source_url = os.environ.get('DOH_SOURCE_URL')
            if not source_url:
                print("ERROR: DOH_SOURCE_URL environment variable not set")
                return []

            response = requests.get(source_url, timeout=30, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            return cls._parse_content(soup)
        except Exception as e:
            print(f"Error fetching DoH data: {e}")
            return []
    
    @classmethod
    def _parse_content(cls, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        dns_list = []
        
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            if len(rows) < 2:
                continue
            
            headers = [h.get_text(strip=True).lower() for h in rows[0].find_all(['th', 'td'])]
            provider_idx = None
            url_idx = None
            
            for i, h in enumerate(headers):
                if 'run' in h or 'who' in h:
                    provider_idx = i
                elif 'base' in h or 'url' in h:
                    url_idx = i
            
            if provider_idx is None or url_idx is None:
                continue
            
            for row in rows[1:]:
                cells = row.find_all(['td', 'th'])
                if len(cells) <= max(provider_idx, url_idx):
                    continue
                
                provider = cells[provider_idx].get_text(strip=True)
                if not provider:
                    continue
                
                url_cell = cells[url_idx]
                urls = []
                for link in url_cell.find_all('a'):
                    href = link.get('href')
                    if href and href.startswith('https://'):
                        urls.append(href.rstrip('/'))
                
                if not urls:
                    text_urls = re.findall(r'https?://[^\s|<"\'\)]+', url_cell.get_text())
                    urls.extend(text_urls)
                
                for url in urls:
                    parsed = urlparse(url)
                    address = parsed.netloc.split(':')[0]
                    dns_list.append({
                        'provider': provider,
                        'doh_url': url,
                        'address': address,
                        'name': provider,
                        'source': cls.SOURCE_NAME,
                        'type': 'DoH',
                        'hostname': parsed.netloc.split(':')[0],
                        'path': parsed.path or '/dns-query',
                        'port': parsed.port or 443,
                        'protocol': 'DoH',
                        'description': f"DoH server provided by {provider}"
                    })
        
        return dns_list
