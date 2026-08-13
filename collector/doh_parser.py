import re
import requests
from typing import List, Dict, Any
from urllib.parse import urlparse

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
            content = response.text
            return cls._parse_content(content)
        except Exception as e:
            print(f"Error fetching DoH data: {e}")
            return []
    
    @classmethod
    def _parse_content(cls, content: str) -> List[Dict[str, Any]]:
        dns_list = []
        lines = content.split('\n')
        in_table = False
        
        for line in lines:
            if '| Who runs it | Base URL |' in line:
                in_table = True
                continue
            if in_table and line.startswith('|---'):
                continue
            if in_table and line.strip() and line.startswith('|'):
                parts = [p.strip() for p in line.split('|')[1:-1]]
                if len(parts) >= 2:
                    provider = parts[0]
                    base_url_part = parts[1]
                    
                    urls = re.findall(r'https?://[^\s|<]+', base_url_part)
                    
                    if provider and urls:
                        for url in urls:
                            url = url.rstrip('/')
                            address = urlparse(url).netloc.split(':')[0]
                            dns_list.append({
                                'provider': provider,
                                'doh_url': url,
                                'address': address,
                                'name': provider,
                                'source': cls.SOURCE_NAME,
                                'type': 'DoH',
                                'protocols': ['DoH'],
                                'description': f"DoH server provided by {provider}"
                            })
            elif in_table and not line.strip():
                break
                
        return dns_list
