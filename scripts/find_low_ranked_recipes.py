#!/usr/bin/env python3

################################################################################
#
# find_low_ranked_recipes.py
# ----------------
# Find low-ranked recipes in the repository
#
# @author nιcнolaѕ wιlde, 0x08b7d7a3
# @date 01 Jul 2026
# @version 0.1.0
#
################################################################################

"""
Find Low-Ranked Recipes in the Repository.

Scans local .cook files, extracts their web source URLs, fetches structured
aggregate rating metadata, calculates their Bayesian averages, and lists the
recipes falling below a specific quality threshold.
"""

import os
import sys
import re
import json
import argparse
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

def calculate_bayesian_average(rating, votes, min_votes=10.0, prior_rating=3.5):
    if votes + min_votes == 0:
        return 0.0
    return (votes * rating + min_votes * prior_rating) / (votes + min_votes)

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
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as response:
            html = response.read().decode('utf-8', errors='ignore')
            
        soup = BeautifulSoup(html, "html.parser")
        
        # 1. Try JSON-LD
        scripts = soup.find_all("script", type="application/ld+json")
        for script in scripts:
            try:
                data = json.loads(script.string or "")
                recipe = find_recipe_in_json(data)
                if recipe:
                    agg_rating = recipe.get("aggregateRating")
                    if isinstance(agg_rating, dict):
                        rating = float(agg_rating.get("ratingValue") or 0.0)
                        votes = int(agg_rating.get("ratingCount") or agg_rating.get("reviewCount") or 0)
                        return {"rating": rating, "votes": votes, "success": True}
            except Exception:
                continue
                
        # 2. Fallback to WPRM classes
        avg_el = soup.find(class_="wprm-recipe-rating-average") or soup.find(class_="recipe-rating-average")
        count_el = soup.find(class_="wprm-recipe-rating-count") or soup.find(class_="recipe-rating-count")
        if avg_el:
            try:
                rating = float(avg_el.get_text(strip=True))
                votes = int(count_el.get_text(strip=True)) if count_el else 0
                return {"rating": rating, "votes": votes, "success": True}
            except ValueError:
                pass
                
        return {"rating": 0.0, "votes": 0, "success": False, "error": "No structured rating found"}
    except Exception as e:
        return {"rating": 0.0, "votes": 0, "success": False, "error": str(e)}

def parse_cook_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for _ in range(15):  # read first 15 lines to locate source
                line = f.readline()
                if not line:
                    break
                match = re.match(r'^>>\s*source:\s*(https?://\S+)', line, re.IGNORECASE)
                if match:
                    return match.group(1).strip()
    except Exception:
        pass
    return None

def process_recipe(filepath, filename):
    url = parse_cook_file(filepath)
    if not url:
        return None
        
    res = extract_recipe_metadata(url)
    res["file_path"] = filepath
    res["recipe_name"] = os.path.splitext(filename)[0]
    res["url"] = url
    return res

def main():
    parser = argparse.ArgumentParser(description="Find low-ranked recipes in the repository.")
    parser.add_argument("--dir", default="cook", help="Recipes directory to scan.")
    parser.add_argument("--min-votes", type=float, default=10.0, help="Minimum votes threshold (m).")
    parser.add_argument("--prior-rating", type=float, default=3.5, help="Prior rating value (C).")
    parser.add_argument("--threshold", type=float, default=4.4, help="Bayesian rating threshold to flag.")
    parser.add_argument("--max-results", type=int, default=15, help="Maximum number of low recipes to list.")
    parser.add_argument("--workers", type=int, default=30, help="Number of concurrent thread workers.")
    args = parser.parse_args()

    if not os.path.exists(args.dir):
        print(f"Error: Directory '{args.dir}' does not exist.")
        sys.exit(1)

    recipe_tasks = []
    for root, _, files in os.walk(args.dir):
        for file in files:
            if file.endswith(".cook"):
                recipe_tasks.append((os.path.join(root, file), file))

    print(f"Found {len(recipe_tasks)} total recipe files in '{args.dir}'.")
    print(f"Scanning for web sources and scraping ratings (m={args.min_votes}, C={args.prior_rating})...")

    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(process_recipe, path, name): (path, name) for path, name in recipe_tasks}
        for future in as_completed(futures):
            res = future.result()
            if res:
                results.append(res)

    evaluated = []
    for r in results:
        if r.get("success") and r["votes"] > 0:
            bayesian = calculate_bayesian_average(
                r["rating"], r["votes"], min_votes=args.min_votes, prior_rating=args.prior_rating
            )
            r["bayesian_average"] = bayesian
            evaluated.append(r)

    # Sort by Bayesian average ascending (lowest first)
    evaluated.sort(key=lambda x: x["bayesian_average"])

    flagged = [r for r in evaluated if r["bayesian_average"] < args.threshold]
    flagged = flagged[:args.max_results]

    if not flagged:
        print(f"\nNo recipes found with a Bayesian average below the threshold of {args.threshold} ★.")
        return

    print(f"\n### Top {len(flagged)} Flagged Low-Ranked Recipes (Score < {args.threshold} ★):\n")
    print("| Recipe Name | Raw Rating | Votes/Reviews | Bayesian Average | Source URL | File Path | Suggested Replacements |")
    print("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |")

    for r in flagged:
        relative_path = os.path.relpath(r["file_path"], os.getcwd())
        
        # Build search query links for replacements
        query = f"best copycat {r['recipe_name']} recipe site:sallysbakingaddiction.com OR site:kingarthurbaking.com OR site:thecozycook.com OR site:seriouseats.com"
        search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        
        print(
            f"| {r['recipe_name']} "
            f"| {r['rating']:.2f} ★ "
            f"| {r['votes']} "
            f"| **{r['bayesian_average']:.4f}** "
            f"| [Link]({r['url']}) "
            f"| [`{relative_path}`](file:///{r['file_path']}) "
            f"| [Search Replacements]({search_url}) |"
        )

if __name__ == "__main__":
    main()
