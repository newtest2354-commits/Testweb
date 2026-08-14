import re
import ipaddress
from urllib.parse import urlparse
from typing import List, Dict, Any


class Normalizer:

    @classmethod
    def normalize(
        cls,
        data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        normalized = []

        for entry in data:
            normalized_entry = cls._normalize_entry(entry)

            if normalized_entry:
                normalized.append(normalized_entry)

        return normalized

    @classmethod
    def _normalize_entry(
        cls,
        entry: Dict[str, Any]
    ) -> Dict[str, Any]:

        normalized = {}

        for key, value in entry.items():
            if isinstance(value, str):
                value = value.strip()
                value = re.sub(r"\s+", " ", value)

                key_lower = key.lower()

                if "url" in key_lower:
                    value = cls._normalize_url(value)

                elif key_lower in (
                    "hostname",
                    "name",
                    "provider"
                ):
                    value = value.lower()

                elif key_lower in (
                    "ip",
                    "address",
                    "bootstrap_address"
                ):
                    value = cls._normalize_address(value)

            normalized[key] = value

        cls._normalize_network_fields(normalized)

        if not normalized.get("source"):
            normalized["source"] = "unknown"

        return normalized

    @classmethod
    def _normalize_network_fields(
        cls,
        entry: Dict[str, Any]
    ) -> None:

        doh_url = entry.get("doh_url")

        if doh_url:
            parsed = cls._parse_url(doh_url)

            if parsed:
                hostname = parsed.hostname

                if hostname:
                    entry["hostname"] = (
                        entry.get("hostname")
                        or hostname.lower()
                    )

                    if not entry.get("address"):
                        entry["address"] = hostname

                if parsed.port:
                    entry["port"] = parsed.port
                elif not entry.get("port"):
                    entry["port"] = 443

                if parsed.path:
                    entry["path"] = parsed.path
                elif not entry.get("path"):
                    entry["path"] = "/dns-query"

        hostname = entry.get("hostname")
        address = entry.get("address")

        if not address and hostname:
            entry["address"] = hostname

        if not hostname and address:
            entry["hostname"] = address

        address = entry.get("address")

        if address:
            entry["type"] = cls._detect_type(address)

        protocol = str(
            entry.get("protocol", "")
        ).lower()

        if protocol == "doh":
            entry["protocol"] = "DoH"

        elif protocol == "dot":
            entry["protocol"] = "DoT"

        elif protocol == "doq":
            entry["protocol"] = "DoQ"

        elif protocol == "dnscrypt":
            entry["protocol"] = "DNSCrypt"

    @classmethod
    def _parse_url(cls, url: str):
        try:
            parsed = urlparse(url)

            if parsed.scheme not in (
                "http",
                "https"
            ):
                return None

            if not parsed.hostname:
                return None

            return parsed

        except (ValueError, TypeError):
            return None

    @classmethod
    def _normalize_url(
        cls,
        url: str
    ) -> str:

        parsed = cls._parse_url(url)

        if not parsed:
            return url.rstrip("/")

        scheme = parsed.scheme.lower()
        hostname = parsed.hostname.lower()

        if ":" in hostname:
            host = f"[{hostname}]"
        else:
            host = hostname

        port = parsed.port

        if port:
            default_port = (
                443
                if scheme == "https"
                else 80
            )

            if port != default_port:
                host = f"{host}:{port}"

        path = parsed.path or "/dns-query"

        result = f"{scheme}://{host}{path}"

        if parsed.query:
            result += f"?{parsed.query}"

        return result.rstrip("/")

    @classmethod
    def _normalize_address(
        cls,
        address: str
    ) -> str:

        address = address.strip()

        if not address:
            return address

        if address.startswith("[") and address.endswith("]"):
            address = address[1:-1]

        try:
            ip = ipaddress.ip_address(address)
            return str(ip)
        except ValueError:
            return address.lower()

    @classmethod
    def _detect_type(
        cls,
        address: str
    ) -> str:

        if not address:
            return "Unknown"

        try:
            ip = ipaddress.ip_address(address)

            if ip.version == 4:
                return "IPv4"

            if ip.version == 6:
                return "IPv6"

        except ValueError:
            pass

        return "Hostname"

    @classmethod
    def validate(
        cls,
        data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        validated = []

        for entry in data:
            if cls._is_valid(entry):
                validated.append(entry)

        return validated

    @classmethod
    def _is_valid(
        cls,
        entry: Dict[str, Any]
    ) -> bool:

        if not entry.get("name"):
            return False

        address = entry.get("address")
        hostname = entry.get("hostname")
        doh_url = entry.get("doh_url")

        if not address and not hostname and not doh_url:
            return False

        protocol = str(
            entry.get("protocol", "")
        ).lower()

        if protocol == "doh":
            if not doh_url and not hostname:
                return False

        if protocol == "dot":
            if not entry.get("dot") and not hostname:
                return False

        if protocol == "doq":
            if not entry.get("doq") and not hostname:
                return False

        return True
