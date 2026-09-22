#!/usr/bin/env python3
"""Generate every image the site needs that is not a YouTube frame.

  assets/img/<slug>/cover.jpg   one text cover per category (1280x720)
  assets/wall/<slug>.png        wordmark tiles for the brand wall (white)
  assets/logos/<slug>.png       monogram tiles for the employer cards (white)
  assets/og-card.jpg            1200x630 share image

Text is set in the site's own faces (Space Grotesk / Onest / Instrument Serif,
pulled from Google Fonts), so the covers read as part of the page rather than
as placeholders. Rendering is headless Google Chrome — the only rasteriser
with web fonts on a stock Mac — then `sips` for the JPEGs. Re-run after
editing titles in data/projects.json or the lists in parts.py.
"""
import json, pathlib, shutil, subprocess, sys, tempfile

import palette as P
import parts

ROOT = pathlib.Path(__file__).parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
FONTS = ('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@1'
         '&family=Onest:wght@400;500;600&family=Space+Grotesk:wght@500;600;700&display=block" rel="stylesheet">')


def slugify(s):
    return "".join(c if c.isalnum() else "-" for c in s.lower()).strip("-")


def shot(html, out, w, h):
    """Render `html` at w×h and write a PNG. One Chrome at a time: parallel
    headless instances deadlock on this machine (ponytail: ~2s/image, fine for 27)."""
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="render-"))
    page = tmp / "page.html"
    page.write_text(html, encoding="utf-8")
    try:
        # no --user-data-dir: a custom profile dir makes headless Chrome hang on this Mac
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


# ── covers ───────────────────────────────────────────────────────────────────
def cover_html(i, p):
    words = p["title"].split(" ")
    head, tail = " ".join(words[:-1]), words[-1]
    n_v, n_i = len(p["videos"]), len(p["images"])
    count = (f"{n_v} film{'s' if n_v != 1 else ''}" if n_v else f"{n_i} piece{'s' if n_i != 1 else ''}")
    meta = " · ".join([count] + p["tags"][1:])
    # the two glows swap corners on alternate covers so the set is not twelve identical frames
    a, t = ("85% 10%", "10% 100%") if i % 2 == 0 else ("15% 5%", "90% 100%")
    css = f"""
.c{{position:relative;width:1280px;height:720px;font-family:'Onest',sans-serif;color:{P.TEXT};
  background:radial-gradient(120% 90% at {a},rgba(255,176,32,.22),transparent 55%),
             radial-gradient(90% 80% at {t},rgba(31,178,160,.18),transparent 60%),{P.BG}}}
.eb{{position:absolute;left:72px;top:72px;font:600 22px 'Onest';letter-spacing:.2em;text-transform:uppercase;color:{P.ACCENT}}}
.n{{position:absolute;right:72px;top:64px;font:italic 400 140px/1 'Instrument Serif';color:rgba(255,176,32,.9)}}
.t{{position:absolute;left:72px;bottom:120px;max-width:1000px;font:600 88px/1.02 'Space Grotesk';letter-spacing:-.035em;text-wrap:balance}}
.t i{{font:italic 400 88px/1.02 'Instrument Serif';color:{P.ACCENT}}}
.m{{position:absolute;left:72px;bottom:72px;font:500 24px 'Onest';color:{P.MUTED}}}
.rule{{position:absolute;left:72px;right:72px;bottom:112px;height:1px;background:rgba(255,255,255,.12)}}
"""
    body = (f'<div class="c"><span class="eb">{p["tags"][0]}</span><span class="n">{i + 1:02d}</span>'
            f'<div class="t">{head} <i>{tail}.</i></div><div class="rule"></div><div class="m">{meta}</div></div>')
    return doc(css, body, 1280, 720, P.BG)


# ── white tiles: wordmarks for the wall, monograms for the employer cards ────
def wordmark_html(name):
    # the wall shows these at ~145px wide, so the canvas is tight around the type
    size = 210 if len(name) <= 8 else (170 if len(name) <= 14 else 136)
    css = f"""
.w{{width:1200px;height:300px;display:flex;align-items:center;justify-content:center;gap:26px;padding:0 24px;background:#fff}}
.w b{{font:700 {size}px/.96 'Space Grotesk';letter-spacing:-.04em;color:#141210;text-align:center;text-wrap:balance}}
.w i{{flex:none;width:30px;height:30px;border-radius:50%;background:{P.ACCENT}}}
"""
    return doc(css, f'<div class="w"><i></i><b>{name}</b></div>', 1200, 300, "#fff")


def monogram_html(mono, name):
    size = 380 if len(mono) <= 2 else 300
    css = f"""
.q{{position:relative;width:800px;height:800px;background:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:24px}}
.q b{{font:700 {size}px/1 'Space Grotesk';letter-spacing:-.05em;color:#141210}}
.q b i{{font-style:normal;color:{P.ACCENT}}}
.q span{{font:600 30px 'Onest';letter-spacing:.18em;text-transform:uppercase;color:#7e756c}}
"""
    return doc(css, f'<div class="q"><b>{mono}<i>.</i></b><span>{name}</span></div>', 800, 800, "#fff")


# ── share image ──────────────────────────────────────────────────────────────
def og_html(n_films):
    css = f"""
.c{{position:relative;width:1200px;height:630px;font-family:'Onest',sans-serif;color:{P.TEXT};
  background:radial-gradient(110% 90% at 88% 8%,rgba(255,176,32,.24),transparent 55%),
             radial-gradient(90% 80% at 8% 100%,rgba(31,178,160,.2),transparent 60%),{P.BG}}}
.eb{{position:absolute;left:72px;top:72px;font:600 20px 'Onest';letter-spacing:.2em;text-transform:uppercase;color:{P.ACCENT}}}
.n{{position:absolute;left:72px;top:190px;font:600 104px/1 'Space Grotesk';letter-spacing:-.04em}}
.tg{{position:absolute;left:72px;top:318px;font:italic 400 60px/1.1 'Instrument Serif';color:{P.ACCENT}}}
.m{{position:absolute;left:72px;bottom:72px;font:500 24px 'Onest';color:{P.MUTED}}}
.rule{{position:absolute;left:72px;right:72px;bottom:118px;height:1px;background:rgba(255,255,255,.12)}}
"""
    body = (f'<div class="c"><span class="eb">Video editor · Short-form · Motion · AI</span>'
            f'<div class="n">Avinash Banjare</div><div class="tg">Every frame, on purpose.</div>'
            f'<div class="rule"></div><div class="m">{n_films} films in the reel · three shorts past a million impressions</div></div>')
    return doc(css, body, 1200, 630, P.BG)


def to_jpeg(png, jpg, q=82):
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
    jobs.append((og_html(n_films),
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
