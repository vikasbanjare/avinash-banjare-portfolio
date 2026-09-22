# HANDOFF — how this portfolio is built, and how to rebuild it for someone else

This repo generates a single-page portfolio (`index.html`) from a Claude Design
export ("AI Flow" bundle) by swapping in one person's content and re-inking the
palette. Nothing that matters lives in a chat: the code, the data, the assets and
the reasoning (in `git log`) are all here. A fresh Claude Code session opened in
this folder gets `CLAUDE.md` automatically and should read this file first.

Built for Avinash Chandra Banjare (vikasbanjare.github.io/avinash-banjare-portfolio)
from avinash-portfolio.super.site. As of 2026-09-22: 12 categories, 18 films,
2 thumbnail designs. It descends from the vikas-portfolio pipeline (Behance-based);
this version is YouTube-based and amber-on-warm-black instead of lime-on-navy.

---

## 1. Repo map

| Path | What it is |
|---|---|
| `source/ai-flow-source.html` | The original Claude Design bundle (3 MB). Never edited. Contains Babel, Three.js, React, the `dc` runtime, fonts, and the page template + manifest. |
| `rebuild.py` | The build. `python3 rebuild.py` → writes `index.html`. All person-specific copy and mappings for the *original* sections live here. |
| `parts.py` | Markup + ES5 scripts for everything *added* to the page: YouTube gallery viewer, Process section + pipeline animation, experience cards, software stack, brand-wall data, analytics loader. |
| `palette.py` | The design tokens and `recolor()`, the pass that re-inks every hard-coded colour in the bundle (hex, `rgb()`, `rgba()`, and the light-mode toggle's colour table). |
| `render_assets.py` | Draws the images that are not YouTube frames: one text cover per category, white wordmark tiles for the brand wall, monogram tiles for the employers, the og-card. Headless Google Chrome + Google Fonts, then `sips`. |
| `components/work-section.html` | Section 02 (the category list + docked "program monitor"). Self-contained: one `<style>`, one `<section data-vbwork2>`, one `<script>`. Data-driven from `window.VB_WORK`. |
| `data/projects.json` | The categories: title, tags, YouTube ids, per-video `meta` (title, `portrait`, `views`), poster paths, image paths + captions for the thumbnail designs. |
| `data/analytics.json` | Empty by default = no tracking. Fill `provider` + `id` (cloudflare / goatcounter / plausible) to switch on. |
| `assets/img/<slug>/cover.jpg` | Generated text cover per category (1280×720). `thumbnail-designs/01.jpg, 02.jpg` are the two real thumbnails from his site. |
| `assets/posters/<videoId>.jpg` | One YouTube frame per film, 960px: `maxresdefault.jpg` for landscape, `oar2.jpg` (9:16) for vertical Shorts. |
| `assets/frames/<slug>-NN.jpg` | 760px stills of design categories (for the work monitor). |
| `assets/wall/`, `assets/logos/` | Generated wordmarks (brand wall) and monograms (employer cards), white tiles. |
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
7. **`100vw` includes the scrollbar** → 15px horizontal overflow on Windows (macOS
   overlay scrollbars hide it). Always `width:100%`.
8. **Safari needs `-webkit-backdrop-filter`.** rebuild.py adds it in a final pass
   over the assembled template so injected markup is covered too.
9. **Colours are hard-coded everywhere** — ~900 inline styles, `THREE.Color('#…')`
   calls in the hero, and a `MAP` of `rgb(r, g, b)` strings the light-mode toggle
   compares computed styles against. `palette.recolor()` handles all three forms;
   it runs *last*, because several build anchors match on the old colours.
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
   `tel:`, the serif tagline under the h1, wordmark → type, `<html lang>`,
   `<title>` + description + canonical + Open Graph + Twitter + favicon.
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
   Experience + Stack (`EXP_UUID`), optional analytics (`AN_UUID`).
8. `palette.recolor()` over the template (and over every injected script as it is
   encoded); `-webkit-backdrop-filter` pass; `node --check`; write.

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
- `EXPERIENCE` (roles, in their own words) + `EMPLOYERS` (name → monogram).
- `WALL` (name → hover text). Studios from the profile; brands only where a video
  title names them.
- `STACK` (software they name; keys map to `assets/icons/<key>.svg`, CC0 from
  `https://cdn.jsdelivr.net/npm/simple-icons@13/icons/<slug>.svg`).

### 4d. `components/work-section.html`
`FEATURED` (line ~260) hardcodes the five slugs that lead the list; the header copy
is inline (`02 — The work`, the h2, both `.vw2-sub-*` lines, the three `<dt>` labels).

### 4e. `palette.py`, `assets/favicon.svg`, `data/analytics.json`
Change the right-hand side of `MAP` (and the token constants) to re-skin; the covers
and tiles read the same tokens, so re-run `render_assets.py` afterwards.

---

## 5. Design tokens (the "design system")

| Token | Value |
|---|---|
| Page background | `#0b0908` (menu/overlays `#100d0b`) |
| Panel | `#161210` / `#1b1613`; frosted `rgba(255,255,255,.035)`; hairline `rgba(255,255,255,.10–.12)` |
| Text | display `#faf7f2`, body `#efe9e1` / `#a0958a`, faint `#736a61` (**never under 14px** — fails 4.5:1) |
| Amber (ink + CTA) | `#ffb020`, on-amber text `#1c1200`, hover `#ffc75c` |
| Teal | `#1fb2a0` (glows, wires, hero nebula), `#5ee6d0` (pipeline steps, secondary dots) |
| Liftoff | `#ff7a45` |
| Display type | Space Grotesk 500–700, letter-spacing −.02 to −.045em |
| Body type | Onest 300–700 |
| Accent type | Instrument Serif italic 400 — numerals and one accent word per heading, in amber |
| Section header | eyebrow `11.5px/600/.18em/uppercase/amber` · h2 `clamp(30px,3.7vw,54px)/600/1.05/-.035em` inside `<span data-lines="1">` · sub `15px/1.6/#a0958a`, max-width ~380px |
| Radii | 14–18px cards · 100px pills · 3–4px stills · 12px video tiles |
| Motion | `cubic-bezier(.2,.7,.3,1)`, .5–.9s, stagger 60–90ms; transform + opacity only; `prefers-reduced-motion` respected |
| Tap targets | ≥ 44px |

Fonts load from Google Fonts (the bundle also embeds woff2). Voice: first person
singular, never "we", never "client" as a noun for people, no invented metrics —
only what the profile states or what can be counted in the data.

Constraints every new component must meet: one root, scoped selectors + prefixed
classes, **strict ES5** (`var`/`function` only), no `wheel` listeners, no
`scrollTo`/`scrollIntoView`, no `100vw`, no `position:fixed` inside sections,
`esc()` on every interpolation, keyboard + tap + click all open in one step,
nothing hover-only, video iframes only on demand.

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
