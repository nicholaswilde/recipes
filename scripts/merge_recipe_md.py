#!/usr/bin/env python3

################################################################################
#
# merge_recipe_md.py
# ----------------
# Merge freshly compiled CookLang Markdown with existing manual Markdown edits
#
# @author nιcнolaѕ wιlde, 0x08b7d7a3
# @date 15 Nov 2026
# @version 0.1.0
#
################################################################################

import argparse
import re
import sys
import yaml

H1_RE = re.compile(r'^#\s+(:[a-zA-Z0-9_+-]+:)?\s*(.+)$')
IMAGE_EMBED_RE = re.compile(r'^!\[[^\]]*\](?:\[[^\]]+\]|\([^)]+\))(?:\{[^}]*\})?\s*$')
REF_DEF_RE = re.compile(r'^(\[[^\]]+\]):\s*(.+)$')
FOOTNOTE_DEF_RE = re.compile(r'^(\[\^[^\]]+\]):(.*)$')
URL_RE = re.compile(r'https?://[^\s)>]+')


def split_frontmatter(content):
    """Return (frontmatter_dict, body_str) for a Markdown document."""
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                fm = yaml.safe_load(parts[1]) or {}
                return (fm if isinstance(fm, dict) else {}), parts[2].lstrip("\n")
            except yaml.YAMLError:
                return {}, content
    return {}, content


def merge_frontmatter(existing_fm, compiled_fm):
    """Merge existing and compiled frontmatter, preserving manual tags/keys."""
    merged = dict(existing_fm)
    for key, val in compiled_fm.items():
        if key == "tags":
            existing_tags = existing_fm.get("tags", [])
            if not isinstance(existing_tags, list):
                existing_tags = []
            compiled_tags = val if isinstance(val, list) else []
            combined = list(existing_tags)
            for tag in compiled_tags:
                if tag not in combined:
                    combined.append(tag)
            merged["tags"] = combined
        else:
            merged[key] = val

    if "comments" not in merged:
        merged["comments"] = True
    return merged


def _is_standard_h2(heading):
    """Return True if an H2 heading corresponds to a standard cook-docs section."""
    low = heading.lower()
    return any(k in low for k in ("ingredients", "cookware", "instructions", "source"))


def _section_kind(heading):
    """Classify a standard H2 heading or return None for custom sections."""
    low = heading.lower()
    if "ingredients" in low:
        return "ingredients"
    if "cookware" in low:
        return "cookware"
    if "instructions" in low:
        return "instructions"
    if "source" in low:
        return "source"
    return None


def _extract_footer_defs(body_lines):
    """Strip and return (body_without_defs, list_of_def_blocks) from trailing defs."""
    ref_defs = []
    keep_lines = []
    i = 0
    while i < len(body_lines):
        line = body_lines[i]
        m_fn = FOOTNOTE_DEF_RE.match(line)
        m_ref = REF_DEF_RE.match(line)
        if m_fn:
            block = [line]
            i += 1
            while i < len(body_lines) and (
                body_lines[i].startswith("    ")
                or body_lines[i].startswith("\t")
                or body_lines[i].strip() == ""
            ):
                if body_lines[i].strip() == "" and (
                    i + 1 >= len(body_lines)
                    or not (
                        body_lines[i + 1].startswith("    ")
                        or body_lines[i + 1].startswith("\t")
                    )
                ):
                    break
                block.append(body_lines[i])
                i += 1
            ref_defs.append((m_fn.group(1), "\n".join(block).strip()))
            continue
        if m_ref:
            ref_defs.append((m_ref.group(1), line.strip()))
            i += 1
            continue
        keep_lines.append(line)
        i += 1

    while keep_lines and keep_lines[-1].strip() == "":
        keep_lines.pop()
    return keep_lines, ref_defs


def _extract_admonitions_and_mermaid(body_lines):
    """Extract manual !!! admonitions and ```mermaid blocks with their heading anchors."""
    blocks = []
    current_heading = "__top__"
    i = 0
    while i < len(body_lines):
        line = body_lines[i]
        if line.startswith("## ") or line.startswith("### "):
            current_heading = line.strip()
            i += 1
            continue

        if line.startswith("!!! "):
            start = i
            i += 1
            while i < len(body_lines):
                nxt = body_lines[i]
                if nxt.startswith("    ") or nxt.startswith("\t"):
                    i += 1
                elif nxt.strip() == "" and i + 1 < len(body_lines) and (
                    body_lines[i + 1].startswith("    ")
                    or body_lines[i + 1].startswith("\t")
                ):
                    i += 1
                else:
                    break
            block_text = "\n".join(body_lines[start:i]).rstrip()
            blocks.append((current_heading, block_text))
            continue

        if re.match(r'^```\s*mermaid\b', line):
            start = i
            i += 1
            while i < len(body_lines) and not body_lines[i].strip().startswith("```"):
                i += 1
            if i < len(body_lines):
                i += 1
            block_text = "\n".join(body_lines[start:i]).rstrip()
            blocks.append((current_heading, block_text))
            continue

        i += 1
    return blocks


