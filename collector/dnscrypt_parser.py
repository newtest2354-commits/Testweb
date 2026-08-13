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
        lines = content.split('\n')
        current_name = None
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            if line.startswith('## '):
                current_name = line[3:].strip()
                i += 1
                while i < len(lines):
                    next_line = lines[i].strip()
                    if next_line.startswith('sdns://'):
                        address = cls._extract_address_from_sdns(next_line)
                        if address:
                            dns_list.append({
                                'name': current_name,
                                'address': address,
                                'source': cls.SOURCE_NAME,
                                'type': 'IPv6' if ':' in address else 'IPv4',
                                'dnscrypt': True
                            })
                            print(f"Found: {current_name} -> {address}")
                    elif next_line.startswith('## '):
                        break
                    i += 1
            i += 1

        return dns_list

    @classmethod
    def _extract_address_from_sdns(cls, sdns_line: str) -> str:
        try:
            parts = sdns_line.split()
            if len(parts) >= 2:
                sdns_data = parts[1]
                padding = 4 - (len(sdns_data) % 4)
                if padding != 4:
                    sdns_data += '=' * padding
                    
                decoded = base64.b64decode(sdns_data)
                decoded_str = decoded.decode('utf-8', errors='ignore')
                
                ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', decoded_str)
                if ip_match:
                    return ip_match.group(1)
                
                ipv6_match = re.search(r'\[([0-9a-fA-F:]+)\]', decoded_str)
                if ipv6_match:
                    return ipv6_match.group(1)
        except Exception as e:
            print(f"Error decoding: {e}")
        return ''
