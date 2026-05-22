# /list-issues [args]

List open issues in the GitHub repository. Optionally filter by label (e.g., 'new recipe', 'required').

## Description
This skill fetches and presents open issues from the GitHub repository `nicholaswilde/recipes`, with optional filtering by labels.

## Protocol
1. **Identify Repository:** The repository is `nicholaswilde/recipes`.
2. **Fetch Issues:**
   - If `<args>` is provided, use `search_issues` with the query `repo:nicholaswilde/recipes is:open label:"<args>"`.
   - If `<args>` is not provided, use `list_issues` for the repository.
3. **Display Format:**
   - Present the issues in a clean Markdown table with the following columns:
     - **#ID**
     - **Title**
     - **Labels** (comma-separated list of names)
     - **URL** (link directly to the issue)
   - Limit the output to the most recent 10-15 issues unless more are specifically requested.
