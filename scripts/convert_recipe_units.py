#!/usr/bin/env python3

################################################################################
#
# convert_recipe_units.py
# ----------------
# Convert recipe measurements between volume and weight and inject emojis
#
# @author nιcнolaѕ wιlde, 0x08b7d7a3
# @date 02 Jun 2026
# @version 0.2.0
#
################################################################################

import os
import re
import sys

EMOJI_YAML_PATH = "includes/emoji.yaml"
MEASURING_MD_PATH = "docs/reference/measuring.md"

KNOWN_UNITS = {
    "cup", "cups", "c",
    "tbsp", "tablespoon", "tablespoons",
    "tsp", "teaspoon", "teaspoons",
    "fl", "fl.", "fluid",
    "pint", "pints", "pt",
    "quart", "quarts", "qt",
    "gallon", "gallons", "gal",
    "g", "gram", "grams",
    "ml", "milliliter", "milliliters",
    "l", "liter", "liters",
    "oz", "ounce", "ounces",
    "lb", "lbs", "pound", "pounds",
    "kg", "kilogram", "kilograms",
    "can", "cans", "clove", "cloves",
    "pinch", "pinches", "slice", "slices",
    "package", "packages", "bag", "bags",
    "head", "heads", "bunch", "bunches",
    "sprig", "sprigs", "piece", "pieces",
    "large", "medium", "small",
    "handful", "handfuls", "ear", "ears",
}

SMALL_VOLUME_UNITS = {
    "tsp", "teaspoon", "teaspoons",
    "tbsp", "tablespoon", "tablespoons",
}

WEIGHT_UNITS = {
    "g", "gram", "grams",
    "kg", "kilogram", "kilograms",
    "oz", "ounce", "ounces",
    "lb", "lbs", "pound", "pounds",
}

SEASONING_OR_SPICE_WORDS = {
    "salt", "pepper", "peppercorns", "peppercorn",
    "coriander", "cumin", "turmeric", "cinnamon",
    "oregano", "thyme", "basil", "parsley", "rosemary",
    "paprika", "cayenne", "nutmeg", "cardamom", "allspice",
    "cloves", "ginger", "curry", "seasoning", "spice",
    "fennel", "caraway", "dill", "sage", "chives",
    "marjoram", "tarragon", "bay", "saffron",
}

PREP_WORDS = {
    "fresh", "freshly", "squeezed", "chopped", "pitted", "sliced",
    "slivered", "diced", "minced", "grated", "melted", "softened",
    "packed", "sifted", "unsifted", "extra", "topping", "some",
    "cold", "warm", "hot", "very", "room", "temperature",
    "large", "medium", "small", "raw", "organic", "pure",
    "and", "or", "with", "of", "in", "for", "to", "taste",
}

QUALIFIER_WORDS = {
    "dried", "dry", "powdered", "powder", "mix", "shortening",
    "paste", "extract", "syrup", "oil", "flour", "starch",
    "meal", "flakes", "chips", "mashed", "cooked", "canned",
    "concentrate", "frozen", "toasted", "roasted", "candied",
    "condensed", "evaporated", "whipped", "sweetened", "unsweetened",
    "stock", "broth", "juice", "sauce", "vinegar",
}

TRANSFORMATIVE_PARENS = {
    "powdered", "dried", "dry", "mashed", "cooked", "canned",
    "melted", "frozen", "dehydrated", "instant",
}

SKIP_ONE_QTY_INGREDIENTS = {
    "salt", "kosher salt", "sea salt", "table salt", "black pepper",
    "freshly ground black pepper", "ground black pepper", "pepper",
    "sugar (optional)", "sugar (if necessary)", "sugar to taste",
    "salt and pepper", "salt and black pepper",
}


def strip_md_links(text):
    """Replace Markdown inline and reference links with their display text."""
    return re.sub(r'\[([^\]]+)\](?:\([^)]+\)|\[[^\]]*\])?', r'\1', text)


