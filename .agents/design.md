---
version: alpha
name: Recipes (nicholaswilde/recipes)
description: >-
  Personal lacto-ovo vegetarian recipe collection built with Zensical Material
  theme (default light and slate dark schemes) using Indigo primary/accent
  tokens, Inter body typography, and JetBrains Mono code/metadata styling.
colors:
  primary: "#4051b5"
  primary-light: "#5d6cc0"
  primary-dark: "#303fa1"
  secondary: "#526cfe"
  tertiary: "#2b9b46"
  neutral: "#ffffff"
  neutral-dark: "#0b0c10"
  surface-subtle: "#f5f5f5"
  text: "#000000de"
  text-dark: "#e2e4ea"
  link-dark: "#5488e8"
typography:
  h1:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: 700
    lineHeight: 1.3
    letterSpacing: -0.025em
  h2:
    fontFamily: Inter
    fontSize: 22.5px
    fontWeight: 700
    lineHeight: 1.4
    letterSpacing: -0.025em
  h3:
    fontFamily: Inter
    fontSize: 18.75px
    fontWeight: 700
    lineHeight: 1.5
    letterSpacing: -0.01em
  body-md:
    fontFamily: Inter
    fontSize: 15px
    fontWeight: 400
    lineHeight: 1.8
    letterSpacing: -0.01em
  code:
    fontFamily: JetBrains Mono
    fontSize: 12.75px
    fontWeight: 400
    lineHeight: 1.4
rounded:
  sm: 4px
  md: 8px
  lg: 12px
  full: 9999px
spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
components:
  button:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.neutral}"
    borderRadius: "{rounded.full}"
  card:
    backgroundColor: "{colors.neutral}"
    textColor: "{colors.text}"
    borderRadius: "{rounded.md}"
    padding: "{spacing.md}"
  admonition-pied-piper:
    backgroundColor: "rgba(43, 155, 70, 0.1)"
    textColor: "{colors.text}"
    borderColor: "{colors.tertiary}"
    borderRadius: "{rounded.md}"
  mermaid-node:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.neutral}"
    borderColor: "{colors.primary-dark}"
    borderRadius: "{rounded.sm}"
---

# Recipes Design System

## Overview

`Recipes` is a personal lacto-ovo vegetarian recipe documentation site powered by
[Zensical](../zensical.toml) using the `material` modern theme. The visual identity
prioritizes calm, scannable kitchen readability: crisp neutral surfaces, high-contrast
typography, concise numbered steps, Twemoji shortcodes for ingredient and cookware
recognition, and dual light (`default`) / dark (`slate`) palette support.

## Colors

All colors derive from Zensical Material `indigo` palette tokens in `zensical.toml`
and custom overrides in `docs/stylesheets/extra.css`.

| Token | Value | Role |
|---|---|---|
| `primary` | `#4051b5` | Primary brand indigo (`--md-primary-fg-color`), headers, active nav, Mermaid nodes |
| `primary-light` | `#5d6cc0` | Lighter indigo hover/emphasis (`--md-primary-fg-color--light`) |
| `primary-dark` | `#303fa1` | Darker indigo border/active state (`--md-primary-fg-color--dark`) |
| `secondary` | `#526cfe` | Accent indigo (`--md-accent-fg-color`), interactive highlights |
| `tertiary` | `#2b9b46` | Custom `pied-piper` admonition accent (`docs/stylesheets/extra.css`) |
| `neutral` | `#ffffff` | Light-mode page background (`--md-default-bg-color`) and on-primary text |
| `neutral-dark` | `#0b0c10` | Dark-mode (`slate`) page background (`hsla(225deg, 15%, 5%, 1)`) |
| `surface-subtle` | `#f5f5f5` | Code blocks and subtle container surfaces (`--md-code-bg-color`) |
| `text` | `#000000de` | Light-mode body text (`--md-default-fg-color`) |
| `text-dark` | `#e2e4ea` | Dark-mode (`slate`) body text (`hsla(225deg, 15%, 90%, 0.82)`) |
| `link-dark` | `#5488e8` | Dark-mode (`slate`) hyperlink color (`--md-typeset-a-color`) |

Both `default` (light) and `slate` (dark) modes enforce >= 4.5:1 WCAG AA text contrast
for body prose, links, buttons, and Mermaid nodes (`#4051b5` background with `#ffffff`
text yields ~7.25:1).

## Typography

Zensical configures a root `font-size: 125%` (`1rem = 20px` at default `16px` browser
base), with `Inter` for prose/headings and `JetBrains Mono` for code, measurements,
and technical blocks.

