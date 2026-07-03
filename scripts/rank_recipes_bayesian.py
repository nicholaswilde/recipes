#!/usr/bin/env python3

################################################################################
#
# rank_recipes_bayesian.py
# ----------------
# Rank recipes using a Bayesian scoring algorithm
#
# @author nιcнolaѕ wιlde, 0x08b7d7a3
# @date 24 Jun 2026
# @version 0.1.0
#
################################################################################

import sys
import json
import argparse

def calculate_bayesian_average(rating, votes, min_votes, prior_rating):
    """
    Calculate the Bayesian average rating:
    W = (v * R + m * C) / (v + m)
    where:
    W = weighted rating (Bayesian average)
    R = raw rating of the recipe (rating)
    v = number of reviews/votes (votes)
    m = minimum votes required to be considered (min_votes)
    C = prior/average rating across all recipes (prior_rating)
    """
    if votes + min_votes == 0:
        return 0.0
    return (votes * rating + min_votes * prior_rating) / (votes + min_votes)

def main():
    parser = argparse.ArgumentParser(
        description="Rank recipes using a simplified Bayesian average rating formula."
    )
    parser.add_argument(
        "--input", "-i",
        help="Path to JSON file containing recipe list. If omitted, reads from stdin."
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
    parser.add_argument(
        "--interactive", "-a",
        action="store_true",
        help="Interactive CLI mode to compare input ratings directly."
    )

    args = parser.parse_args()

    if args.interactive:
        print("Interactive Bayesian Average Calculator")
        print(f"Parameters: min_votes (m) = {args.min_votes}, prior_rating (C) = {args.prior_rating}")
        print("Enter rating and votes separated by space (e.g. '4.8 5'). Enter 'q' to finish.")
        recipes = []
        count = 1
        while True:
            try:
                line = input(f"Recipe #{count} rating & votes: ").strip()
                if line.lower() == 'q':
                    break
                parts = line.split()
                if len(parts) != 2:
                    print("Error: Please enter exactly two numbers (rating and votes).")
                    continue
                rating = float(parts[0])
                votes = int(parts[1])
                name = f"Recipe #{count}"
                recipes.append({"title": name, "rating": rating, "votes": votes})
                count += 1
            except ValueError:
                print("Error: Invalid numeric inputs.")
            except (KeyboardInterrupt, EOFError):
                break
    else:
        # Load from file or stdin
        if args.input:
            try:
                with open(args.input, "r", encoding="utf-8") as f:
                    recipes = json.load(f)
            except Exception as e:
                print(f"Error reading input file: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            if sys.stdin.isatty():
                print("Error: No input file specified and stdin is empty.", file=sys.stderr)
                parser.print_help()
                sys.exit(1)
            try:
                recipes = json.load(sys.stdin)
            except Exception as e:
                print(f"Error parsing JSON from stdin: {e}", file=sys.stderr)
                sys.exit(1)

    if not isinstance(recipes, list):
        print("Error: Input JSON must be a list of recipe objects.", file=sys.stderr)
        sys.exit(1)

    # Process and calculate Bayesian average
    ranked_recipes = []
    for recipe in recipes:
        title = recipe.get("title", "Unnamed Recipe")
        # Handle potential string or null ratings/votes
        try:
            rating = float(recipe.get("rating", 0.0) or 0.0)
            votes = int(recipe.get("votes", 0) or 0)
        except ValueError:
            # Fallbacks
            rating = 0.0
            votes = 0

        url = recipe.get("url", recipe.get("source", ""))
        bayesian_avg = calculate_bayesian_average(rating, votes, args.min_votes, args.prior_rating)
        
        ranked_recipes.append({
            "title": title,
            "rating": rating,
            "votes": votes,
            "bayesian_average": bayesian_avg,
            "url": url
        })

    # Sort descending by Bayesian average
    ranked_recipes.sort(key=lambda x: x["bayesian_average"], reverse=True)

    # Print results as Markdown table
    print(f"### Bayesian Average Rankings (m={args.min_votes}, C={args.prior_rating})")
    print()
    print("| Rank | Recipe Title | Raw Rating | Votes/Reviews | Bayesian Average | Source / URL |")
    print("| :--- | :--- | :--- | :--- | :--- | :--- |")
    for idx, r in enumerate(ranked_recipes, 1):
        url_markdown = f"[Link]({r['url']})" if r['url'] else "-"
        print(f"| {idx} | {r['title']} | {r['rating']:.2f} ★ | {r['votes']} | **{r['bayesian_average']:.4f}** | {url_markdown} |")

if __name__ == "__main__":
    main()