def normalize_text(text):
    """Normalize typography and soft hyphens for reliable matching."""
    return text.replace("\u00ad", "").replace("\u2019", "'").strip()


def singularize(word):
    """Return a simple singular form of an English food noun."""
    if word.endswith("ies") and len(word) > 4:
        return word[:-3] + "y"
    if word.endswith("es") and len(word) > 3 and not word.endswith(("ses", "xes", "zes")):
        return word[:-1] if word.endswith(("oes", "ches", "shes")) else word[:-2]
    if word.endswith("s") and len(word) > 2 and not word.endswith("ss"):
        return word[:-1]
    return word


def load_emoji_mappings(filepath):
    """Load ingredient and cookware emoji mappings from includes/emoji.yaml."""
    mappings = {
        "ingredients": {},
        "cookware": {},
    }
    current_category = None
    current_emoji = None

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line_no_comment = line.split("#")[0]
            stripped = line_no_comment.strip()
            if not stripped or stripped == "---":
                continue
            if stripped == "ingredients:":
                current_category = "ingredients"
                current_emoji = None
                continue
            if stripped == "cookware:":
                current_category = "cookware"
                current_emoji = None
                continue

            m_emoji = re.match(r'^ {4}-\s*([^:#]+):', line_no_comment)
            if m_emoji:
                current_emoji = m_emoji.group(1).strip()
                continue

            m_item = re.match(r'^\s*-\s*(.+)$', line_no_comment)
            if m_item and current_category and current_emoji:
                item_name = normalize_text(m_item.group(1).strip().strip('"\''))
                mappings[current_category][item_name.lower()] = current_emoji

    return mappings


