import json
import requests
from typing import List, Dict, Any

class DNSCryptParser:
    SOURCE_URL = "https://raw.githubusercontent.com/DNSCrypt/dnscrypt-resolvers/master/v3/public-resolvers.md"
    SOURCE_NAME = "dnscrypt"
    
    @classmethod
    def fetch(cls) -> List[Dict[str, Any]]:
        try:
            response = requests.get(cls.SOURCE_URL, timeout=30)
            response.raise_for_status()
            content = response.text
            return cls._parse_content(content)
        except Exception as e:
            print(f"Error fetching DNSCrypt data: {e}")
            return []
    
    @classmethod
    def _parse_content(cls, content: str) -> List[Dict[str, Any]]:
        dns_list = []
        current_entry = {}
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('## '):
                if current_entry:
                    dns_list.append(current_entry)
                current_entry = {
                    'name': line[3:].strip(),
                    'source': cls.SOURCE_NAME
                }
            elif line.startswith('* '):
                key_value = line[2:].strip()
                if ': ' in key_value:
                    key, value = key_value.split(': ', 1)
                    current_entry[key.lower()] = value
                elif '@' in key_value:
                    current_entry['address'] = key_value
                    
        if current_entry:
            dns_list.append(current_entry)
            
        return dns_list
