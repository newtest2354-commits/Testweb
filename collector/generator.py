import json
import uuid
import os
import hashlib
from datetime import datetime, timezone
from typing import List, Dict, Any


class Generator:

    def __init__(self, data: List[Dict[str, Any]]):
        self.data = data
        self.stats = {}

    def save(self) -> None:
        current_data = self._generate_output()
        self._generate_stats()

        current_hash = self._hash_data(
            current_data["dns"]
        )

        existing_data = None

        if os.path.exists("../data/dns.json"):
            try:
                with open(
                    "../data/dns.json",
                    "r",
                    encoding="utf-8"
                ) as f:
                    existing_data = json.load(f)
            except (OSError, json.JSONDecodeError):
                existing_data = None

        if existing_data:
            old_hash = self._hash_data(
                existing_data.get("dns", [])
            )

            if current_hash == old_hash:
                print("No changes detected, skipping save")
                return

        self._save_json(
            "../data/dns.json",
            current_data
        )

        self._save_json(
            "../data/dns.min.json",
            self._generate_minified(current_data)
        )

        self._save_json(
            "../data/stats.json",
            self.stats
        )

    def _hash_data(
        self,
        data: List[Dict[str, Any]]
    ) -> str:

        normalized = []

        for item in data:
            item_copy = dict(item)
            item_copy.pop("id", None)
            normalized.append(item_copy)

        normalized.sort(
            key=lambda x: (
                str(x.get("address", "")),
                str(x.get("hostname", "")),
                str(x.get("doh_url", "")),
                str(x.get("name", ""))
            )
        )

        payload = json.dumps(
            normalized,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":")
        )

        return hashlib.sha256(
            payload.encode("utf-8")
        ).hexdigest()

    def _generate_output(self) -> Dict[str, Any]:
        return {
            "version": 1,
            "updated_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "total": len(self.data),
            "categories": self._get_category_counts(),
            "dns": self._prepare_dns_entries()
        }

    def _prepare_dns_entries(
        self
    ) -> List[Dict[str, Any]]:

        entries = []

        for entry in self.data:

            dns_entry = {
                "id": self._generate_stable_id(entry),
                "address": entry.get("address", ""),
                "type": entry.get("type", "Unknown"),
                "provider": entry.get("provider", ""),
                "name": entry.get("name", ""),
                "sources": self._normalize_sources(entry),
                "categories": entry.get(
                    "categories",
                    ["Standard"]
                ),
                "protocols": entry.get(
                    "protocols",
                    ["DNS"]
                ),
                "status": "active"
            }

            optional_fields = (
                "doh_url",
                "dot",
                "dnscrypt",
                "country",
                "description",
                "hostname",
                "port",
                "path"
            )

            for field in optional_fields:
                value = entry.get(field)

                if value is not None and value != "":
                    dns_entry[field] = value

            entries.append(dns_entry)

        return entries

    def _generate_stable_id(
        self,
        entry: Dict[str, Any]
    ) -> str:

        identity = {
            "address": entry.get("address", ""),
            "hostname": entry.get("hostname", ""),
            "doh_url": entry.get("doh_url", ""),
            "dot": entry.get("dot", ""),
            "name": entry.get("name", "")
        }

        payload = json.dumps(
            identity,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":")
        )

        digest = hashlib.sha256(
            payload.encode("utf-8")
        ).hexdigest()

        return str(
            uuid.UUID(digest[:32])
        )

    def _normalize_sources(
        self,
        entry: Dict[str, Any]
    ) -> List[str]:

        sources = entry.get("sources", [])

        if not isinstance(sources, list):
            sources = [sources] if sources else []

        source = entry.get("source")

        if source and source not in sources:
            sources.append(source)

        return list(
            dict.fromkeys(
                str(source)
                for source in sources
                if source
            )
        )

    def _generate_stats(self) -> None:

        self.stats = {
            "total_dns": len(self.data),
            "total_ipv4": self._count_type("IPv4"),
            "total_ipv6": self._count_type("IPv6"),
            "total_doh": self._count_protocol("DoH"),
            "total_dot": self._count_protocol("DoT"),
            "total_dnscrypt": self._count_protocol("DNSCrypt"),
            "total_standard": self._count_category("Standard"),
            "total_private": self._count_category("Private"),
            "total_family": self._count_category("Family"),
            "total_adblock": self._count_category("AdBlock"),
            "total_adult_filter": self._count_category(
                "Adult Filter"
            ),
            "total_security": self._count_category("Security"),
            "total_malware": self._count_category("Malware"),
            "total_unfiltered": self._count_category(
                "Unfiltered"
            ),
            "total_freeshekan": self._count_category(
                "FreeShekan"
            ),
            "total_sources": len(
                {
                    source
                    for entry in self.data
                    for source in entry.get(
                        "sources",
                        []
                    )
                    if source
                }
            ),
            "last_updated": datetime.now(
                timezone.utc
            ).isoformat()
        }

    def _count_type(
        self,
        type_name: str
    ) -> int:

        return sum(
            1
            for entry in self.data
            if entry.get("type") == type_name
        )

    def _count_protocol(
        self,
        protocol: str
    ) -> int:

        return sum(
            1
            for entry in self.data
            if protocol in entry.get(
                "protocols",
                []
            )
        )

    def _count_category(
        self,
        category: str
    ) -> int:

        return sum(
            1
            for entry in self.data
            if category in entry.get(
                "categories",
                []
            )
        )

    def _get_category_counts(
        self
    ) -> Dict[str, int]:

        counts = {}

        for entry in self.data:
            for category in entry.get(
                "categories",
                []
            ):
                counts[category] = (
                    counts.get(category, 0) + 1
                )

        return dict(
            sorted(
                counts.items(),
                key=lambda item: item[0].lower()
            )
        )

    def _generate_minified(
        self,
        current_data: Dict[str, Any]
    ) -> Dict[str, Any]:

        output = json.loads(
            json.dumps(
                current_data,
                ensure_ascii=False
            )
        )

        for dns in output.get("dns", []):
            for key in (
                "description",
                "source",
                "path",
                "port"
            ):
                dns.pop(key, None)

        return output

    def _save_json(
        self,
        filepath: str,
        data: Dict[str, Any]
    ) -> None:

        directory = os.path.dirname(filepath)

        if directory:
            os.makedirs(
                directory,
                exist_ok=True
            )

        with open(
            filepath,
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(
                data,
                f,
                indent=2,
                ensure_ascii=False
            )
