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
