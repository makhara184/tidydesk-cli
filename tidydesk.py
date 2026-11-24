#!/usr/bin/env python3
"""TidyDesk CLI — Smart Folder Organizer, Duplicate Finder, and Undo Utility."""

import argparse
import hashlib
import json
import shutil
from collections import defaultdict
from pathlib import Path

DEFAULT_RULES = {
    "Documents": [".pdf", ".docx", ".doc", ".txt", ".md", ".xlsx", ".csv", ".pptx"],
    "Images": [".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"],
    "Audio": [".mp3", ".wav", ".m4a", ".flac"],
    "Video": [".mp4", ".mov", ".mkv", ".avi"],
    "Archives": [".zip", ".tar", ".gz", ".rar", ".7z"],
    "Code": [".py", ".js", ".ts", ".html", ".css", ".json", ".swift"],
}

MANIFEST_NAME = ".tidydesk_manifest.json"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def find_duplicates(target: Path) -> dict[str, list[Path]]:
    hashes: dict[str, list[Path]] = defaultdict(list)
    for item in sorted(target.rglob("*")):
        if item.is_file() and item.name != MANIFEST_NAME:
            hashes[sha256_file(item)].append(item)
    return {k: v for k, v in hashes.items() if len(v) > 1}


def resolve_category(ext: str, rules: dict[str, list[str]]) -> str:
    ext_lower = ext.lower()
    for category, extensions in rules.items():
        if ext_lower in [e.lower() for e in extensions]:
            return category
    return "Other"


def organize_folder(target: Path, rules: dict[str, list[str]], dry_run: bool = False) -> list[dict]:
    moves = []
    for item in sorted(target.iterdir()):
        if not item.is_file() or item.name == MANIFEST_NAME or item.name.startswith("."):
            continue
        category = resolve_category(item.suffix, rules)
        dest_dir = target / category
        dest_path = dest_dir / item.name
        counter = 1
        while dest_path.exists():
            dest_path = dest_dir / f"{item.stem}_{counter}{item.suffix}"
            counter += 1
        moves.append({"src": str(item), "dst": str(dest_path)})
        if not dry_run:
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(item), str(dest_path))

    if not dry_run and moves:
        (target / MANIFEST_NAME).write_text(json.dumps(moves, indent=2), encoding="utf-8")
    return moves


def undo_last(target: Path) -> int:
    manifest = target / MANIFEST_NAME
    if not manifest.exists():
        return 0
    moves = json.loads(manifest.read_text(encoding="utf-8"))
    restored = 0
    for entry in reversed(moves):
        src, dst = Path(entry["src"]), Path(entry["dst"])
        if dst.exists():
            src.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(dst), str(src))
            restored += 1
    manifest.unlink(missing_ok=True)
    return restored


def main():
    parser = argparse.ArgumentParser(description="TidyDesk CLI — Organize folders cleanly.")
    parser.add_argument("target", type=Path, help="Target directory to organize or scan")
    parser.add_argument("--rules", type=Path, help="Optional JSON rules file")
    parser.add_argument("--dry-run", action="store_true", help="Preview moves without modifying files")
    parser.add_argument("--duplicates", action="store_true", help="Scan for duplicate files by SHA-256")
    parser.add_argument("--undo", action="store_true", help="Undo the last organize operation")
    args = parser.parse_args()

    if not args.target.is_dir():
        raise SystemExit(f"Error: {args.target} is not a directory.")

    if args.undo:
        count = undo_last(args.target)
        print(f"Restored {count} file(s).")
        return

    if args.duplicates:
        dupes = find_duplicates(args.target)
        if not dupes:
            print("No duplicate files found.")
        else:
            for digest, paths in dupes.items():
                print(f"Duplicate group ({digest[:10]}...):")
                for p in paths:
                    print(f"  - {p}")
        return

    rules = json.loads(args.rules.read_text(encoding="utf-8")) if args.rules else DEFAULT_RULES
    moves = organize_folder(args.target, rules, dry_run=args.dry_run)
    prefix = "[DRY RUN] " if args.dry_run else ""
    for m in moves:
        print(f"{prefix}{Path(m['src']).name} -> {Path(m['dst']).parent.name}/{Path(m['dst']).name}")
    print(f"{prefix}Processed {len(moves)} file(s).")


if __name__ == "__main__":
    main()
