from typing import List, Dict, Any


class Deduplicator:

    @classmethod
    def deduplicate(
        cls,
        data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        unique_map: Dict[str, Dict[str, Any]] = {}

        for entry in data:
            key = cls._generate_key(entry)

            if key not in unique_map:
                item = entry.copy()

                sources = item.get("sources", [])

                if not isinstance(sources, list):
                    sources = [sources] if sources else []

                source = item.get("source")

                if source and source not in sources:
                    sources.append(source)

                item["sources"] = sources
                unique_map[key] = item
                continue

            existing = unique_map[key]

            cls._merge_sources(existing, entry)
            cls._merge_data(existing, entry)

        return list(unique_map.values())

    @classmethod
    def _generate_key(cls, entry: Dict[str, Any]) -> str:
        doh_url = str(
            entry.get("doh_url", "")
        ).strip().lower().rstrip("/")

        dot = str(
            entry.get("dot", "")
        ).strip().lower()

        address = str(
            entry.get("address", "")
        ).strip().lower()

        hostname = str(
            entry.get("hostname", "")
        ).strip().lower()

        protocol = str(
            entry.get("protocol", "")
        ).strip().lower()

        if doh_url:
            return f"doh|{doh_url}"

        if dot:
            return f"dot|{dot}"

        if address and protocol:
            return f"{protocol}|{address}"

        if hostname and protocol:
            return f"{protocol}|{hostname}"

        if address:
            return f"address|{address}"

        if hostname:
            return f"hostname|{hostname}"

        name = str(
            entry.get("name", "")
        ).strip().lower()

        if name:
            return f"name|{name}"

        return str(hash(frozenset(entry.items())))

    @classmethod
    def _merge_sources(
        cls,
        existing: Dict[str, Any],
        new: Dict[str, Any]
    ) -> None:
        sources = existing.get("sources", [])

        if not isinstance(sources, list):
            sources = [sources] if sources else []

        source = new.get("source")

        if source and source not in sources:
            sources.append(source)

        new_sources = new.get("sources", [])

        if isinstance(new_sources, list):
            for item in new_sources:
                if item and item not in sources:
                    sources.append(item)

        existing["sources"] = sources

    @classmethod
    def _merge_data(
        cls,
        existing: Dict[str, Any],
        new: Dict[str, Any]
    ) -> None:
        for key, value in new.items():

            if key in (
                "source",
                "sources"
            ):
                continue

            if value is None or value == "":
                continue

            if key not in existing or not existing[key]:
                existing[key] = value
                continue

            current = existing[key]

            if current == value:
                continue

            if isinstance(current, list):
                if isinstance(value, list):
                    for item in value:
                        if item not in current:
                            current.append(item)
                elif value not in current:
                    current.append(value)

                continue

            if isinstance(value, list):
                merged = [current]

                for item in value:
                    if item not in merged:
                        merged.append(item)

                existing[key] = merged