def load_measuring_table(filepath):
    """Load the Ingredient Weight Chart from docs/reference/measuring.md."""
    table = {}
    inside_table = False

    with open(filepath, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = normalize_text(raw_line)
            stripped = line.strip()
            if stripped.startswith("| Ingredient"):
                inside_table = True
                continue
            if inside_table:
                if not stripped.startswith("|"):
                    if stripped == "":
                        continue
                    inside_table = False
                    continue
                parts = [p.strip() for p in stripped.split("|")]
                if len(parts) >= 5:
                    name = strip_md_links(parts[1]).strip()
                    volume = parts[2].strip()
                    grams = parts[3].strip()

                    if name.startswith("-") or name == "Ingredient":
                        continue

                    try:
                        if grams and grams != "-":
                            nums = re.findall(r'\d+(?:\.\d+)?', grams)
                            if nums:
                                table[name.lower()] = {
                                    "volume": volume,
                                    "grams": float(nums[0]),
                                }
                    except ValueError:
                        pass
    return table


def _clean_ingredient_for_lookup(name):
    """Strip links, optional prefix 'some ', and trailing notes for matching."""
    cleaned = normalize_text(strip_md_links(name))
    cleaned = re.sub(r'^some\s+', '', cleaned, flags=re.IGNORECASE).strip()
    return cleaned.lower()


def _tokenize(text, drop_prep=True):
    """Split text into normalized word tokens."""
    s = re.sub(r'[\(\),\-#]', ' ', text.lower())
    words = [w for w in s.split() if w]
    if drop_prep:
        words = [w for w in words if w not in PREP_WORDS]
    return words


def _build_base_key_map(table):
    """Map base names (without safe trailing parentheticals) to table keys."""
    base_map = {}
    for key in table:
        m = re.match(r'^([^\(,]+?)\s*\(([^)]+)\)\s*$', key)
        if m:
            base = m.group(1).strip()
            paren = m.group(2).lower()
            if not any(t in paren for t in TRANSFORMATIVE_PARENS):
                base_map.setdefault(base, key)
    return base_map


def find_best_match(name, mappings):
    """Find the closest emoji shortcode for an ingredient or cookware name."""
    name_lower = _clean_ingredient_for_lookup(name)
    if not name_lower:
        return None

    candidates = [
        name_lower,
        re.split(r'\s*[,(]', name_lower)[0].strip(),
        " ".join(_tokenize(re.split(r'\s*[,(]', name_lower)[0], drop_prep=True)),
    ]
    for cand in candidates:
        if not cand:
            continue
        if cand in mappings:
            return mappings[cand]
        if cand.endswith("s") and cand[:-1] in mappings:
            return mappings[cand[:-1]]
        if (cand + "s") in mappings:
            return mappings[cand + "s"]

    name_tokens = set(_tokenize(name_lower, drop_prep=True))
    if not name_tokens:
        return None

    best_key = None
    best_score = (0, 0)

    for key in mappings:
        key_tokens = set(_tokenize(key, drop_prep=True))
        intersection = name_tokens.intersection(key_tokens)
        if not intersection:
            continue
        score = (len(intersection), -abs(len(key) - len(name_lower)))
        if score > best_score:
            best_score = score
            best_key = key

    return mappings[best_key] if best_key else None


def find_best_key(name, table):
    """Find a reliable measuring table key without false cross-category matches."""
    name_lower = _clean_ingredient_for_lookup(name)
    if not name_lower:
        return None

    base_map = _build_base_key_map(table)
    base_name = re.split(r'\s*[,(]', name_lower)[0].strip()
    stripped_name = " ".join(_tokenize(base_name, drop_prep=True))

    for cand in (name_lower, base_name, stripped_name):
        if not cand:
            continue
        for lookup in (cand, cand[:-1] if cand.endswith("s") else "", cand + "s"):
            if lookup and lookup in table:
                return lookup
            if lookup and lookup in base_map:
                return base_map[lookup]

    cand_tokens = _tokenize(base_name, drop_prep=True)
    if not cand_tokens:
        return None

    cand_set = {singularize(t) for t in cand_tokens}
    cand_head = singularize(cand_tokens[-1])
    cand_qualifiers = cand_set.intersection(QUALIFIER_WORDS)

    best_key = None
    best_score = (0.0, -999)

    for key in table:
        key_base = re.split(r'\s*[,(]', key)[0].strip()
        key_tokens = _tokenize(key_base, drop_prep=True)
        if not key_tokens:
            continue

        key_all_tokens = {singularize(t) for t in _tokenize(key, drop_prep=True)}
        key_set = {singularize(t) for t in key_tokens}
        key_head = singularize(key_tokens[-1])

        if cand_head != key_head:
            continue

        # Reject if the table entry introduces a qualifier absent from candidate
        # (e.g. "dried whole milk (powdered)" for "whole milk").
        key_qualifiers = key_all_tokens.intersection(QUALIFIER_WORDS)
        if key_qualifiers - cand_qualifiers or cand_qualifiers - key_qualifiers:
            continue

        # For two-word "X seeds" / "X flour" entries, require modifier overlap.
        overlap = cand_set.intersection(key_set)
        if len(key_set) >= 2 and len(overlap) < len(key_set):
            continue

        coverage = len(overlap) / max(len(cand_set), len(key_set))
        if coverage < 0.5:
            continue

        score = (coverage, -abs(len(key_base) - len(base_name)))
        if score > best_score:
            best_score = score
            best_key = key

    return best_key


def parse_quantity(qty_str):
    """Parse integers, decimals, fractions, or mixed numbers into a float."""
    qty_str = qty_str.strip()
    total = 0.0
    for part in qty_str.split():
        if "/" in part:
            p = part.split("/", 1)
            try:
                denom = float(p[1])
                if denom != 0:
                    total += float(p[0]) / denom
            except ValueError:
                pass
        else:
            try:
                total += float(part)
            except ValueError:
                pass
    return total


def get_volume_in_cups(qty, unit):
    """Convert a volumetric measurement to US cups; return None for non-volumes."""
    unit_lower = unit.lower().strip().rstrip(".")
    if unit_lower in {"cup", "cups", "c"}:
        return qty
    if unit_lower in {"tbsp", "tablespoon", "tablespoons"}:
        return qty / 16.0
    if unit_lower in {"tsp", "teaspoon", "teaspoons"}:
        return qty / 48.0
    if unit_lower in {"fl oz", "fl. oz", "fluid oz", "fluid ounce", "fluid ounces"}:
        return qty / 8.0
    if unit_lower in {"pt", "pint", "pints"}:
        return qty * 2.0
    if unit_lower in {"qt", "quart", "quarts"}:
        return qty * 4.0
    if unit_lower in {"gal", "gallon", "gallons"}:
        return qty * 16.0
    if unit_lower in {"ml", "milliliter", "milliliters"}:
        return qty / 236.588
    if unit_lower in {"l", "liter", "liters"}:
        return (qty * 1000.0) / 236.588
    return None


def _is_small_seasoning_or_spice(unit, name):
    """Return True when AGENTS.md omits grams for small spice/herb/salt amounts."""
    if unit.lower().strip().rstrip(".") not in SMALL_VOLUME_UNITS:
        return False
    tokens = set(_tokenize(re.split(r'\s*[,(]', name)[0], drop_prep=False))
    if tokens.intersection({"pesto", "oil", "butter", "paste", "sauce", "extract", "syrup", "honey", "sugar", "jam"}):
        return False
    return bool(tokens.intersection(SEASONING_OR_SPICE_WORDS))


def convert_ingredient(qty_str, unit, name, measuring_table):
    """Convert an ingredient quantity + unit to integer grams if possible."""
    if not unit:
        return None
    unit_lower = unit.lower().strip().rstrip(".")
    if unit_lower in WEIGHT_UNITS:
        return None
    if _is_small_seasoning_or_spice(unit, name):
        return None

    qty = parse_quantity(qty_str)
    if qty == 0.0:
        return None

    current_cups = get_volume_in_cups(qty, unit)
    if not current_cups:
        return None

    best_key = find_best_key(name, measuring_table)
    if not best_key:
        return None

    conv = measuring_table[best_key]
    vol_text = normalize_text(conv["volume"])
    m_vol = re.match(
        r'^(\d+(?:\s+\d+/\d+|\.\d+|/\d+)?)\s*([a-zA-Z. ]+?)(?:\s*\(|$)',
        vol_text,
    )
    if not m_vol:
        return None

    conv_qty = parse_quantity(m_vol.group(1))
    conv_unit = m_vol.group(2).strip() if m_vol.group(2) else "cup"

    conv_cups = get_volume_in_cups(conv_qty, conv_unit)
    if not conv_cups or conv_cups == 0.0:
        return None

    grams_per_cup = conv["grams"] / conv_cups
    return int(round(current_cups * grams_per_cup))


def _format_ingredient_line(line, emoji_mappings, measuring_table):
    """Annotate a single ingredient bullet line with emoji and gram weight."""
    indent = re.match(r'^(\s*)', line).group(1)
    stripped = line.strip()

    clean_line = re.sub(r'^-\s*:[a-zA-Z0-9_+-]+:\s*', '- ', stripped)
    clean_line = re.sub(r'\s*\(\d+(?:\.\d+)?\s*g\)', '', clean_line, count=1)

    qty_pat = r'(?:\d+\s+\d+/\d+|\d+/\d+|\d+(?:\.\d+)?)'
    unit_pat = r'(?:fl\.?\s*oz|fluid\s+ounces?|\w+)'
    m = re.match(
        rf'^-\s*(?:({qty_pat})\s+({unit_pat})\s+(.+)|({qty_pat})\s+(.+)|(.+))$',
        clean_line,
    )
    if not m:
        return line

    qty_str, unit, name = None, None, None
    if m.group(1):
        potential_unit = m.group(2)
        unit_head = potential_unit.lower().split()[0].rstrip(".")
        if unit_head in KNOWN_UNITS:
            qty_str, unit, name = m.group(1), potential_unit, m.group(3)
        else:
            qty_str, unit, name = m.group(1), "", f"{potential_unit} {m.group(3)}"
    elif m.group(4):
        qty_str, unit, name = m.group(4), "", m.group(5)
    else:
        name = m.group(6)

    name_clean = re.sub(r'^some\s+', '', name).strip()
    name_clean_plain = strip_md_links(name_clean)
    if qty_str == "1" and not unit and name_clean_plain.lower() in SKIP_ONE_QTY_INGREDIENTS:
        qty_str = None

    emoji = find_best_match(name_clean, emoji_mappings["ingredients"])
    grams = None
    if qty_str and unit:
        grams = convert_ingredient(qty_str, unit, name_clean, measuring_table)

    emoji_str = f":{emoji}: " if emoji else ""
    if grams:
        new_line = f"- {emoji_str}{qty_str} {unit} ({grams} g) {name}\n"
    elif qty_str:
        unit_str = f" {unit}" if unit else ""
        new_line = f"- {emoji_str}{qty_str}{unit_str} {name}\n"
    else:
        new_line = f"- {emoji_str}{name}\n"

    return indent + new_line


def _format_cookware_line(line, emoji_mappings):
    """Annotate a single cookware bullet line with its matching emoji."""
    indent = re.match(r'^(\s*)', line).group(1)
    stripped = line.strip()

    clean_line = re.sub(r'^-\s*:[a-zA-Z0-9_+-]+:\s*', '- ', stripped)
    m = re.match(r'^-\s*(\d+(?:\s+\d+/\d+|\.\d+|/\d+)?\s+)?(.+)$', clean_line)
    if not m:
        return line

    count_prefix = m.group(1) or ""
    item_name = m.group(2).strip()
    emoji = find_best_match(item_name, emoji_mappings["cookware"])
    emoji_str = f":{emoji}: " if emoji else ""
    return f"{indent}- {emoji_str}{count_prefix}{item_name}\n"


def convert_markdown_file(md_path, emoji_path=EMOJI_YAML_PATH, measuring_path=MEASURING_MD_PATH):
    """Update ingredient weights/emojis and cookware emojis in a Markdown recipe."""
    emoji_mappings = load_emoji_mappings(emoji_path)
    measuring_table = load_measuring_table(measuring_path)

    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    updated_lines = []
    section = None

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            heading_lower = stripped.lower()
            if "ingredients" in heading_lower:
                section = "ingredients"
            elif "cookware" in heading_lower:
                section = "cookware"
            else:
                section = None
            updated_lines.append(line)
            continue

        if section == "ingredients" and stripped.startswith("- "):
            updated_lines.append(
                _format_ingredient_line(line, emoji_mappings, measuring_table)
            )
        elif section == "cookware" and stripped.startswith("- "):
            updated_lines.append(_format_cookware_line(line, emoji_mappings))
        else:
            updated_lines.append(line)

    with open(md_path, "w", encoding="utf-8") as f:
        f.writelines(updated_lines)


def main():
    """CLI entrypoint to annotate a compiled Markdown recipe."""
    if len(sys.argv) < 2:
        print("Usage: convert_recipe_units.py <recipe.md>")
        sys.exit(1)

    md_path = sys.argv[1]
    if not os.path.exists(md_path):
        print(f"Error: {md_path} not found")
        sys.exit(1)

    if not os.path.exists(EMOJI_YAML_PATH):
        print(f"Error: {EMOJI_YAML_PATH} not found")
        sys.exit(1)
    if not os.path.exists(MEASURING_MD_PATH):
        print(f"Error: {MEASURING_MD_PATH} not found")
        sys.exit(1)

    convert_markdown_file(md_path, EMOJI_YAML_PATH, MEASURING_MD_PATH)
    print(f"Successfully converted and updated ingredients in {md_path}")


if __name__ == "__main__":
    main()
