import json
import requests
import base64
import re
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
            elif line.startswith('sdns://'):
                address = cls._extract_address_from_sdns(line)
                if address:
                    current_entry['address'] = address
                    if ':' in address:
                        current_entry['type'] = 'IPv6'
                    else:
                        current_entry['type'] = 'IPv4'
                current_entry['dnscrypt'] = True
            elif line.startswith('* '):
                key_value = line[2:].strip()
                if ': ' in key_value:
                    key, value = key_value.split(': ', 1)
                    current_entry[key.lower()] = value
                    
        if current_entry:
            dns_list.append(current_entry)
            
        return dns_list
    
    @classmethod
    def _extract_address_from_sdns(cls, sdns_line: str) -> str:
        try:
            parts = sdns_line.split()
            if len(parts) >= 2:
                sdns_data = parts[1]
                decoded = base64.b64decode(sdns_data + '=' * (4 - len(sdns_data) % 4))
                decoded_str = decoded.decode('utf-8', errors='ignore')
                
                ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', decoded_str)
                if ip_match:
                    return ip_match.group(1)
                
                ipv6_match = re.search(r'\[([0-9a-fA-F:]+)\]', decoded_str)
                if ipv6_match:
                    return ipv6_match.group(1)
                    
                hostname_match = re.search(r'([a-zA-Z0-9][a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', decoded_str)
                if hostname_match:
                    return hostname_match.group(1)
                    
        except Exception as e:
            print(f"Error extracting address: {e}")
            
        return ''
