#!/usr/bin/env python3
"""Generate every image the site needs that is not a YouTube frame.

  assets/img/<slug>/cover.jpg   one poster-style cover per category (1280x720)
  assets/wall/<slug>.png        wordmark tiles for the brand wall (white)
  assets/logos/<slug>.png       monogram tiles for the employer cards (white)
  assets/og-card.jpg            1200x630 share image

Covers are built like real thumbnails: a saturated two-colour scheme per
category (six schemes, cycling), the title set huge in Unbounded 900, a
rotated icon sticker, a ghost numeral, halftone dots and film grain. They
are deliberately theme-independent — the site has five colour themes — so
they pop on any of them. Rendering is headless Google Chrome (the only
rasteriser with web fonts on a stock Mac), one image at a time, then `sips`.
Re-run after editing titles in data/projects.json or the lists in parts.py.

  python3 render_assets.py             # everything
  python3 render_assets.py og-card     # only jobs whose path contains "og-card"
"""
import json, pathlib, shutil, subprocess, sys, tempfile

import parts
from parts import slugify

ROOT = pathlib.Path(__file__).parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
FONTS = ('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Unbounded:wght@700;900'
         '&family=Space+Grotesk:wght@500;600;700&family=Onest:wght@500;600&display=block" rel="stylesheet">')
GRAIN = ("url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='200' height='200'>"
         "<filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.8' numOctaves='2' stitchTiles='stitch'/>"
         "<feColorMatrix values='0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 .7 0'/></filter>"
         "<rect width='100%' height='100%' filter='url(%23n)'/></svg>\")")

# bg, bg-end, ink (type), pop (sticker + blob), ink-on-pop
SCHEMES = [
    ("#004fff", "#3d7bff", "#ffffff", "#d7ff3d", "#101400"),   # electric blue · lime
    ("#ff3d6e", "#ff8a3d", "#1a0a10", "#fff3c4", "#1a0a10"),   # coral → orange · cream
    ("#c8ff3d", "#6fe03d", "#0d1400", "#5b2bff", "#ffffff"),   # lime · violet
    ("#22d3f0", "#3d7bff", "#061018", "#ff3d6e", "#ffffff"),   # cyan → blue · coral
    ("#ffb020", "#ff5e3d", "#1c1200", "#5b2bff", "#ffffff"),   # amber → coral · violet
    ("#ff4fd8", "#7c2bff", "#ffffff", "#c8ff3d", "#101400"),   # magenta → violet · lime
]

# one glyph per category (24x24 paths, filled with currentColor)
ICONS = {
    "viral-shorts": "M13 2 4 14h6l-1 8 9-12h-6l1-8z",
    "short-form": "M7 2h10a2 2 0 0 1 2 2v16a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2zm3 6v8l6-4-6-4z",
    "ugc-videos": "M4 4h16a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-7l-5 4v-4H4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z",
    "personal-branding": "M12 12a4.5 4.5 0 1 0 0-9 4.5 4.5 0 0 0 0 9zm-8 9a8 8 0 0 1 16 0z",
    "event-films": "M3 7a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v2a2 2 0 1 0 0 4v2a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-2a2 2 0 1 0 0-4z",
    "influencer-video": "M3 10v4l11 4V6L3 10zm13-3v10a4 4 0 0 0 4-5 4 4 0 0 0-4-5z",
    "story-visualisation": "M3 20h4V9H3zm7 0h4V4h-4zm7 0h4v-7h-4z",
    "ui-animation": "M4 3l16 7-7 2-2 7z",
    "ai-video": "M12 2l2.2 6.3L21 10l-6.8 1.7L12 18l-2.2-6.3L3 10l6.8-1.7z",
    "corporate-film": "M4 22V3h10v6h6v13h-5v-4h-4v4zM7 6v2h2V6zm4 0v2h2V6zM7 10v2h2v-2zm4 0v2h2v-2zm4 2v2h2v-2zM7 14v2h2v-2zm4 0v2h2v-2zm4 2v2h2v-2z",
    "case-study": "M6 2h9l5 5v15H6zm2 10h8v2H8zm0 4h8v2H8zm0-8h5v2H8z",
    "thumbnail-designs": "M3 4h18v16H3zm3 13h12l-3.8-5-3 3.8-1.7-2.2z",
}


