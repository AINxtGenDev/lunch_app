"""
Caching utilities
"""

def cache_key_prefix():
    """Generate cache key prefix based on date"""
    from datetime import datetime
    return f"menu_{datetime.now().date()}"
