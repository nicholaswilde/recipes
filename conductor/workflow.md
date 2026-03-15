# Project Workflow

## Guiding Principles

1. **The Plan is the Source of Truth:** All work must be tracked in `plan.md`
2. **The Tech Stack is Deliberate:** Changes to the tech stack must be documented in `tech-stack.md` *before* implementation
3. **Test-Driven Development:** Write unit tests before implementing functionality
4. **High Code Coverage:** Aim for >80% code coverage for all modules
5. **User Experience First:** Every decision should prioritize user experience
6. **Non-Interactive & CI-Aware:** Prefer non-interactive commands. Use `CI=true` for watch-mode tools (tests, linters) to ensure single execution.

## Task Workflow

All tasks follow a strict lifecycle:

### Standard Task Workflow

1. **Select Task:** Choose the next available task from `plan.md` in sequential order

2. **Mark In Progress:** Before beginning work, edit `plan.md` and change the task from `[ ]` to `[~]`

3. **Write Failing Tests (Red Phase):**
   - Create a new test file for the feature or bug fix.
   - Write one or more unit tests that clearly define the expected behavior and acceptance criteria for the task.
   - **CRITICAL:** Run the tests and confirm that they fail as expected. This is the "Red" phase of TDD. Do not proceed until you have failing tests.

4. **Implement to Pass Tests (Green Phase):**
   - Write the minimum amount of application code necessary to make the failing tests pass.
   - Run the test suite again and confirm that all tests now pass. This is the "Green" phase.

5. **Refactor (Optional but Recommended):**
   - With the safety of passing tests, refactor the implementation code and the test code to improve clarity, remove duplication, and enhance performance without changing the external behavior.
   - Rerun tests to ensure they still pass after refactoring.

6. **Verify Coverage:** Run coverage reports using the project's chosen tools. For example, in a Python project, this might look like:

   ```bash
   pytest --cov=app --cov-report=html
   ```

   Target: >80% coverage for new code. The specific tools and commands will vary by language and framework.

7. **Document Deviations:** If implementation differs from tech stack:
   - **STOP** implementation
   - Update `tech-stack.md` with new design
   - Add dated note explaining the change
   - Resume implementation

8. **Commit Code Changes:**
   - Stage all code changes related to the task.
   - Propose a clear, concise commit message e.g, `feat(ui): Create basic HTML structure for calculator`.
   - Perform the commit.

9. **Attach Task Summary with Git Notes:**
   - **Step 9.1: Get Commit Hash:** Obtain the hash of the *just-completed commit* (`git log -1 --format="%H"`).
   - **Step 9.2: Draft Note Content:** Create a detailed summary for the completed task. This should include the task name, a summary of changes, a list of all created/modified files, and the core "why" for the change.
   - **Step 9.3: Attach Note:** Use the `git notes` command to attach the summary to the commit.

     ```bash

     # The note content from the previous step is passed via the -m flag.

     git notes add -m "<note content>" <commit_hash>
     ```

10. **Get and Record Task Commit SHA:**
    - **Step 10.1: Update Plan:** Read `plan.md`, find the line for the completed task, update its status from `[~]` to `[x]`, and append the first 7 characters of the *just-completed commit's* commit hash.
    - **Step 10.2: Write Plan:** Write the updated content back to `plan.md`.

11. **Commit Plan Update:**
    - **Action:** Stage the modified `plan.md` file.
    - **Action:** Commit this change with a descriptive message (e.g., `conductor(plan): Mark task 'Create user model' as complete`).

### Phase Completion Verification and Checkpointing Protocol

**Trigger:** This protocol is executed immediately after a task is completed that also concludes a phase in `plan.md`.

1. **Announce Protocol Start:** Inform the user that the phase is complete and the verification and checkpointing protocol has begun.

