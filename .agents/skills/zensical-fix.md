# /zensical-fix

Validate the Zensical project and fix common issues found during build.

## Description
This skill validates the Zensical configuration and automatically or systematically fixes any issues found during the build process.

## Protocol
1. **Validate Configuration:** Run `task validate` to ensure `zensical.toml` is syntactically correct.
2. **Perform Build:** Run `zensical build` and capture the output.
3. **Analyze and Fix:**
   - **Unused Link Definitions:** If the build reports unused link definitions in newly modified or relevant files, remove them.
   - **Unresolved Link References:** Fix any broken internal links or missing reference definitions.
   - **Spellcheck:** If there are spelling warnings (e.g., from `task move` or a manual check), add valid technical terms or ingredient names to `dictionary.txt` and run `task sort`.
   - **Missing Emojis:** If ingredients are missing emojis, update `includes/emoji.yaml` and then update the recipe markdown.
   - **Missing Conversions:** If gram conversions are missing or incorrect, update `docs/reference/measuring.md` and the recipe markdown.
4. **Final Verification:** Run `zensical build` again to confirm that critical issues (errors and relevant warnings) are resolved.
