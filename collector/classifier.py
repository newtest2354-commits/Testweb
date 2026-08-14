import re
from typing import List, Dict, Any

class Classifier:
    CATEGORIES = {
        'AdBlock': ['adblock', 'ad block', 'ads', 'tracker', 'tracking', 'ad-filter'],
        'Family': ['family', 'parental', 'kids', 'children'],
        'Adult Filter': ['adult', 'porn', 'nsfw', 'mature'],
        'Security': ['malware', 'security', 'threat', 'phishing', 'protect'],
        'Standard': ['standard', 'unfiltered', 'default'],
        'Private': ['private', 'local', 'internal'],
        'Malware': ['malware', 'virus', 'ransomware', 'botnet']
    }
    
    @classmethod
    def classify(cls, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        for entry in data:
            entry['categories'] = cls._determine_categories(entry)
            entry['protocols'] = cls._determine_protocols(entry)
            entry['type'] = cls._determine_type(entry)
        return data
    
    @classmethod
    def _determine_categories(cls, entry: Dict[str, Any]) -> List[str]:
        categories = []
        text = ' '.join([
            str(entry.get('name', '')),
            str(entry.get('provider', '')),
            str(entry.get('description', '')),
            str(entry.get('tags', ''))
        ]).lower()
        
        for category, keywords in cls.CATEGORIES.items():
            for keyword in keywords:
                if keyword in text:
                    categories.append(category)
                    break
        
        if 'free shekan' in text or 'freeshekan' in text:
            categories.append('FreeShekan')
        
        if not categories:
            categories.append('Standard')
        
        return categories
    
    @classmethod
    def _determine_protocols(cls, entry: Dict[str, Any]) -> List[str]:
        protocols = ['DNS']
        
        if entry.get('doh_url'):
            protocols.append('DoH')
        if entry.get('dot'):
            protocols.append('DoT')
        if entry.get('dnscrypt'):
            protocols.append('DNSCrypt')
        
        return protocols
    
    @classmethod
    def _determine_type(cls, entry: Dict[str, Any]) -> str:
        address = entry.get('address', '')
        if address:
            if ':' in address and '.' not in address:
                return 'IPv6'
            elif '.' in address:
                return 'IPv4'
        if entry.get('doh_url'):
            return 'DoH'
        if entry.get('dot'):
            return 'DoT'
        return 'Unknown'