2. **Ensure Test Coverage for Phase Changes:**
    - **Step 2.1: Determine Phase Scope:** To identify the files changed in this phase, you must first find the starting point. Read `plan.md` to find the Git commit SHA of the *previous* phase's checkpoint. If no previous checkpoint exists, the scope is all changes since the first commit.
    - **Step 2.2: List Changed Files:** Execute `git diff --name-only <previous_checkpoint_sha> HEAD` to get a precise list of all files modified during this phase.
    - **Step 2.3: Verify and Create Tests:** For each file in the list:
        - **CRITICAL:** First, check its extension. Exclude non-code files (e.g., `.json`, `.md`, `.yaml`).
        - For each remaining code file, verify a corresponding test file exists.
        - If a test file is missing, you **must** create one. Before writing the test, **first, analyze other test files in the repository to determine the correct naming convention and testing style.** The new tests **must** validate the functionality described in this phase's tasks (`plan.md`).

3. **Execute Automated Tests with Proactive Debugging:**
    - Before execution, you **must** announce the exact shell command you will use to run the tests.
    - **Example Announcement:** "I will now run the automated test suite to verify the phase. **Command:** `CI=true npm test`"
    - Execute the announced command.
    - If tests fail, you **must** inform the user and begin debugging. You may attempt to propose a fix a **maximum of two times**. If the tests still fail after your second proposed fix, you **must stop**, report the persistent failure, and ask the user for guidance.

4. **Propose a Detailed, Actionable Manual Verification Plan:**
    - **CRITICAL:** To generate the plan, first analyze `product.md`, `product-guidelines.md`, and `plan.md` to determine the user-facing goals of the completed phase.
    - You **must** generate a step-by-step plan that walks the user through the verification process, including any necessary commands and specific, expected outcomes.
    - The plan you present to the user **must** follow this format:

        **For a Frontend Change:**

        ```bash
        The automated tests have passed. For manual verification, please follow these steps:

        **Manual Verification Steps:**

        1. **Start the development server with the command:** `npm run dev`
        2. **Open your browser to:** `http://localhost:3000`
        3. **Confirm that you see:** The new user profile page, with the user's name and email displayed correctly.
        ```

        **For a Backend Change:**

        ```
        The automated tests have passed. For manual verification, please follow these steps:

        **Manual Verification Steps:**

        1. **Ensure the server is running.**
        2. **Execute the following command in your terminal:** `curl -X POST http://localhost:8080/api/v1/users -d '{"name": "test"}'`
        3. **Confirm that you receive:** A JSON response with a status of `201 Created`.
        ```

5. **Await Explicit User Feedback:**
    - After presenting the detailed plan, ask the user for confirmation: "**Does this meet your expectations? Please confirm with yes or provide feedback on what needs to be changed.**"
    - **PAUSE** and await the user's response. Do not proceed without an explicit yes or confirmation.

6. **Create Checkpoint Commit:**
    - Stage all changes. If no changes occurred in this step, proceed with an empty commit.
    - Perform the commit with a clear and concise message (e.g., `conductor(checkpoint): Checkpoint end of Phase X`).

7. **Attach Auditable Verification Report using Git Notes:**
    - **Step 7.1: Draft Note Content:** Create a detailed verification report including the automated test command, the manual verification steps, and the user's confirmation.
    - **Step 7.2: Attach Note:** Use the `git notes` command and the full commit hash from the previous step to attach the full report to the checkpoint commit.

8. **Get and Record Phase Checkpoint SHA:**
    - **Step 8.1: Get Commit Hash:** Obtain the hash of the *just-created checkpoint commit* (`git log -1 --format="%H"`).
    - **Step 8.2: Update Plan:** Read `plan.md`, find the heading for the completed phase, and append the first 7 characters of the commit hash in the format `[checkpoint: <sha>]`.
    - **Step 8.3: Write Plan:** Write the updated content back to `plan.md`.

9. **Commit Plan Update:**
    - **Action:** Stage the modified `plan.md` file.
    - **Action:** Commit this change with a descriptive message following the format `conductor(plan): Mark phase '<PHASE NAME>' as complete`.

10. **Announce Completion:** Inform the user that the phase is complete and the checkpoint has been created, with the detailed verification report attached as a git note.

### Quality Gates

Before marking any task complete, verify:

- [ ] All tests pass
- [ ] Code coverage meets requirements (>80%)
- [ ] Code follows project's code style guidelines (as defined in `code_styleguides/`)
- [ ] All public functions/methods are documented (e.g., docstrings, JSDoc, GoDoc)
- [ ] Type safety is enforced (e.g., type hints, TypeScript types, Go types)
- [ ] No linting or static analysis errors (using the project's configured tools)
- [ ] Works correctly on mobile (if applicable)
- [ ] Documentation updated if needed
- [ ] No security vulnerabilities introduced

## Development Commands

### Building and Running

- **Install Zensical:** `task docs:deps` (uses `uv` and `pip`)
- **Update Zensical:** `task docs:update`
- **Start local development server:** `task serve` (access at `http://127.0.0.1:8000`)
- **Start Cooklang server:** `task server`
- **Deploy to GitHub Pages:** The GitHub Actions workflow `ci.yaml` automatically deploys the docs on pushes to `main` branch (paths `docs/**`, `mkdocs.**`). Manually, this would involve `zensical gh-deploy --force` after installing dependencies.

