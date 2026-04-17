import json
import sqlite3
import logging
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Bookmark:
    title: str
    url: str
    browser: str
    folder_path: list = field(default_factory=list)
    added: int | None = None


# Chrome epoch: microseconds since 1601-01-01
_CHROME_EPOCH_OFFSET = 11644473600


def _chrome_ts_to_unix(ts_str: str) -> int | None:
    try:
        ts = int(ts_str)
        if ts == 0:
            return None
        return int(ts / 1_000_000) - _CHROME_EPOCH_OFFSET
    except (ValueError, TypeError):
        return None


def _walk_chromium_node(node: dict, path: list, browser: str, results: list) -> None:
    node_type = node.get("type")
    if node_type == "url":
        results.append(Bookmark(
            title=node.get("name", ""),
            url=node.get("url", ""),
            browser=browser,
            folder_path=list(path),
            added=_chrome_ts_to_unix(node.get("date_added", "0")),
        ))
    elif node_type == "folder":
        folder_name = node.get("name", "")
        new_path = path + [folder_name] if folder_name else path
        for child in node.get("children", []):
            _walk_chromium_node(child, new_path, browser, results)


def read_chromium(path: Path, browser: str = "Chrome") -> list:
    data = json.loads(path.read_text(encoding="utf-8"))
    results = []
    roots = data.get("roots", {})
    for root_key in ("bookmark_bar", "other", "synced"):
        root_node = roots.get(root_key)
        if root_node:
            _walk_chromium_node(root_node, [], browser, results)
    return results


def read_firefox(path: Path, browser: str = "Firefox") -> list:
    conn = sqlite3.connect(f"file:{path}?mode=ro&immutable=1", uri=True)
    try:
        cur = conn.cursor()

        # Build folder id -> (title, parent_id) map
        cur.execute(
            "SELECT id, title, parent FROM moz_bookmarks WHERE type = 2"
        )
        folders = {row[0]: (row[1] or "", row[2]) for row in cur.fetchall()}

        def get_folder_path(folder_id: int) -> list:
            path_parts = []
            visited = set()
            fid = folder_id
            while fid and fid not in visited:
                visited.add(fid)
                info = folders.get(fid)
                if info is None:
                    break
                title, parent_id = info
                if title:
                    path_parts.append(title)
                fid = parent_id
            path_parts.reverse()
            # Strip top-level virtual root names that Firefox adds internally
            skip = {"", "root________", "menu________", "toolbar_____",
                    "unfiled_____", "mobile______", "places"}
            return [p for p in path_parts if p not in skip]

        # Fetch all URL bookmarks joined with places
        cur.execute("""
            SELECT b.title, p.url, b.parent, b.dateAdded
            FROM moz_bookmarks b
            JOIN moz_places p ON b.fk = p.id
            WHERE b.type = 1
        """)
        results = []
        for title, url, parent_id, date_added in cur.fetchall():
            try:
                unix_added = int(date_added / 1_000_000) if date_added else None
            except (TypeError, ValueError):
                unix_added = None
            results.append(Bookmark(
                title=title or url,
                url=url,
                browser=browser,
                folder_path=get_folder_path(parent_id),
                added=unix_added,
            ))
        return results
    finally:
        conn.close()
