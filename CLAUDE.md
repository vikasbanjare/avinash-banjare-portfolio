# vikas portfolio — project notes for Claude Code

Single-page portfolio generated from a Claude Design bundle. **Read `HANDOFF.md`
before changing anything** — it explains the bundle mechanics, the build, and
every person-specific knob.

## Commands
- Build: `python3 rebuild.py` (writes `index.html`; fails on any injected-script syntax error)
- Preview: `python3 -m http.server 4173` → http://localhost:4173/ (or `.claude/launch.json`)
- Deploy: `python3 rebuild.py && git add -A && git commit && git push` (GitHub Pages, ~1 min; CDN caches ~1 min)

## Rules
- Confirm before `git push` or anything else outward.
- Person-specific content lives in `rebuild.py` (constants + `R` list + `CAREER`/`QUOTES`/`SLOTS`),
  `parts.py` (`TOOLS_DATA`/`EXPERIENCE`/`STACK`), `data/projects.json`, and
  `components/work-section.html` (`FEATURED`). The repo is public — no stale contact details.
- New behaviour = a manifest asset with a UUID id referenced from `<head>`; inline body scripts never run.
- Injected JS must be strict ES5; never listen to `wheel`; never `scrollTo`/`scrollIntoView`; never `100vw`.
- Overlays must `stopPropagation()` on wheel/touchmove (the host hijacks the wheel) — never `preventDefault`.
- Escape every value interpolated into innerHTML (`esc()`); Behance data is external input.
- Test with the browser tab fronted (background tabs throttle rAF and freeze scroll-linked UI).
