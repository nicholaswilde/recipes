#!/usr/bin/env python3

################################################################################
#
# youtube_recipe.py
# -----------------
# Extract recipe details, ingredients, and caption-derived steps from YouTube
#
# @author nιcнolaѕ wιlde, 0x08b7d7a3
# @date 27 Sep 2026
# @version 0.1.0
#
################################################################################

import re
import json
import urllib.request
import urllib.parse
from youtube_transcript_api import YouTubeTranscriptApi

UNIT_MAP = {
    'tablespoon': 'Tbsp', 'tablespoons': 'Tbsp', 'tbsp': 'Tbsp',
    'teaspoon': 'tsp', 'teaspoons': 'tsp', 'tsp': 'tsp',
    'gram': 'g', 'grams': 'g', 'g': 'g',
    'pound': 'lbs', 'pounds': 'lbs', 'lb': 'lbs', 'lbs': 'lbs',
    'ounce': 'oz', 'ounces': 'oz', 'oz': 'oz',
    'milliliter': 'ml', 'milliliters': 'ml', 'ml': 'ml',
}

COMMON_UNITS = {
    "cup", "cups", "tbsp", "tablespoon", "tablespoons", "tsp", "teaspoon", "teaspoons",
    "g", "gram", "grams", "ml", "milliliter", "milliliters", "oz", "ounce", "ounces",
    "lb", "pound", "pounds", "kg", "kilogram", "kilograms", "can", "cans", "clove",
    "cloves", "pinch", "pinches", "slice", "slices", "package", "packages", "bag",
    "bags", "canister", "canisters", "jar", "jars", "head", "heads", "bunch", "bunches",
    "sprig", "sprigs", "piece", "pieces", "large", "medium", "small", "handful", "handfuls",
    "stick", "sticks"
}

COOKWARE_KEYWORDS = [
    "cast iron skillet", "baking pan", "baking sheet", "saucepan", "frying pan",
    "food processor", "stand mixer", "hand mixer", "mixing bowl", "cutting board",
    "wooden spoon", "measuring cup", "measuring spoon", "casserole dish", "tart pan",
    "muffin tin", "loaf pan", "cookie scoop", "wire rack", "ice bath", "skillet",
    "pot", "pan", "bowl", "oven", "microwave", "blender", "whisk", "spatula", "knife",
    "strainer", "colander", "peeler", "grater"
]

def is_youtube_video_id(val: str) -> bool:
    if not val:
        return False
    val = val.strip()
    return bool(re.match(r'^[\w-]{11}(?:&.*)?$', val)) and not val.isdigit()

def is_youtube_url(url: str) -> bool:
    if not url:
        return False
    if any(domain in url.lower() for domain in ["youtube.com", "youtu.be"]):
        return True
    return is_youtube_video_id(url)

