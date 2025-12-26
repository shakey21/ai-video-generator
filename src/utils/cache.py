"""Caching system for pipeline stages."""

import json
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional


class CacheManager:
    """
    Manages content-hash based caching for pipeline stages.
    """
    
    def __init__(self, run_dir: Path, cache_config: Dict[str, Any]):
        self.run_dir = Path(run_dir)
        self.cache_dir = self.run_dir / ".cache"
        self.cache_dir.mkdir(exist_ok=True)
        
        self.enabled = cache_config.get('strategy', 'content_hash') == 'content_hash'
        self.hash_algorithm = cache_config.get('hash_algorithm', 'sha256')
    
    def is_cached(self, stage_name: str) -> bool:
        """Check if stage result is cached."""
        if not self.enabled:
            return False
        
        cache_file = self.cache_dir / f"{stage_name}.json"
        return cache_file.exists()
    
    def save(self, stage_name: str, output: Dict[str, Any]):
        """Save stage output to cache."""
        if not self.enabled:
            return
        
        cache_file = self.cache_dir / f"{stage_name}.json"
        
        cache_data = {
            'stage': stage_name,
            'output': {
                'output_path': str(output.get('output_path')),
                'metadata': output.get('metadata', {})
            }
        }
        
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)
    
    def load(self, stage_name: str) -> Optional[Dict[str, Any]]:
        """Load stage output from cache."""
        if not self.enabled:
            return None
        
        cache_file = self.cache_dir / f"{stage_name}.json"
        
        if not cache_file.exists():
            return None
        
        with open(cache_file) as f:
            return json.load(f)
    
    def compute_hash(self, data: str) -> str:
        """Compute content hash."""
        hasher = hashlib.new(self.hash_algorithm)
        hasher.update(data.encode('utf-8'))
        return hasher.hexdigest()
