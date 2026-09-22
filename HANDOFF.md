# HANDOFF — how this portfolio is built, and how to rebuild it for someone else

This repo generates a single-page portfolio (`index.html`) from a Claude Design
export ("AI Flow" bundle) by swapping in one person's content. Nothing that
matters lives in a chat: the code, the data, the assets and the reasoning (in
`git log`) are all here. A fresh Claude Code session opened in this folder gets
`CLAUDE.md` automatically and should read this file first.

Built for Vikas Banjare (vikasbanjare.github.io/vikas-portfolio). As of
2026-09-20: 13 projects, 71 design pieces, 41 films.

---

## 1. Repo map

| Path | What it is |
|---|---|
| `source/ai-flow-source.html` | The original Claude Design bundle (3 MB). Never edited. Contains Babel, Three.js, React, the `dc` runtime, fonts, and the page template + manifest. |
| `rebuild.py` | The build. `python3 rebuild.py` → writes `index.html`. All person-specific copy and mappings for the *original* sections live here. |
| `parts.py` | Markup + ES5 scripts for everything *added* to the page: gallery viewer, tools section + pipeline animation, experience cards, software stack, analytics loader. |
| `components/work-section.html` | Section 02 (the project list + docked "program monitor"). Self-contained: one `<style>`, one `<section data-vbwork2>`, one `<script>`. Data-driven from `window.VB_WORK`. |
| `data/projects.json` | Scraped Behance projects: covers, gallery image URLs, video ids, poster paths. Regenerate for a new person (§4). |
| `data/analytics.json` | Empty by default = no tracking. Fill `provider` + `id` (cloudflare / goatcounter / plausible) to switch on. |
| `assets/img/<slug>/` | Self-hosted gallery images + `cover.*` per project. |
| `assets/posters/<videoId>.jpg` | One real frame per Behance video (640px). |
| `assets/frames/<slug>-NN.jpg` | 760px stills of the first ≤5 gallery images of design projects (for the work monitor). |
| `assets/tools/`, `assets/icons/` | Logos for the person's own tools, and CC0 brand marks (simple-icons) for the stack row. |
| `assets/favicon.svg`, `assets/og-card.jpg` | Favicon and 1200×630 share image. |
| `.claude/launch.json` | Local preview: `python3 -m http.server 4173`. |
| `prototypes/` (git-ignored) | Design explorations for section 02 (a-timeline, b-stack, c-index, d-filmstrip, e-monitor-index, f-editorial-monitor = shipped). `_data.js` is the shared fixture. |

Commands:

```bash
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
   `/`; rebuild.py does the same when writing back (`tpl_json.replace("/", "\\u002F")`).
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
9. **Two self-inflicted classes of bug, now guarded:** JS-in-Python quoting
   (`\\'` depth) and placeholder collisions (a `__FIGMA__` placeholder that also
   appeared as data). The build fails on any injected-script syntax error.
10. **Testing gotchas:** background browser tabs throttle `requestAnimationFrame`,
    so scroll-linked activation and the flipbook look frozen — front the tab.
    GitHub Pages' CDN serves stale HTML for a minute after deploy — cache-bust
    (`?v=…`) before concluding a push failed. Synthetic `WheelEvent`s never scroll
    anything; test the event *path* instead.
11. **Behance videos are Adobe CCV iframes** — no MP4 exists. Poster frames come
    from `https://www-ccv.adobe.io/v1/player/ccv/<ID>/embed?api_key=behance1` →
    regex `posterframe":"…"` → a *signed URL that expires in ~3 days*, so posters
    are downloaded at build time, never hotlinked.

---

## 3. Build pipeline (what `rebuild.py` does, in order)

1. Load the bundle; parse template + manifest; load `data/projects.json`.
2. **Copy replacements `R`**: a list of `(old, new)` pairs applied to the template.
   *Every anchor is asserted to exist* — a template change fails loudly instead of
   leaving the base copy on the page. Plus targeted edits: hero tagline line,
   availability cell removal, wordmark swap for the raster logo, `<html lang>`,
   `<title>` + description + canonical + Open Graph + Twitter + favicon.
3. **Image slots** (`SLOTS`: slot-id → project slug; `STAR_LOGOS`: slot-id →
   manifest logo uuid) → new `imageSlotsState` asset. Covers are downscaled with
   `sips` (macOS) into `.build/opt/`.
4. Structural fixes: launch rocket + team tiles to 16:9, social links wired by link
   text (they ship as `href="#"`), `100vw` → `100%`, wall logos enlarged.
5. Per-card rewrites by position (the template reuses identical placeholder
   markup, so global replace would brand every card the same): experience
   dossiers `CAREER`, star pin labels, launch cards `LAUNCH_CARDS`, the two quote
   cards `QUOTES` (+ avatar initials), node-graph wiring `OS_LINKS`.
