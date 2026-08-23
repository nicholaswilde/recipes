# /create-issue <title> [description]

Create a new GitHub issue using the `gh` CLI, with structured titles and appropriate labels.

## Description

This skill automates the creation of GitHub issues ensuring consistent prefixing (e.g., `[feat]`, `[bug]`, `[docs]`) and automatically appending relevant tags (e.g., `enhancement`, `bug`).

## Protocol

1. **Format the Title:**
   - Prepend the issue title with a conventional tag based on the issue type:
     - Features/Enhancements: `[feat]: <description>`
     - Bug Fixes: `[bug]: <description>`
     - Documentation: `[docs]: <description>`
     - Chores/Maintenance: `[chore]: <description>`

2. **Select Labels:**
   - Map the issue type to standard GitHub labels:
     - `[feat]` -> `enhancement`
     - `[bug]` -> `bug`
     - `[docs]` -> `documentation`

3. **Execute via CLI:**
   - Always use the `rtk` prefix to optimize token output.
   - Run the GitHub CLI issue creation command:
     ```bash
     rtk gh issue create --title "[<type>]: <Title>" --body "<Detailed description or motivation>" --label "<label>" | cat
     ```

4. **Confirmation:**
   - Report the created issue ID and URL to the user.
