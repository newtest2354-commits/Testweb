import re
import ipaddress
from urllib.parse import urlparse
from typing import List, Dict, Any

class Normalizer:
    
    @classmethod
    def normalize(cls, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        normalized = []
        for entry in data:
            normalized_entry = cls._normalize_entry(entry)
            if normalized_entry:
                normalized.append(normalized_entry)
        return normalized
    
    @classmethod
    def _normalize_entry(cls, entry: Dict[str, Any]) -> Dict[str, Any]:
        normalized = {}
        
        for key, value in entry.items():
            if isinstance(value, str):
                value = value.strip()
                value = re.sub(r'\s+', ' ', value)
                
                if 'url' in key.lower() or key == 'doh_url':
                    value = cls._normalize_url(value)
                elif 'hostname' in key.lower() or key == 'name':
                    value = value.lower()
                elif 'ip' in key.lower() or key == 'address':
                    value = cls._normalize_ip(value)
                    
            normalized[key] = value
        
        if 'address' not in normalized or not normalized['address']:
            if 'doh_url' in normalized and normalized['doh_url']:
                parsed = urlparse(normalized['doh_url'])
                hostname = parsed.netloc.split(':')[0]
                normalized['address'] = hostname
            elif 'hostname' in normalized:
                normalized['address'] = normalized['hostname']
                
        if 'source' not in normalized:
            normalized['source'] = 'unknown'
            
        return normalized
    
    @classmethod
    def _normalize_url(cls, url: str) -> str:
        try:
            parsed = urlparse(url)
            normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            if normalized.endswith('/'):
                normalized = normalized[:-1]
            return normalized
        except:
            return url
    
    @classmethod
    def _normalize_ip(cls, ip: str) -> str:
        try:
            ipaddress.ip_address(ip)
            return ip
        except:
            return ip
    
    @classmethod
    def validate(cls, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        validated = []
        for entry in data:
            if cls._is_valid(entry):
                validated.append(entry)
        return validated
    
    @classmethod
    def _is_valid(cls, entry: Dict[str, Any]) -> bool:
        if 'name' not in entry or not entry['name']:
            return False
        if 'address' not in entry and 'doh_url' not in entry:
            return False
        return True
