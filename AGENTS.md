# Project Rules & Guidelines

## RTK Command Guidelines
- **Git Operations**: Prefix `git` commands with `rtk` (e.g., `rtk git status`, `rtk git diff`, `rtk git log`, `rtk git commit`, `rtk git push`).
- **GitHub CLI**: Prefix `gh` commands with `rtk` (e.g., `rtk gh issue list | cat`, `rtk gh pr status | cat`). Always pipe `gh` commands to `cat` to bypass interactive pagers.
- **File & Directory Inspection**: Use `rtk ls`, `rtk tree`, `rtk find`, or `rtk read` when listing or reading files to get token-optimized output.
- **Searching**: Use `rtk rg` for line search pattern matching.
- **Build & Test Outputs**: Use `rtk err` or `rtk test` when running build/test commands to filter output to errors/failures only (e.g. `rtk test pio test -e native`).

## Context-Mode Routing Guidelines
- **Derive, Do Not Dump**: Do NOT use `context-mode/ctx_execute_file` or `ctx_execute` to print a whole file or a full method/config. Print only the specific value, matches, count, or known line-range needed.
- **Tool call surface**: If using generic MCP wrappers, call `call_mcp_tool` with `ServerName: "context-mode"` and `ToolName: "ctx_execute"`, `"ctx_execute_file"`, `"ctx_batch_execute"`, `"ctx_fetch_and_index"`, `"ctx_search"`, or `"ctx_index"`.
- **Mandatory Routing**:
  - For analyze/count/filter/compare/search/parse/transform tasks, write code with `context-mode/ctx_execute` and print only the final answer.
  - For analyzing/exploring/searching inside a file, use `context-mode/ctx_execute_file`. Use native `Read` / `view_file` only when editing requires exact bytes or a small known range.
  - Use `context-mode/ctx_batch_execute` for multi-command repository reconnaissance.
  - Use `context-mode/ctx_execute` for shell commands whose output may exceed a short fixed answer.
  - Use `context-mode/ctx_fetch_and_index` for web content, then `context-mode/ctx_search` to query it.
  - Return only derived answers, concise summaries, selected snippets, or file paths to written artifacts.

## Ponytail (Lazy Senior Dev Mode) Guidelines
- **Stop at the first rung that holds**:
  1. Does this need to be built at all? (YAGNI)
  2. Does it already exist in this codebase? Reuse existing helpers/utils/patterns.
  3. Does the standard library already do this?
  4. Does a native platform feature cover it?
  5. Does an already-installed dependency solve it?
  6. Can this be one line?
  7. Only then: write the minimum code that works.
- **Bug fix = root cause, not symptom**: Fix the shared function/path rather than individual callers.
- **Rules**:
  - No unrequested abstractions, boilerplate, or avoidable dependencies.
  - Deletion over addition. Boring over clever. Fewest files possible.
  - Shortest working diff wins, once the problem is understood.
  - Mark deliberate simplifications cutting a real corner with a `ponytail:` comment naming the ceiling and upgrade path.
  - Ensure logic leaves behind ONE runnable check (assert-based demo/self-check or small test file; no frameworks/fixtures). Trivial one-liners need no test.

## Caveman Guidelines
Respond terse like smart caveman. All technical substance stay. Only fluff die.

Rules:
- Drop: articles (a/an/the), filler (just/really/basically), pleasantries, hedging
- Fragments OK. Short synonyms. Technical terms exact. Code unchanged.
- Pattern: [thing] [action] [reason]. [next step].
- Not: "Sure! I'd be happy to help you with that."
- Yes: "Bug in auth middleware. Fix:"

Switch level: /caveman lite|full|ultra|wenyan
Stop: "stop caveman" or "normal mode"

Auto-Clarity: drop caveman for security warnings, irreversible actions, user confused. Resume after.

Boundaries: code/commits/PRs written normal.

## CodeGraph

In repositories indexed by CodeGraph (a `.codegraph/` directory exists at the repo root), reach for it BEFORE grep/find or reading files when you need to understand or locate code:

