import json
import hashlib
from typing import Dict, Any, Optional
import time

class MockIPFS:
    def __init__(self):
        self.storage = {}
        self.metadata = {}
        
    def add(self, content: Any, content_type: str = "json") -> str:
        """Add content to storage and return CID"""
        if content_type == "json":
            content_str = json.dumps(content, sort_keys=True)
        else:
            content_str = str(content)
        
        # Generate content ID (hash)
        cid = hashlib.sha256(content_str.encode()).hexdigest()[:16]
        
        self.storage[cid] = content_str
        self.metadata[cid] = {
            'content_type': content_type,
            'size': len(content_str),
            'timestamp': time.time(),
            'access_count': 0
        }
        
        return cid
    
    def get(self, cid: str) -> Optional[Any]:
        """Retrieve content by CID"""
        if cid in self.storage:
            self.metadata[cid]['access_count'] += 1
            content_str = self.storage[cid]
            content_type = self.metadata[cid]['content_type']
            
            if content_type == "json":
                try:
                    return json.loads(content_str)
                except json.JSONDecodeError:
                    return content_str
            return content_str
        return None
    
    def pin(self, cid: str) -> bool:
        """Pin content (mark as important)"""
        if cid in self.metadata:
            self.metadata[cid]['pinned'] = True
            return True
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        total_size = sum(meta['size'] for meta in self.metadata.values())
        total_access = sum(meta['access_count'] for meta in self.metadata.values())
        
        return {
            'total_objects': len(self.storage),
            'total_size_bytes': total_size,
            'total_accesses': total_access,
            'pinned_objects': sum(1 for meta in self.metadata.values() 
                                if meta.get('pinned', False))
        }

# Global storage instance
mock_ipfs = MockIPFS()