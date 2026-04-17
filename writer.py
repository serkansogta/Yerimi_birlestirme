import html
from pathlib import Path
from readers import Bookmark


_HEADER = """\
<!DOCTYPE NETSCAPE-Bookmark-file-1>
<!-- This is an automatically generated file. Do NOT edit manually. -->
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<TITLE>Bookmarks</TITLE>
<H1>Bookmarks</H1>
<DL><p>
"""

_FOOTER = "</DL><p>\n"


def _build_tree(bookmarks: list) -> dict:
    """Build nested dict: {folder_name: {subfolders..., '__items__': [Bookmark]}}"""
    root: dict = {"__items__": []}

    def ensure_path(node: dict, parts: list) -> dict:
        for part in parts:
            node = node.setdefault(part, {"__items__": []})
        return node

    for bm in bookmarks:
        node = ensure_path(root, bm.folder_path)
        node["__items__"].append(bm)

    return root


def _emit_node(lines: list, node: dict, indent: int) -> None:
    pad = "    " * indent

    for bm in node.get("__items__", []):
        add_date = f' ADD_DATE="{bm.added}"' if bm.added else ""
        title = html.escape(bm.title or bm.url)
        href = html.escape(bm.url, quote=True)
        lines.append(f'{pad}    <DT><A HREF="{href}"{add_date}>{title}</A>')

    for key, child in node.items():
        if key == "__items__":
            continue
        folder_name = html.escape(key)
        lines.append(f"{pad}    <DT><H3>{folder_name}</H3>")
        lines.append(f"{pad}    <DL><p>")
        _emit_node(lines, child, indent + 1)
        lines.append(f"{pad}    </DL><p>")


def write_netscape_html(bookmarks: list, output_path: Path, dedup: bool = True) -> int:
    if dedup:
        from urllib.parse import urlparse, urlunparse

        def normalize(url: str) -> str:
            try:
                p = urlparse(url.strip())
                return urlunparse((p.scheme.lower(), p.netloc.lower(), p.path, p.params, p.query, ""))
            except Exception:
                return url.strip().lower()

        seen: set = set()
        deduped = []
        for bm in bookmarks:
            key = normalize(bm.url)
            if key not in seen:
                seen.add(key)
                deduped.append(bm)
        bookmarks = deduped

    # Group by browser
    by_browser: dict = {}
    for bm in bookmarks:
        by_browser.setdefault(bm.browser, []).append(bm)

    lines = [_HEADER.rstrip("\n")]

    for browser_name in sorted(by_browser):
        bms = by_browser[browser_name]
        tree = _build_tree(bms)
        lines.append(f"    <DT><H3>{html.escape(browser_name)}</H3>")
        lines.append("    <DL><p>")
        _emit_node(lines, tree, 0)
        lines.append("    </DL><p>")

    lines.append(_FOOTER.rstrip("\n"))

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(bookmarks)