6. **Section 02 swap**: the whole `#work` section is replaced by
   `components/work-section.html`; its script is registered as manifest asset
   `WORK_UUID` wrapped in a poller + a watchdog that reveals rows if the entrance
   observer never fires. `VB_WORK` (covers/images/posters/frames as file paths) is
   inlined into it.
7. Gallery viewer (`GAL_UUID`), Tools section inserted after `#os` (`TOOLS_UUID`,
   sections 04–09 renumbered 05–10), Experience + Stack (`EXP_UUID`), optional
   analytics (`AN_UUID`).
8. `-webkit-backdrop-filter` pass; `node --check` on every injected script; write.

Section ids after the build: `#work` 02 · `#os` 03 · `#tools` 04 · `#clients` 05
(labelled "Brands") · `#starchart` 06 (Experience) · `#launches` 07 · `#studio` 08 ·
`#results` 09 · `#contact` 10. Menu links: `#work #tools #studio #results #contact`.

---

## 4. Rebuilding for a NEW person — the checklist

Everything below is Vikas-specific and must be replaced. The build will not warn
you about stale *content* (only about missing anchors), so go through all of it.

### 4a. Their Behance → `data/projects.json` + assets
Behance is JS-rendered (curl returns no projects). Use a real browser:
1. Profile page: scroll, collect `a[href*="/gallery/"]` → project ids + slugs;
   collect cover images (`/projects/<size>/<hash><projectId>.…` → normalise to
   `/projects/max_808_webp/`).
2. Each project: **scroll until the count stops changing** (players lazy-load;
   a fixed scroll under-counted one project), then collect `img` sources containing
   `project_modules` and iframes matching `ccv/<id>/embed`.
3. Write `projects.json` entries: `{id, slug, behanceSlug, title, tags[],
   kind:"image"|"video", cover, images[], videos[], posters{}}`. Newest first.
   (The `profile` block at the top of the file is a leftover and **not used** by
   rebuild.py; contact details come from the constants in rebuild.py.)
4. Download images: `curl -L -A "Mozilla/5.0" -e https://www.behance.net/ …` into
   `assets/img/<slug>/NN.<ext>` and `cover.<ext>` (hotlinking works but a deleted
   project would blank a gallery).
5. Posters: for each video id fetch the CCV embed, extract `posterframe`, download,
   `sips -Z 640` into `assets/posters/<id>.jpg`, set `posters[id]`.
6. Frames: `sips -Z 760` of the first ≤5 gallery images of each design project →
   `assets/frames/<slug>-NN.jpg`.

### 4b. `rebuild.py`
- `EMAIL`, `PHONE`, `LINKEDIN`, `BEHANCE` (lines ~77–80). The repo is public —
  never push someone else's file with these still set to Vikas.
- `R` — every line of copy: hero eyebrow/title/lede, menu service pairs, section
  02 header, `Project title one/two/three` → their three featured projects (+ the
  payload/result lines), 03 copy, 04 "Brands I've", 05 experience labels + city/
  year pins, 06 launch pad names/labels/`data-launch-fig` counts, 07 studio
  principles, 08 results stats + quote-card copy, 09 contact, `'aifloh-theme'`.
- `SITE`, `DESC`, `TITLE` block (meta/OG).
- `SLOTS` (which project covers go in which image slot) and `STAR_LOGOS`
  (company logos for the experience cards — see 4d).
- `CAREER` (3 employers: name/role/one-liner), `LAUNCH_CARDS`, `QUOTES` (two
  factual cards + avatar initials), `OS_LINKS` (which disciplines link to which —
  the node *labels* are set in `R`: `>Website<` → `>UI/UX<` etc.).
- `WORDS` only matters if the project count leaves 11–15.

