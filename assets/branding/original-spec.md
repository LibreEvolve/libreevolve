# LibreEvolve Branding Spec

**Date:** 2026-03-18
**Owner:** Timothy Gregg / CompleteTech (complete.tech)
**Domain:** libreevolve.com
**GitHub org:** libreevolve

## Logo

**Concept: Diff Arrow** — Three rows of `>>>` chevrons (the SEARCH/REPLACE diff syntax) dissolve upward into a single rising arrow. Each row is brighter than the last, representing generations of code converging toward the optimal solution.

**Lockup:** Symbol (Diff Arrow mark) + Wordmark ("LibreEvolve")
- Wordmark: "Libre" in muted gray (#8B949E), "Evolve" in electric green (#00FF41)
- Font: IBM Plex Mono, 600 weight
- Display/heading font: Space Grotesk, 700 weight

**Files:**
- `assets/logo-dark.svg` — full lockup on dark background
- `assets/logo-mark.svg` — symbol only (for favicon, app icons)
- `assets/logo-mark-light.svg` — symbol on light backgrounds (#00802A stroke)
- `assets/social-preview.png` — 1280x640 GitHub social card

**Favicon behavior:** At 16px, the mark simplifies to a single chevron + arrow. Stroke weights increase proportionally to maintain legibility.

## Color Palette

| Role | Hex | Usage |
|------|-----|-------|
| Primary | `#00FF41` | Logo, accents, links, success states, CLI highlights |
| Primary Dim | `#00CC33` | Hover states, secondary accents |
| Primary (light bg) | `#00802A` | Logo/accents when on light backgrounds |
| Background | `#0D1117` | GitHub-aligned dark background |
| Surface | `#161B22` | Cards, code blocks, elevated surfaces |
| Surface Raised | `#1C2129` | Badge labels, nested surfaces |
| Text Primary | `#E6EDF3` | Body text |
| Text Secondary | `#8B949E` | Captions, muted text, "Libre" in wordmark |
| Border | `#30363D` | Dividers, card borders |
| Danger | `#FF4444` | Failed mutations, errors |
| Amber | `#FFB800` | Warnings, accent (CLI arguments) |
| Blue | `#58A6FF` | Info, links (CLI flags) |

**Design note:** Palette is intentionally GitHub-native — looks at home on dark-mode README without clashing.

## Typography

| Role | Font | Weight | Size guidance |
|------|------|--------|---------------|
| Display | Space Grotesk | 700 | 32-42px, letter-spacing: -1px |
| Headings | IBM Plex Mono | 600 | 18-22px |
| Body | IBM Plex Mono | 400 | 14-15px, line-height: 1.7 |
| Code | JetBrains Mono | 400 | 13-14px |
| Labels/badges | JetBrains Mono | 400 | 10-11px, letter-spacing: 1-3px, uppercase |

## Badge Style

```
[label | value]
```
- Label: surface-raised background, secondary text, border
- Value: tinted background matching semantic color (green/blue/amber), colored text, colored border at 30% opacity

Standard badges:
- `license | MIT` (green)
- `python | 3.11+` (blue)
- `tests | 115 passed` (green)
- `papers | 23` (amber)

## Social Preview Card (1280x640)

- Background: `#0D1117` with subtle grid pattern (green lines at 4% opacity)
- Bottom glow: radial gradient of primary-glow from bottom center
- Center: Diff Arrow mark (56px) + "LibreEvolve" in Space Grotesk display
- Tagline: "LLM-guided evolutionary program discovery. MAP-Elites, island migration, cascade evaluation."
- Footer: "built by complete.tech" in JetBrains Mono

## Tone

- Developer/hacker — bold, technical, slightly edgy
- Terminal energy — dark backgrounds, monospace fonts, green-on-black
- Scanline overlay on marketing pages for CRT texture
- Animations: subtle glow pulse on logo marks, fade-up on page sections

## File Organization

```
assets/
  logo-dark.svg
  logo-mark.svg
  logo-mark-light.svg
  social-preview.png
  favicon.ico
  favicon-32.png
  favicon-16.png
```
