import re
from typing import List, Dict, Any

class Classifier:
    CATEGORIES = {
        'adblock': ['adblock', 'ad block', 'ads', 'tracker', 'tracking', 'ad-filter'],
        'family': ['family', 'parental', 'kids', 'children'],
        'adult_filter': ['adult', 'porn', 'nsfw', 'mature'],
        'security': ['malware', 'security', 'threat', 'phishing', 'protect'],
        'standard': ['standard', 'unfiltered', 'default'],
        'private': ['private', 'local', 'internal'],
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
        text = str(entry).lower()
        
        for category, keywords in cls.CATEGORIES.items():
            for keyword in keywords:
                if keyword in text:
                    categories.append(category.title())
                    break
                    
        if 'free shekan' in text or 'freeshekan' in text:
            categories.append('FreeShekan')
            
        if not categories:
            categories.append('Standard')
            
        return categories
    
    @classmethod
    def _determine_protocols(cls, entry: Dict[str, Any]) -> List[str]:
        protocols = ['DNS']
        
        if 'doh_url' in entry or 'doh' in str(entry).lower():
            protocols.append('DoH')
        if 'dot' in entry or 'dot' in str(entry).lower():
            protocols.append('DoT')
        if 'dnscrypt' in str(entry).lower():
            protocols.append('DNSCrypt')
            
        return protocols
    
    @classmethod
    def _determine_type(cls, entry: Dict[str, Any]) -> str:
        if 'address' in entry and entry['address']:
            address = entry['address']
            if ':' in address and '.' not in address:
                return 'IPv6'
            elif '.' in address:
                return 'IPv4'
        if 'doh_url' in entry:
            return 'DoH'
        if 'dot' in entry:
            return 'DoT'
        if 'hostname' in entry:
            return 'Hostname'
        return 'Unknown'
