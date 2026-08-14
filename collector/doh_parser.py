import re
import requests
import os
import ipaddress
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from urllib.parse import urlparse


class DOHParser:
    SOURCE_NAME = "curl"
    DEFAULT_DOT_PORT = 853

    URL_PATTERN = re.compile(
        r'https?://[^\s<>"\'\)\]\}]+',
        re.IGNORECASE
    )

    DOT_URL_PATTERN = re.compile(
        r'\btls://'
        r'(?P<host>'
        r'\[[0-9a-fA-F:]+\]'
        r'|'
        r'[a-zA-Z0-9]'
        r'(?:[a-zA-Z0-9.-]*[a-zA-Z0-9])?'
        r')'
        r'(?::(?P<port>\d{1,5}))?',
        re.IGNORECASE
    )

    DOT_HOST_PORT_PATTERN = re.compile(
        r'(?<![A-Za-z0-9._/-])'
        r'(?P<host>'
        r'\[[0-9a-fA-F:]+\]'
        r'|'
        r'(?:[a-zA-Z0-9]'
        r'(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?'
        r'\.)+'
        r'[a-zA-Z]{2,63}'
        r'|'
        r'(?:\d{1,3}\.){3}\d{1,3}'
        r')'
        r':(?P<port>\d{1,5})'
        r'(?!\d)',
        re.IGNORECASE
    )

    DOT_853_PATTERN = re.compile(
        r'(?<![A-Za-z0-9._/-])'
        r'(?P<host>'
        r'\[[0-9a-fA-F:]+\]'
        r'|'
        r'(?:[a-zA-Z0-9]'
        r'(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?'
        r'\.)+'
        r'[a-zA-Z]{2,63}'
        r'|'
        r'(?:\d{1,3}\.){3}\d{1,3}'
        r')'
        r':853'
        r'(?!\d)',
        re.IGNORECASE
    )

    DOT_LABEL_PATTERN = re.compile(
        r'(?:'
        r'\bdns\s*[- ]?\s*over\s*tls\b'
        r'|'
        r'\bdns\s*over\s*transport\s*layer\s*security\b'
        r'|'
        r'\bsupports?\s+dot\b'
        r'|'
        r'\bdot\s+support\b'
        r'|'
        r'\bdot\b'
        r')',
        re.IGNORECASE
    )

    DOT_LABELED_HOST_PATTERN = re.compile(
        r'(?:'
        r'\bdns\s*[- ]?\s*over\s*tls\b'
        r'|'
        r'\bdot\b'
        r')'
        r'\s*'
        r'(?:'
        r'endpoint'
        r'|server'
        r'|resolver'
        r'|address'
        r')?'
        r'\s*[:=\-]?\s*'
        r'(?P<host>'
        r'\[[0-9a-fA-F:]+\]'
        r'|'
        r'(?:[a-zA-Z0-9]'
        r'(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?'
        r'\.)+'
        r'[a-zA-Z]{2,63}'
        r'|'
        r'(?:\d{1,3}\.){3}\d{1,3}'
        r')'
        r'(?::(?P<port>\d{1,5}))?',
        re.IGNORECASE
    )

    DNS_PATHS = (
        "/dns-query",
        "/resolve",
        "/doh",
        "/query",
    )

    DNS_HOSTS = (
        "dns.google",
        "cloudflare-dns.com",
        "cloudflare-dns.net",
        "adguard-dns.com",
        "adguard.com",
        "nextdns.io",
        "quad9.net",
        "quad9.org",
    )

    PROVIDER_PATTERNS = (
        "run by",
        "who runs",
        "operator",
        "provider",
        "company",
        "organization",
        "organisation",
        "operated by",
    )

    @classmethod
    def fetch(cls) -> List[Dict[str, Any]]:
        try:
            source_url = os.environ.get("DOH_SOURCE_URL")

            if not source_url:
                print(
                    "ERROR: DOH_SOURCE_URL environment variable not set"
                )
                return []

            response = requests.get(
                source_url,
                timeout=30,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 "
                        "(KHTML, like Gecko) "
                        "Chrome/120.0 Safari/537.36"
                    )
                }
            )

            response.raise_for_status()

            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )

            dns_list = cls._parse_content(soup)

            doh_count = sum(
                1
                for entry in dns_list
                if entry.get("protocol") == "DoH"
            )

            dot_count = sum(
                1
                for entry in dns_list
                if entry.get("protocol") == "DoT"
            )

            print(
                f"Total DoH/DoT entries extracted: "
                f"{len(dns_list)} "
                f"(DoH: {doh_count}, DoT: {dot_count})"
            )

            return dns_list

        except requests.RequestException as e:
            print(f"Error fetching DoH/DoT data: {e}")
            return []

        except Exception as e:
            print(f"Unexpected parser error: {e}")
            return []

    @classmethod
    def _parse_content(
        cls,
        soup: BeautifulSoup
    ) -> List[Dict[str, Any]]:
        dns_list = []
        seen_doh = set()
        seen_dot = set()

        def add_entry(entry):
            if not entry:
                return

            protocol = entry.get("protocol")

            if protocol == "DoH":
                key = cls._doh_key(entry)

                if key in seen_doh:
                    return

                seen_doh.add(key)
                dns_list.append(entry)

            elif protocol == "DoT":
                key = cls._dot_key(entry)

                if key in seen_dot:
                    return

                seen_dot.add(key)
                dns_list.append(entry)

        for table in soup.find_all("table"):
            rows = table.find_all("tr")

            if not rows:
                continue

            headers = cls._extract_headers(rows[0])

            provider_idx = cls._find_provider_column(headers)
            url_idx = cls._find_url_column(headers)

            for row in rows[1:]:
                cells = row.find_all(
                    ["td", "th"]
                )

                if not cells:
                    continue

                row_text = cls._clean_text(
                    row.get_text(" ", strip=True)
                )

                provider = cls._extract_provider_from_row(
                    row,
                    cells,
                    provider_idx,
                    url_idx
                )

                urls = []

                for cell in cls._get_url_cells(
                    cells,
                    url_idx
                ):
                    urls.extend(
                        cls._extract_urls(cell)
                    )

                if not urls:
                    urls = cls._extract_urls(row)

                for url in urls:
                    if not cls._is_dns_url(url):
                        continue

                    add_entry(
                        cls._build_entry(
                            url,
                            provider
                        )
                    )

                for dot_entry in cls._extract_dot_entries(
                    row,
                    row_text,
                    provider,
                    urls
                ):
                    add_entry(dot_entry)

        for element in cls._get_generic_containers(soup):
            text = cls._clean_text(
                element.get_text(
                    " ",
                    strip=True
                )
            )

            if not text:
                continue

            provider = cls._extract_provider_from_element(
                element
            )

            urls = cls._extract_urls(element)

            for url in urls:
                if not cls._is_dns_url(url):
                    continue

                add_entry(
                    cls._build_entry(
                        url,
                        provider
                    )
                )

            for dot_entry in cls._extract_dot_entries(
                element,
                text,
                provider,
                urls
            ):
                add_entry(dot_entry)

        if dns_list:
            return dns_list

        return cls._parse_fallback(soup)

    @classmethod
    def _get_generic_containers(
        cls,
        soup: BeautifulSoup
    ) -> List[Any]:
        containers = []

        for element in soup.find_all(
            ["article", "li", "section", "div"]
        ):
            if element.find_parent("table"):
                continue

            text = cls._clean_text(
                element.get_text(
                    " ",
                    strip=True
                )
            )

            if not text:
                continue

            has_dns_signal = (
                cls._contains_url(text)
                or cls._contains_dot_endpoint(text)
                or cls._supports_dot(text)
                or "dns" in text.lower()
            )

            if not has_dns_signal:
                continue

            containers.append(element)

        return containers

    @classmethod
    def _extract_provider_from_element(
        cls,
        element
    ) -> str:
        text = cls._clean_text(
            element.get_text(
                " ",
                strip=True
            )
        )

        if not text:
            return "Unknown"

        provider = cls._clean_provider(
            text
        )

        provider = re.sub(
            r'\b(?:standard|adblock|family|security|malware|adult|'
            r'unfiltered|free|shekan|private|ipv4|ipv6|doh|dot|'
            r'dns)\b',
            ' ',
            provider,
            flags=re.IGNORECASE
        )

        provider = re.sub(
            r'\s+',
            ' ',
            provider
        ).strip()

        if len(provider) > 100:
            return "Unknown"

        if not provider:
            return "Unknown"

        return provider

    @classmethod
    def _extract_headers(
        cls,
        row
    ) -> List[str]:
        return [
            cls._clean_text(
                cell.get_text(
                    " ",
                    strip=True
                ).lower()
            )
            for cell in row.find_all(
                ["th", "td"]
            )
        ]

    @classmethod
    def _find_provider_column(
        cls,
        headers: List[str]
    ) -> Optional[int]:
        for index, header in enumerate(headers):
            if any(
                pattern in header
                for pattern in cls.PROVIDER_PATTERNS
            ):
                return index

        return None

    @classmethod
    def _find_url_column(
        cls,
        headers: List[str]
    ) -> Optional[int]:
        patterns = (
            "base url",
            "url",
            "endpoint",
            "server",
            "resolver",
            "dns endpoint",
            "doh",
            "dns over https",
        )

        for index, header in enumerate(headers):
            if any(
                pattern in header
                for pattern in patterns
            ):
                return index

        return None

    @classmethod
    def _get_url_cells(
        cls,
        cells,
        url_idx: Optional[int]
    ) -> List[Any]:
        if (
            url_idx is not None
            and url_idx < len(cells)
        ):
            return [cells[url_idx]]

        candidates = []

        for cell in cells:
            text = cell.get_text(
                " ",
                strip=True
            )

            if (
                cell.find("a", href=True)
                or cls._contains_url(text)
                or cls._contains_dot_endpoint(text)
            ):
                candidates.append(cell)

        return candidates or cells

    @classmethod
    def _extract_provider_from_row(
        cls,
        row,
        cells,
        provider_idx: Optional[int],
        url_idx: Optional[int]
    ) -> str:
        if (
            provider_idx is not None
            and provider_idx < len(cells)
        ):
            provider = cells[
                provider_idx
            ].get_text(
                " ",
                strip=True
            )

            if provider:
                return cls._clean_provider(
                    provider
                )

        candidates = []

        for index, cell in enumerate(cells):
            if (
                url_idx is not None
                and index == url_idx
            ):
                continue

            text = cell.get_text(
                " ",
                strip=True
            )

            if not text:
                continue

            if cls._contains_url(text):
                continue

            if cls._contains_dot_endpoint(text):
                continue

            if len(text) > 200:
                continue

            if re.fullmatch(
                r'(?:standard|adblock|family|security|malware|adult|'
                r'unfiltered|free|shekan|private|ipv4|ipv6|doh|dot|'
                r'dns|active|copy)+',
                re.sub(r'\s+', '', text),
                re.IGNORECASE
            ):
                continue

            candidates.append(text)

        if candidates:
            return cls._clean_provider(
                candidates[0]
            )

        return "Unknown"

    @classmethod
    def _extract_urls(
        cls,
        element
    ) -> List[str]:
        urls = []

        for link in element.find_all(
            "a",
            href=True
        ):
            href = link.get(
                "href",
                ""
            ).strip()

            if cls._is_http_url(href):
                urls.append(href)

        text = element.get_text(
            " ",
            strip=True
        )

        urls.extend(
            cls.URL_PATTERN.findall(text)
        )

        result = []

        for url in urls:
            url = cls._clean_url(url)

            if (
                url
                and cls._is_http_url(url)
            ):
                result.append(url)

        return list(
            dict.fromkeys(result)
        )

    @classmethod
    def _extract_dot_entries(
        cls,
        row,
        row_text: str,
        provider: str,
        doh_urls: List[str]
    ) -> List[Dict[str, Any]]:
        candidates = []

        for link in row.find_all(
            "a",
            href=True
        ):
            href = link.get(
                "href",
                ""
            ).strip()

            if href.lower().startswith("tls://"):
                endpoint = cls._parse_dot_endpoint(
                    href
                )

                if endpoint:
                    candidates.append(
                        (
                            endpoint,
                            False
                        )
                    )

        for match in cls.DOT_URL_PATTERN.finditer(
            row_text
        ):
            host = match.group("host")
            port = match.group("port")

            endpoint = cls._make_dot_endpoint(
                host,
                int(port)
                if port
                else cls.DEFAULT_DOT_PORT
            )

            if endpoint:
                candidates.append(
                    (
                        endpoint,
                        False
                    )
                )

        for match in cls.DOT_853_PATTERN.finditer(
            row_text
        ):
            host = match.group("host")

            endpoint = cls._make_dot_endpoint(
                host,
                cls.DEFAULT_DOT_PORT
            )

            if endpoint:
                candidates.append(
                    (
                        endpoint,
                        False
                    )
                )

        for match in cls.DOT_HOST_PORT_PATTERN.finditer(
            row_text
        ):
            host = match.group("host")
            port = int(
                match.group("port")
            )

            endpoint = cls._make_dot_endpoint(
                host,
                port
            )

            if endpoint:
                candidates.append(
                    (
                        endpoint,
                        False
                    )
                )

        labeled_hosts = cls._extract_labeled_dot_hosts(
            row_text
        )

        for host, port in labeled_hosts:
            endpoint = cls._make_dot_endpoint(
                host,
                port
            )

            if endpoint:
                candidates.append(
                    (
                        endpoint,
                        False
                    )
                )

        if (
            not candidates
            and cls._supports_dot(row_text)
        ):
            for doh_url in doh_urls:
                hostname = cls._extract_hostname(
                    doh_url
                )

                if not hostname:
                    continue

                endpoint = cls._make_dot_endpoint(
                    hostname,
                    cls.DEFAULT_DOT_PORT
                )

                if endpoint:
                    candidates.append(
                        (
                            endpoint,
                            True
                        )
                    )

        result = []
        local_seen = set()

        for endpoint, inferred in candidates:
            entry = cls._build_dot_entry(
                endpoint,
                provider,
                inferred=inferred
            )

            if not entry:
                continue

            key = cls._dot_key(entry)

            if key in local_seen:
                continue

            local_seen.add(key)
            result.append(entry)

        return result

    @classmethod
    def _extract_labeled_dot_hosts(
        cls,
        text: str
    ) -> List[tuple]:
        hosts = []

        for match in cls.DOT_LABELED_HOST_PATTERN.finditer(
            text
        ):
            host = match.group("host")
            port = match.group("port")

            if not host:
                continue

            hosts.append(
                (
                    host,
                    int(port)
                    if port
                    else cls.DEFAULT_DOT_PORT
                )
            )

        return list(
            dict.fromkeys(hosts)
        )

    @classmethod
    def _parse_dot_endpoint(
        cls,
        endpoint: str
    ) -> Optional[str]:
        try:
            parsed = urlparse(endpoint)

            if parsed.scheme.lower() != "tls":
                return None

            if not parsed.hostname:
                return None

            hostname = parsed.hostname

            port = (
                parsed.port
                or cls.DEFAULT_DOT_PORT
            )

            return cls._make_dot_endpoint(
                hostname,
                port
            )

        except (
            ValueError,
            TypeError
        ):
            return None

    @classmethod
    def _make_dot_endpoint(
        cls,
        host: str,
        port: int = DEFAULT_DOT_PORT
    ) -> Optional[str]:
        host = str(host).strip()

        if not host:
            return None

        if (
            host.startswith("[")
            and host.endswith("]")
        ):
            host = host[1:-1]

        try:
            ip = ipaddress.ip_address(host)

            if ip.version == 6:
                host = f"[{host}]"

        except ValueError:
            if not re.match(
                r"^(?=.{1,253}$)"
                r"[a-zA-Z0-9]"
                r"(?:[a-zA-Z0-9.-]*"
                r"[a-zA-Z0-9])?$",
                host
            ):
                return None

            labels = host.split(".")

            if any(
                not label
                or len(label) > 63
                or label.startswith("-")
                or label.endswith("-")
                for label in labels
            ):
                return None

        try:
            port = int(port)

        except (
            ValueError,
            TypeError
        ):
            return None

        if not 1 <= port <= 65535:
            return None

        return f"{host}:{port}"

    @classmethod
    def _build_dot_entry(
        cls,
        endpoint: str,
        provider: str,
        inferred: bool = False
    ) -> Dict[str, Any]:
        try:
            if not endpoint:
                return {}

            if endpoint.lower().startswith(
                "tls://"
            ):
                endpoint = endpoint[6:]

            endpoint = endpoint.strip().rstrip("/")

            hostname = ""
            port = cls.DEFAULT_DOT_PORT

            if endpoint.startswith("["):
                match = re.match(
                    r"^\[([0-9a-fA-F:]+)\]"
                    r"(?::(\d+))?$",
                    endpoint
                )

                if not match:
                    return {}

                hostname = match.group(1)

                port = int(
                    match.group(2)
                    or cls.DEFAULT_DOT_PORT
                )

            else:
                if ":" in endpoint:
                    host_part, port_part = endpoint.rsplit(
                        ":",
                        1
                    )

                    if port_part.isdigit():
                        hostname = host_part
                        port = int(port_part)
                    else:
                        hostname = endpoint
                else:
                    hostname = endpoint

            hostname = hostname.strip().lower()

            if not hostname:
                return {}

            if not 1 <= port <= 65535:
                return {}

            try:
                ipaddress.ip_address(hostname)

            except ValueError:
                if not re.match(
                    r"^(?=.{1,253}$)"
                    r"[a-zA-Z0-9]"
                    r"(?:[a-zA-Z0-9.-]*"
                    r"[a-zA-Z0-9])?$",
                    hostname
                ):
                    return {}

                labels = hostname.split(".")

                if any(
                    not label
                    or len(label) > 63
                    or label.startswith("-")
                    or label.endswith("-")
                    for label in labels
                ):
                    return {}

            provider = cls._clean_provider(
                provider
            )

            if (
                not provider
                or provider == "Unknown"
            ):
                provider = hostname

            entry = {
                "provider": provider,
                "address": hostname,
                "name": provider,
                "source": cls.SOURCE_NAME,
                "type": "DoT",
                "hostname": hostname,
                "port": port,
                "protocol": "DoT",
                "dot": f"{hostname}:{port}",
                "description": (
                    f"DoT server provided by "
                    f"{provider}"
                ),
            }

            if inferred:
                entry["dot_inferred"] = True

            return entry

        except (
            ValueError,
            TypeError
        ):
            return {}

    @classmethod
    def _parse_fallback(
        cls,
        soup: BeautifulSoup
    ) -> List[Dict[str, Any]]:
        dns_list = []
        seen_doh = set()
        seen_dot = set()

        def add_entry(entry):
            if not entry:
                return

            if entry.get("protocol") == "DoH":
                key = cls._doh_key(entry)

                if key in seen_doh:
                    return

                seen_doh.add(key)
                dns_list.append(entry)

            elif entry.get("protocol") == "DoT":
                key = cls._dot_key(entry)

                if key in seen_dot:
                    return

                seen_dot.add(key)
                dns_list.append(entry)

        for element in soup.find_all(
            ["table", "article", "li", "section", "div"]
        ):
            cells = element.find_all(
                ["td", "th"]
            )

            row_text = cls._clean_text(
                element.get_text(
                    " ",
                    strip=True
                )
            )

            if not row_text:
                continue

            urls = cls._extract_urls(element)

            provider = cls._extract_provider_from_element(
                element
            )

            if cells:
                provider = cls._extract_provider_from_row(
                    element,
                    cells,
                    None,
                    None
                )

            for url in urls:
                if not cls._is_dns_url(url):
                    continue

                add_entry(
                    cls._build_entry(
                        url,
                        provider
                    )
                )

            for entry in cls._extract_dot_entries(
                element,
                row_text,
                provider,
                urls
            ):
                add_entry(entry)

        if dns_list:
            return dns_list

        for link in soup.find_all(
            "a",
            href=True
        ):
            href = link.get(
                "href",
                ""
            ).strip()

            if not cls._is_dns_url(href):
                continue

            provider = cls._find_provider(
                link
            )

            entry = cls._build_entry(
                href,
                provider
            )

            add_entry(entry)

            context = cls._get_link_context(
                link
            )

            dot_entries = cls._extract_dot_entries(
                link.parent,
                context,
                provider,
                [href]
            )

            for dot_entry in dot_entries:
                add_entry(dot_entry)

        return dns_list

    @classmethod
    def _build_entry(
        cls,
        url: str,
        provider: str
    ) -> Dict[str, Any]:
        try:
            parsed = urlparse(url)

            scheme = parsed.scheme.lower()

            if (
                scheme not in (
                    "https",
                    "http"
                )
                or not parsed.hostname
            ):
                return {}

            hostname = parsed.hostname.lower()

            port = (
                parsed.port
                or (
                    443
                    if scheme == "https"
                    else 80
                )
            )

            path = parsed.path or "/dns-query"

            clean_url = parsed._replace(
                fragment=""
            ).geturl().rstrip("/")

            provider = cls._clean_provider(
                provider
            )

            if (
                not provider
                or provider == "Unknown"
            ):
                provider = hostname

            return {
                "provider": provider,
                "doh_url": clean_url,
                "address": hostname,
                "name": provider,
                "source": cls.SOURCE_NAME,
                "type": "DoH",
                "hostname": hostname,
                "path": path,
                "port": port,
                "protocol": "DoH",
                "description": (
                    f"DoH server provided by "
                    f"{provider}"
                ),
            }

        except (
            ValueError,
            TypeError
        ):
            return {}

    @classmethod
    def _supports_dot(
        cls,
        text: str
    ) -> bool:
        normalized = cls._clean_text(
            text
        ).lower()

        return bool(
            cls.DOT_LABEL_PATTERN.search(
                normalized
            )
        )

    @classmethod
    def _contains_dot_endpoint(
        cls,
        text: str
    ) -> bool:
        return bool(
            cls.DOT_URL_PATTERN.search(text)
            or cls.DOT_HOST_PORT_PATTERN.search(text)
            or cls.DOT_853_PATTERN.search(text)
            or cls.DOT_LABELED_HOST_PATTERN.search(text)
        )

    @classmethod
    def _find_provider(
        cls,
        link
    ) -> str:
        for parent in link.parents:
            if parent.name == "tr":
                cells = parent.find_all(
                    ["td", "th"]
                )

                for cell in cells:
                    text = cell.get_text(
                        " ",
                        strip=True
                    )

                    if (
                        text
                        and not cls._contains_url(text)
                        and not cls._contains_dot_endpoint(text)
                        and len(text) <= 200
                    ):
                        return cls._clean_provider(
                            text
                        )

                break

            if parent.name in (
                "section",
                "article",
                "li",
            ):
                text = parent.get_text(
                    " ",
                    strip=True
                )

                text = cls.URL_PATTERN.sub(
                    " ",
                    text
                )

                text = re.sub(
                    r"\s+",
                    " ",
                    text
                ).strip()

                if text:
                    return cls._clean_provider(
                        text
                    )

        return "Unknown"

    @classmethod
    def _get_link_context(
        cls,
        link
    ) -> str:
        parts = []

        if link.parent:
            parts.append(
                link.parent.get_text(
                    " ",
                    strip=True
                )
            )

        for parent in link.parents:
            if parent.name in (
                "tr",
                "li",
                "section",
                "article",
                "div"
            ):
                text = parent.get_text(
                    " ",
                    strip=True
                )

                if text:
                    parts.append(text)

                if parent.name in (
                    "tr",
                    "section",
                    "article"
                ):
                    break

        return " ".join(parts)

    @classmethod
    def _doh_key(
        cls,
        entry: Dict[str, Any]
    ) -> str:
        return (
            "doh|"
            + cls._normalize_url(
                entry.get(
                    "doh_url",
                    ""
                )
            )
        )

    @classmethod
    def _dot_key(
        cls,
        entry: Dict[str, Any]
    ) -> str:
        hostname = str(
            entry.get(
                "hostname",
                entry.get(
                    "address",
                    ""
                )
            )
        ).lower()

        try:
            port = int(
                entry.get(
                    "port",
                    cls.DEFAULT_DOT_PORT
                )
            )

        except (
            ValueError,
            TypeError
        ):
            port = cls.DEFAULT_DOT_PORT

        return (
            f"dot|{hostname}|{port}"
        )

    @classmethod
    def _extract_hostname(
        cls,
        url: str
    ) -> Optional[str]:
        try:
            parsed = urlparse(url)

            if parsed.hostname:
                return parsed.hostname.lower()

        except (
            ValueError,
            TypeError
        ):
            pass

        return None

    @classmethod
    def _is_dns_url(
        cls,
        url: str
    ) -> bool:
        try:
            parsed = urlparse(url)

            if (
                parsed.scheme.lower()
                not in (
                    "https",
                    "http"
                )
                or not parsed.hostname
            ):
                return False

            host = parsed.hostname.lower()
            path = parsed.path.lower()
            query = parsed.query.lower()

            if any(
                dns_host == host
                or host.endswith(
                    "." + dns_host
                )
                for dns_host in cls.DNS_HOSTS
            ):
                return True

            if any(
                dns_path in path
                for dns_path in cls.DNS_PATHS
            ):
                return True

            if (
                "dns" in query
                or "dns" in path
                or "doh" in host
            ):
                return True

            return False

        except (
            ValueError,
            TypeError
        ):
            return False

    @classmethod
    def _is_http_url(
        cls,
        url: str
    ) -> bool:
        try:
            parsed = urlparse(url)

            return (
                parsed.scheme.lower()
                in (
                    "https",
                    "http"
                )
                and bool(parsed.hostname)
            )

        except (
            ValueError,
            TypeError
        ):
            return False

    @classmethod
    def _contains_url(
        cls,
        text: str
    ) -> bool:
        return bool(
            cls.URL_PATTERN.search(text)
        )

    @classmethod
    def _clean_url(
        cls,
        url: str
    ) -> str:
        return url.strip().rstrip(
            ".,;:)]}\"'"
        )

    @classmethod
    def _normalize_url(
        cls,
        url: str
    ) -> str:
        try:
            parsed = urlparse(url)

            scheme = parsed.scheme.lower()

            hostname = (
                parsed.hostname or ""
            ).lower()

            port = parsed.port

            if port in (
                80,
                443,
                None
            ):
                netloc = hostname
            else:
                netloc = (
                    f"{hostname}:{port}"
                )

            path = (
                parsed.path
                or "/dns-query"
            )

            return (
                f"{scheme}://"
                f"{netloc}"
                f"{path}"
                f"?{parsed.query}"
            ).rstrip("?")

        except (
            ValueError,
            TypeError
        ):
            return url.lower().rstrip("/")

    @classmethod
    def _clean_text(
        cls,
        text: str
    ) -> str:
        text = str(text or "")

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

    @classmethod
    def _clean_provider(
        cls,
        provider: str
    ) -> str:
        provider = cls._clean_text(
            provider
        )

        provider = re.sub(
            r"https?://\S+",
            "",
            provider,
            flags=re.IGNORECASE
        )

        provider = re.sub(
            r"\s+",
            " ",
            provider
        ).strip()

        return provider