def shot(html, out, w, h):
    """Render `html` at w×h to a PNG. One Chrome at a time — parallel headless
    instances deadlock here, and a custom --user-data-dir makes it hang."""
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="render-"))
    page = tmp / "page.html"
    page.write_text(html, encoding="utf-8")
    try:
        r = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                            f"--window-size={w},{h}", "--virtual-time-budget=9000",
                            f"--screenshot={out}", page.as_uri()],
                           capture_output=True, text=True, timeout=90)
    except subprocess.TimeoutExpired:
        sys.exit(f"chrome hung rendering {out}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if r.returncode or not pathlib.Path(out).exists():
        sys.exit(f"chrome failed for {out}:\n{r.stderr[-800:]}")


def doc(css, body, w, h, bg):
    return (f'<!doctype html><html><head><meta charset="utf-8">{FONTS}<style>'
            f'html,body{{margin:0;width:{w}px;height:{h}px;overflow:hidden;background:{bg}}}'
            f'*{{box-sizing:border-box}}{css}</style></head><body>{body}</body></html>')


def icon(slug, size):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" style="display:block;">'
            f'<path d="{ICONS.get(slug, ICONS["viral-shorts"])}" fill="currentColor"/></svg>')


# ── covers ───────────────────────────────────────────────────────────────────
def cover_html(i, p):
    bg, bg2, ink, pop, pop_ink = SCHEMES[i % len(SCHEMES)]
    title = p["title"].upper()
    longest = max(len(w) for w in title.split())
    size = min(176, int(1136 / (longest * 0.95)))          # Unbounded caps run ~0.95em wide
    n_v, n_i = len(p["videos"]), len(p["images"])
    count = f"{n_v} film{'s' if n_v != 1 else ''}" if n_v else f"{n_i} piece{'s' if n_i != 1 else ''}"
    meta = " · ".join([count] + p["tags"][1:]).upper()
    css = f"""
.c{{position:relative;width:1280px;height:720px;overflow:hidden;color:{ink};font-family:'Unbounded',sans-serif;
  background:linear-gradient(135deg,{bg} 0%,{bg2} 100%)}}
.blob{{position:absolute;right:-220px;top:-260px;width:820px;height:820px;border-radius:50%;
  background:radial-gradient(circle,{pop} 0%,rgba(0,0,0,0) 62%);opacity:.5}}
.blob2{{position:absolute;left:-180px;bottom:-320px;width:640px;height:640px;border-radius:50%;
  background:radial-gradient(circle,{ink} 0%,rgba(0,0,0,0) 62%);opacity:.14}}
.dots{{position:absolute;left:0;top:0;width:58%;height:62%;opacity:.16;
  background-image:radial-gradient({ink} 1.7px,transparent 1.8px);background-size:22px 22px;
  -webkit-mask-image:linear-gradient(135deg,#000 20%,transparent 75%);mask-image:linear-gradient(135deg,#000 20%,transparent 75%)}}
.grain{{position:absolute;inset:0;background-image:{GRAIN};opacity:.2;mix-blend-mode:overlay}}
.ghost{{position:absolute;right:-30px;top:-70px;font:900 560px/1 'Unbounded';letter-spacing:-.06em;color:{ink};opacity:.12}}
.stk{{position:absolute;left:72px;top:64px;width:136px;height:136px;border-radius:36px;background:{pop};color:{pop_ink};
  display:flex;align-items:center;justify-content:center;transform:rotate(-8deg);box-shadow:0 22px 44px rgba(0,0,0,.28)}}
.eb{{position:absolute;left:238px;top:96px;padding:14px 24px;border-radius:100px;border:3px solid {ink};
  font:700 24px 'Space Grotesk';letter-spacing:.14em;text-transform:uppercase;color:{ink}}}
.t{{position:absolute;left:72px;right:60px;bottom:158px;font:900 {size}px/.94 'Unbounded';letter-spacing:-.045em;
  text-transform:uppercase;text-wrap:balance}}
.m{{position:absolute;left:72px;bottom:72px;display:inline-flex;align-items:center;gap:14px;padding:14px 26px;border-radius:100px;
  background:{ink};color:{bg};font:700 25px 'Space Grotesk';letter-spacing:.08em;white-space:nowrap}}
"""
    body = (f'<div class="c"><div class="blob"></div><div class="blob2"></div><div class="dots"></div>'
            f'<div class="ghost">{i + 1:02d}</div>'
            f'<div class="stk">{icon(p["slug"], 72)}</div><span class="eb">{p["tags"][0]}</span>'
            f'<div class="t">{title}</div><span class="m">{meta}</span><div class="grain"></div></div>')
    return doc(css, body, 1280, 720, bg)