### 4c. `parts.py`
- `TOOLS_DATA` + `PIPELINE`/`PIPE_SUB` (their own software; ContentIntel/VoiceFlow/
  Pulse/Daxio are Vikas's). Logos in `assets/tools/`.
- `EXPERIENCE` (full bullets per employer, from their resume).
- `STACK` (software they use; keys map to `assets/icons/<key>.svg`, CC0 from
  `https://cdn.jsdelivr.net/npm/simple-icons@13/icons/<slug>.svg`; `None` = monogram tile).

### 4d. Assets baked into the *bundle* itself
The base bundle's manifest contains **17 real client logos from Vikas's studio**
(rendered as the "Brands" wall, each repeated 3× in the marquee) and his wordmark.
For another person these must be replaced (same uuids, new base64) or the
section removed. Wall uuids, in template order:

```
01f4091d-be8b-4550-be7f-a35230217bdf  m.Stock by Mirae Asset
2d7aadb2-5e6a-48a0-b48b-475be136476b  Novo Nordisk
fb3ba0d9-e4ae-4ff5-8a02-1fdd1119941a  Unacademy
041a9c5f-4859-4674-b831-60ce1c6f12da  Vedantu
c6f31087-90f2-4533-841e-b0ca22efb5a1  Skydo
4f18b6ad-811b-4858-ab83-d38301b5eb71  Wealthy
1f70d57c-d6e9-4481-8d05-327573418004  Novus
da693d5c-d9e0-423b-9429-6e87cc104927  Natural Remedies
4c525ed5-636b-48f6-a6e1-059c25938b6e  TrueProfile.io
42671faf-857d-408e-bec1-d29e5407de21  DataFlow Group
c0d880cb-adbe-416c-bb3c-39dac9d970d3  Purple Finance
4e702b37-262f-4ded-926f-ee66148d425d  Hrfy.ai
1c425850-a0d0-478b-b871-690158c97b7a  i talk
802b3a46-d67c-493f-adc8-a13b49395edd  GGame
62f6d687-6645-467b-b7bc-2939c2b5eadd  Toyflix
bf2a2aa6-f39e-43ca-9ac8-5a6aad4e7821  i30 Learning Centre
fc6d2283-9876-4602-9724-343b4aa930bb  The Hub Bengaluru
```
`STAR_LOGOS` in rebuild.py points three of these at the experience cards.
The `<img alt>` texts in the template also name these brands — update them in `R`.

### 4e. `components/work-section.html`
Data-driven, but `FEATURED` (line ~260) hardcodes the five slugs that lead the
list; the approved header copy is inline (`02 — The work`, the h2, both `.vw2-sub-*`
lines). The count line and filter counts are computed.

### 4f. `assets/favicon.svg`, `assets/og-card.jpg` (share image), `data/analytics.json`.

---

## 5. Design tokens (the "design system")

| Token | Value |
|---|---|
| Page background | `#04060d` (menu/overlays `#060a14`) |
| Panel | `rgba(255,255,255,.035)`; hairline `rgba(255,255,255,.10–.12)` |
| Text | display `#f6f9ff`, body `#eaf0ff` / `#8da0c4`, faint `#5d6e8e` (**never under 14px** — fails 4.5:1) |
| Lime (ink + CTA) | `#b6f500`, on-lime text `#06140a`, hover `#cbff3d` |
| Blue / cyan | `#2f6bff` (glows, wires), `#7fd4ff` (design nodes) |
| Liftoff orange | `#ff9d3d` |
| Display type | Space Grotesk 500–700, letter-spacing −.02 to −.045em |
| Body type | Onest 300–700 |
| Accent type | Instrument Serif italic 400 — numerals and one accent word per heading, in lime |
| Section header | eyebrow `11.5px/600/.18em/uppercase/lime` · h2 `clamp(30px,3.7vw,54px)/600/1.05/-.035em` inside `<span data-lines="1">` (host animates each `<br>` line) · sub `15px/1.6/#8da0c4`, max-width ~380px |
| Radii | 14–18px cards · 100px pills (site chrome only) · 3–4px contact prints / stills |
| Motion | `cubic-bezier(.2,.7,.3,1)`, .5–.9s, stagger 60–90ms; transform + opacity only; `prefers-reduced-motion` respected |
| Tap targets | ≥ 44px |
| Section padding | `clamp(90px,13vh,160px) clamp(20px,5vw,90px) clamp(80px,10vh,130px)` |

Fonts load from Google Fonts (the bundle also embeds woff2). Voice: first person
singular, never "we", never the word "client", no invented metrics — only counts
derivable from the data.

Constraints every new component must meet (they are what the reviewers checked):
one root, scoped selectors + prefixed classes, **strict ES5** (`var`/`function`
only), no `wheel` listeners, no `scrollTo`/`scrollIntoView`, no `100vw`, no
`position:fixed` inside sections, `esc()` on every interpolation (Behance data is
external input), keyboard + tap + click all open in one step, nothing hover-only.

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
> Their Behance: **<URL>**. Their resume is pasted below / at **<path>**. Contact:
> **<email> / <phone> / <LinkedIn>**. Replace every Vikas-specific item in §4a–4f
> (including the 17 client logos baked into the bundle and the tools/stack), keep
> the design system in §5 and every constraint, rebuild with `python3 rebuild.py`,
> verify in a real browser at 375 and 1440 (zero horizontal overflow, rows open the
> right gallery, zero console errors), and show me the result before pushing
> anything. Do not push without asking.

If the new person needs a *different* base design, export a new bundle from Claude
Design to `source/ai-flow-source.html`; every `R` anchor will then fail (by design)
and the replacement list has to be re-mapped to the new template — that is a
larger job than swapping content.
