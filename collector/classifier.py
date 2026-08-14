import ipaddress
from typing import List, Dict, Any


class Classifier:

    CATEGORIES = {
        'AdBlock': [
            'adblock',
            'ad block',
            'ad-filter',
            'ad filter',
            'ads',
            'tracker',
            'tracking',
            'adguard'
        ],

        'Family': [
            'family',
            'parental',
            'kids',
            'children'
        ],

        'Adult Filter': [
            'adult',
            'porn',
            'nsfw',
            'mature'
        ],

        'Security': [
            'malware',
            'security',
            'threat',
            'phishing',
            'protect',
            'protection'
        ],

        'Malware': [
            'malware',
            'virus',
            'ransomware',
            'botnet'
        ],

        'Standard': [
            'standard',
            'default'
        ],

        'Private': [
            'private',
            'local',
            'internal'
        ],

        'Unfiltered': [
            'unfiltered',
            'no filter',
            'no filtering'
        ]
    }

    @classmethod
    def classify(
        cls,
        data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        for entry in data:
            entry['categories'] = cls._determine_categories(entry)
            entry['protocols'] = cls._determine_protocols(entry)
            entry['type'] = cls._determine_type(entry)

        return data

    @classmethod
    def _determine_categories(
        cls,
        entry: Dict[str, Any]
    ) -> List[str]:

        categories = []

        text = ' '.join([
            str(entry.get('name', '')),
            str(entry.get('provider', '')),
            str(entry.get('description', '')),
            str(entry.get('tags', ''))
        ]).lower()

        for category, keywords in cls.CATEGORIES.items():
            if any(keyword in text for keyword in keywords):
                categories.append(category)

        if (
            'free shekan' in text
            or 'freeshekan' in text
            or 'free-shekan' in text
        ):
            categories.append('FreeShekan')

        if not categories:
            categories.append('Standard')

        return categories

    @classmethod
    def _determine_protocols(
        cls,
        entry: Dict[str, Any]
    ) -> List[str]:

        protocols = ['DNS']

        if entry.get('doh_url'):
            protocols.append('DoH')

        if entry.get('dot'):
            protocols.append('DoT')

        if entry.get('dnscrypt'):
            protocols.append('DNSCrypt')

        return protocols

    @classmethod
    def _determine_type(
        cls,
        entry: Dict[str, Any]
    ) -> str:

        address = str(
            entry.get('address', '')
        ).strip()

        if address:
            try:
                ip = ipaddress.ip_address(address)

                if ip.version == 4:
                    return 'IPv4'

                if ip.version == 6:
                    return 'IPv6'

            except ValueError:
                pass

        if entry.get('doh_url'):
            return 'DoH'

        if entry.get('dot'):
            return 'DoT'

        if entry.get('hostname'):
            return 'Hostname'

        return 'Unknown'