# ── white tiles: wordmarks for the wall, monograms for the employer cards ────
def wordmark_html(name):
    # the wall shows these at ~145px wide, so the canvas is tight around the type
    size = 210 if len(name) <= 8 else (170 if len(name) <= 14 else 136)
    css = f"""
.w{{width:1200px;height:300px;display:flex;align-items:center;justify-content:center;gap:26px;padding:0 24px;background:#fff}}
.w b{{font:700 {size}px/.96 'Space Grotesk';letter-spacing:-.04em;color:#141210;text-align:center;text-wrap:balance}}
.w i{{flex:none;width:30px;height:30px;border-radius:50%;background:#141210;opacity:.85}}
"""
    return doc(css, f'<div class="w"><i></i><b>{name}</b></div>', 1200, 300, "#fff")


def monogram_html(mono, name):
    size = 380 if len(mono) <= 2 else 300
    css = f"""
.q{{position:relative;width:800px;height:800px;background:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:24px}}
.q b{{font:700 {size}px/1 'Space Grotesk';letter-spacing:-.05em;color:#141210}}
.q b i{{font-style:normal;color:#8a827a}}
.q span{{font:600 30px 'Onest';letter-spacing:.18em;text-transform:uppercase;color:#7e756c;text-align:center;max-width:700px}}
"""
    return doc(css, f'<div class="q"><b>{mono}<i>.</i></b><span>{name}</span></div>', 800, 800, "#fff")


# ── share image: the default theme's colours, his portrait, the same poster language ──
def og_html(n_films, portrait_uri):
    bg, bg2, ink, pop, pop_ink = SCHEMES[0]
    css = f"""
.c{{position:relative;width:1200px;height:630px;overflow:hidden;color:{ink};font-family:'Unbounded',sans-serif;
  background:linear-gradient(135deg,#05070f 0%,{bg} 55%,{bg2} 100%)}}
.blob{{position:absolute;right:-160px;top:-220px;width:760px;height:760px;border-radius:50%;background:radial-gradient(circle,#8fb4ff 0%,rgba(0,0,0,0) 62%);opacity:.4}}
.dots{{position:absolute;left:0;bottom:0;width:60%;height:60%;opacity:.14;background-image:radial-gradient({ink} 1.6px,transparent 1.7px);background-size:22px 22px;
  -webkit-mask-image:linear-gradient(45deg,#000 20%,transparent 75%);mask-image:linear-gradient(45deg,#000 20%,transparent 75%)}}
.grain{{position:absolute;inset:0;background-image:{GRAIN};opacity:.2;mix-blend-mode:overlay}}
.eb{{position:absolute;left:72px;top:72px;padding:12px 22px;border-radius:100px;border:3px solid {ink};font:700 20px 'Space Grotesk';letter-spacing:.16em;text-transform:uppercase}}
.n{{position:absolute;left:72px;top:170px;font:900 98px/.94 'Unbounded';letter-spacing:-.045em;text-transform:uppercase}}
.tg{{position:absolute;left:72px;top:400px;max-width:640px;font:600 28px/1.3 'Space Grotesk';color:{ink};opacity:.92}}
.m{{position:absolute;left:72px;bottom:64px;display:inline-flex;padding:12px 22px;border-radius:100px;background:{ink};color:{bg};font:700 20px 'Space Grotesk';letter-spacing:.08em;white-space:nowrap}}
.ph{{position:absolute;right:88px;top:105px;width:400px;height:400px;border-radius:50%;overflow:hidden;border:6px solid {pop};box-shadow:0 30px 80px rgba(0,0,0,.45)}}
.ph img{{width:100%;height:100%;object-fit:cover;filter:grayscale(1) contrast(1.06)}}
.ph i{{position:absolute;inset:0;background:rgba(215,255,61,.22);mix-blend-mode:color}}
.stk{{position:absolute;right:60px;top:120px;width:104px;height:104px;border-radius:28px;background:{pop};color:{pop_ink};display:flex;align-items:center;justify-content:center;transform:rotate(9deg);box-shadow:0 18px 40px rgba(0,0,0,.35)}}
"""
    body = (f'<div class="c"><div class="blob"></div><div class="dots"></div>'
            f'<span class="eb">Video editor</span><div class="n">Avinash<br>Banjare</div>'
            f'<div class="tg">Short-form, personal-brand and UGC videos, motion graphics and AI films.</div>'
            f'<span class="m">{n_films} FILMS · 3 SHORTS PAST 1M IMPRESSIONS</span>'
            f'<div class="ph"><img src="{portrait_uri}" alt=""><i></i></div>'
            f'<div class="stk"><svg width="44" height="50" viewBox="0 0 16 18" style="margin-left:5px"><path d="M0 0l16 9L0 18z" fill="currentColor"/></svg></div>'
            f'<div class="grain"></div></div>')
    return doc(css, body, 1200, 630, "#05070f")


