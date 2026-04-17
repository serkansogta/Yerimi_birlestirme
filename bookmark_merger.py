#!/usr/bin/env python3
"""Birden fazla tarayıcının yer imlerini tek bir HTML dosyasında birleştirir."""

import argparse
import logging
import sys
from pathlib import Path

import readers
import writer

BROWSER_REGISTRY = {
    "chrome":  (".config/google-chrome/Default/Bookmarks",  "Chrome",  readers.read_chromium),
    "edge":    (".config/microsoft-edge/Default/Bookmarks", "Edge",    readers.read_chromium),
    "firefox": (".mozilla/firefox/*.default*/places.sqlite", "Firefox", readers.read_firefox),
}


def _find_path(rel_pattern: str) -> Path | None:
    home = Path.home()
    if "*" in rel_pattern:
        matches = sorted(home.glob(rel_pattern), key=lambda p: p.stat().st_mtime, reverse=True)
        return matches[0] if matches else None
    p = home / rel_pattern
    return p if p.exists() else None


def _load_browser(key: str) -> list:
    rel_pattern, display_name, reader_fn = BROWSER_REGISTRY[key]
    path = _find_path(rel_pattern)
    if path is None:
        logging.info("%s: profil bulunamadı, atlanıyor", display_name)
        return []
    try:
        bms = reader_fn(path, display_name)
        logging.info("%s: %d yer imi yüklendi (%s)", display_name, len(bms), path)
        return bms
    except PermissionError:
        logging.warning("%s: erişim reddedildi: %s", display_name, path)
    except Exception as exc:
        logging.warning("%s: okuma hatası: %s", display_name, exc)
    return []


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Chrome, Edge ve Firefox yer imlerini tek bir HTML dosyasında birleştirir."
    )
    parser.add_argument(
        "--output", "-o",
        default="bookmarks_merged.html",
        help="Çıktı dosyası (varsayılan: bookmarks_merged.html)",
    )
    parser.add_argument(
        "--browsers", "-b",
        nargs="+",
        choices=list(BROWSER_REGISTRY),
        default=list(BROWSER_REGISTRY),
        metavar="TARAYICI",
        help=f"Dahil edilecek tarayıcılar: {', '.join(BROWSER_REGISTRY)}. Varsayılan: hepsi.",
    )
    parser.add_argument(
        "--no-dedup",
        action="store_true",
        help="URL tekrar elemeyi devre dışı bırak",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Ayrıntılı log göster",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(levelname)s: %(message)s",
    )

    all_bookmarks = []
    for key in args.browsers:
        all_bookmarks.extend(_load_browser(key))

    if not all_bookmarks:
        print("Hata: Hiçbir tarayıcıda yer imi bulunamadı.", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output)
    count = writer.write_netscape_html(all_bookmarks, output_path, dedup=not args.no_dedup)
    print(f"{count} yer imi '{output_path}' dosyasına yazıldı.")


if __name__ == "__main__":
    main()
