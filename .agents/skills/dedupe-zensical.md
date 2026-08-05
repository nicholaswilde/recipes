---
name: dedupe-zensical
description: Remove duplicate array entries in the zensical.toml configuration file.
---

# Dedupe Zensical Skill

This skill removes duplicate array entries in `zensical.toml` (such as duplicate recipe links under menu categories like `Sides = [...]`).

## Usage

When a user requests to deduplicate or remove duplicates from `zensical.toml`, you should simply run the following task:

```bash
task dedupe-zensical
```

This task executes the `scripts/dedupe_zensical.py` Python script, which parses `zensical.toml`, finds exact string duplicates within any array blocks (lines between `[` and `]`), removes them, and overwrites the file in place. It prints the number of duplicates removed.