def to_jpeg(png, jpg, q=84):
    subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", str(q), str(png), "--out", str(jpg)],
                   capture_output=True, check=True)
    pathlib.Path(png).unlink()


def main():
    if not pathlib.Path(CHROME).exists():
        sys.exit("Google Chrome not found — render_assets.py needs it for web-font rasterising")
    projects = json.loads((ROOT / "data" / "projects.json").read_text())["projects"]
    jobs = []   # (html, png, w, h, jpg_or_None)
    for i, p in enumerate(projects):
        d = ROOT / "assets" / "img" / p["slug"]
        d.mkdir(parents=True, exist_ok=True)
        jobs.append((cover_html(i, p), d / "cover.png", 1280, 720, d / "cover.jpg"))
    (ROOT / "assets" / "wall").mkdir(parents=True, exist_ok=True)
    for name, _did in parts.WALL:
        jobs.append((wordmark_html(name), ROOT / "assets" / "wall" / f"{slugify(name)}.png", 1200, 300, None))
    (ROOT / "assets" / "logos").mkdir(parents=True, exist_ok=True)
    for _key, (name, mono) in parts.EMPLOYERS.items():
        jobs.append((monogram_html(mono, name), ROOT / "assets" / "logos" / f"{slugify(name)}.png", 800, 800, None))
    only = sys.argv[1:]          # python3 render_assets.py og-card wall  → just those
    n_films = sum(len(p["videos"]) for p in projects)
    jobs.append((og_html(n_films, (ROOT / "assets" / "portrait.jpg").as_uri()),
                 ROOT / "assets" / "og-card.png", 1200, 630, ROOT / "assets" / "og-card.jpg"))

    if only:
        jobs = [j for j in jobs if any(k in str(j[1]) for k in only)]
    for k, (html, png, w, h, _jpg) in enumerate(jobs, 1):
        shot(html, png, w, h)
        print(f"  [{k}/{len(jobs)}] {pathlib.Path(png).relative_to(ROOT)}", flush=True)
    for _html, png, _w, _h, jpg in jobs:
        if jpg:
            to_jpeg(png, jpg)
    print(f"rendered {len(jobs)} images: {len(projects)} covers, {len(parts.WALL)} wall tiles, "
          f"{len(parts.EMPLOYERS)} monograms, 1 share image")


if __name__ == "__main__":
    main()