### Helper Tasks

- **Search Emojis:** `task emoji-search` (filters `includes/emoji.yaml`).
- **List Ingredients:** `task list-ingredients` (lists all used ingredients to help with consistency).
- **Validate Config:** `task validate` (checks `zensical.toml` syntax).
- **Spellcheck File:** `task spellcheck-file FILE=path/to/file`.

### GitHub CLI Operations

- **List Issues:** `gh issue list` (lists open issues in the repository).
- **Filter Issues by Label:** `gh issue list --label required` (filters issues to show only those requiring action).

## Testing Requirements

### Unit Testing

- Every module must have corresponding tests.
- Use appropriate test setup/teardown mechanisms (e.g., fixtures, beforeEach/afterEach).
- Mock external dependencies.
- Test both success and failure cases.

### Integration Testing

- Test complete user flows
- Verify database transactions
- Test authentication and authorization
- Check form submissions

### Mobile Testing

- Test on actual iPhone when possible
- Use Safari developer tools
- Test touch interactions
- Verify responsive layouts
- Check performance on 3G/4G

## Code Review Process

### Self-Review Checklist

Before requesting review:

1. **Functionality**
   - Feature works as specified
   - Edge cases handled
   - Error messages are user-friendly

2. **Code Quality**
   - Follows style guide
   - DRY principle applied
   - Clear variable/function names
   - Appropriate comments

3. **Testing**
   - Unit tests comprehensive
   - Integration tests pass
   - Coverage adequate (>80%)

4. **Security**
   - No hardcoded secrets
   - Input validation present
   - SQL injection prevented
   - XSS protection in place

5. **Performance**
   - Database queries optimized
   - Images optimized
   - Caching implemented where needed

6. **Mobile Experience**
   - Touch targets adequate (44x44px)
   - Text readable without zooming
   - Performance acceptable on mobile
   - Interactions feel native

## Commit Guidelines

### Message Format

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting, missing semicolons, etc.
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `test`: Adding missing tests
- `chore`: Maintenance tasks

### Examples

```bash
git commit -m "feat(auth): Add remember me functionality"
git commit -m "fix(posts): Correct excerpt generation for short posts"
git commit -m "test(comments): Add tests for emoji reaction limits"
git commit -m "style(mobile): Improve button touch targets"
```

## Definition of Done

A task is complete when:

1. All code implemented to specification
2. Unit tests written and passing
3. Code coverage meets project requirements
4. Documentation complete (if applicable)
5. Code passes all configured linting and static analysis checks
6. Works beautifully on mobile (if applicable)
7. Implementation notes added to `plan.md`
8. Changes committed with proper message
9. Git note with task summary attached to the commit

## Emergency Procedures

### Critical Bug in Production

1. Create hotfix branch from main
2. Write failing test for bug
3. Implement minimal fix
4. Test thoroughly including mobile
5. Deploy immediately
6. Document in plan.md

### Data Loss

