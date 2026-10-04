# Serena Semantic Code Tools

Serena MCP provides Language Server Protocol (LSP) backed semantic coding tools, token-efficient AST symbol search, reference-aware refactoring, and persistent project memories.

## Guidelines

- **Project Activation**: When Serena is available, ensure the workspace is active before querying code. If Serena returns `No active project`, call `activate_project` with the project root directory.
- **Symbol Inspection Over File Dumps**: Do not dump entire source code files into context. Use `get_symbols_overview` for a high-level view of symbols in a file, or `find_symbol` to retrieve specific classes, functions, or methods with their bodies.
- **Pattern & Reference Search**: Use `search_for_pattern` to locate symbols when the exact path is unknown, and `find_referencing_symbols` to analyze blast radius and callers.
- **Atomic Refactoring**: Prefer Serena's reference-aware editing tools (`rename_symbol`, `safe_delete_symbol`, `replace_symbol_body`) over manual regex or line-based text edits when refactoring existing symbols.
- **Persistent Memory**: Use `read_memory`, `write_memory`, and `list_memories` to retrieve or store durable project facts and conventions across agent sessions.
- **Diagnostics**: Use `get_diagnostics_for_file` to inspect LSP compiler/linter warnings and errors on modified files.
