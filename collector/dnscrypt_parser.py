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
            
            # چاپ تعداد کل خطوط برای دیباگ
            print(f"Total lines in content: {len(content.splitlines())}")
            
            return cls._parse_content(content)
        except Exception as e:
            print(f"Error fetching DNSCrypt data: {e}")
            return []

    @classmethod
    def _parse_content(cls, content: str) -> List[Dict[str, Any]]:
        dns_list = []
        lines = content.split('\n')
        current_name = None
        sdns_count = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('## '):
                current_name = line[3:].strip()
            elif line.startswith('sdns://'):
                sdns_count += 1
                if current_name:
                    address = cls._extract_address_from_sdns(line)
                    if address:
                        dns_list.append({
                            'name': current_name,
                            'address': address,
                            'source': cls.SOURCE_NAME,
                            'type': 'IPv6' if ':' in address else 'IPv4',
                            'dnscrypt': True
                        })
                        print(f"Found: {current_name} -> {address}")
        
        print(f"Total sdns lines found: {sdns_count}")
        print(f"Total DNSCrypt entries extracted: {len(dns_list)}")
        return dns_list

    @classmethod
    def _extract_address_from_sdns(cls, sdns_line: str) -> str:
        try:
            # چاپ خط برای دیباگ
            print(f"Processing: {sdns_line[:50]}...")
            
            parts = sdns_line.split()
            if len(parts) >= 2:
                sdns_data = parts[1]
                padding = 4 - (len(sdns_data) % 4)
                if padding != 4:
                    sdns_data += '=' * padding
                    
                decoded = base64.b64decode(sdns_data)
                decoded_str = decoded.decode('utf-8', errors='ignore')
                
                print(f"Decoded: {decoded_str[:50]}...")
                
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
            print(f"Error decoding: {e}")
        return ''
