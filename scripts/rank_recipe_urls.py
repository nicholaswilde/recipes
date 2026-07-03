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
import json
import argparse
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import re

def calculate_bayesian_average(rating, votes, min_votes, prior_rating):
    if votes + min_votes == 0:
        return 0.0
    return (votes * rating + min_votes * prior_rating) / (votes + min_votes)

def fetch_html(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        return response.read().decode('utf-8')

def find_recipe_in_json(data):
    if isinstance(data, dict):
        if data.get("@type") == "Recipe" or data.get("@type") == ["Recipe"]:
            return data
        for k, v in data.items():
            if k == "@graph" and isinstance(v, list):
                for item in v:
                    recipe = find_recipe_in_json(item)
                    if recipe:
                        return recipe
            elif isinstance(v, (dict, list)):
                recipe = find_recipe_in_json(v)
                if recipe:
                    return recipe
    elif isinstance(data, list):
        for item in data:
            recipe = find_recipe_in_json(item)
            if recipe:
                return recipe
    return None

def extract_recipe_metadata(url):
    try:
        html = fetch_html(url)
        soup = BeautifulSoup(html, "html.parser")
        
        # 1. Try to find name from document title or H1
        title_el = soup.find("h1")
        name = title_el.get_text(strip=True) if title_el else ""
        if not name:
            title_tag = soup.find("title")
            name = title_tag.get_text(strip=True) if title_tag else "Unknown Recipe"
            
        # Remove site branding from title (e.g. " - Serious Eats" or " | Isabel Eats")
        name = re.sub(r'\s+[-|]\s+.*$', '', name)
        
        # 2. Try JSON-LD
        scripts = soup.find_all("script", type="application/ld+json")
        for script in scripts:
            try:
                data = json.loads(script.string or "")
                recipe = find_recipe_in_json(data)
                if recipe:
                    # Get name if available in schema
                    schema_name = recipe.get("name")
                    if schema_name:
                        name = schema_name
                    
                    agg_rating = recipe.get("aggregateRating")
                    if isinstance(agg_rating, dict):
                        rating = float(agg_rating.get("ratingValue") or 0.0)
                        votes = int(agg_rating.get("ratingCount") or agg_rating.get("reviewCount") or 0)
                        return {"title": name, "rating": rating, "votes": votes, "url": url}
            except Exception:
                continue
                
        # 3. Fallback to WPRM or other parsing if JSON-LD fails
        # Look for class wprm-recipe-rating-average or similar
        avg_el = soup.find(class_="wprm-recipe-rating-average") or soup.find(class_="recipe-rating-average")
        count_el = soup.find(class_="wprm-recipe-rating-count") or soup.find(class_="recipe-rating-count")
        if avg_el:
            try:
                rating = float(avg_el.get_text(strip=True))
                votes = int(count_el.get_text(strip=True)) if count_el else 0
                return {"title": name, "rating": rating, "votes": votes, "url": url}
            except ValueError:
                pass
                
        return {"title": name, "rating": 0.0, "votes": 0, "url": url, "error": "No structured rating found"}
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