def _split_h2_sections(body_lines):
    """Split body lines into (preamble_lines, list_of_(heading, content_lines))."""
    preamble = []
    sections = []
    cur_heading = None
    cur_lines = []

    for line in body_lines:
        if line.startswith("## "):
            if cur_heading is None:
                preamble = cur_lines
            else:
                sections.append((cur_heading, cur_lines))
            cur_heading = line.strip()
            cur_lines = []
        else:
            cur_lines.append(line)

    if cur_heading is None:
        preamble = cur_lines
    else:
        sections.append((cur_heading, cur_lines))
    return preamble, sections


def _merge_source_lines(existing_lines, compiled_lines):
    """Keep formatted existing source bullets and append any new compiled URLs."""
    existing_bullets = [l.strip() for l in existing_lines if l.strip().startswith("- ")]
    compiled_bullets = [l.strip() for l in compiled_lines if l.strip().startswith("- ")]

    if not existing_bullets:
        return compiled_lines

    seen_urls = set()
    seen_texts = set()
    for b in existing_bullets:
        seen_texts.add(b.lower())
        for url in URL_RE.findall(b):
            seen_urls.add(url.rstrip("/"))

    merged = list(existing_bullets)
    for b in compiled_bullets:
        urls = [u.rstrip("/") for u in URL_RE.findall(b)]
        if urls and any(u in seen_urls for u in urls):
            continue
        if b.lower() in seen_texts:
            continue
        merged.append(b)

    return [""] + merged + [""]


def _preserve_manual_blocks(lines, blocks, compiled_text):
    """Insert preserved admonition/mermaid blocks into matching anchors."""
    if not blocks:
        return lines

    norm_compiled = re.sub(r'\s+', ' ', compiled_text)
    pending = []
    for anchor, block in blocks:
        norm_block = re.sub(r'\s+', ' ', block)
        if norm_block in norm_compiled:
            continue
        pending.append((anchor, block))

    if not pending:
        return lines

    # Map each block to its target anchor or fallback just before ## :link: Source
    by_anchor = {}
    fallback_before_source = []
    existing_headings = {l.strip() for l in lines if l.startswith("## ") or l.startswith("### ")}

    for anchor, block in pending:
        if anchor in existing_headings and "source" not in anchor.lower():
            by_anchor.setdefault(anchor, []).append(block)
        else:
            fallback_before_source.append(block)

    out = []
    i = 0
    inserted_fallback = False
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("## ") and "source" in stripped.lower() and not inserted_fallback:
            for blk in fallback_before_source:
                if out and out[-1].strip() != "":
                    out.append("")
                out.extend(blk.splitlines())
                out.append("")
            inserted_fallback = True

        out.append(line)
        if stripped in by_anchor:
            # Advance to end of this heading's block (before next heading)
            i += 1
            while i < len(lines) and not (lines[i].startswith("## ") or lines[i].startswith("### ")):
                out.append(lines[i])
                i += 1
            for blk in by_anchor[stripped]:
                if out and out[-1].strip() != "":
                    out.append("")
                out.extend(blk.splitlines())
                out.append("")
            continue
        i += 1

    if fallback_before_source and not inserted_fallback:
        for blk in fallback_before_source:
            if out and out[-1].strip() != "":
                out.append("")
            out.extend(blk.splitlines())
            out.append("")

    return out


