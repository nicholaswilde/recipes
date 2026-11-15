#!/usr/bin/env python3
"""Audit docs/ recipes for missing, corrupt, low-res, or duplicate heroes."""

import argparse
import collections
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import check_missing_images as cmi  # noqa: E402


def extract_embeds(text: str) -> list[str]:
    """Extract body image embed paths from markdown text.

    Args:
        text: Full markdown file contents.

    Returns:
        List of raw image URLs or relative paths found in ![...] embeds.
    """
    refs = {
        m.group(1): m.group(2).strip()
        for m in re.finditer(r"^\[([^\]]+)\]:\s*<?([^>\s\n]+)>?", text, re.M)
    }
    embeds: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("!["):
            continue
        m_ref = re.match(r"!\[[^\]]*\]\[([^\]]+)\]", stripped)
        m_inl = re.match(r"!\[[^\]]*\]\((.+?)\)(?:\{.*\})?$", stripped)
        if m_ref and m_ref.group(1) in refs:
            embeds.append(refs[m_ref.group(1)])
        elif m_inl:
            embeds.append(m_inl.group(1))
    return embeds


def resolve_image_path(
    filepath: str, hero: str, embeds: list[str]
) -> str | None:
    """Resolve the primary image file path on disk for a recipe.

    Args:
        filepath: Path to the recipe markdown file.
        hero: Hero field from YAML frontmatter.
        embeds: Extracted body image embed paths.

    Returns:
        Normalized filesystem path if resolvable, else None.
    """
    if hero:
        _, resolved, is_corrupt = cmi.resolve_hero_image(filepath, hero)
        if is_corrupt:
            return None
        if os.path.isfile(resolved):
            return os.path.normpath(resolved)
        return os.path.normpath(os.path.join(cmi.DOCS_DIR, hero))
    if embeds and not embeds[0].startswith("http"):
        return os.path.normpath(
            os.path.join(os.path.dirname(filepath), embeds[0])
        )
    return None


def scan_recipes(
    min_dim: int = 300, min_bytes: int = 5000
) -> dict[str, Any]:
    """Scan recipe files in docs/ for hero image generation candidates.

    Args:
        min_dim: Minimum acceptable pixel width or height.
        min_bytes: Minimum acceptable image file size in bytes.

    Returns:
        Dictionary categorizing corrupt, missing, low_res, duplicate_hashes,
        no_hero, mismatches, and non_webp recipes.
    """
    recipe_files = cmi.find_recipe_files()
    corrupt: list[dict[str, Any]] = []
    missing: list[dict[str, Any]] = []
    low_res: list[dict[str, Any]] = []
    no_hero: list[str] = []
    mismatches: list[dict[str, str]] = []
    non_webp: list[str] = []
    hash_groups: dict[str, list[str]] = collections.defaultdict(list)

    for filepath in recipe_files:
        relpath = os.path.relpath(filepath, cmi.REPO_ROOT)
        frontmatter = cmi.parse_frontmatter(filepath)
        hero = frontmatter.get("hero", "")
        with open(filepath, "r", encoding="utf-8") as fh:
            embeds = extract_embeds(fh.read())

        if not hero:
            no_hero.append(relpath)

        if hero and embeds and not embeds[0].startswith("http"):
            hero_norm = os.path.normpath(os.path.join(cmi.DOCS_DIR, hero))
            embed_norm = os.path.normpath(
                os.path.join(os.path.dirname(filepath), embeds[0])
            )
            if hero_norm != embed_norm:
                mismatches.append(
                    {"file": relpath, "hero": hero, "embed": embeds[0]}
                )

        img_path = resolve_image_path(filepath, hero, embeds)
        if not img_path or not os.path.isfile(img_path):
            missing.append({"file": relpath, "image": img_path or hero})
            continue

        if not img_path.lower().endswith(".webp"):
            non_webp.append(relpath)

        size = os.path.getsize(img_path)
        with open(img_path, "rb") as bf:
            digest = hashlib.sha256(bf.read()).hexdigest()
        hash_groups[digest].append(relpath)

        try:
            with Image.open(img_path) as img:
                img.verify()
            with Image.open(img_path) as img:
                width, height = img.size
            if min(width, height) < min_dim or size < min_bytes:
                low_res.append({
                    "file": relpath,
                    "width": width,
                    "height": height,
                    "bytes": size,
                })
        except Exception as exc:  # noqa: BLE001
            corrupt.append({
                "file": relpath,
                "image": os.path.relpath(img_path, cmi.REPO_ROOT),
                "bytes": size,
                "error": str(exc),
            })

    duplicates = [
        {"hash": h[:12], "files": files}
        for h, files in sorted(
            hash_groups.items(), key=lambda item: -len(item[1])
        )
        if len(files) > 1
    ]

    return {
        "total_recipes": len(recipe_files),
        "corrupt": corrupt,
        "missing": missing,
        "low_res": sorted(low_res, key=lambda x: x["width"] * x["height"]),
        "duplicates": duplicates,
        "no_hero": no_hero,
        "mismatches": mismatches,
        "non_webp_count": len(non_webp),
    }


def print_report(report: dict[str, Any]) -> None:
    """Print a concise summary report of hero image candidates."""
    print(f"Scanned {report['total_recipes']} recipes in docs/\n")

    sections = [
        ("Corrupt / Non-Image Files", report["corrupt"]),
        ("Missing Image Files", report["missing"]),
        ("Low-Res / Small Images", report["low_res"]),
        ("Duplicate Image Groups", report["duplicates"]),
        ("Missing hero: Frontmatter", report["no_hero"]),
        ("Hero vs Embed Mismatches", report["mismatches"]),
    ]
    for title, items in sections:
        print(f"== {title} ({len(items)}) ==")
        for item in items:
            if isinstance(item, str):
                print(f"  - {item}")
            elif "files" in item:
                print(f"  - [{item['hash']}] " + " | ".join(item["files"]))
            elif "width" in item:
                print(
                    f"  - {item['file']} "
                    f"({item['width']}x{item['height']}, {item['bytes']} B)"
                )
            elif "embed" in item:
                print(
                    f"  - {item['file']} "
                    f"(hero={item['hero']} vs embed={item['embed']})"
                )
            else:
                print(f"  - {item['file']} -> {item['image']}")
        print()
    print(f"Non-WebP hero images: {report['non_webp_count']}")


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Identify recipe hero images to generate or fix."
    )
    parser.add_argument(
        "--min-dim", type=int, default=300, help="Min pixel width/height."
    )
    parser.add_argument(
        "--min-bytes", type=int, default=5000, help="Min file size in bytes."
    )
    parser.add_argument(
        "--json", action="store_true", help="Output JSON report."
    )
    args = parser.parse_args()

    report = scan_recipes(min_dim=args.min_dim, min_bytes=args.min_bytes)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_report(report)


if __name__ == "__main__":
    main()
