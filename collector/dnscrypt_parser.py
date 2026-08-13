import requests
import base64
import re
import ipaddress
from typing import List, Dict, Any


class DNSCryptParser:
    SOURCE_URL = (
        "https://raw.githubusercontent.com/DNSCrypt/"
        "dnscrypt-resolvers/master/v3/public-resolvers.md"
    )

    SOURCE_NAME = "dnscrypt"

    @classmethod
    def fetch(cls) -> List[Dict[str, Any]]:
        try:
            response = requests.get(
                cls.SOURCE_URL,
                timeout=30,
                headers={
                    "User-Agent": "DNS-Parser/1.0"
                }
            )
            response.raise_for_status()

            return cls._parse_content(response.text)

        except requests.RequestException as e:
            print(f"Error fetching DNSCrypt data: {e}")
            return []

        except Exception as e:
            print(f"Unexpected error: {e}")
            return []

    @classmethod
    def _parse_content(cls, content: str) -> List[Dict[str, Any]]:
        dns_list = []

        # هر رکورد Resolver از ## شروع می‌شود
        blocks = re.split(r"(?=##\s+)", content)

        for block in blocks:
            block = block.strip()

            if not block.startswith("## "):
                continue

            # فقط نام Resolver
            name_match = re.match(
                r"^##\s+([^\s]+)",
                block
            )

            if not name_match:
                continue

            name = name_match.group(1)

            # تمام SDNSهای موجود در رکورد
            sdns_entries = re.findall(
                r"sdns://[A-Za-z0-9_-]+",
                block
            )

            for sdns in sdns_entries:
                endpoint = cls._decode_sdns(sdns)

                if not endpoint:
                    continue

                address, port = endpoint

                dns_list.append({
                    "name": name,
                    "address": address,
                    "port": port,
                    "source": cls.SOURCE_NAME,
                    "type": (
                        "IPv6"
                        if ipaddress.ip_address(address).version == 6
                        else "IPv4"
                    ),
                    "dnscrypt": True
                })

                print(
                    f"Found: {name} -> "
                    f"{address}:{port}"
                )

        print(
            f"Total DNSCrypt entries extracted: "
            f"{len(dns_list)}"
        )

        return dns_list

    @classmethod
    def _decode_sdns(cls, sdns: str):
        try:
            encoded = sdns[len("sdns://"):]

            padding = "=" * (-len(encoded) % 4)

            decoded = base64.urlsafe_b64decode(
                encoded + padding
            )

            text = decoded.decode(
                "utf-8",
                errors="ignore"
            )

            # -------------------------
            # IPv4
            # -------------------------
            ipv4_matches = re.findall(
                r"(?<![\d.])"
                r"(\d{1,3}(?:\.\d{1,3}){3})"
                r"(?::(\d{1,5}))?",
                text
            )

            for ip, port in ipv4_matches:
                try:
                    ipaddress.IPv4Address(ip)

                    return (
                        ip,
                        int(port) if port else None
                    )

                except ValueError:
                    continue

            # -------------------------
            # IPv6 داخل []
            # -------------------------
            ipv6_match = re.search(
                r"\[([0-9a-fA-F:]+)\]"
                r"(?::(\d{1,5}))?",
                text
            )

            if ipv6_match:
                ip = ipv6_match.group(1)
                port = ipv6_match.group(2)

                try:
                    ipaddress.IPv6Address(ip)

                    return (
                        ip,
                        int(port) if port else None
                    )

                except ValueError:
                    pass

            # -------------------------
            # IPv6 بدون []
            # -------------------------
            ipv6_match = re.search(
                r"(?<![0-9a-fA-F:])"
                r"([0-9a-fA-F]{1,4}"
                r"(?:\:[0-9a-fA-F]{1,4}){2,7})"
                r"(?![0-9a-fA-F:])",
                text
            )

            if ipv6_match:
                ip = ipv6_match.group(1)

                try:
                    ipaddress.IPv6Address(ip)

                    return (
                        ip,
                        None
                    )

                except ValueError:
                    pass

        except Exception as e:
            print(f"Error decoding SDNS: {e}")

        return None