def merge_markdown(existing_content, compiled_content):
    """Merge manual edits from existing_content into freshly compiled_content."""
    existing_fm, existing_body = split_frontmatter(existing_content)
    compiled_fm, compiled_body = split_frontmatter(compiled_content)

    merged_fm = merge_frontmatter(existing_fm, compiled_fm)

    ex_lines, ex_defs = _extract_footer_defs(existing_body.splitlines())
    co_lines, co_defs = _extract_footer_defs(compiled_body.splitlines())

    ex_preamble, ex_sections = _split_h2_sections(ex_lines)
    co_preamble, co_sections = _split_h2_sections(co_lines)

    # 1. Preserve H1 emoji from existing if compiled lacks one
    ex_h1_emoji = None
    ex_image_line = None
    for l in ex_preamble:
        m_h1 = H1_RE.match(l.strip())
        if m_h1 and m_h1.group(1):
            ex_h1_emoji = m_h1.group(1)
        elif IMAGE_EMBED_RE.match(l.strip()):
            ex_image_line = l.strip()

    co_has_image = any(IMAGE_EMBED_RE.match(l.strip()) for l in co_preamble)
    new_preamble = []
    for l in co_preamble:
        m_h1 = H1_RE.match(l.strip())
        if m_h1 and not m_h1.group(1) and ex_h1_emoji:
            new_preamble.append(f"# {ex_h1_emoji} {m_h1.group(2).strip()}")
            if not co_has_image and ex_image_line:
                new_preamble.append("")
                new_preamble.append(ex_image_line)
            continue
        if m_h1 and not co_has_image and ex_image_line:
            new_preamble.append(l)
            new_preamble.append("")
            new_preamble.append(ex_image_line)
            continue
        new_preamble.append(l)

    # 2. Separate existing custom sections (before vs after Source) and manual tabs
    ex_source_lines = None
    custom_before_source = []
    custom_after_source = []
    ex_tab_sections = {}
    seen_source = False
    co_headings_lower = {h.lower() for h, _ in co_sections}

    for heading, sec_lines in ex_sections:
        kind = _section_kind(heading)
        if kind == "source":
            seen_source = True
            ex_source_lines = sec_lines
        elif kind in ("ingredients", "instructions"):
            if any(l.strip().startswith('=== "') for l in sec_lines):
                ex_tab_sections[kind] = (heading, sec_lines)
        elif not _is_standard_h2(heading) and heading.lower() not in co_headings_lower:
            if seen_source:
                custom_after_source.append((heading, sec_lines))
            else:
                custom_before_source.append((heading, sec_lines))

    # 3. Rebuild sections from compiled, preserving manual tabs, source formatting, custom sections
    merged_sections = []
    has_compiled_source = any(_section_kind(h) == "source" for h, _ in co_sections)

    for heading, sec_lines in co_sections:
        kind = _section_kind(heading)
        if kind in ("ingredients", "instructions") and kind in ex_tab_sections:
            if not any(l.strip().startswith('=== "') for l in sec_lines):
                print(
                    f"INFO: Preserved manual === tabs in '{heading}' "
                    "(use --force to overwrite from .cook)"
                )
                merged_sections.append(ex_tab_sections[kind])
                continue

        if kind == "source":
            for ch, cl in custom_before_source:
                merged_sections.append((ch, cl))
            if ex_source_lines is not None:
                merged_sections.append((heading, _merge_source_lines(ex_source_lines, sec_lines)))
            else:
                merged_sections.append((heading, sec_lines))
            for ch, cl in custom_after_source:
                merged_sections.append((ch, cl))
            continue

        merged_sections.append((heading, sec_lines))

    if not has_compiled_source:
        for ch, cl in custom_before_source:
            merged_sections.append((ch, cl))
        if ex_source_lines is not None:
            merged_sections.append(("## :link: Source", ex_source_lines))
        for ch, cl in custom_after_source:
            merged_sections.append((ch, cl))

    body_lines = list(new_preamble)
    for heading, sec_lines in merged_sections:
        if body_lines and body_lines[-1].strip() != "":
            body_lines.append("")
        body_lines.append(heading)
        body_lines.extend(sec_lines)

    # 4. Preserve manual admonitions (!!! ...) and mermaid diagrams
    admonitions = _extract_admonitions_and_mermaid(ex_lines)
    body_lines = _preserve_manual_blocks(body_lines, admonitions, "\n".join(body_lines))

    # 5. Merge footer reference / footnote definitions
    merged_defs = list(co_defs)
    co_def_keys = {k for k, _ in co_defs}
    for k, block in ex_defs:
        if k == "[1]" and k in co_def_keys:
            continue
        if k not in co_def_keys:
            merged_defs.append((k, block))
            co_def_keys.add(k)

    # If compiled had no hero image and existing had [1], keep [1]
    if not co_has_image and ex_image_line:
        for k, block in ex_defs:
            if k == "[1]" and "[1]" not in {dk for dk, _ in merged_defs}:
                merged_defs.insert(0, (k, block))

    out_parts = ["---"]
    fm_yaml = yaml.dump(merged_fm, default_flow_style=False, sort_keys=False).rstrip("\n")
    if fm_yaml:
        out_parts.append(fm_yaml)
    out_parts.append("---")
    out_parts.append("")
    out_parts.extend(body_lines)
    if merged_defs:
        if out_parts[-1].strip() != "":
            out_parts.append("")
        for _, block in merged_defs:
            out_parts.append(block)

    return "\n".join(out_parts).rstrip("\n") + "\n"


def main():
    """CLI entrypoint to merge existing and compiled recipe Markdown files."""
    parser = argparse.ArgumentParser(
        description="Merge manual edits from existing Markdown into newly compiled Markdown."
    )
    parser.add_argument("existing_md", help="Path to existing Markdown file before overwrite")
    parser.add_argument("compiled_md", help="Path to newly compiled Markdown file")
    parser.add_argument("output_md", nargs="?", default=None, help="Output path (defaults to compiled_md)")
    args = parser.parse_args()

    out_path = args.output_md or args.compiled_md
    with open(args.existing_md, "r", encoding="utf-8") as f:
        existing_content = f.read()
    with open(args.compiled_md, "r", encoding="utf-8") as f:
        compiled_content = f.read()

    merged = merge_markdown(existing_content, compiled_content)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(merged)

    print(f"Successfully merged manual edits into {out_path}")


if __name__ == "__main__":
    main()
