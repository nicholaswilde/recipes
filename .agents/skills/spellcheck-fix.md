# /spellcheck-fix

Perform a fast spell check using typos and automatically fix any spelling errors in the repository.

## Description
This skill leverages the Rust-based `typos` engine to quickly scan the repository for spelling errors and apply fixes automatically using its built-in correction mapper.

## Protocol
1. **Run the Spellcheck Task**:
   - Check the entire repository for spelling errors:
     ```bash
     task spellcheck
     ```
   - If typos are found, the command will exit with an error and print the file paths and suggested corrections.

2. **Apply Auto-Fixes**:
   - Run the typos auto-fixer command to write all suggested spelling corrections directly to the files:
     ```bash
     typos --write-changes
     ```
   - Verify that all typos have been resolved by running the check task once more:
     ```bash
     task spellcheck
     ```

3. **Handle False Positives**:
   - If `typos` flags a correct word (such as a name, technical term, or specific ingredient name), append the term to the end of `dictionary.txt` in the root directory.
   - Run the sort task to keep the dictionary file organized:
     ```bash
     task sort
     ```
   - Re-run `task spellcheck` (which will regenerate `_typos.toml` with the newly whitelisted term and run the check again).

4. **Verify and Deploy**:
   - Verify the modifications using `git diff`.
   - Stage, commit, and push the changes following conventional commit guidelines.
