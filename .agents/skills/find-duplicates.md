# /find-duplicates

Parse the repository recipes, analyze them for title and ingredient similarities, and identify duplicates or highly similar recipes.

## Description

This skill systematically walks through all active recipe markdown files in the repository, normalizes their titles and ingredient lists, performs similarity comparisons (title similarity ratio and ingredient Jaccard index), and generates a report highlighting suspected duplicates, shape/format variations, and identical base formulas (e.g., pastry doughs).

## Protocol

1. **Identify Recipe Files:**
   - Walk through all directories under `docs/` (excluding non-recipe asset and configuration folders: `assets`, `css`, `javascripts`, `stylesheets`, `reference`).
   - Collect all `.md` files except `index.md`, `README.md`, and `tags.md`.

2. **Parse Titles and Ingredients:**
   - For each recipe file, extract the title from the first `# ` header, stripping away markdown symbols and any emoji shortcodes (e.g., `:lemon:`, `:jack_o_lantern:`).
   - Locate the ingredients sections by scanning for subheadings starting with `##` that contain the word "Ingredients" or the emoji shortcode `:salt:`.
   - Extract all lines starting with `-` or `*` within those sections until the next subheading.
   - Clean and isolate core ingredient names:
     - Keep the anchor text from markdown links: `[text](url)` -> `text`, `[text][ref]` -> `text`.
     - Remove quantities, fractions, decimals, and unicode fraction symbols (e.g., `1.5`, `1/2`, `½`, `¼`).
     - Filter out common cooking units and adjectives (e.g., `cups`, `cup`, `g`, `oz`, `tsp`, `tbsp`, `pinch`, `dash`, `slice`, `large`, `medium`, `divided`, `optional`, `melted`, `room temperature`).
     - Standardize the remaining words to lowercase.

3. **Perform Similarity Analysis:**
   - **Title Similarity:**
     - Normalize recipe titles by converting them to lowercase, removing punctuation, and filtering out common stop words and adjectives (e.g., `the`, `a`, `an`, `easy`, `best`, `simple`, `homemade`, `quick`, `perfect`, `classic`, `recipe`, `of`).
     - Calculate the similarity ratio (e.g., SequenceMatcher ratio or Levenshtein distance) between all normalized title pairs.
     - Identify subset matches where one normalized title is entirely contained inside another (e.g., "pumpkin bread" in "the best pumpkin bread").
   - **Ingredient Similarity:**
     - For every pair of recipes, calculate the Jaccard similarity index: $J(A, B) = \frac{|A \cap B|}{|A \cup B|}$.
     - Also calculate the max overlap ratio: $\max\left(\frac{|A \cap B|}{|A|}, \frac{|A \cap B|}{|B|}\right)$.

4. **Flag Duplicates and Similarities:**
   - Flag recipe pairs with a normalized title similarity ratio $\ge 0.85$ (or subset title match) as **Suspected Duplicates by Title**.
   - Flag recipe pairs with an ingredient Jaccard index $\ge 0.65$ (or max overlap ratio $\ge 0.85$ for recipes with at least 4 ingredients) as **Suspected Duplicates by Ingredients**.

5. **Generate and Present Report:**
   - Present the findings in a clean Markdown report with four distinct sections:
     - **Direct Duplicates** (highly similar titles and significant ingredient overlaps).
     - **Technique/Format Variations** (similar base mixtures but different formats, e.g. bread vs. rolls, cake vs. cupcakes).
     - **Identical Foundations** (recipes with 100% ingredient Jaccard match, e.g. identical pastry dough bases).
     - **High Ingredient Overlaps** (distinct recipes with high ingredient similarity).
   - Recommend cleanup options (e.g., merging, archiving, or redirecting).
