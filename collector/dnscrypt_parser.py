import requests
import base64
import re
import ipaddress
import os
from typing import List, Dict, Any, Optional, Tuple

class DNSCryptParser:
    SOURCE_NAME = "dnscrypt"

    @classmethod
    def fetch(cls) -> List[Dict[str, Any]]:
        try:
            source_url = os.environ.get('DNSCRYPT_SOURCE_URL')
            if not source_url:
                print("ERROR: DNSCRYPT_SOURCE_URL environment variable not set")
                return []

            response = requests.get(source_url, timeout=30)
            response.raise_for_status()
            return cls._parse_content(response.text)
        except Exception as e:
            print(f"Error fetching DNSCrypt data: {e}")
            return []

    @classmethod
    def _parse_content(cls, content: str) -> List[Dict[str, Any]]:
        dns_list = []
        blocks = re.split(r"(?=##\s+)", content)
        
        for block in blocks:
            block = block.strip()
            if not block.startswith("## "):
                continue
            
            name_match = re.match(r"^##\s+([^\s]+)", block)
            if not name_match:
                continue
            
            name = name_match.group(1)
            sdns_entries = re.findall(r"sdns://[A-Za-z0-9_-]+", block)
            
            for sdns in sdns_entries:
                result = cls._decode_sdns(sdns)
                if not result:
                    continue
                
                address, port, hostname, path, protocol = result
                
                entry = {
                    "name": name,
                    "address": address or hostname,
                    "source": cls.SOURCE_NAME,
                    "dnscrypt": True,
                    "port": port,
                    "hostname": hostname,
                    "path": path,
                    "protocol": protocol
                }
                
                if address:
                    entry["type"] = "IPv6" if ':' in address else "IPv4"
                elif hostname:
                    entry["type"] = "Hostname"
                
                if protocol == "DoH" and hostname:
                    entry["doh_url"] = f"https://{hostname}{path or '/dns-query'}"
                elif protocol == "DoT" and hostname:
                    entry["dot"] = hostname
                
                dns_list.append(entry)
                print(f"Found: {name} -> {address or hostname}:{port}")
        
        print(f"Total DNSCrypt entries extracted: {len(dns_list)}")
        return dns_list

    @classmethod
    def _decode_sdns(cls, sdns: str) -> Optional[Tuple[str, Optional[int], Optional[str], Optional[str], str]]:
        try:
            encoded = sdns[len("sdns://"):]
            padding = "=" * (-len(encoded) % 4)
            decoded = base64.urlsafe_b64decode(encoded + padding)
            text = decoded.decode("utf-8", errors="ignore")
            
            protocol = "DNSCrypt"
            address = None
            port = None
            hostname = None
            path = "/dns-query"
            
            ipv4_matches = re.findall(r"(?<![\d.])(\d{1,3}(?:\.\d{1,3}){3})(?::(\d{1,5}))?", text)
            for ip, p in ipv4_matches:
                try:
                    ipaddress.IPv4Address(ip)
                    address = ip
                    port = int(p) if p else None
                    if "https://" in text or "doh" in text.lower():
                        protocol = "DoH"
                    return address, port, hostname, path, protocol
                except ValueError:
                    continue
            
            ipv6_match = re.search(r"\[([0-9a-fA-F:]+)\](?::(\d{1,5}))?", text)
            if ipv6_match:
                ip = ipv6_match.group(1)
                try:
                    ipaddress.IPv6Address(ip)
                    address = ip
                    port = int(ipv6_match.group(2)) if ipv6_match.group(2) else None
                    if "https://" in text or "doh" in text.lower():
                        protocol = "DoH"
                    return address, port, hostname, path, protocol
                except ValueError:
                    pass
            
            hostname_match = re.search(r'([a-zA-Z0-9][a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
            if hostname_match:
                hostname = hostname_match.group(1)
                if "https://" in text or "doh" in text.lower():
                    protocol = "DoH"
                elif "dot" in text.lower() or "tls" in text.lower():
                    protocol = "DoT"
                return address, port, hostname, path, protocol
            
        except Exception as e:
            print(f"Error decoding SDNS: {e}")
        
        return None