- **Headings (`h1`–`h3`)**: Bold `700` weight, tight negative tracking (`-0.025em` for
  `h1`/`h2`, `-0.01em` for `h3`), prefixed with Twemoji `:shortcode:` icons in Markdown.
- **Body (`body-md`)**: `15px` (`0.75rem`) with generous `1.8` line-height for easy
  reading while cooking.
- **Code (`code`)**: `JetBrains Mono` at `0.85em` (`~12.75px`) and `1.4` line-height.

## Layout & Spacing

Content sits within Material's centered `.md-grid` container (`max-width: 61rem` /
`1220px`) flanked by left navigation and right table-of-contents sidebars on desktop.

- **Recipe Page Rhythm**: Hero image (`loading=lazy`) -> Servings/Total Time summary
  table -> Ingredients (with optional `===` tabs) -> Cookware -> Optional Baking
  Schedule (`flowchart TD`) -> Numbered Steps (`### Step N`) -> `## :link: Source`.
- **Spacing Scale**: Multiples of `4px` (`0.2rem`), using `16px` (`0.8rem`) padding
  inside cards and admonitions and `24px`–`32px` vertical rhythm between sections.
- **Reference Grids**: `<div class="grid cards" markdown>` layouts use `0.8rem`
  (`16px`) card padding and `---` horizontal rules separating card titles from bodies.

## Elevation & Depth

Depth uses subtle Material shadow tiers paired with hairline borders rather than heavy
drop shadows:

- **Tier 1 (`--md-shadow-z1`)**: `0 0.2rem 0.5rem #0000000d, 0 0 0.05rem #0000001a`
  for elevated headers and popovers.
- **Tier 2 (`--md-shadow-z2`)**: `0 0.2rem 0.5rem #0000001a, 0 0 0.05rem #00000040`
  for floating search/menus.
- **Tier 3 (`--md-shadow-z3`)**: `0 0.2rem 0.5rem #0003, 0 0 0.05rem #00000059`
  for dialogs and overlays.
- **Mermaid Diagrams**: Drop shadows disabled (`dropShadow: "none"`) for clean flat
  diagram geometry across light and dark modes.

## Shapes

- **Cards, Admonitions, Code Blocks**: `8px` (`0.4rem`) rounded corners (`rounded.md`)
  with `0.05rem` hairline borders where applicable.
- **Buttons**: Pill radius (`1.2rem` / `24px`, or `9999px` full pill).
- **Mermaid Flowchart Nodes**: Rectangular/soft-cornered `4px` (`rounded.sm`) boxes
  with `1px`–`1.5px` strokes.

## Components

- **Recipe Content Tabs (`pymdownx.tabbed`)**: `alternate_style = true` tabs with
  4-space indented bodies for batch or pan variations (e.g., `"1 Batch"`, `"1/2 Batch"`).
- **Admonitions (`!!! tip`, `!!! pied-piper`)**: `0.4rem` (`8px`) radius, `0.8rem`
  (`16px`) horizontal padding, tinted background (`#448aff1a` default,
  `rgba(43, 155, 70, 0.1)` for `.pied-piper` in `docs/stylesheets/extra.css`).
- **Grid Cards (`.grid.cards`)**: `0.8rem` (`16px`) padding, `0.05rem` subtle border,
  `0.4rem` (`8px`) radius.
- **Mermaid Baking Schedules (`flowchart TD`)**: Vertical top-down flowcharts with
  Unicode emoji prefixes in labels and single-color styling via `classDef step`
  (`fill:#4051b5,stroke:#303fa1,color:#ffffff`).
- **Hero Images & Emojis**: WebP/PNG hero images with `{ loading=lazy }`; Twemoji
  SVG shortcodes (`:bread:`, `:salt:`) in Markdown headings/lists.

## Do's and Don'ts

- **Do** use Material `indigo` theme tokens (`#4051b5` / `#526cfe` / `#303fa1`) or
  CSS custom properties (`var(--md-primary-fg-color)`) instead of arbitrary hex colors.
- **Do** use Twemoji `:shortcode:` syntax from `includes/emoji.yaml` in Markdown
  titles, ingredients, and cookware lists.
- **Do** use Unicode emojis inside `mermaid` fenced code blocks (since `pymdownx.emoji`
  skips `<pre class="mermaid">` blocks and `:` conflicts with Mermaid delimiters).
- **Do** indent `pymdownx.tabbed` content blocks by exactly 4 spaces.
- **Don't** use `::timeline::` (`neoteroi.timeline`) syntax in recipes; Zensical lacks
  support for it. Use Mermaid `flowchart TD` (or `timeline`) instead.
- **Don't** omit `{ loading=lazy }` on recipe hero images or introduce unverified
  low-contrast color pairs (< 4.5:1) in custom CSS or diagrams.
