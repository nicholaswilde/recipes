#!/usr/bin/env python3
"""Sync includes/weights.yaml from docs/reference/measuring.md for cook-docs."""

import argparse
import re
import sys
import unicodedata
from pathlib import Path

import yaml

DEFAULT_MEASURING_PATH = Path("docs/reference/measuring.md")
DEFAULT_WEIGHTS_PATH = Path("includes/weights.yaml")

# Parenthetical qualifiers that fundamentally alter density (skip base-name alias)
TRANSFORMATIVE_PARENS = {
    "powdered",
    "dried",
    "dehydrated",
    "instant",
    "paste",
    "puree",
    "purée",
    "juice",
    "oil",
    "butter",
    "flour",
    "meal",
    "syrup",
    "sauce",
    "jam",
    "cooked",
    "uncooked",
    "dry",
    "roasted",
    "toasted",
    "fried",
    "canned",
    "frozen",
    "concentrate",
    "blanched",
    "unsweetened",
    "sweetened",
}

# Spices, herbs, and seasonings omitted for tsp/tbsp per AGENTS.md.
EXCLUDE_SMALL_UNITS = [
    "allspice",
    "basil",
    "bay",
    "caraway",
    "cardamom",
    "cayenne",
    "chives",
    "cinnamon",
    "cloves",
    "coriander",
    "cumin",
    "curry",
    "dill",
    "fennel",
    "ginger",
    "marjoram",
    "nutmeg",
    "oregano",
    "paprika",
    "parsley",
    "pepper",
    "peppercorn",
    "peppercorns",
    "rosemary",
    "saffron",
    "sage",
    "salt",
    "seasoning",
    "spice",
    "tarragon",
    "thyme",
    "turmeric",
]

# Compound ingredient tokens that bypass exclude_small_units (cook-docs >= v0.9.7),
# so items like "basil pesto", "cinnamon sugar", "baker's cinnamon filling",
# "cinnamon sweet bits", "crystallized ginger", and "mini diced ginger" still convert.
EXCLUDE_SMALL_UNITS_EXCEPT = [
    "bits",
    "crystallized",
    "filling",
    "mini",
    "oil",
    "paste",
    "pesto",
    "sauce",
    "sugar",
    "syrup",
]

UNICODE_FRACTIONS = {
    "¼": " 1/4",
    "½": " 1/2",
    "¾": " 3/4",
    "⅓": " 1/3",
    "⅔": " 2/3",
    "⅛": " 1/8",
    "⅜": " 3/8",
    "⅝": " 5/8",
    "⅞": " 7/8",
}

CUPS_PER_UNIT = {
    "cup": 1.0,
    "cups": 1.0,
    "c": 1.0,
    "tbsp": 1.0 / 16.0,
    "tablespoon": 1.0 / 16.0,
    "tablespoons": 1.0 / 16.0,
    "tsp": 1.0 / 48.0,
    "teaspoon": 1.0 / 48.0,
    "teaspoons": 1.0 / 48.0,
    "fl oz": 1.0 / 8.0,
    "fl. oz": 1.0 / 8.0,
    "fluid oz": 1.0 / 8.0,
    "fluid ounce": 1.0 / 8.0,
    "fluid ounces": 1.0 / 8.0,
    "pt": 2.0,
    "pint": 2.0,
    "pints": 2.0,
    "qt": 4.0,
    "quart": 4.0,
    "quarts": 4.0,
    "gal": 16.0,
    "gallon": 16.0,
    "gallons": 16.0,
    "ml": 1.0 / 236.588236,
    "milliliter": 1.0 / 236.588236,
    "milliliters": 1.0 / 236.588236,
    "l": 1000.0 / 236.588236,
    "liter": 1000.0 / 236.588236,
    "liters": 1000.0 / 236.588236,
}


