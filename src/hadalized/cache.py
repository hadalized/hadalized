"""Application cache layer."""

import sqlite3
from typing import TYPE_CHECKING, Self

from loguru import logger

if TYPE_CHECKING:
    from pathlib import Path

from hadalized.options import Options


class Cache:
    """Caching layer."""

    def __init__(self, opts: Options | None = None):
        """Create a new instance.

        Args:
            opts: Runtime options controlling location of cache, whether to
               use it, etc.

        """
        self.opt = opts or Options()
        self.cache_dir: Path = self.opt.cache_dir
        self._db_file: Path = self.cache_dir / "builds.db"
        if not self.opt.cache_in_memory:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._conn: sqlite3.Connection

    def _setup(self):
        with self._conn:
            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS
                digests(path TEXT PRIMARY KEY, digest TEXT)""")
            # self._conn.execute("""
            #     CREATE TABLE IF NOT EXISTS
            #     palettes(name TEXT PRIMARY KEY, data TEXT)""")

    def connect(self) -> Self:
        """Connect to the underlying sqlite database.

        Returns:
            The connected instance.

        """
        file = ":memory:" if self.opt.cache_in_memory else self._db_file
        self._conn = sqlite3.connect(file)
        self._setup()
        return self

    def close(self):
        """Close the database connection."""
        self._conn.close()

    def add(self, path: str | Path, digest: str):
        """Add a (path, hash hexdigest) to the database.

        Used after a file is successfully generated to store a proxy for
        the contents of the generated file.
        """
        with self._conn:
            self._conn.execute(
                """INSERT INTO digests VALUES(:path, :digest)
                ON CONFLICT(path) DO UPDATE SET digest=:digest""",
                {
                    "path": str(path),
                    "digest": digest,
                },
            )

    def delete(self, path: str | Path):
        """Remove a cache entry."""
        with self._conn:
            self._conn.execute(
                """DELETE FROM digests WHERE path == ?""",
                [str(path)],
            )

    def get(self, path: str | Path) -> str | None:
        """Get a build digest for the input path.

        Returns:
            A hash (proxy) of the previously generated file or None if no
            record is found.

        """
        with self._conn:
            cur = self._conn.execute(
                """SELECT digest FROM digests WHERE path == ? LIMIT 1""",
                [str(path)],
            )
            data = cur.fetchone()
        return data[0] if isinstance(data, tuple) else None

    def get_digests(self) -> dict[str, str]:
        """Obtain the contents of all cache build digests as a mapping.

        Returns:
            Mapping of path -> hash digest for all paths in the cache.

        """
        with self._conn:
            return dict(self._conn.execute("SELECT * from digests"))

    def __enter__(self) -> Self:
        """Connect to the database.

        Returns:
            The connected instance.

        """
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Close the database connection."""
        if exc_type is not None:
            logger.error((exc_type, exc_value, traceback))
        self.close()
