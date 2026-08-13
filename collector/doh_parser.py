import re
import requests
from typing import List, Dict, Any
from bs4 import BeautifulSoup

class DOHParser:
    SOURCE_URL = "https://github.com/curl/curl/wiki/DNS-over-HTTPS"
    SOURCE_NAME = "curl"
    
    @classmethod
    def fetch(cls) -> List[Dict[str, Any]]:
        try:
            response = requests.get(cls.SOURCE_URL, timeout=30, headers={
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
        
        table = soup.find('table')
        if not table:
            return dns_list
            
        rows = table.find_all('tr')
        if len(rows) < 2:
            return dns_list
            
        for row in rows[1:]:
            cells = row.find_all('td')
            if len(cells) >= 2:
                provider = cells[0].get_text(strip=True)
                base_url_cell = cells[1]
                
                urls = []
                for link in base_url_cell.find_all('a'):
                    href = link.get('href')
                    if href and href.startswith('https://'):
                        urls.append(href.rstrip('/'))
                
                if provider and urls:
                    for url in urls:
                        dns_list.append({
                            'provider': provider,
                            'doh_url': url,
                            'name': provider,
                            'source': cls.SOURCE_NAME,
                            'description': f"DoH server provided by {provider}"
                        })
        
        return dns_list
