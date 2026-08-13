import re
import requests
from typing import List, Dict, Any

class DOHParser:
    SOURCE_URL = "https://raw.githubusercontent.com/curl/curl/wiki/DNS-over-HTTPS"
    SOURCE_NAME = "curl"
    
    @classmethod
    def fetch(cls) -> List[Dict[str, Any]]:
        try:
            response = requests.get(cls.SOURCE_URL, timeout=30)
            response.raise_for_status()
            content = response.text
            return cls._parse_content(content)
        except Exception as e:
            print(f"Error fetching DoH data: {e}")
            return []
    
    @classmethod
    def _parse_content(cls, content: str) -> List[Dict[str, Any]]:
        dns_list = []
        pattern = r'\|\s*\[([^\]]+)\]\(([^)]+)\)\s*\|\s*([^|]+)\|\s*([^|]+)\|'
        
        matches = re.findall(pattern, content)
        for match in matches:
            name, url, provider, description = match
            dns_list.append({
                'name': name.strip(),
                'doh_url': url.strip(),
                'provider': provider.strip(),
                'description': description.strip(),
                'source': cls.SOURCE_NAME
            })
            
        return dns_list
