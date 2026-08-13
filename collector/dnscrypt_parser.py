import requests
from typing import List, Dict, Any
import dns.dnscrypt  # کتابخانه جدید برای پردازش استاندارد Stamp

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
            # استخراج بخش stamp از خط
            stamp_str = sdns_line.split('sdns://')[1].strip()
            # استفاده از کتابخانه dnspython برای decode کردن stamp
            stamp = dns.dnscrypt.DNSCryptStamp.from_text(stamp_str)
            
            # استخراج آدرس و پورت از stamp
            if stamp.address:
                # اگر آدرس یک IPv6 است، آن را درون کروشه قرار می‌دهیم تا استاندارد شود
                if ':' in stamp.address:
                    return f"[{stamp.address}]"
                return stamp.address
        except Exception as e:
            print(f"Error decoding stamp from line '{sdns_line}': {e}")

        return ''