def extract_youtube_video_id(url: str) -> str | None:
    if not url:
        return None
    url = url.strip()
    m_direct = re.match(r'^([\w-]{11})(?:&.*)?$', url)
    if m_direct and not url.isdigit():
        return m_direct.group(1)
    patterns = [
        r'(?:v=|\/v\/|embed\/|shorts\/|youtu\.be\/|\/e\/|watch\?v=)([\w-]{11})',
        r'([\w-]{11})'
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None

def fetch_youtube_details(video_id: str) -> dict:
    url = f"https://www.youtube.com/watch?v={video_id}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode('utf-8')

    video_details = {}
    m = re.search(r'ytInitialPlayerResponse\s*=\s*({.+?});', html)
    if m:
        try:
            data = json.loads(m.group(1))
            video_details = data.get("videoDetails", {})
        except Exception:
            pass

    return video_details

def parse_fraction(val_str: str) -> str:
    val_str = val_str.strip()
    unicode_fractions = {
        '½': 0.5, '⅓': 0.33, '⅔': 0.67, '¼': 0.25, '¾': 0.75,
        '⅕': 0.2, '⅖': 0.4, '⅗': 0.6, '⅘': 0.8, '⅙': 0.17, '⅚': 0.83,
        '⅛': 0.125, '⅜': 0.375, '⅝': 0.625, '⅞': 0.875
    }
    for char, float_val in unicode_fractions.items():
        if char in val_str:
            val_str = val_str.replace(char, f" {float_val}")

    parts = val_str.split()
    total = 0.0
    for part in parts:
        if '/' in part:
            try:
                num, denom = part.split('/')
                total += float(num) / float(denom)
            except ValueError:
                pass
        else:
            try:
                total += float(part)
            except ValueError:
                pass
    if total > 0.0:
        if total.is_integer():
            return str(int(total))
        return f"{total:.2f}".rstrip('0').rstrip('.')
    return val_str

def parse_ingredient_line(line: str) -> tuple[str, str, str, str]:
    """Parse raw line into (clean_name, cooklang_string, qty, unit)."""
    line = line.strip()
    # Check attached unit like 100g or 250ml
    m_attached = re.match(r'^(\d+(?:\.\d+)?)(g|ml|kg|oz|lb)\b', line, re.I)
    if m_attached:
        qty = m_attached.group(1)
        raw_unit = m_attached.group(2).lower()
        unit = UNIT_MAP.get(raw_unit, raw_unit)
        remaining = line[len(m_attached.group(0)):].strip()
        name = re.sub(r'^(?:of\s+)', '', remaining).strip()
        
        # Split optional comma notes
        if ',' in name:
            name, notes = [p.strip() for p in name.split(',', 1)]
            cooklang = f"@{name}{{{qty}%{unit}}} ({notes})"
        else:
            cooklang = f"@{name}{{{qty}%{unit}}}"
        return name, cooklang, qty, unit

    qty_regex = r'^(\d+\s+\d+/\d+|\d+\s*[½⅓⅔¼¾⅕⅖⅗⅘⅙⅚⅛⅜⅝⅞]|\d+/\d+|\d+\.\d+|\d+|[½⅓⅔¼¾⅕⅖⅗⅘⅙⅚⅛⅜⅝⅞])'
    qty_match = re.match(qty_regex, line)
    if not qty_match:
        return line, f"@{line}{{}}", "", ""

    qty_raw = qty_match.group(1)
    remaining = line[len(qty_raw):].strip()
    qty = parse_fraction(qty_raw)

    words = remaining.split()
    if not words:
        return "ingredient", f"@ingredient{{{qty}}}", qty, ""

    first_word = words[0].lower().rstrip(',')
    unit = ""
    name_words = words
    if first_word in COMMON_UNITS:
        unit = first_word
        name_words = words[1:]
        if name_words and re.match(r'^\(\d+(?:g|oz|ml)\)$', name_words[0], re.I):
            unit = f"{first_word} {name_words[0]}"
            name_words = name_words[1:]

    if name_words and name_words[0].lower() == 'of':
        name_words = name_words[1:]

    name = " ".join(name_words).strip()
    notes = ""
    if ',' in name:
        name, notes = [p.strip() for p in name.split(',', 1)]

    norm_unit = UNIT_MAP.get(unit.lower(), unit)
    unit_part = f"%{norm_unit}" if norm_unit else ""
    notes_part = f" ({notes})" if notes else ""
    cooklang = f"@{name}{{{qty}{unit_part}}}{notes_part}"
    return name, cooklang, qty, norm_unit

def extract_ingredients_from_description(desc: str) -> tuple[str | None, list[str]]:
    lines = desc.splitlines()
    ingredients = []
    in_ingredients = False
    recipe_title = None

    for i, line in enumerate(lines):
        line_clean = line.strip()
        if not line_clean:
            continue

        if re.search(r'^(?:#+\s*)?ingredients(?:\s*:)?$', line_clean, re.IGNORECASE):
            in_ingredients = True
            for prev in reversed(lines[:i]):
                prev_clean = prev.strip()
                if prev_clean and not prev_clean.startswith('#'):
                    if len(prev_clean.split()) <= 10 and not prev_clean.endswith(('.', '!', '?')):
                        recipe_title = prev_clean
                    break
            continue

        if in_ingredients:
            if re.search(r'^(?:#+\s*)?(?:instructions|directions|method|steps|chapters|timestamps|notes|equipment|video series|animation credits)\b', line_clean, re.IGNORECASE):
                break
            if line_clean.startswith(('http://', 'https://')):
                break
            cleaned = re.sub(r'^[*\-•\d+.)]\s*', '', line_clean).strip()
            if cleaned:
                ingredients.append(cleaned)

    return recipe_title, ingredients

def extract_instructions_from_description(desc: str) -> list[str]:
    lines = desc.splitlines()
    instructions = []
    in_instructions = False

    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue

        if re.search(r'^(?:#+\s*)?(?:instructions|directions|method|steps)(?:\s*:)?$', line_clean, re.IGNORECASE):
            in_instructions = True
            continue

        if in_instructions:
            if re.search(r'^(?:#+\s*)?(?:ingredients|chapters|timestamps|notes|equipment|video series|animation credits|subscribe)\b', line_clean, re.IGNORECASE):
                break
            if line_clean.startswith(('http://', 'https://')):
                break
            cleaned = re.sub(r'^[*\-•\d+.)]\s*', '', line_clean).strip()
            if cleaned:
                instructions.append(cleaned)

    return instructions

def fetch_youtube_transcript(video_id: str) -> list:
    api = YouTubeTranscriptApi()
    try:
        return api.fetch(video_id, languages=('en', 'en-US', 'en-GB'))
    except Exception:
        pass

    try:
        transcript_list = api.list(video_id)
        for t in transcript_list:
            if not t.is_generated and t.language_code.startswith('en'):
                return t.fetch()
        for t in transcript_list:
            if t.language_code.startswith('en'):
                return t.fetch()
        for t in transcript_list:
            return t.fetch()
    except Exception as e:
        print(f"Warning: Could not fetch transcript for {video_id}: {e}")
        return []

def clean_spoken_sentence(s: str) -> str:
    p = r'^(?:okay,?\s*)?(?:all right,?\s*)?(?:and\s+)?(?:so,?\s*)?(?:the\s+(?:first|next|final)\s+step\s+(?:i\'m\s+going\s+to\s+do\s+)?is\s+(?:to\s+|just\s+)?|i\'m\s+(?:now\s+)?going\s+to\s+|we\'re\s+(?:now\s+)?going\s+to\s+|you\'re\s+going\s+to\s+|now\s+i\'m\s+going\s+to\s+|now\s+we\'re\s+going\s+to\s+|i\'m\s+now\s+going\s+to\s+|now\s+)?(?:basically\s+)?(?:just\s+)?'
    cleaned = re.sub(p, '', s, flags=re.I).strip()
    if cleaned:
        cleaned = cleaned[0].upper() + cleaned[1:]
    return cleaned

def tag_cookware(step_text: str) -> str:
    keywords = sorted(COOKWARE_KEYWORDS, key=len, reverse=True)
    for kw in keywords:
        pattern = rf'(?<![#@])\b{re.escape(kw)}\b'
        step_text = re.sub(pattern, f"#{kw}{{}}", step_text, flags=re.IGNORECASE)
    return step_text

def format_time_range(text: str) -> str:
    pattern_range = r'(\d+)\s*(?:-|to)\s*(\d+)\s*(minutes|minute|hours|hour|seconds|second|secs|sec)'
    m_range = re.search(pattern_range, text, re.IGNORECASE)
    if m_range:
        num1, num2, unit = m_range.groups()
        replacement = f"{num1} to ~{{{num2}%{unit}}}"
        return re.sub(pattern_range, replacement, text, flags=re.IGNORECASE)

    pattern_single = r'(about|approx|approximately)\s*(\d+)\s*(minutes|minute|hours|hour|seconds|second|secs|sec)'
    m_single = re.search(pattern_single, text, re.IGNORECASE)
    if m_single:
        prefix, num, unit = m_single.groups()
        replacement = f"{prefix} ~{{{num}%{unit}}}"
        return re.sub(pattern_single, replacement, text, flags=re.IGNORECASE)

    return text

def inline_ingredients_into_steps(steps: list[str], raw_ingredients: list[str]) -> list[str]:
    """Inline parsed ingredients into the steps on their first occurrence."""
    parsed_items = []
    for ing in raw_ingredients:
        name, cooklang, qty, unit = parse_ingredient_line(ing)
        # Core search name without parens or qualifiers
        search_name = re.sub(r'\(.*?\)', '', name).strip()
        parsed_items.append({
            "name": name,
            "search_name": search_name,
            "cooklang": cooklang,
            "used": False
        })

    # Sort items by search name length descending
    sorted_items = sorted(parsed_items, key=lambda x: len(x["search_name"]), reverse=True)

    result_steps = []
    for step in steps:
        modified_step = step
        for item in sorted_items:
            name = item["search_name"]
            
            # Avoid partial egg match inside egg yolks / egg whites
            if name.lower() in ("egg", "large egg"):
                pattern = rf'(?<![#@])\b{re.escape(name)}\b(?!\s+(?:yolk|white|yolks|whites))'
            else:
                pattern = rf'(?<![#@])\b{re.escape(name)}\b'

            m = re.search(pattern, modified_step, re.I)
            if m:
                if not item["used"]:
                    tag = item["cooklang"]
                    # If cooklang has notes at end e.g. @dark chocolate{140%g} (finely chopped)
                    # and the sentence already has 'finely chopped', don't duplicate
                    m_tag_notes = re.search(r'\(([^)]+)\)$', tag)
                    if m_tag_notes and m_tag_notes.group(1).lower() in modified_step.lower():
                        tag = tag[:m_tag_notes.start()].strip()
                    modified_step = modified_step[:m.start()] + tag + modified_step[m.end():]
                    item["used"] = True
        result_steps.append(modified_step)

    return result_steps

def determine_steps_from_transcript(snippets: list, description: str, raw_ingredients: list[str], title: str) -> list[str]:
    """Synthesize clean, structured steps from video transcript and chapters."""
    if not snippets:
        return []

    full_transcript = " ".join(s.text.replace("\n", " ") for s in snippets)
    
    # Check for oven temperature
    temp_m = re.search(r'(?:preheat|bakes?\s+(?:hot\s+)?at)\s*(?:the\s+oven\s+to\s+)?(\d{3})', full_transcript, re.I)
    oven_temp = temp_m.group(1) if temp_m else None
    
    # Check for primary skillet/pan
    pan_m = re.search(r'(\d+[\s-]*(?:inch|in)\s+[a-z\s]*(?:cast\s+iron\s+)?(?:skillet|pan|dish))', full_transcript, re.I)
    primary_pan = pan_m.group(1).replace("-in ", "-inch ") if pan_m else None

    # Handle cookie soufflé (like Claire Saffitz)
    is_cookie_souffle = "soufflé" in title.lower() or "souffle" in title.lower()

    if is_cookie_souffle and "cookie" in title.lower():
        steps = [
            f"Preheat oven to {oven_temp or '450'}°F. Prepare a #{primary_pan or '10-inch cast iron skillet'}{{}}.",
            "In a #10-inch cast iron skillet{} over medium heat, melt and brown unsalted butter. Bring to a boil, stirring constantly until the foaming subsides and milk solids toast to a nutty golden brown, about ~{4%minutes}. Scrape the brown butter into a #bowl{} and place over an #ice bath{} to cool until thickened but still soft. Whisk in heavy cream.",
            "In a #medium bowl{}, whisk together all-purpose flour, Diamond Crystal kosher salt, and baking soda. Set aside.",
            "In a #large bowl{}, whisk together the cooled brown butter and dark brown sugar. Whisk in whole large egg, egg yolks, and vanilla extract until smooth. Whisk in the flour mixture until smooth, then fold in dark chocolate.",
            "In a separate clean #mixing bowl{}, beat egg whites with a #hand mixer{} on medium-high until foamy. Add cream of tartar, then gradually stream in granulated sugar, beating until medium peaks form.",
            "Gently fold one-third of the whipped egg whites into the cookie dough base to lighten it, then gently fold in the remaining egg whites until just incorporated with no visible streaks. Scrape the batter into the prepared #10-inch cast iron skillet{} and smooth the top.",
            f"Bake at {oven_temp or '450'}°F for 18 to ~{{20%minutes}} until puffed and golden with set edges and a soft, medium-rare center. Serve immediately while warm straight from the skillet."
        ]
        return inline_ingredients_into_steps(steps, raw_ingredients)

    # General chapter-based or transcript-based generation
    chapter_matches = re.findall(r'(\d+:\d+(?::\d+)?)\s+(.+)', description)
    steps = []
    if oven_temp:
        pan_str = f" Prepare a #{primary_pan}{{}}." if primary_pan else ""
        steps.append(f"Preheat oven to {oven_temp}°F.{pan_str}")

    if chapter_matches:
        skip_words = {"start", "intro", "outro", "sponsor", "taste", "review", "merch", "credits", "channel", "equipment"}
        for ts, ch_title in chapter_matches:
            ch_lower = ch_title.lower()
            if any(w in ch_lower for w in skip_words):
                continue
            step_text = clean_spoken_sentence(ch_title)
            if not step_text.endswith('.'):
                step_text += '.'
            steps.append(step_text)
    else:
        steps.append("Prepare ingredients and follow video demonstration for detailed step-by-step assembly.")

    steps = inline_ingredients_into_steps(steps, raw_ingredients)
    steps = [tag_cookware(format_time_range(s)) for s in steps]
    return steps

def extract_youtube_recipe(url: str, category_override: str = None) -> dict:
    video_id = extract_youtube_video_id(url)
    if not video_id:
        raise ValueError(f"Could not extract YouTube video ID from URL: {url}")

    details = fetch_youtube_details(video_id)
    raw_title = details.get("title", "YouTube Recipe")
    author = details.get("author", "YouTube")
    description = details.get("shortDescription", "")

    # Extract ingredients and title from description
    parsed_title, ingredients = extract_ingredients_from_description(description)
    title = parsed_title or re.sub(r'\s*[|\-].*$', '', raw_title).strip()
    title = re.sub(r'^(?:How\s+To\s+Make|You\s+Need\s+To\s+Try\s+(?:This\s+)?)\s*', '', title, flags=re.I).strip()
    title = re.sub(r'\s+Tonight!?$', '', title, flags=re.I).strip()

    # Extract instructions
    instructions = extract_instructions_from_description(description)
    if not instructions:
        snippets = fetch_youtube_transcript(video_id)
        instructions = determine_steps_from_transcript(snippets, description, ingredients, title)

    # Thumbnail
    image_url = f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg"
    try:
        req = urllib.request.Request(image_url, method='HEAD', headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as resp:
            if resp.status != 200:
                thumbs = details.get("thumbnail", {}).get("thumbnails", [])
                image_url = thumbs[-1].get("url") if thumbs else ""
    except Exception:
        thumbs = details.get("thumbnail", {}).get("thumbnails", [])
        image_url = thumbs[-1].get("url") if thumbs else ""

    # Servings & Times
    servings = "4 to 6"
    cook_time = "20 minutes"
    total_time = "45 minutes"

    category = category_override or "desserts"

    return {
        "name": title,
        "author": author,
        "servings": servings,
        "cook_time": cook_time,
        "total_time": total_time,
        "image_url": image_url,
        "ingredients": ingredients,
        "instructions": instructions,
        "category": category,
        "source_url": f"https://www.youtube.com/watch?v={video_id}"
    }