- **MCP tool** (when available): `codegraph_explore` answers most code questions in one call — the relevant symbols' verbatim source plus the call paths between them, including dynamic-dispatch hops grep can't follow. Name a file or symbol in the query to read its current line-numbered source. If it's listed but deferred, load it by name via tool search.
- **Shell** (always works): `codegraph explore "<symbol names or question>"` prints the same output.

If there is no `.codegraph/` directory, skip CodeGraph entirely — indexing is the user's decision.

## Serena Semantic Code Tools

Serena MCP provides Language Server Protocol (LSP) backed semantic coding tools, token-efficient AST symbol search, reference-aware refactoring, and persistent project memories.

- **Project Activation**: When Serena is available, ensure the workspace is active before querying code. If Serena returns `No active project`, call `activate_project` with the project root directory.
- **Symbol Inspection Over File Dumps**: Do not dump entire source code files into context. Use `get_symbols_overview` for a high-level view of symbols in a file, or `find_symbol` to retrieve specific classes, functions, or methods with their bodies.
- **Pattern & Reference Search**: Use `search_for_pattern` to locate symbols when the exact path is unknown, and `find_referencing_symbols` to analyze blast radius and callers.
- **Atomic Refactoring**: Prefer Serena's reference-aware editing tools (`rename_symbol`, `safe_delete_symbol`, `replace_symbol_body`) over manual regex or line-based text edits when refactoring existing symbols.
- **Persistent Memory**: Use `read_memory`, `write_memory`, and `list_memories` to retrieve or store durable project facts and conventions across agent sessions.
- **Diagnostics**: Use `get_diagnostics_for_file` to inspect LSP compiler/linter warnings and errors on modified files.

## Project Overview & Tech Stack

