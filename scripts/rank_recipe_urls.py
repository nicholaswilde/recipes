#!/usr/bin/env python3

################################################################################
#
# rank_recipe_urls.py
# ----------------
# Rank recipe source URLs
#
# @author nιcнolaѕ wιlde, 0x08b7d7a3
# @date 30 Jun 2026
# @version 0.1.0
#
################################################################################

import sys
import os
import argparse
import shutil
import subprocess
import urllib.request
import urllib.error
from bs4 import BeautifulSoup
import re

try:
    from scripts.scrape_to_cook import extract_json_ld_recipe, fetch_via_browserless
except ImportError:
    from scrape_to_cook import extract_json_ld_recipe, fetch_via_browserless

BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
}


def calculate_bayesian_average(rating, votes, min_votes, prior_rating):
    """Calculate weighted Bayesian rating."""
    if votes + min_votes == 0:
        return 0.0
    return (votes * rating + min_votes * prior_rating) / (votes + min_votes)


def _is_challenge_page(html):
    """Detect common anti-bot interstitial pages that yield no recipe HTML."""
    if not html:
        return True
    lower = html[:8000].lower()
    return (
        "<title>just a moment...</title>" in lower
        or "cf-browser-verification" in lower
        or "enable javascript and cookies to continue" in lower
    )


def _fetch_via_curl(url):
    """Attempt HTTP/2 browser-like fetch via curl when urllib is blocked."""
    curl_bin = shutil.which("curl")
    if not curl_bin:
        return None
    cmd = [curl_bin, "-sL", "--fail", "--max-time", "20"]
    for key, val in BROWSER_HEADERS.items():
        cmd.extend(["-H", f"{key}: {val}"])
    cmd.append(url)
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
    if res.returncode == 0 and not _is_challenge_page(res.stdout):
        return res.stdout
    return None


def fetch_html(url):
    """Fetch HTML with browser headers, curl HTTP/2 fallback, and Browserless fallback."""
    last_error = None
    req = urllib.request.Request(url, headers=BROWSER_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode("utf-8", errors="replace")
            if not _is_challenge_page(html):
                return html
            last_error = RuntimeError("HTTP challenge page returned")
    except urllib.error.HTTPError as e:
        if e.code not in (401, 403, 429):
            raise
        last_error = e

    curl_html = _fetch_via_curl(url)
    if curl_html:
        return curl_html

    browserless_url = os.environ.get("BROWSERLESS_URL", "http://localhost:3000")
    if browserless_url:
        bl_html = fetch_via_browserless(url, browserless_url)
        if bl_html and not _is_challenge_page(bl_html):
            return bl_html

    raise last_error


def _parse_int(value):
    """Parse an integer vote/review count that may contain commas."""
    if value is None:
        return 0
    return int(float(str(value).replace(",", "").strip()))


def extract_recipe_metadata(url):
    """Fetch a recipe URL and extract title, rating, and vote count."""
    try:
        html = fetch_html(url)
        soup = BeautifulSoup(html, "html.parser")

        title_el = soup.find("h1")
        name = title_el.get_text(strip=True) if title_el else ""
        if not name:
            title_tag = soup.find("title")
            name = title_tag.get_text(strip=True) if title_tag else "Unknown Recipe"

        # Remove site branding from title (e.g. " - Serious Eats" or " | Isabel Eats")
        name = re.sub(r"\s+[-|]\s+.*$", "", name)

        recipe = extract_json_ld_recipe(html)
        if recipe:
            schema_name = recipe.get("name")
            if schema_name:
                name = schema_name

            agg_rating = recipe.get("aggregateRating")
            if isinstance(agg_rating, dict):
                rating = float(agg_rating.get("ratingValue") or 0.0)
                votes = _parse_int(
                    agg_rating.get("ratingCount") or agg_rating.get("reviewCount")
                )
                return {"title": name, "rating": rating, "votes": votes, "url": url}

        # Fallback to WPRM or common rating classes if JSON-LD lacks aggregateRating
        avg_el = soup.find(class_="wprm-recipe-rating-average") or soup.find(
            class_="recipe-rating-average"
        )
        count_el = soup.find(class_="wprm-recipe-rating-count") or soup.find(
            class_="recipe-rating-count"
        )
        if avg_el:
            try:
                rating = float(avg_el.get_text(strip=True))
                votes = _parse_int(count_el.get_text(strip=True)) if count_el else 0
                return {"title": name, "rating": rating, "votes": votes, "url": url}
            except ValueError:
                pass

        return {
            "title": name,
            "rating": 0.0,
            "votes": 0,
            "url": url,
            "error": "No structured rating found",
        }
    except Exception as e:
        return {"title": url, "rating": 0.0, "votes": 0, "url": url, "error": str(e)}

def main():
    parser = argparse.ArgumentParser(
        description="Fetch recipe webpages, extract rating metadata, and rank them using Bayesian average."
    )
    parser.add_argument(
        "urls",
        nargs="*",
        help="List of recipe URLs to rank."
    )
    parser.add_argument(
        "--min-votes", "-m",
        type=float,
        default=10.0,
        help="Minimum number of votes/ratings required for consideration (default: 10.0)"
    )
    parser.add_argument(
        "--prior-rating", "-c",
        type=float,
        default=3.5,
        help="The prior/average rating (C) to smooth towards (default: 3.5)"
    )
    
    args = parser.parse_args()
    
    urls = args.urls
    if not urls:
        # Read from stdin if no arguments provided
        if sys.stdin.isatty():
            print("Error: No URLs specified. Provide URLs as arguments or pipe them via stdin.", file=sys.stderr)
            parser.print_help()
            sys.exit(1)
        urls = [line.strip() for line in sys.stdin if line.strip()]
        
    print(f"Fetching and parsing {len(urls)} recipe URL(s)...", file=sys.stderr)
    
    recipes = []
    for url in urls:
        print(f"Parsing: {url}", file=sys.stderr)
        recipe = extract_recipe_metadata(url)
        recipes.append(recipe)
        
    # Process and calculate Bayesian average
    ranked_recipes = []
    for r in recipes:
        rating = r["rating"]
        votes = r["votes"]
        bayesian_avg = calculate_bayesian_average(rating, votes, args.min_votes, args.prior_rating)
        
        ranked_recipes.append({
            "title": r["title"],
            "rating": rating,
            "votes": votes,
            "bayesian_average": bayesian_avg,
            "url": r["url"],
            "error": r.get("error")
        })
        
    # Sort descending by Bayesian average
    ranked_recipes.sort(key=lambda x: x["bayesian_average"], reverse=True)
    
    # Print results as Markdown table
    print(f"### Bayesian Average Rankings for Scraped URLs (m={args.min_votes}, C={args.prior_rating})")
    print()
    print("| Rank | Recipe Title | Raw Rating | Votes/Reviews | Bayesian Average | Source / URL | Notes |")
    print("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
    for idx, r in enumerate(ranked_recipes, 1):
        url_markdown = f"[Link]({r['url']})" if r['url'] else "-"
        notes = f"⚠️ {r['error']}" if r.get("error") else "Success"
        print(f"| {idx} | {r['title']} | {r['rating']:.2f} ★ | {r['votes']} | **{r['bayesian_average']:.4f}** | {url_markdown} | {notes} |")

if __name__ == "__main__":
    main()
