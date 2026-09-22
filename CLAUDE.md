# avinash portfolio — project notes for Claude Code

Single-page portfolio for Avinash Chandra Banjare (video editor), generated from a
Claude Design bundle. **Read `HANDOFF.md` before changing anything** — it explains
the bundle mechanics, the build, and every person-specific knob.

## Commands
- Render generated images: `python3 render_assets.py` (covers, wall wordmarks, employer
  monograms, og-card — needs Google Chrome; only when titles/brands/palette change)
- Build: `python3 rebuild.py` (writes `index.html`; fails on any missing anchor or injected-script syntax error)
- Preview: `python3 -m http.server 4173` → http://localhost:4173/ (or `.claude/launch.json`)
- Deploy: `python3 rebuild.py && git add -A && git commit && git push` (GitHub Pages, ~1 min; CDN caches ~1 min)

## Rules
- Confirm before `git push` or anything else outward.
- Person-specific content lives in `rebuild.py` (constants + `R` + `MENU`/`OS_LABELS` +
  `CAREER`/`LAUNCH_CARDS`/`QUOTES`/`SLOTS`), `parts.py` (`PROCESS_DATA`/`EXPERIENCE`/
  `EMPLOYERS`/`WALL`/`STACK`), `data/projects.json` (categories + YouTube ids) and
  `components/work-section.html` (`FEATURED`). Colours: five themes in `palette.py`;
  components use role variables only (`var(--accent)`), never hex.
  The repo is public — no stale contact details.
- Only facts from his résumé, avinash-portfolio.super.site or the videos themselves: no
  invented metrics, clients or tools. Brands on the wall beyond his employers and clients
  are inferred from video titles — say so if asked.
- New behaviour = a manifest asset with a UUID id referenced from `<head>`; inline body scripts never run.
- Injected JS must be strict ES5; never listen to `wheel`; never `scrollTo`/`scrollIntoView`; never `100vw`.
- Overlays must `stopPropagation()` on wheel/touchmove (the host hijacks the wheel) — never `preventDefault`.
- Escape every value interpolated into innerHTML (`esc()`); video titles are external input.
- YouTube players are created only on click (`youtube-nocookie.com/embed`), never eagerly.
- Test with the browser tab fronted (background tabs throttle rAF and freeze scroll-linked UI).
