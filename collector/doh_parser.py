import re
import requests
import os
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from urllib.parse import urlparse


class DOHParser:
    SOURCE_NAME = "curl"

    URL_PATTERN = re.compile(
        r'https?://[^\s<>"\'\)\]\}]+',
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

    @classmethod
    def fetch(cls) -> List[Dict[str, Any]]:
        try:
            source_url = os.environ.get("DOH_SOURCE_URL")

            if not source_url:
                print("ERROR: DOH_SOURCE_URL environment variable not set")
                return []

            response = requests.get(
                source_url,
                timeout=30,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36"
                    )
                }
            )

            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            dns_list = cls._parse_content(soup)

            print(f"Total DoH entries extracted: {len(dns_list)}")

            return dns_list

        except Exception as e:
            print(f"Error fetching DoH data: {e}")
            return []

    @classmethod
    def _parse_content(cls, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        dns_list = []
        seen = set()

        for table in soup.find_all("table"):
            rows = table.find_all("tr")

            if len(rows) < 2:
                continue

            headers = cls._extract_headers(rows[0])

            provider_idx = cls._find_provider_column(headers)
            url_idx = cls._find_url_column(headers)

            for row in rows[1:]:
                cells = row.find_all(["td", "th"])

                if not cells:
                    continue

                provider = cls._extract_provider_from_row(
                    row,
                    cells,
                    provider_idx,
                    url_idx
                )

                url_cells = cls._get_url_cells(
                    cells,
                    url_idx
                )

                urls = []

                for cell in url_cells:
                    urls.extend(cls._extract_urls(cell))

                if not urls:
                    urls = cls._extract_urls(row)

                for url in urls:
                    if not cls._is_dns_url(url):
                        continue

                    entry = cls._build_entry(
                        url,
                        provider
                    )

                    if not entry:
                        continue

                    key = cls._normalize_url(
                        entry["doh_url"]
                    )

                    if key in seen:
                        continue

                    seen.add(key)
                    dns_list.append(entry)

        if dns_list:
            return dns_list

        return cls._parse_fallback(soup)

    @classmethod
    def _extract_headers(cls, row) -> List[str]:
        return [
            re.sub(
                r"\s+",
                " ",
                cell.get_text(" ", strip=True).lower()
            )
            for cell in row.find_all(["th", "td"])
        ]

    @classmethod
    def _find_provider_column(
        cls,
        headers: List[str]
    ) -> Optional[int]:
        patterns = (
            "run by",
            "who runs",
            "operator",
            "provider",
            "company",
            "organization",
            "organisation",
            "who",
        )

        for index, header in enumerate(headers):
            if any(
                pattern in header
                for pattern in patterns
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
            text = cell.get_text(" ", strip=True)

            if (
                cell.find("a", href=True)
                or cls._contains_url(text)
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
                return cls._clean_provider(provider)

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

            if len(text) > 200:
                continue

            candidates.append(text)

        if candidates:
            return cls._clean_provider(
                candidates[0]
            )

        return "Unknown"

    @classmethod
    def _extract_urls(cls, element) -> List[str]:
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
    def _parse_fallback(
        cls,
        soup: BeautifulSoup
    ) -> List[Dict[str, Any]]:
        dns_list = []
        seen = set()

        for table in soup.find_all("table"):
            for row in table.find_all("tr"):
                urls = cls._extract_urls(row)

                if not urls:
                    continue

                provider = cls._extract_provider_from_row(
                    row,
                    row.find_all(["td", "th"]),
                    None,
                    None
                )

                for url in urls:
                    if not cls._is_dns_url(url):
                        continue

                    entry = cls._build_entry(
                        url,
                        provider
                    )

                    if not entry:
                        continue

                    key = cls._normalize_url(
                        entry["doh_url"]
                    )

                    if key in seen:
                        continue

                    seen.add(key)
                    dns_list.append(entry)

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

            provider = cls._find_provider(link)

            entry = cls._build_entry(
                href,
                provider
            )

            if not entry:
                continue

            key = cls._normalize_url(
                entry["doh_url"]
            )

            if key in seen:
                continue

            seen.add(key)
            dns_list.append(entry)

        return dns_list

    @classmethod
    def _find_provider(cls, link) -> str:
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
    def _build_entry(
        cls,
        url: str,
        provider: str
    ) -> Dict[str, Any]:
        try:
            parsed = urlparse(url)

            if (
                parsed.scheme not in (
                    "https",
                    "http"
                )
                or not parsed.hostname
            ):
                return {}

            hostname = parsed.hostname
            port = parsed.port or (
                443
                if parsed.scheme == "https"
                else 80
            )

            path = parsed.path or "/dns-query"

            clean_url = parsed._replace(
                fragment=""
            ).geturl().rstrip("/")

            provider = cls._clean_provider(
                provider
            )

            if not provider or provider == "Unknown":
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
    def _is_dns_url(cls, url: str) -> bool:
        try:
            parsed = urlparse(url)

            if (
                parsed.scheme not in (
                    "https",
                    "http"
                )
                or not parsed.hostname
            ):
                return False

            host = parsed.hostname.lower()
            path = parsed.path.lower()

            if any(
                dns_host in host
                for dns_host in cls.DNS_HOSTS
            ):
                return True

            if any(
                dns_path in path
                for dns_path in cls.DNS_PATHS
            ):
                return True

            query = parsed.query.lower()

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
    def _is_http_url(cls, url: str) -> bool:
        try:
            parsed = urlparse(url)

            return (
                parsed.scheme in (
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
    def _contains_url(cls, text: str) -> bool:
        return bool(
            cls.URL_PATTERN.search(text)
        )

    @classmethod
    def _clean_url(cls, url: str) -> str:
        return url.strip().rstrip(
            ".,;:)]}\"'"
        )

    @classmethod
    def _normalize_url(cls, url: str) -> str:
        try:
            parsed = urlparse(url)

            scheme = parsed.scheme.lower()
            hostname = (
                parsed.hostname or ""
            ).lower()

            port = parsed.port

            if port in (80, 443, None):
                netloc = hostname
            else:
                netloc = f"{hostname}:{port}"

            path = parsed.path or "/dns-query"

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
    def _clean_provider(
        cls,
        provider: str
    ) -> str:
        provider = re.sub(
            r"\s+",
            " ",
            str(provider)
        ).strip()

        provider = re.sub(
            r"https?://\S+",
            "",
            provider,
            flags=re.IGNORECASE
        )

        return provider.strip()