1. Stop all write operations
2. Restore from latest backup
3. Verify data integrity
4. Document incident
5. Update backup procedures

### Security Breach

1. Rotate all secrets immediately
2. Review access logs
3. Patch vulnerability
4. Notify affected users (if any)
5. Document and update security procedures

## Deployment Workflow

### Pre-Deployment Checklist

- [ ] All tests passing
- [ ] Coverage >80%
- [ ] No linting errors
- [ ] Mobile testing complete
- [ ] Environment variables configured
- [ ] Database migrations ready
- [ ] Backup created

### Deployment Steps

1. Merge feature branch to main
2. Tag release with version
3. Push to deployment service
4. Run database migrations
5. Verify deployment
6. Test critical paths
7. Monitor for errors

### Post-Deployment

1. Monitor analytics
2. Check error logs
3. Gather user feedback
4. Plan next iteration

## Continuous Improvement

- Review workflow weekly
- Update based on pain points
- Document lessons learned
- Optimize for user happiness
- Keep things simple and maintainable

## Development Conventions

- **Pre-commit hooks:**
    - `trailing-whitespace`: Removes trailing whitespace.
    - `end-of-file-fixer`: Ensures files end with a newline.
    - `mixed-line-ending`: Standardizes line endings.
    - `markdownlint`: Lints Markdown files for style and consistency.
    - `markdown-link-check`: Checks for broken links in Markdown files.
- **Linting:**
    - `task lint`: Runs `markdownlint` and `yamllint`.
    - `task markdownlint`: Runs `markdownlint-cli`.
    - `task yamllint`: Runs `yamllint`.
- **Spellchecking:** `task spellcheck` (uses `spellchecker-cli` with `dictionary.txt`).
- **Link Checking:** `task linkcheck` (uses `markdown-link-check`).
    - **Note:** DO NOT run `task linkcheck` project-wide as it takes a long time to check links in all files. Only use targeted link checks if necessary.
- **Recipe Management:** Recipes are stored in `cook/` as `.cook` files and must be organized by category in subdirectories (e.g., `cook/breakfast/`, `cook/desserts/`). There are scripts to manage these, such as `scripts/commit.sh` and `scripts/move.sh`.
- **Markdown Formatting:** Specific formatting for images (`add-lazy-loading`) and temperatures (`deg`) is applied using `sed`.
- **Front Matter:** Markdown files use front matter for metadata like comments and tags.
- **Dependencies:** Python dependencies for Zensical are managed via `pip install` in the CI workflow. `spellchecker-cli` is installed globally via `npm install`.
- **Git Commits:** If a commit addresses a GitHub issue, include the issue reference in the commit message using the `Fixes #123` syntax to automatically close the issue.
- **Zensical Navigation:** Any removal of entries from `zensical.toml` must be confirmed by the user.
- **Recipe Markdown Pages:** Recipe markdown pages in `docs/` should use emoji from `includes/emoji.yaml`.
- **Recipe Markdown Format:** Recipe markdown pages should follow a consistent format, including front matter for metadata (e.g., comments, tags), a main title with an emoji, an image with `loading=lazy`, a table for serving and time information, and sections for ingredients, cookware, and instructions. Each ingredient in the ingredients section should be prefixed with an emoji shortcode from `includes/emoji.yaml`. Instructions should be numbered steps, with `!!! tip` used for additional information.

## Recipe Import Process

