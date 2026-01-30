"""
Simple caching utilities for the analyzer.
"""

import hashlib
import json
import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

from district_pathway_analyzer.config import get_config

logger = logging.getLogger(__name__)


class Cache:
    """Simple SQLite-based cache for discovery results."""

    def __init__(self, db_path: Optional[str] = None):
        """Initialize the cache.

        Args:
            db_path: Path to SQLite database file. Defaults to cache/cache.db
        """
        self.config = get_config()

        if db_path:
            self.db_path = Path(db_path)
        else:
            self.db_path = Path("cache/cache.db")

        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize the database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    created_at TEXT,
                    expires_at TEXT
                )
                """
            )
            conn.commit()

    def _make_key(self, key: str) -> str:
        """Create a hash key from the input.

        Args:
            key: The cache key

        Returns:
            Hashed key
        """
        return hashlib.sha256(key.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache.

        Args:
            key: The cache key

        Returns:
            Cached value or None if not found/expired
        """
        if not self.config.discovery.cache_enabled:
            return None

        hashed_key = self._make_key(key)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT value, expires_at FROM cache WHERE key = ?",
                (hashed_key,),
            )
            row = cursor.fetchone()

            if not row:
                return None

            value, expires_at = row

            # Check expiration
            if datetime.fromisoformat(expires_at) < datetime.now():
                self.delete(key)
                return None

            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value

    def set(self, key: str, value: Any, ttl_days: Optional[int] = None):
        """Set a value in the cache.

        Args:
            key: The cache key
            value: The value to cache
            ttl_days: Time to live in days. Defaults to config value.
        """
        if not self.config.discovery.cache_enabled:
            return

        hashed_key = self._make_key(key)
        ttl = ttl_days or self.config.discovery.cache_ttl_days

        created_at = datetime.now()
        expires_at = created_at + timedelta(days=ttl)

        # Serialize value
        if isinstance(value, (dict, list)):
            serialized = json.dumps(value, default=str)
        else:
            serialized = str(value)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO cache (key, value, created_at, expires_at)
                VALUES (?, ?, ?, ?)
                """,
                (hashed_key, serialized, created_at.isoformat(), expires_at.isoformat()),
            )
            conn.commit()

    def delete(self, key: str):
        """Delete a value from the cache.

        Args:
            key: The cache key
        """
        hashed_key = self._make_key(key)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM cache WHERE key = ?", (hashed_key,))
            conn.commit()

    def clear(self):
        """Clear all cache entries."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM cache")
            conn.commit()

    def cleanup_expired(self):
        """Remove expired cache entries."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "DELETE FROM cache WHERE expires_at < ?",
                (datetime.now().isoformat(),),
            )
            conn.commit()
