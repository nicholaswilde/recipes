# context-mode routing for Antigravity CLI

context-mode MCP tools are installed for this agy session. Use them when the
task analyzes, counts, filters, compares, searches, parses, transforms, fetches,
or otherwise processes data. Raw bytes should stay in the sandbox; only the
derived answer should enter the conversation.

## Do not dump — derive (most common mistake)

Do NOT use `context-mode/ctx_execute_file` or `ctx_execute` to print a whole file
or a full method/config (e.g. `print(FILE_CONTENT)`, `cat config.yaml`, dumping a
281-line file). That defeats the purpose: on agy the tool's stdout is saved to a
step file that you then read back, so a full dump costs your context window TWICE
(once in the result, once on the follow-up read). Print only the specific value,
matches, count, or known line-range you need:

- WRONG: `ctx_execute_file(path:"config.yaml", language:"python", code:"print(FILE_CONTENT)")`
- RIGHT (value): `code:"import yaml; d=yaml.safe_load(FILE_CONTENT); print(d['active_strategy'])"`
- RIGHT (matches): `code:"import re;[print(i+1,l) for i,l in enumerate(FILE_CONTENT.splitlines()) if 'active_strategies' in l]"`
- RIGHT (known slice): `code:"print(chr(10).join(FILE_CONTENT.splitlines()[190:230]))"`

If you truly need to read a small, exact byte range to edit it, native `Read` /
`view_file` on that range is fine — but never dump an entire file through a hook.

## Tool call surface

Antigravity CLI exposes context-mode tools as `context-mode/<tool>` calls. If
the host uses the generic MCP wrapper, call `call_mcp_tool` with:

- `ServerName`: `"context-mode"`
- `ToolName`: `"ctx_execute"`, `"ctx_execute_file"`, `"ctx_batch_execute"`,
  `"ctx_fetch_and_index"`, `"ctx_search"`, or `"ctx_index"`
- `Arguments`: a JSON object for that tool

Do not read `~/.gemini/antigravity-cli/mcp/context-mode/*.json` to discover
schemas. Those files are agy's cached tool schemas and reading them spends
context. Use these argument shapes instead:

- `context-mode/ctx_execute`: `{"language":"python","code":"..."}`
- `context-mode/ctx_execute_file`:
  `{"path":"path/to/file","language":"python","code":"..."}`
- `context-mode/ctx_batch_execute`:
  `{"commands":[{"label":"...","command":"..."}],"queries":["..."]}`
- `context-mode/ctx_fetch_and_index`: `{"url":"https://...","source":"..."}`
- `context-mode/ctx_search`: `{"queries":["q1","q2"]}`
- `context-mode/ctx_index`: `{"path":"path/to/file-or-dir","source":"..."}`
  or `{"content":"...","source":"..."}`

## Mandatory routing

- Think in code. For analyze/count/filter/compare/search/parse/transform tasks,
  write code with `context-mode/ctx_execute` and print only the final answer.
  Program the analysis; do not read raw data and compute mentally.
- File read for analysis: there is no separate `ctx_read` tool.
  `context-mode/ctx_execute_file` is the context-mode file-read surface. It
  loads the file into `FILE_CONTENT` inside the sandbox. Print only selected
  lines, counts, matches, summaries, or structured results. Never print
  `FILE_CONTENT` wholesale unless the user explicitly asks for a full file dump.
- Native `Read` / `view_file` is correct when editing requires exact bytes, or
  when a small known range is needed. For analysis, exploration, summarization,
  counting, filtering, or searching inside a file, use
  `context-mode/ctx_execute_file`.
- Use one `context-mode/ctx_batch_execute` call for multi-command repository
  reconnaissance. One batch should replace many shell/list/search calls.
- Use `context-mode/ctx_execute` for shell commands whose output may exceed a
  short fixed answer. Native Bash is only for git, mkdir, rm, mv, navigation,
  installs, or short observable output.
- Use `context-mode/ctx_fetch_and_index` for web content, then
  `context-mode/ctx_search` to query it. Do not dump raw HTML into the
  conversation.
- Use `context-mode/ctx_index` only when content should be stored and searched
  later. For a one-off file question, prefer `context-mode/ctx_execute_file`;
  for follow-up retrieval, index with a descriptive `source` and query with
  `context-mode/ctx_search`.
- Return only derived answers, concise summaries, selected snippets, or file
  paths to written artifacts. Do not paste raw command dumps, full files, large
  search results, cached schemas, or raw HTML into the conversation.