1. **Find/Scrape the Recipe:**
    - Use `manage_recipes(action='search', query='...')` to find a high-quality source if needed.
    - Use `manage_recipes(action='format', format_type='cooklang', urls=[...])` to generate the initial `.cook` file content from a URL.
    - **Image/PDF Sources:** If the recipe is provided via an image or PDF (e.g., provided in a GitHub issue via an image link), download the image to a temporary file and use `tesseract <image_path> -` to extract the text. Use the extracted text to create the recipe.
    - **Pancake Princess:** If there is a "Pancake Princess" link in the source issue, include that link as an additional reference in the `## :link: Source` section of the generated Markdown recipe page.
    - **Validation:** Verify the output matches the [Cooklang Specification](./product-guidelines.md#cooklang-specification) section.
    - **Recipe Name:** Use only the name of the recipe (e.g., `My Best Friend's Mom's Paprikash` -> `Paprikash`). The name of the source or author should only be added to the title if a recipe with the same name already exists.
    - **Duplicate Handling:** If a recipe with the same name already exists, you MUST prompt the user to decide whether to:
        1. Replace the existing recipe with the new one.
        2. Rename the new recipe to include the author or source name (e.g., `Teriyaki Sauce (The Daring Gourmet)`).
    - **Unit Abbreviations:** When adding units to the cook recipe file, use the first upper case for tablespoon (e.g. `Tbsp`) and lowercase for teaspoon (e.g. `tsp`).
    - **Time Ranges:** When there is a time range in the `.cook` file, put the longest time inside of a `~{}` block and keep the shortest time outside of the block. Replace the dash with a `to` and add necessary spaces (e.g. `7-8 minutes` -> `7 to ~{8%minutes}`).
    - **Ignored Items:** Before tagging an item as an ingredient (with `@`), check `cook/config/ignored_ingredients.yaml`. If the item is listed there, do **not** tag it as an ingredient.
2. **Add the Image:** Download an image from the source, name it the same as the cook file (e.g., `Recipe Name.jpg`), and place it in the same directory as the `.cook` file. If an image cannot be found, use `manage_recipes(action='scrape', ...)` to attempt to find one or use other image generation tools.
3. **Run the Move Task:** Execute `FILES=<path/to/cookfile> task move`. This converts the `.cook` file to Markdown, runs spellcheck and link check, and generates the `zensical.toml` mapping entry (copying it to clipboard if possible).
4. **Update `zensical.toml`:** Paste the mapping entry generated by the previous step into the correct section of `zensical.toml`.
5. **Add Ingredient Emojis:** Update the generated Markdown file by adding emoji shortcodes to each item in the ingredients section (referencing `includes/emoji.yaml`). If an ingredient is missing from `includes/emoji.yaml`, use your best judgement to pick one and update `includes/emoji.yaml` with the new mapping. Ensure that the selected emoji is compatible with mkdocs-material.
6. **Add Title Emoji:** Prefix the main recipe title in the Markdown file with its corresponding emoji shortcode from `includes/emoji.yaml`.
7. **Add Tags:** Generate relevant tags for the recipe and add them to the front matter of the generated Markdown file.
8. **Volumetric to Weight Conversions:** Convert volumetric measurements to grams in the Markdown file using the following rules:
    - **Automation:** Use `convert_ingredients(ingredients=[...])` to automate weight conversions.
    - **Formatting:** Place the weight in parentheses after the volume, e.g., `2 cups (240 g) all-purpose flour`.
    - **Reference:** Use `docs/reference/measuring.md` for weight conversions.
    - **Missing Conversions:** If a conversion is missing from the reference file, look it up on the [King Arthur Baking Ingredient Weight Chart](https://www.kingarthurbaking.com/learn/ingredient-weight-chart).
    - **Update Reference:** If a new conversion is found externally, add it to `docs/reference/measuring.md` for future use.
    - **Exceptions:** Ignore gram conversions for small measurements (e.g., teaspoons, tablespoons) of spices, herbs, and seasonings.
9. **Verify the Build:** Run `zensical build` and fix any issues (e.g., broken links, linting errors) to ensure the site builds correctly.

## Issue Triage and Labeling

When reviewing open issues for potential recipes:

1. **Check for Duplicates:** Search the codebase to see if the recipe already exists.
    - If it exists, apply the `duplicate` label and add a comment linking to the existing `.cook` file.
2. **New Recipes:** If the recipe is new and valid, apply the `new recipe` label.
3. **Image/PDF Sources:** If the recipe is provided via an image or PDF, ensure it is tracked or processed using the "Recipe from Image" template standards.
4. **Enhancements:** For general improvements or lists (e.g., charts), use the `enhancement` label.
