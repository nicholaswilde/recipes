# /linkcheck-online

Perform an online link check to verify external web URLs across the repository and systematically identify and fix genuine dead links (404 errors).

## Description
This skill leverages `lychee` to scan all external hyperlinks across markdown files. It distinguishes between transient anti-scraping blocks (403/429 status codes) and genuine dead links (404 status codes), providing a systematic protocol to verify, resolve, and fix broken URLs.

## Protocol

1. **Perform Online Link Check**:
   - Execute the online link checker to test all local and remote hyperlinks under the `docs/` folder:
     ```bash
     task linkcheck
     ```
   - *Note*: This task automatically leverages `lychee` in a single Docker container, executing a parallel stream-based scan across the entire project in less than 30 seconds.

2. **Unpack and Filter Log Output**:
   - Since `lychee` checks thousands of links, isolate actual `404 Not Found` errors by searching the task logs:
     ```bash
     grep "\[404\]" .system_generated/tasks/<task-id>.log
     ```
     *(Or grep within your terminal runner's log file)*

3. **Handle Rate Limits and Transient Firewalls (403 / 429)**:
   - Many major culinary sites (such as *Food Network*, *AllRecipes*, *Food52*, *Spruce Eats*, and *Trader Joe's*) use Cloudflare/Akamai bot firewalls that block command-line requests with `403 Forbidden` or `429 Too Many Requests`.
   - These are handled automatically in the project's [lychee.toml](file:///home/nicholas/git/nicholaswilde/recipes/lychee.toml) via the `accept` array:
     ```toml
     accept = [200, 201, 202, 204, 206, 403, 405, 429, 520]
     ```
   - Keep these codes in the `accept` block to ensure transient firewall rates do not fail the CI pipeline, while still reporting host statistics.

4. **Resolve and Fix Genuine 404 Errors**:
   - For each confirmed `404` error found in Step 2:
     - Visit the parent domain or search the web to locate the updated, correct URL for that recipe or source.
     - Look up the filename in the codebase using `git grep` or a directory-wide query.
     - Replace the outdated URL with the correct one in **both** the CookLang `.cook` file and the compiled `.md` document.

5. **Final Verification & Push**:
   - Re-run `task validate` and `task linkcheck` to confirm all fixes are correct.
   - Stage and commit the corrected files using a conventional commit message (e.g. `style: fix broken 404 external links in <recipe>`) and push to the remote repository.
