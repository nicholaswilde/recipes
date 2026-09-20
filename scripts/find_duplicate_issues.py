#!/usr/bin/env python3

################################################################################
#
# find_duplicate_issues.py
# ----------------
# Comprehensive detection of duplicate GitHub issues and already-imported recipes
#
# @author nιcнolaѕ wιlde, 0x08b7d7a3
# @date 19 Sep 2026
# @version 0.3.0
#
################################################################################

import os
import sys
import json
import subprocess
import re
import argparse
from urllib.parse import urlparse, parse_qs
from difflib import SequenceMatcher

SITE_SUFFIX_REGEX = re.compile(
    r'\s*[-|–]\s*(The Great British Bake Off|King Arthur Baking|The Kitchn|Sally\'s Baking Addiction|Dessert Person|NYT Cooking|Preppy Kitchen|Allrecipes|Food & Wine|Food Network|America\'s Test Kitchen|ATK|Bon Appétit|Serious Eats|Epicurious|EatingWell|Country Roads Sourdough|YouTube|Food\.com|Taste of Home|Broma Bakery|Cup of Jo|Once Upon a Chef|Magnolia|Eater).*$',
    re.IGNORECASE
)

FILLER_WORDS_REGEX = re.compile(
    r'\b(recipe|recipes|review|how to make|watch|the best|easy|classic|homemade|simple|perfect|the|a|an|with|from|copycat)\b',
    re.IGNORECASE
)

ROUNDUP_URL_PATTERNS = [
    r'top-\d+', r'best-', r'collection', r'interactive', r'roundup',
    r'recipes-for-', r'most-popular', r'all-time', r'favorite', r'-reviews'
]

TRACKING_PARAMS = {
    'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
    'fbclid', 'gclid', 'ref', 'source', 'ocid', 'CMP', 'feature', 'si'
}

def is_roundup_url(url_str):
    return any(re.search(pat, url_str, re.IGNORECASE) for pat in ROUNDUP_URL_PATTERNS)

def normalize_url(url_str):
    if not url_str:
        return None
    url_str = url_str.strip().strip('<>)"\'').rstrip('/')
    if 'github.com' in url_str and ('/issues/' in url_str or '/user-attachments/' in url_str or '/assets/' in url_str):
        return None

    try:
        p = urlparse(url_str)
    except Exception:
        return None

    netloc = p.netloc.lower()
    if not netloc:
        return None
    if netloc.startswith('www.'):
        netloc = netloc[4:]

    # YouTube normalization
    if 'youtube.com' in netloc or 'youtu.be' in netloc:
        vid = None
        if 'youtu.be' in netloc:
            vid = p.path.strip('/')
        else:
            qs = parse_qs(p.query)
            if 'v' in qs and qs['v']:
                vid = qs['v'][0]
            elif p.path.startswith('/shorts/') or p.path.startswith('/live/'):
                vid = p.path.split('/')[2] if len(p.path.split('/')) > 2 else None
        if vid:
            return f"youtube:{vid}"

    # Reddit normalization
    if 'reddit.com' in netloc:
        m = re.search(r'/comments/([a-z0-9]+)', p.path, re.IGNORECASE)
        if m:
            return f"reddit:comment:{m.group(1).lower()}"
        m_short = re.search(r'/s/([a-z0-9]+)', p.path, re.IGNORECASE)
        if m_short:
            return f"reddit:share:{m_short.group(1)}"

    # Generic query param stripping
    if p.query:
        qs = parse_qs(p.query)
        cleaned_qs = {k: v for k, v in qs.items() if k.lower() not in TRACKING_PARAMS}
        sorted_params = "&".join(f"{k}={v[0]}" for k, v in sorted(cleaned_qs.items()))
        query_str = f"?{sorted_params}" if sorted_params else ""
    else:
        query_str = ""

    path = p.path.rstrip('/')
    return f"https://{netloc}{path}{query_str}"

