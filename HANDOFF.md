# HANDOFF — how this portfolio is built, and how to rebuild it for someone else

This repo generates a single-page portfolio (`index.html`) from a Claude Design
export ("AI Flow" bundle) by swapping in one person's content and re-inking the
palette. Nothing that matters lives in a chat: the code, the data, the assets and
the reasoning (in `git log`) are all here. A fresh Claude Code session opened in
this folder gets `CLAUDE.md` automatically and should read this file first.

Built for Avinash Chandra Banjare (vikasbanjare.github.io/avinash-banjare-portfolio)
from avinash-portfolio.super.site and his résumé (Sep 2026). As of 2026-09-22:
12 categories, 18 films, 2 thumbnail designs, 7 roles. It descends from the
vikas-portfolio pipeline (Behance-based); this version is YouTube-based, every
colour is a CSS variable, the visitor picks one of five colour themes (Electric,
#004fff, is the default), and the hero is an editing-timeline canvas instead of
the bundle's Three.js globe.

---

## 1. Repo map

| Path | What it is |
|---|---|
| `source/ai-flow-source.html` | The original Claude Design bundle (3 MB). Never edited. Contains Babel, Three.js, React, the `dc` runtime, fonts, and the page template + manifest. |
| `rebuild.py` | The build. `python3 rebuild.py` → writes `index.html`. All person-specific copy and mappings for the *original* sections live here. |
| `parts.py` | Markup + ES5 scripts for everything *added* to the page: YouTube gallery viewer, Process section + pipeline animation, experience cards, software stack, brand-wall data, analytics loader. |
| `palette.py` | The five themes (`THEMES`, `DEFAULT`) and `tokenize()`, the pass that rewrites every hard-coded colour in the bundle to a role variable (`var(--accent)`, `rgba(var(--accent-rgb),.3)`); `theme_css()` emits the per-theme variable table. |
| `render_assets.py` | Draws the images that are not YouTube frames: one poster-style cover per category (Unbounded 900, six colour schemes, icon sticker, grain), white wordmark tiles for the brand wall, monogram tiles for the employers, the og-card with his portrait. Headless Google Chrome + Google Fonts, then `sips`. |
| `components/work-section.html` | Section 02 (the category list + docked "program monitor"). Self-contained: one `<style>`, one `<section data-vbwork2>`, one `<script>`. Data-driven from `window.VB_WORK`. |
| `data/projects.json` | The categories: title, tags, YouTube ids, per-video `meta` (title, `portrait`, `views`), poster paths, image paths + captions for the thumbnail designs. |
| `data/analytics.json` | Empty by default = no tracking. Fill `provider` + `id` (cloudflare / goatcounter / plausible) to switch on. |
| `assets/img/<slug>/cover.jpg` | Generated text cover per category (1280×720). `thumbnail-designs/01.jpg, 02.jpg` are the two real thumbnails from his site. |
| `assets/posters/<videoId>.jpg` | One YouTube frame per film, 960px: `maxresdefault.jpg` for landscape, `oar2.jpg` (9:16) for vertical Shorts. |
| `assets/frames/<slug>-NN.jpg` | 760px stills of design categories (for the work monitor). |
| `assets/wall/`, `assets/logos/` | Generated wordmarks (brand wall) and monograms (employer cards), white tiles. |
| `assets/portrait.jpg` | His photo from the Super.site, cropped to the head-and-shoulders disc (490×490). Ring, tint, grain and stickers are DOM, so they follow the theme. |
| `assets/thumbs/<id>.jpg` | 320px frames for the hero timeline's clips (`sips -Z 320` of the posters + the two thumbnail designs). |
| `assets/icons/` | CC0 brand marks (simple-icons) for the stack row. |
| `assets/favicon.svg`, `assets/og-card.jpg` | Amber play-mark favicon and 1200×630 share image. |
| `.claude/launch.json` | Local preview: `python3 -m http.server 4173`. |
| `prototypes/` (git-ignored) | Design explorations for section 02 from the original pipeline. |

Commands:

```bash
python3 render_assets.py                 # only when titles, brands, employers or the palette change
python3 rebuild.py                       # build index.html (runs node --check on every injected script)
python3 -m http.server 4173              # preview at http://localhost:4173/
python3 rebuild.py && git add -A && git commit -m "…" && git push   # deploy (GitHub Pages, ~1 min)
```

---

## 2. How the bundle works (the things that cost hours to learn)

1. **The page is a bundle, not plain HTML.** `index.html` holds a `__bundler/manifest`
   (JSON: uuid → `{mime, compressed, data:base64}`) and a `__bundler/template`
   (a JSON string of the real document). A loader decompresses assets into blob
   URLs and swaps the document in at runtime.
2. **Only manifest scripts run.** An inline `<script>` in the template body is
   silently ignored. To add behaviour: add a `text/javascript` manifest entry with a
   *strictly UUID-shaped* id and reference it as `<script src="<uuid">` **in
   `<head>`**, next to the existing `eb552694-…` tag (`head_anchor` in rebuild.py).
   Because head scripts run before the `dc` runtime mounts the document, every
   injected script polls for its own root node before wiring anything.
3. **`</script>` inside the template.** The template JSON escapes every `/` as
   `\u002F`; rebuild.py does the same when writing back.
4. **`<image-slot>` elements** are filled from the `imageSlotsState` manifest asset
   (`{ "<slot-id>": { "u": "<data URI>" } }`). Slots support `fit="contain"`.
5. **The host hijacks the wheel** (a `window` `wheel` listener, `passive:false`,
   `preventDefault()` on every event, then its own smooth `scrollTo`). Any overlay
   must `stopPropagation()` on `wheel`/`touchmove` (never `preventDefault`) or a
   trackpad can't scroll it. Scroll-linked components must derive position from
   `getBoundingClientRect()` inside a passive scroll listener + rAF — never listen
   to `wheel`.
6. **Removing the hero flyby is safe**: the host's `_setupWork()` returns early when
   `[data-fly-pin]` is absent. Section ids/`data-sec` keep the dot-nav working.
   **Removing the Three.js globe is safe the same way**: `_init()` starts with
   `if (!this.host) return`, and `this.host` only exists through the canvas host's
   `ref="{{ hostRef }}"`. rebuild.py drops that ref, so no scene, drag handlers,
   orbit labels or render loop are ever created; the same box holds
   `<canvas data-ab-hero>` and `parts.HERO_SCRIPT` draws the timeline into it.
7. **`100vw` includes the scrollbar** → 15px horizontal overflow on Windows (macOS
   overlay scrollbars hide it). Always `width:100%`.
8. **Safari needs `-webkit-backdrop-filter`.** rebuild.py adds it in a final pass
   over the assembled template so injected markup is covered too.
9. **Colours are hard-coded everywhere** — ~900 inline styles and a few JS style
   assignments. `palette.tokenize()` rewrites all of them to role variables and
   runs *last*, because several build anchors match on the old colours. The dead
   globe code's `THREE.Color` literals get the default theme's hex (shaders cannot
   read CSS; harmless now). The hero canvas reads the variables with
   `getComputedStyle` and re-reads them on a `data-theme` mutation. The old
   light-mode toggle is gone: its button element is the picker's slot, and its
   handler is guarded so it never binds.
10. **Testing gotchas:** background browser tabs throttle `requestAnimationFrame`,
    so scroll-linked activation and the flipbook look frozen — front the tab.
    GitHub Pages' CDN serves stale HTML for a minute after deploy — cache-bust
    (`?v=…`) before concluding a push failed.
11. **YouTube, not Behance.** Titles come from oEmbed
    (`youtube.com/oembed?url=…&format=json`). Orientation: `i.ytimg.com/vi/<id>/oar2.jpg`
    exists (9:16) only for vertical Shorts and 404s otherwise — that is the test.
    Players are `youtube-nocookie.com/embed/<id>?autoplay=1` iframes created on click.
12. **Parallel headless Chrome deadlocks** on this machine; render_assets.py renders
    one image at a time (~2s each) with a 90s timeout per image; a custom
    `--user-data-dir` is what makes it hang, so the script never passes one.

---

## 3. Build pipeline (what `rebuild.py` does, in order)

1. Load the bundle; parse template + manifest; load `data/projects.json`.
2. **Copy replacements `R`**: `(old, new)` pairs applied to the template. *Every
   anchor is asserted to exist* (a few also asserted unique). Then positional
   rewrites: `MENU` (the eight hero orbit labels), `OS_LABELS` + `OS_LINKS` (node
   graph), social links wired by link text (+ an extra X anchor), hero CTAs,
   `tel:`, the serif tagline under the h1, the theme-picker slot in place of the
   light-mode button, `window.__abScene`, the portrait block opening the About
   column, wordmark → type, `<html lang>`, `<title>` + description + canonical +
   Open Graph + Twitter + favicon.
3. **Image slots** (`SLOTS`: slot-id → category slug; `STAR_LOGOS`: slot-id →
   employer monogram) → new `imageSlotsState` asset. Covers are downscaled with
   `sips` (macOS) into `.build/opt/`. Monograms and wall wordmarks are registered
   as new manifest PNGs with `uuid5` ids; the 17 old logos + old wordmark are dropped.
4. Structural fixes: launch rocket + team tiles to 16:9, wall tiles rebuilt from
   `parts.WALL` (three marquee tracks × three *identical* groups — the keyframes
   translate one third of the track, so each track gets its own slice of the list:
   4 / 3 / 3 brands) and the host's `const did = {…}` readout map replaced,
   `100vw` → `100%`.
5. Per-card rewrites by position: experience dossiers `CAREER` + star pin labels,
   launch cards `LAUNCH_CARDS`, the two quote cards `QUOTES` (+ avatar initials).
6. **Section 02 swap**: the whole `#work` section is replaced by
   `components/work-section.html`; its script is registered as manifest asset
   `WORK_UUID` wrapped in a poller + a watchdog. `VB_WORK` is inlined into it.
7. Gallery viewer (`GAL_UUID`, also wires launch cards `LAUNCH` and the four
   "closer look" tiles `TEAM`), Process section inserted after `#os`
   (`PROCESS_UUID`, sections 04–09 renumbered 05–10, nav link `#os` → `#process`),
   Experience + Stack (`EXP_UUID`), optional analytics (`AN_UUID`), the hero
   timeline (`HERO_UUID`, clips = every film + the two thumbnails, with
   `assets/thumbs` frames; vertical Shorts on V2).
8. Theme variable table + picker script (`THEME_UUID`), then `palette.tokenize()`
   over the template (and over every injected script as it is encoded);
   `-webkit-backdrop-filter` pass; `node --check`; write.

Section ids after the build: `#work` 02 · `#os` 03 · `#process` 04 · `#clients` 05
(labelled "Brands") · `#starchart` 06 (Experience) · `#launches` 07 · `#studio` 08
(labelled "About") · `#results` 09 · `#contact` 10. Nav: Work · Process · About ·
Results · Contact.

---

## 4. Rebuilding for a NEW person — the checklist

The build will not warn you about stale *content* (only about missing anchors), so
go through all of it.

### 4a. Their videos → `data/projects.json` + assets
1. Collect YouTube ids per category (his came from the Super.site page: every
   `youtube.com/embed/<id>` iframe under an `<h2>`).
2. Titles: oEmbed. Orientation: `oar2.jpg` exists → `portrait: true`. Stated
   view/impression figures → `meta[id].views` (only what *they* publish).
3. Write one project per category: `{id, slug, title, tags[2], kind:"video"|"image",
   cover:"assets/img/<slug>/cover.jpg", images[], videos[], posters{}, meta{},
   captions[]}`. Display order = file order; `FEATURED` in the component leads.
4. Posters: `curl i.ytimg.com/vi/<id>/{maxresdefault|oar2}.jpg`, `sips -Z 960`
   into `assets/posters/<id>.jpg`. Design pieces → `assets/img/<slug>/NN.jpg` +
   `sips -Z 760` stills into `assets/frames/<slug>-NN.jpg`.
5. `python3 render_assets.py` → covers, wall, logos, og-card.

### 4b. `rebuild.py`
- `NAME`, `EMAIL`, `PHONE`/`TEL`, `LINKEDIN`, `YOUTUBE`, `INSTAGRAM`, `X_URL`.
- `R` — every line of copy: hero eyebrow/lede/tagline (`TAGLINE`), nav, 02 header,
  03 header, 04 wall copy + sector chips, 05 experience labels + pin labels, 06
  launch pads/labels/`data-launch-fig`, 07 about copy + three principles + four
  "closer look" captions, 08 results stats + quote-card copy, 09 contact.
- `MENU` (8 orbit labels), `OS_LABELS`/`OS_LINKS` (8 nodes), `SITE`/`DESC`/`PAGE_TITLE`.
- `SLOTS`, `STAR_LOGOS`, `CAREER` (3 studios), `LAUNCH_CARDS`, `LAUNCH`, `TEAM`, `QUOTES`.

### 4c. `parts.py`
- `PROCESS_DATA` + `PIPELINE`/`PIPE_SUB` (their crafts and the categories they open).
- `EXPERIENCE` (roles, in their own words — résumé first, site second) + `EMPLOYERS`
  (name → monogram; one per `logo` placeholder).
- `WALL` (name → hover text). Studios from the profile; brands only where a video
  title names them.
- `STACK` (software they name + the résumé's skill dots; keys map to
  `assets/icons/<key>.svg`, CC0 from `https://cdn.jsdelivr.net/npm/simple-icons@13/icons/<slug>.svg`).

### 4d. `components/work-section.html`
`FEATURED` (line ~260) hardcodes the five slugs that lead the list; the header copy
is inline (`02 — The work`, the h2, both `.vw2-sub-*` lines, the three `<dt>` labels).

### 4e. `palette.py`, `assets/favicon.svg`, `assets/portrait.jpg`, `data/analytics.json`
Themes are the `THEMES` dict: add or edit one (every role, hex), set `DEFAULT`, rebuild.
The favicon and the covers' `SCHEMES` in render_assets.py are theme-independent on
purpose. The portrait is a 490×490 crop (`sips -c 490 490 --cropOffset y x`).

---

## 5. Design tokens (the "design system")

Every colour on the page is a role variable; the five themes in `palette.THEMES`
define the roles. New components never write hex — `var(--accent)`,
`rgba(var(--glow-rgb),.4)`. Default theme: **Electric**.

| Role | Used for | Electric · Violet · Ember · Mint · Coral |
|---|---|---|
| `--bg` / `--bg-2` | page · menu, overlays | `#05070f` · `#0a0812` · `#0b0908` · `#07090c` · `#0c0a0a` |
| `--panel` / `--panel-2` / `--panel-3` | cards, stills, hairline edges | per theme, one step lighter each |
| `--text` / `--body` / `--body-2` | display · body · secondary body | near-white, tinted to the theme |
| `--muted` / `--faint` | captions ≥ 6.5:1 · eyebrows ~3.8:1 (**never under 14px body copy**) | |
| `--accent` / `--accent-hover` / `--on-accent` | ink + CTA · hover · text on the CTA | `#4d86ff` · `#a58bff` · `#ffb020` · `#5cf2c2` · `#ff6a4d` |
| `--glow` / `--glow-2` / `--glow-deep` | wires, dots, timeline clips · pipeline steps · section glows | `#004fff` · `#ff4fa3` · `#1fb2a0` · `#7c5cff` · `#38d1f0` |
| `--flame` | the LIFTOFF label | |
| `--hero-top` / `--hero-fill` | the hero nebula's shader colours | |

| Token | Value |
|---|---|
| Display type | Space Grotesk 500–700, letter-spacing −.02 to −.045em |
| Body type | Onest 300–700 |
| Accent type | Instrument Serif italic 400 — numerals and one accent word per heading, in `--accent` |
| Covers (images) | Unbounded 900 uppercase, six saturated schemes cycling (electric blue leads), icon sticker, ghost numeral, halftone dots, grain — theme-independent |
| Hero | Canvas-2D editing timeline: V2 shorts · V1 films · A1 VO · A2 music (two video tracks only when the band is under 150px), ruler at 5px/s with a timecode every minute, playhead follows the cursor (eased), flashes on cuts; frames tinted with `--glow` via multiply. It measures the copy (h1/p/a inside `[data-hero-fg]`) and sits beside it ≥1024px or under it below, fading out from the copy's edge via a mask set in JS; paused off-screen, hidden tab, or once scrolled past; static under reduced motion |
| Section header | eyebrow `11.5px/600/.18em/uppercase/--accent` · h2 `clamp(30px,3.7vw,54px)/600/1.05/-.035em` inside `<span data-lines="1">` · sub `15px/1.6/--muted`, max-width ~380px |
| Radii | 14–18px cards · 100px pills · 3–4px stills · 12px video tiles |
| Motion | `cubic-bezier(.2,.7,.3,1)`, .5–.9s, stagger 60–90ms; transform + opacity only; `prefers-reduced-motion` respected |
| Tap targets | ≥ 44px |

Fonts load from Google Fonts (the bundle also embeds woff2). Voice: first person
singular, never "we", never "client" as a noun for people, no invented metrics —
only what the profile or résumé states or what can be counted in the data.

Constraints every new component must meet: one root, scoped selectors + prefixed
classes, **strict ES5** (`var`/`function` only), no `wheel` listeners, no
`scrollTo`/`scrollIntoView`, no `100vw`, no `position:fixed` inside sections,
`esc()` on every interpolation, keyboard + tap + click all open in one step,
nothing hover-only, video iframes only on demand, colours only as variables
(and SVG colours via `style=""`, since presentation attributes cannot take `var()`).

---

## 6. Deployment (GitHub Pages)

```bash
gh repo create <name> --public --source=. --remote=origin --push
gh api -X POST repos/<owner>/<name>/pages -f "source[branch]=main" -f "source[path]=/"
gh api repos/<owner>/<name>/pages/builds/latest --jq .status     # poll until "built"
```
Site: `https://<owner>.github.io/<name>/`. Free Pages requires a public repo.
Custom domain: add a `CNAME` file, point DNS at GitHub, enforce HTTPS.

---

## 7. Starting the new chat — paste this

> Read `HANDOFF.md` fully, then §4 again. Rebuild this portfolio for **<NAME>**.
> Their videos: **<YouTube channel / page with embeds>**. Their roles and contact:
> **<source>**. Replace every Avinash-specific item in §4a–4e (categories, copy,
> employers, wall, stack, generated covers), keep the design system in §5 and every
> constraint, run `python3 render_assets.py` then `python3 rebuild.py`, verify in a
> real browser at 375 and 1440 (zero horizontal overflow, rows open the right
> category, videos play on click, zero console errors), and show me the result
> before pushing anything. Do not push without asking.

If the new person needs a *different* base design, export a new bundle from Claude
Design to `source/ai-flow-source.html`; every `R` anchor will then fail (by design)
and the replacement list has to be re-mapped to the new template — that is a
larger job than swapping content.
