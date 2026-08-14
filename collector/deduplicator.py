from typing import List, Dict, Any

class Deduplicator:
    
    @classmethod
    def deduplicate(cls, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        unique_map = {}
        
        for entry in data:
            key = cls._generate_key(entry)
            
            if key not in unique_map:
                unique_map[key] = entry.copy()
                unique_map[key]['sources'] = [entry.get('source', 'unknown')]
            else:
                existing = unique_map[key]
                if entry.get('source') not in existing.get('sources', []):
                    existing['sources'].append(entry.get('source', 'unknown'))
                cls._merge_data(existing, entry)
                
        return list(unique_map.values())
    
    @classmethod
    def _generate_key(cls, entry: Dict[str, Any]) -> str:
        key_parts = []
        
        if entry.get('address'):
            key_parts.append(str(entry['address']))
        if entry.get('doh_url'):
            key_parts.append(str(entry['doh_url']))
        if entry.get('dot'):
            key_parts.append(str(entry['dot']))
        if entry.get('hostname'):
            key_parts.append(str(entry['hostname']).lower())
        if entry.get('name'):
            key_parts.append(str(entry['name']).lower())
            
        if not key_parts:
            return str(hash(str(entry)))
            
        return '|'.join(key_parts)
    
    @classmethod
    def _merge_data(cls, existing: Dict[str, Any], new: Dict[str, Any]) -> None:
        for key, value in new.items():
            if key not in existing or not existing[key]:
                existing[key] = value
            elif key != 'source' and key != 'sources' and existing[key] != value:
                if isinstance(existing[key], list):
                    if value not in existing[key]:
                        existing[key].append(value)
