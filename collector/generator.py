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
        
    def save(self):
        self._generate_stats()
        current_data = self._generate_output()
        
        if os.path.exists('../data/dns.json'):
            with open('../data/dns.json', 'r', encoding='utf-8') as f:
                try:
                    old_data = json.load(f)
                    if self._hash_data(current_data['dns']) == self._hash_data(old_data.get('dns', [])):
                        print("No changes detected, skipping save")
                        return
                except:
                    pass
        
        self._save_json('../data/dns.json', current_data)
        self._save_json('../data/dns.min.json', self._generate_minified())
        self._save_json('../data/stats.json', self.stats)
    
    def _hash_data(self, data: List[Dict]) -> str:
        sorted_data = sorted(data, key=lambda x: (x.get('address', ''), x.get('name', '')))
        return hashlib.md5(str(sorted_data).encode()).hexdigest()
        
    def _generate_output(self) -> Dict[str, Any]:
        return {
            'version': 1,
            'updated_at': datetime.now(timezone.utc).isoformat(),
            'total': len(self.data),
            'categories': self._get_category_counts(),
            'dns': self._prepare_dns_entries()
        }
    
    def _prepare_dns_entries(self) -> List[Dict[str, Any]]:
        entries = []
        for entry in self.data:
            dns_entry = {
                'id': str(uuid.uuid4()),
                'address': entry.get('address', ''),
                'type': entry.get('type', 'Unknown'),
                'provider': entry.get('provider', ''),
                'name': entry.get('name', ''),
                'sources': entry.get('sources', [entry.get('source', 'unknown')]),
                'categories': entry.get('categories', ['Standard']),
                'protocols': entry.get('protocols', ['DNS']),
                'status': 'active'
            }
            
            optional_fields = ['doh_url', 'dot', 'dnscrypt', 'country', 'description', 'hostname', 'port', 'path']
            for field in optional_fields:
                if field in entry and entry[field]:
                    dns_entry[field] = entry[field]
                    
            entries.append(dns_entry)
        return entries
    
    def _generate_stats(self) -> None:
        self.stats = {
            'total_dns': len(self.data),
            'total_ipv4': self._count_type('IPv4'),
            'total_ipv6': self._count_type('IPv6'),
            'total_doh': self._count_protocol('DoH'),
            'total_dot': self._count_protocol('DoT'),
            'total_dnscrypt': self._count_protocol('DNSCrypt'),
            'total_standard': self._count_category('Standard'),
            'total_private': self._count_category('Private'),
            'total_family': self._count_category('Family'),
            'total_adblock': self._count_category('AdBlock'),
            'total_security': self._count_category('Security'),
            'total_malware': self._count_category('Malware'),
            'total_freeshekan': self._count_category('FreeShekan'),
            'total_sources': len(set([s for entry in self.data for s in entry.get('sources', [])])),
            'last_updated': datetime.now(timezone.utc).isoformat()
        }
        
    def _count_type(self, type_name: str) -> int:
        return sum(1 for entry in self.data if entry.get('type') == type_name)
    
    def _count_protocol(self, protocol: str) -> int:
        return sum(1 for entry in self.data if protocol in entry.get('protocols', []))
    
    def _count_category(self, category: str) -> int:
        return sum(1 for entry in self.data if category in entry.get('categories', []))
    
    def _get_category_counts(self) -> Dict[str, int]:
        counts = {}
        for entry in self.data:
            for category in entry.get('categories', []):
                counts[category] = counts.get(category, 0) + 1
        return counts
    
    def _generate_minified(self) -> Dict[str, Any]:
        output = self._generate_output()
        for dns in output['dns']:
            for key in ['description', 'source', 'path', 'port']:
                if key in dns:
                    del dns[key]
        return output
    
    def _save_json(self, filepath: str, data: Dict[str, Any]) -> None:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