def normalize_text(text: str) -> str:
    """Strip soft hyphens/zero-width chars and normalize punctuation/fractions."""
    text = text.replace("\u00ad", "").replace("\u200b", "").replace("\ufeff", "")
    text = text.replace("\u00a0", " ")
    text = text.replace("\u2019", "'").replace("\u2018", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2013", "-").replace("\u2014", "-")
    for uf, repl in UNICODE_FRACTIONS.items():
        text = text.replace(uf, repl)
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", text)).strip()


def strip_md_links(text: str) -> str:
    """Replace Markdown links [label](url) or [label][ref] with plain label."""
    return re.sub(r"\[([^\]]+)\](?:\([^)]*\)|\[[^\]]*\])", r"\1", text)


def parse_quantity(qty_str: str) -> float:
    """Parse integer, decimal, fraction, or mixed number string to float."""
    total = 0.0
    for part in qty_str.strip().split():
        if "/" in part:
            num, den = part.split("/", 1)
            den_f = float(den)
            if den_f != 0:
                total += float(num) / den_f
        else:
            total += float(part)
    return total


def build_weights_data(measuring_path: Path) -> dict:
    """Parse Ingredient Weight Chart from measuring.md into cook-docs YAML dict."""
    raw_entries: dict[str, dict] = {}
    in_chart = False
    in_table = False

    with measuring_path.open("r", encoding="utf-8") as fh:
        for raw_line in fh:
            line = normalize_text(raw_line)
            if line.startswith("## ") and "ingredient weight chart" in line.lower():
                in_chart = True
                continue
            if in_chart and line.startswith("## "):
                break
            if not in_chart:
                continue
            if line.startswith("| Ingredient"):
                in_table = True
                continue
            if not in_table:
                continue
            if not line.startswith("|"):
                if line:
                    in_table = False
                continue

            parts = [p.strip() for p in line.split("|")]
            if len(parts) < 5:
                continue
            name = strip_md_links(parts[1]).strip().lower()
            volume = parts[2].strip()
            grams_str = parts[3].strip()
            if not name or name.startswith("-") or name == "ingredient":
                continue
            if not grams_str or grams_str == "-":
                continue

            nums = re.findall(r"\d+(?:\.\d+)?", grams_str)
            if not nums:
                continue
            grams = float(nums[0])
            if grams <= 0:
                continue

            m_vol = re.match(
                r"^(\d+(?:\s+\d+/\d+|\.\d+|/\d+)?)\s*([a-zA-Z. ]+?)(?:\s*\(|$)",
                volume,
            )
            if not m_vol:
                continue
            qty = parse_quantity(m_vol.group(1))
            unit_key = m_vol.group(2).strip().lower().rstrip(".")
            cups_factor = CUPS_PER_UNIT.get(unit_key)
            if not cups_factor or qty <= 0:
                continue

            grams_per_cup = round(grams / (qty * cups_factor), 4)
            if grams_per_cup == int(grams_per_cup):
                grams_per_cup = int(grams_per_cup)
            raw_entries[name] = {"grams_per_cup": grams_per_cup}

    # Add safe base-name aliases when not colliding with an existing explicit key
    existing_keys = set(raw_entries.keys())
    claimed_aliases: set[str] = set()
    weights: dict[str, object] = {}

    for name in sorted(raw_entries):
        gpc = raw_entries[name]["grams_per_cup"]
        aliases: list[str] = []
        m_paren = re.match(r"^([^\(,]+?)\s*\(([^)]+)\)\s*$", name)
        if m_paren:
            base = m_paren.group(1).strip()
            paren = m_paren.group(2).lower()
            if (
                base
                and base not in existing_keys
                and base not in claimed_aliases
                and not any(t in paren for t in TRANSFORMATIVE_PARENS)
            ):
                aliases.append(base)
                claimed_aliases.add(base)

        if aliases:
            weights[name] = {"grams_per_cup": gpc, "aliases": aliases}
        else:
            weights[name] = gpc

    return {
        "exclude_small_units": sorted(EXCLUDE_SMALL_UNITS),
        "exclude_small_units_except": sorted(EXCLUDE_SMALL_UNITS_EXCEPT),
        "weights": weights,
    }


def write_weights_yaml(data: dict, output_path: Path) -> None:
    """Write deterministic yamllint-clean weights YAML file."""
    header = (
        "---\n"
        "# Auto-generated from docs/reference/measuring.md\n"
        "# Run `task sync-weights` after editing the Ingredient Weight Chart.\n"
    )
    body = yaml.safe_dump(
        data,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(header + body, encoding="utf-8")


def main() -> int:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="Generate includes/weights.yaml from docs/reference/measuring.md."
    )
    parser.add_argument(
        "--measuring",
        type=Path,
        default=DEFAULT_MEASURING_PATH,
        help="Path to measuring.md (default: docs/reference/measuring.md)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_WEIGHTS_PATH,
        help="Output YAML path (default: includes/weights.yaml)",
    )
    args = parser.parse_args()

    if not args.measuring.is_file():
        print(f"Error: {args.measuring} not found", file=sys.stderr)
        return 1

    data = build_weights_data(args.measuring)
    write_weights_yaml(data, args.output)
    print(f"Generated {args.output} with {len(data['weights'])} weight entries.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