def clean_title(title):
    t = re.sub(r'(?i)^\s*(\[recipe\]\s*:?|recipe\s*:?)\s*', '', title).strip()
    t = SITE_SUFFIX_REGEX.sub('', t)
    t = FILLER_WORDS_REGEX.sub(' ', t)
    t = re.sub(r'[^a-z0-9]+', ' ', t.lower()).strip()
    return t

def fetch_issues(state="open", limit=500):
    cmd = ["gh", "issue", "list", "--state", state, "--limit", str(limit), "--json", "number,title,body,url,state,stateReason,labels"]
    env = os.environ.copy()
    env["GH_NOPAGER"] = "1"
    res = subprocess.run(cmd, env=env, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error fetching {state} issues: {res.stderr}", file=sys.stderr)
        return []
    try:
        return json.loads(res.stdout)
    except Exception as e:
        print(f"Error parsing JSON for {state} issues: {e}", file=sys.stderr)
        return []

def index_repo_recipes():
    recipe_sources = {}
    recipe_names = {}

    for root, _, files in os.walk("docs"):
        for f in files:
            if not f.endswith(".md") or f in ("index.md", "tags.md", "README.md"):
                continue
            path = os.path.join(root, f)
            name_base = clean_title(os.path.splitext(f)[0].replace("-", " "))
            if name_base:
                recipe_names[name_base] = path

            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as fp:
                    txt = fp.read()
                urls = re.findall(r'https?://[^\s\)\>]+', txt)
                for u in urls:
                    norm = normalize_url(u)
                    if norm:
                        recipe_sources[norm] = path
            except Exception:
                pass

    for root, _, files in os.walk("cook"):
        for f in files:
            if not f.endswith(".cook"):
                continue
            path = os.path.join(root, f)
            name_base = clean_title(os.path.splitext(f)[0])
            if name_base:
                recipe_names[name_base] = path

            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as fp:
                    txt = fp.read()
                urls = re.findall(r'(?:source:\s*|>>\s*source:\s*)(https?://[^\s\n\r]+)', txt)
                for u in urls:
                    norm = normalize_url(u)
                    if norm:
                        recipe_sources[norm] = path
            except Exception:
                pass

    return recipe_sources, recipe_names

def close_github_issue(number, duplicate_of=None, comment=None):
    cmd = ["gh", "issue", "close", str(number)]
    if duplicate_of:
        cmd.extend(["--duplicate-of", str(duplicate_of)])
    if comment:
        cmd.extend(["-c", comment])

    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"  [+] Closed issue #{number}" + (f" (duplicate of #{duplicate_of})" if duplicate_of else ""))
        return True
    else:
        print(f"  [-] Failed to close issue #{number}: {res.stderr.strip()}", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description="Find and resolve duplicate GitHub issues and already-imported recipes.")
    parser.add_argument("--limit", type=int, default=500, help="Maximum number of issues to fetch (default: 500)")
    parser.add_argument("--mode", choices=["all", "issues", "imported"], default="all", help="Scan mode")
    parser.add_argument("--no-closed", action="store_true", help="Do not check open issues against closed issues")
    parser.add_argument("--close", action="store_true", help="Automatically close verified exact duplicates")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    open_issues = fetch_issues("open", args.limit)
    if not open_issues:
        print("No open issues found.")
        return

    closed_issues = []
    if not args.no_closed and args.mode in ("all", "issues"):
        closed_issues = fetch_issues("closed", limit=1000)

    recipe_sources, recipe_names = index_repo_recipes()

    open_by_url = {}
    open_parsed = []
    for iss in open_issues:
        num = iss["number"]
        title = iss["title"]
        body = iss.get("body", "") or ""
        ct = clean_title(title)

        urls = []
        raw_urls = re.findall(r'https?://[^\s)\]"\']+', body)
        for ru in raw_urls:
            nu = normalize_url(ru)
            if nu and nu not in urls:
                urls.append(nu)

        item = {
            "number": num,
            "title": title,
            "clean_title": ct,
            "urls": urls,
            "raw_issue": iss
        }
        open_parsed.append(item)

        for u in urls:
            if u not in open_by_url:
                open_by_url[u] = []
            open_by_url[u].append(item)

    closed_by_url = {}
    for iss in closed_issues:
        if iss.get("stateReason") == "DUPLICATE":
            continue
        labels = [l.get("name", "").lower() for l in iss.get("labels", []) if isinstance(l, dict)]
        if "duplicate" in labels:
            continue
        body = iss.get("body", "") or ""
        raw_urls = re.findall(r'https?://[^\s)\]"\']+', body)
        for ru in raw_urls:
            nu = normalize_url(ru)
            if nu:
                closed_by_url[nu] = iss

    results = {
        "open_issue_exact_recipe_duplicates": [],
        "open_issue_shared_roundup_urls": [],
        "open_issue_duplicates_closed": [],
        "open_issue_already_imported_exact": [],
        "open_issue_already_imported_similar": [],
        "open_issue_high_similarity_titles": []
    }

    # 1. Open <-> Open URL Duplicates
    if args.mode in ("all", "issues"):
        for u, iss_list in open_by_url.items():
            if len(iss_list) > 1:
                sorted_list = sorted(iss_list, key=lambda x: x["number"])
                primary = sorted_list[0]
                duplicates = sorted_list[1:]

                is_roundup = is_roundup_url(u)
                target_key = "open_issue_shared_roundup_urls" if is_roundup else "open_issue_exact_recipe_duplicates"

                results[target_key].append({
                    "url": u,
                    "primary": {"number": primary["number"], "title": primary["title"]},
                    "duplicates": [{"number": d["number"], "title": d["title"]} for d in duplicates]
                })

        # 2. Open <-> Open High Similarity Titles
        for i in range(len(open_parsed)):
            item1 = open_parsed[i]
            ct1 = item1["clean_title"]
            if len(ct1) < 6:
                continue
            for j in range(i + 1, len(open_parsed)):
                item2 = open_parsed[j]
                ct2 = item2["clean_title"]
                if len(ct2) < 6:
                    continue

                sim = SequenceMatcher(None, ct1, ct2).ratio()
                if sim >= 0.88 or (ct1 == ct2):
                    results["open_issue_high_similarity_titles"].append({
                        "similarity": round(sim, 2),
                        "issue_1": {"number": item1["number"], "title": item1["title"]},
                        "issue_2": {"number": item2["number"], "title": item2["title"]}
                    })

    # 3. Open <-> Closed Duplicates
    if not args.no_closed and args.mode in ("all", "issues"):
        for item in open_parsed:
            for u in item["urls"]:
                if u in closed_by_url and not is_roundup_url(u):
                    c_iss = closed_by_url[u]
                    if c_iss["number"] != item["number"]:
                        results["open_issue_duplicates_closed"].append({
                            "url": u,
                            "open_issue": {"number": item["number"], "title": item["title"]},
                            "closed_issue": {"number": c_iss["number"], "title": c_iss["title"]}
                        })
                        break

    # 4. Open <-> Imported in Codebase
    if args.mode in ("all", "imported"):
        for item in open_parsed:
            exact_match_path = None
            for u in item["urls"]:
                if u in recipe_sources and not is_roundup_url(u):
                    exact_match_path = recipe_sources[u]
                    results["open_issue_already_imported_exact"].append({
                        "open_issue": {"number": item["number"], "title": item["title"]},
                        "repo_path": exact_match_path,
                        "url": u
                    })
                    break

            if not exact_match_path and len(item["clean_title"]) >= 7:
                best_sim = 0
                best_match = None
                for rname, rpath in recipe_names.items():
                    if len(rname) < 7:
                        continue
                    if item["clean_title"] == rname:
                        best_sim = 1.0
                        best_match = rpath
                        break
                    sim = SequenceMatcher(None, item["clean_title"], rname).ratio()
                    if sim > best_sim and sim >= 0.88:
                        best_sim = sim
                        best_match = rpath

                if best_match:
                    results["open_issue_already_imported_similar"].append({
                        "open_issue": {"number": item["number"], "title": item["title"]},
                        "repo_path": best_match,
                        "similarity": round(best_sim, 2)
                    })

    if args.json:
        print(json.dumps(results, indent=2))
        return

    # Terminal Report
    print("=" * 70)
    print("RECIPE REPOSITORY DUPLICATE SCANNER")
    print("=" * 70)
    print(f"Scanned {len(open_issues)} open issues, {len(closed_issues)} closed issues, and {len(recipe_names)} repo recipes.")
    print()

    # 1. Exact URL duplicates
    dups = results["open_issue_exact_recipe_duplicates"]
    print(f"1. Open Issue Exact Recipe Duplicates ({len(dups)} groups):")
    if not dups:
        print("   None found.")
    else:
        for d in dups:
            print(f"   URL: {d['url']}")
            print(f"     Primary (Keep):  #{d['primary']['number']} - {d['primary']['title']}")
            for dup in d['duplicates']:
                print(f"     Duplicate (Close): #{dup['number']} - {dup['title']}")
                if args.close:
                    close_github_issue(dup['number'], duplicate_of=d['primary']['number'])
    print()

    # 2. Open duplicates of closed issues
    closed_dups = results["open_issue_duplicates_closed"]
    print(f"2. Open Issues Duplicating Closed Issues ({len(closed_dups)} found):")
    if not closed_dups:
        print("   None found.")
    else:
        for cd in closed_dups:
            oi = cd['open_issue']
            ci = cd['closed_issue']
            print(f"   Open #{oi['number']}: {oi['title']}")
            print(f"     -> Closed #{ci['number']}: {ci['title']} ({cd['url']})")
            if args.close:
                close_github_issue(oi['number'], duplicate_of=ci['number'])
    print()

    # 3. Exact URL matches already imported in codebase
    imported_exact = results["open_issue_already_imported_exact"]
    print(f"3. Open Issues With Exact URL Already Imported in Codebase ({len(imported_exact)} found):")
    if not imported_exact:
        print("   None found.")
    else:
        for imp in imported_exact:
            oi = imp['open_issue']
            print(f"   Open #{oi['number']}: {oi['title']}")
            print(f"     -> Codebase: {imp['repo_path']} ({imp['url']})")
            if args.close:
                close_github_issue(oi['number'], comment=f"Closed as duplicate. Recipe already imported in codebase: {imp['repo_path']}")
    print()

    # 4. High-similarity titles matching existing repo recipes
    imported_sim = results["open_issue_already_imported_similar"]
    print(f"4. Open Issues With Similar Recipe in Codebase ({len(imported_sim)} found):")
    if not imported_sim:
        print("   None found.")
    else:
        for imp in imported_sim:
            oi = imp['open_issue']
            print(f"   Open #{oi['number']}: {oi['title']}")
            print(f"     -> Codebase: {imp['repo_path']} ({imp['similarity']*100:.0f}% match)")
    print()

    # 5. Shared roundup URLs
    roundups = results["open_issue_shared_roundup_urls"]
    if roundups:
        print(f"5. Issues Sharing Multi-Recipe Roundups / Article URLs ({len(roundups)} collections):")
        for r in roundups:
            print(f"   Roundup: {r['url']}")
            print(f"     #{r['primary']['number']} - {r['primary']['title']}")
            for dup in r['duplicates']:
                print(f"     #{dup['number']} - {dup['title']}")
        print()

    # 6. High-similarity open titles
    sims = results["open_issue_high_similarity_titles"]
    if sims:
        print(f"6. Open Issues With High Title Similarity ({len(sims)} pairs):")
        for s in sims:
            print(f"   [{s['similarity']*100:.0f}% similarity]:")
            print(f"     Issue A: #{s['issue_1']['number']} - {s['issue_1']['title']}")
            print(f"     Issue B: #{s['issue_2']['number']} - {s['issue_2']['title']}")
        print()

    print("=" * 70)

if __name__ == "__main__":
    main()