This project is a personal recipe collection managed as a documentation site using [Zensical](file:///home/nicholas/git/nicholaswilde/recipes/zensical.toml) ([MkDocs](file:///home/nicholas/git/nicholaswilde/recipes/mkdocs.yml)). Recipes are authored in [Cooklang](https://cooklang.org/docs/spec/) format (`.cook`), converted to Markdown (`.md`), and served by Zensical. The site is deployed to GitHub Pages via automated CI/CD workflows.

- **Static Site Generator:** Zensical / MkDocs with custom CSS/JS and MathJax support.
- **Recipe Source:** Cooklang (`cook/**/*.cook`) organized by category subdirectories (e.g., `cook/breakfast/`, `cook/desserts/`).
- **Intermediate Docs:** Markdown (`docs/**/*.md`) served by Zensical.
- **Automation & Tools:** Taskfile ([Taskfile.yml](file:///home/nicholas/git/nicholaswilde/recipes/Taskfile.yml)), GitHub Actions ([ci.yaml](file:///home/nicholas/git/nicholaswilde/recipes/.github/workflows/ci.yaml)), Docker, `uv` / `pip` for Python dependency management, `cwebp` for WebP conversion, `oxipng` for PNG optimization.
- **Quality Assurance:** `rumdl`, `yamllint`, `spellchecker-cli`, `markdown-link-check`.

## Development Commands

### Building & Serving

- **Install Zensical Dependencies:** `task docs:deps` (uses `uv` and `pip`).
- **Update Zensical:** `task docs:update`.
- **Start Development Server:** `task serve` (serves site locally at `http://127.0.0.1:8000`).
- **Start Cooklang Server:** `task server`.

### Helper Tasks

- **Search Emojis:** `task emoji-search` (queries [includes/emoji.yaml](file:///home/nicholas/git/nicholaswilde/recipes/includes/emoji.yaml)).
- **List Ingredients:** `task list-ingredients` (lists all used ingredients for consistency).
- **Validate Config:** `task validate` (validates [zensical.toml](file:///home/nicholas/git/nicholaswilde/recipes/zensical.toml) syntax).
- **Validate Cooklang File:** `task validate-cook FILE="path/to/recipe.cook"`.
- **Spellcheck File:** `task spellcheck-file FILE=path/to/file` (targeted spellcheck using [dictionary.txt](file:///home/nicholas/git/nicholaswilde/recipes/dictionary.txt)).
- **Lint Files:** `task lint` (runs `rumdl` and `yamllint`). Specific linters: `task rumdl`, `task yamllint`.
- **Compile & Move Recipe:** `FILES=<path/to/cookfile> task move` (converts `.cook` to Markdown, runs checks, and generates `zensical.toml` mapping entry).
- **Link Checking Note:** DO NOT run `task linkcheck` project-wide as it is excessively slow. Only use targeted link checks when necessary.

## Recipe Content & Formatting Guidelines

- **Prose Style & Tone:** Casual, friendly, encouraging, and unambiguous. Brief anecdotes or personal context in front matter or comments are welcome.
- **Personal Recipes:** Retain personal or family recipes without URLs (e.g., `Recipe Box`, `Tante Myrna Seccia`). Do not remove or deprecate them during cleanup or duplicate audits. Always consult [.agents/author_whitelist.txt](file:///home/nicholas/git/nicholaswilde/recipes/.agents/author_whitelist.txt).
- **Visual Identity:** Every recipe should feature a high-quality finished dish photograph (WebP or PNG) with `loading="lazy"`. Placeholders or generated hero images are used when source photos are unavailable.
- **Titles:** Prefix each recipe title with its corresponding emoji shortcode from [includes/emoji.yaml](file:///home/nicholas/git/nicholaswilde/recipes/includes/emoji.yaml). Always use text shortcodes (e.g. `:bread:`), never paste raw Unicode emoji characters.
- **Ingredients:** Prefix each ingredient with its corresponding emoji shortcode from `includes/emoji.yaml`. The emoji must precede the measurement (e.g., `:bread: 1/2 cup (60 g) all-purpose flour`).
- **Cookware:** Prefix each cookware item with its corresponding emoji shortcode from `includes/emoji.yaml`.
- **Measurements & Gram Conversions:**
    - Standard unit abbreviations: `Tbsp`, `tsp`, `cup`, `lbs`.
    - Volumetric to weight conversions: Provide gram conversions in parentheses for major ingredients (e.g., `2 cups (240 g) all-purpose flour`). Reference [docs/reference/measuring.md](file:///home/nicholas/git/nicholaswilde/recipes/docs/reference/measuring.md) or the King Arthur Baking Ingredient Weight Chart.
    - Exceptions: Omit gram conversions for small amounts (teaspoons/tablespoons) of spices, herbs, and seasonings.
- **Instructions:** Numbered steps focusing on concise, actionable tasks.
- **Callouts:** Use `!!! tip` for variations, suggestions, or pro-tips.
- **Sources:** All recipes must include a `## :link: Source` section at the end of the Markdown file. If a "Pancake Princess" bake-off link is provided in the source issue, include it as an additional reference.
- **Dietary Restrictions & Selection:** Recipes must be lacto-ovo vegetarian (no meat, poultry, fish, or seafood; dairy and eggs allowed). Rank candidates using a Bayesian average rating formula ([scripts/rank_recipes_bayesian.py](file:///home/nicholas/git/nicholaswilde/recipes/scripts/rank_recipes_bayesian.py)).
- **Reference Charts:** Use the Grid Cards layout (`<div class="grid cards" markdown>`) with horizontal rules (`---`) separating card titles from content.
- **Navigation Safety:** Any removal of entries from [zensical.toml](file:///home/nicholas/git/nicholaswilde/recipes/zensical.toml) must be confirmed by the user.

## Cooklang Authoring Guidelines

Recipes are authored in `.cook` files following the Cooklang specification and project conventions:

- **Metadata:** Defined at the top with `>> key: value` (`source`, `serves`, `total time`, `image`, `tags`).
- **Inline Ingredients:** Embedded directly into the instruction steps where first used (`@ingredient{quantity%unit}`). Do NOT list ingredients separately at the top.
- **Ignored Ingredients:** Check [cook/config/ignored_ingredients.yaml](file:///home/nicholas/git/nicholaswilde/recipes/cook/config/ignored_ingredients.yaml) before tagging an item with `@`. If listed, do not tag it as an ingredient.
- **Cookware:** Use `#cookware{}` syntax (e.g., `#frying pan{}`).
- **Timers & Time Ranges:** Use `~{duration%unit}`. For time ranges, place the longest duration inside the timer block and the shortest outside using `to` (e.g., `7 to ~{8%minutes}`, never `~{7-8%minutes}`).
- **Clean Formatting:** Use standard decimals or fractions (`1.5`, `1/8`); avoid HTML entities like `&amp; 1/2`.
- **Validation:** Always validate `.cook` files with `task validate-cook FILE="path/to/recipe.cook"`.

## Markdown & Content Tabs Style Guide

For multi-serving, multi-variation, or batch recipes, use `pymdownx.tabbed` content tabs:

- **Syntax & Indentation:** Use `=== "Tab Label"` syntax. All content within the tab block must be indented with **4 spaces**.
- **Separation:** A blank line must separate the tab definition from its content, as well as successive tab blocks.
- **Naming Conventions:** Short, descriptive Title Case labels (e.g., `"9 Inch"`, `"10 Inch"`).
- **Header Nesting:** If a tab contains subsections, use indented H3 (`###`) or H4 (`####`) headers (indented 4 spaces).
- **Multi-Section Alignment:** When both ingredients and instructions have variations, use separate tab blocks under `## :salt: Ingredients` and `## :pencil: Instructions` with matching tab labels.

## Code Style Guides

### General Principles

- **Readability & Consistency:** Simple, readable code that matches existing codebase patterns.
- **Documentation:** Document *why* something is done, not just *what*. Update [scripts-registry.md](file:///.agents/skills/scripts-registry.md) for any new helper or automation script in `scripts/`.

### Python (Google Style Summary)

- **Line Length & Indentation:** 80 characters maximum line length; 4 spaces indentation (no tabs).
- **Naming:** `snake_case` for modules, functions, methods, and variables; `PascalCase` for classes; `ALL_CAPS_WITH_UNDERSCORES` for constants.
- **Docstrings:** `"""triple double quotes"""` with one-line summary and `Args:`, `Returns:`, `Raises:` sections for all public modules, functions, classes, and methods.
- **Type Annotations:** Encouraged for all public functions/APIs.
- **Executable Scripts:** Include a `main()` function called within an `if __name__ == '__main__':` block.

### JavaScript (Google Style Summary)

- **Modules & Exports:** ES modules (`import`/`export`) with named exports only (no default exports). Mandatory `.js` extensions in imports.
- **Formatting:** 2 spaces indentation; semicolons required; 80 character limit; single quotes (`'`) for string literals.
- **Variables:** Use `const` by default, `let` if reassignment needed; `var` is forbidden.
- **Equality:** Always use strict equality (`===` / `!==`).

### HTML / CSS (Google Style Summary)

- **General:** HTTPS for embedded resources; 2 spaces indentation; lowercase element names, attributes, and selectors.
- **Quotes:** Double quotes (`""`) for HTML attribute values; single quotes (`''`) for CSS attribute selectors and properties.
- **CSS Selectors & Units:** Meaningful kebab-case class names; avoid ID selectors and `!important`; omit units for `0` values (e.g., `margin: 0;`).

## Recipe Import & Issue Triage Workflow

### Recipe Import Steps

1. **Find / Scrape:** Find a high-quality lacto-ovo vegetarian source with a high Bayesian rating. For OCR sources (images/PDFs), extract text using `tesseract` or `liteparse`.
2. **Naming & Duplicates:** Use the base recipe name only. If a recipe with the same name already exists, prompt the user to choose between replacing the existing recipe or appending the author/source to the title.
3. **Draft Cooklang:** Format as `.cook` with inline ingredients, correct unit abbreviations (`Tbsp`, `tsp`), time ranges, and ignored ingredients verified.
4. **Hero Image:** Place corresponding image alongside the `.cook` file. Generate custom hero image if requested.
5. **Compile & Move:** Run `FILES=<path/to/cookfile> task move`.
6. **Update Navigation:** Insert the generated entry into [zensical.toml](file:///home/nicholas/git/nicholaswilde/recipes/zensical.toml).
7. **Emojis & Conversions:** Add emoji shortcodes from `includes/emoji.yaml` to title and ingredients; add gram weight conversions in parentheses for major ingredients.
8. **Verify Build:** Run `task validate` and `zensical build` to ensure error-free compilation.

### Issue Triage

- **Duplicate:** Label as `duplicate` with a link to existing `.cook` file.
- **New Recipe:** Label as `new recipe` when valid.
- **Enhancement:** Label as `enhancement` for general improvements, charts, or reference guides.
