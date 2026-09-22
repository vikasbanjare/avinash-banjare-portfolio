#!/usr/bin/env python3
"""
Rebuild the AI Flow bundle as Avinash Chandra Banjare's portfolio.

Keeps the original design's structure — same markup, Three.js hero, React/dc
runtime, fonts, scroll and hover behaviour — and swaps the content and the
palette: copy, the image slots, the brand wall, the employer logos and every
colour (palette.py turns aifloh's hard-coded colours into theme variables; the
visitor picks one of five themes from the header).

Sources of truth:
  - https://avinash-portfolio.super.site/  (copy, roles, contact, categories)
  - data/projects.json                      (the categories + their YouTube ids)
"""
import base64, html, json, os, pathlib, re, shutil, subprocess, sys, uuid

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "source" / "ai-flow-source.html"
if not SRC.exists():
    sys.exit("source bundle not found — expected source/ai-flow-source.html")
OPT = ROOT / ".build" / "opt"
OUT = ROOT / "index.html"

raw = SRC.read_text(encoding="utf-8")


def grab(kind):
    m = re.search(r'<script type="__bundler/%s">(.*?)</script>' % kind, raw, re.S)
    if not m:
        sys.exit(f"missing bundler/{kind}")
    return m.group(1), m.span(1)


tpl_txt, _ = grab("template")
man_txt, _ = grab("manifest")
manifest = json.loads(man_txt)
try:
    tpl = json.loads(tpl_txt)
except json.JSONDecodeError:
    tpl = tpl_txt

projects = json.loads((ROOT / "data" / "projects.json").read_text())["projects"]
BY = {p["slug"]: p for p in projects}
N_IMG = sum(len(p["images"]) for p in projects)
N_VID = sum(len(p["videos"]) for p in projects)

import palette
import parts

# ── image prep ────────────────────────────────────────────────────────────────
OPT.mkdir(parents=True, exist_ok=True)


def cover_jpeg(slug, px=900, q=68):
    """Downscaled JPEG bytes for a category cover (rendered by render_assets.py)."""
    dst = OPT / f"{slug}-{px}.jpg"
    if not dst.exists():
        src = sorted((ROOT / "assets" / "img" / slug).glob("cover.*"))[0]
        subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", str(q),
                        "-Z", str(px), str(src), "--out", str(dst)],
                       capture_output=True, check=True)
    return dst.read_bytes()


def data_uri(b):
    return "data:image/jpeg;base64," + base64.b64encode(b).decode()


def asset_uuid(kind, name):
    """Stable, strictly UUID-shaped ids for generated manifest assets."""
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"avinash-portfolio:{kind}:{name}"))


def add_png(uid, path):
    manifest[uid] = {"mime": "image/png", "compressed": False,
                     "data": base64.b64encode(pathlib.Path(path).read_bytes()).decode()}


# ── 1. copy replacements ──────────────────────────────────────────────────────
# Every pair is asserted to hit at least once, so a template change fails loudly
# rather than silently leaving aifloh's copy on the page.
NAME = "Avinash Banjare"
EMAIL = "avinash.banjare27@gmail.com"
PHONE = "+91 90099 39979"
TEL = "+919009939979"
LINKEDIN = "https://www.linkedin.com/in/avinash-banjare/"
YOUTUBE = "https://www.youtube.com/@avinashbanjare-rn3gi"
INSTAGRAM = "https://instagram.com/slowcheeta._"
X_URL = "https://twitter.com/AvBanjare27"

R = [
    # ── identity ──
    ("aifloh — assembling the system", "avinash banjare — rolling"),   # loader caption: letter-spaced, must fit 375px
    ("hello@aifloh.com", EMAIL),
    ("© 2026 aifloh — designed, filmed, built and automated in-house.",
     "© 2026 Avinash Chandra Banjare — shot, cut and animated in-house."),

    # ── hero ──
    ("Creative studio · AI-native", "Video editor · Short-form · Motion · AI"),
    ("One core.<br>Every craft<br>in orbit.", NAME),
    ("aifloh designs, films, builds and automates — video, websites, SEO and AI working as one system that revolves around your brand.",
     "I cut short-form, personal-brand and UGC videos, motion graphics and AI films for studios in India, the UAE "
     "and the US. Three shorts in this reel passed a million impressions each — one of them 17.7 million."),
    ("Start a project →", "See the work →"),
    (">See the work<", ">Get in touch<"),
    ('<span style="width:13px; height:13px; border:1px solid currentColor; border-radius:3px; display:inline-block;"></span>Drag to explore</span>',
     '<span style="width:13px; height:13px; border:1px solid currentColor; border-radius:3px; display:inline-block;"></span>Hover to scrub</span>'),
    # the hint wrapped into three lines on phones; keep it on one, and drop "hover" where there is no hover
    ('gap:18px; font-size:12px; font-weight:500; letter-spacing:.04em; color:#6f7f9e; text-transform:uppercase; animation:aifFloat',
     'gap:18px; white-space:nowrap; font-size:12px; font-weight:500; letter-spacing:.04em; color:#6f7f9e; text-transform:uppercase; animation:aifFloat'),
    (">Start a project<", ">Get in touch<"),

    # ── nav + CTAs ──
    (">Services<", ">Process<"),
    (">Studio<", ">About<"),
    ("Let's build something", "Let's make something"),
    ("Work with us →", "Work with me →"),

    # ── 02 selected work (the flyby is replaced by the component; its copy still has to be swapped) ──
    ("Proof, not a", "The work,"),
    ("portfolio grid.", "by category."),
    ("Three engagements where design, film, build and automation shipped as one system.",
     "Twelve categories, eighteen films. Open any one to play everything in it."),
    ("Project title one", "Million-view shorts"),
    ("Project title two", "Short-form videos"),
    ("Project title three", "Event films"),
    ("Brand · Website · Film", "Mr. Least · Double It Up · Drive X"),
    ("Motion · AI · Automation", "Reels · Shorts · UGC"),
    ("SEO · Content · Website", "After movie · Live show supercut"),
    ("+240% qualified signups", "29M impressions"),
    ("4.1M organic views", "2 films"),
    ("#1 for 40 target terms", "2 films"),

    # ── 03 node graph ──
    ("03 — Creative operating system", "03 — How I work"),
    ("Eight disciplines,<br>one nervous system.", "Eight skills,<br>one timeline."),
    ("Hover any capability to see what it pulls with it. Nothing here operates alone.",
     "Hover a skill to see what it pulls with it. Every one of them shows up in the reel above."),

    # ── 04 brand wall ──
    ("04 — Clients", "04 — Brands"),
    ("Brands we've", "Brands I've"),
    ("built with.", "cut for."),
    ("From first frame to shipped system — across pharma, fintech, edtech, gaming and consumer.",
     "The studios I've edited for, and the brands and channels named in the reel — fintech, D2C, creators, mobility and live events."),
    (">Pharma<", ">D2C<"),
    (">Edtech<", ">Creators<"),
    (">Gaming<", ">Mobility<"),
    (">Consumer<", ">Events<"),

    # ── 05 sector map → career ──
    ("05 — Sector map", "05 — Experience"),
    ("Every mission on the map.", "Seven roles. Three countries."),
    ("Hover a star to read its case dossier.", "Hover a studio to read what I did there."),
    ("Hover a star to read its dossier", "Hover a studio to read the detail"),
    ("AIF sector map · epoch 2026.6", "Career map · 2022 — 2026"),
    ("RA 04h 12m · DEC −08° · FINTECH", "USA · REMOTE · 2025 — PRESENT"),
    ("RA 11h 47m · DEC +22° · CONSUMER APP", "UAE · 2025"),
    ("RA 19h 03m · DEC −31° · B2B SAAS", "BENGALURU · 2023 — 2024"),

    # ── 06 launches ──
    ("Recent missions off the pad — each one counted down, launched, and left in orbit.",
     "What the reel adds up to — counted from the films, not estimated."),
    ("Pad 01 — Fintech", "Pad 01 — Reel"),
    ("Pad 02 — Consumer app", "Pad 02 — Reach"),
    ("Pad 03 — B2B SaaS", "Pad 03 — Roles"),
    ("qualified signups", "films in the reel"),
    ("organic views", "impressions on three shorts"),
    ("for 40 target terms", "roles since 2022 · India · UAE · US"),
    # the animated count-up target lives in data-launch-fig, not the label
    ('data-launch-fig="+240%"', f'data-launch-fig="{N_VID}"'),
    ('data-launch-fig="4.1M"', 'data-launch-fig="29M"'),
    ('data-launch-fig="#1"', f'data-launch-fig="{len(parts.EXPERIENCE)}"'),
    # the static text before the count-up runs, in the same shape as each new figure
    (">+0%<", ">0<"),
    (">0.0M<", ">0M<"),
    (">#0<", ">0<"),

    # ── 07 studio → about ──
    ("07 — Studio", "07 — About"),
    ("Everyone sells<br>strategy. We ship<br>the thing.", "Everyone talks<br>content. I ship<br>the cut."),
    ("aifloh is one team that designs, films, builds and automates. No handoffs, no three vendors blaming each other, no six-week wait for a deck nobody reads.",
     "I'm a video editor with a passion for visual experiences that captivate and inspire. A mechanical engineer by degree "
     "(Institute of Technology, Korba), cutting video full-time since 2022. Alongside the edit I shoot, design thumbnails and run "
     "Exploring Korba Camp — an ecotourism business and one of the best-known travel pages in Chhattisgarh."),
    ("One team, one loop", "One editor, start to finish"),
    ("The person who writes it edits it, and the person who designs it ships it. Feedback lands in hours, not sprints.",
     "I take the brief, build the structure, cut, animate and deliver. Feedback lands with the person who made the edit, not a chain of handoffs."),
    ("Systems, not deliverables", "Hooks first, then polish"),
    ("You do not get a folder of files. You get the machine that keeps producing them after we leave.",
     "A short earns its next three seconds or it doesn't. Structure and pacing are decided before a single effect goes on."),
    ("Automation takes the repetitive eighty percent. Humans keep the twenty percent that people actually remember.",
     "Generative video is used where it adds a shot the budget couldn't — the Shopdeck AI film in the reel is one example."),

    # ── 07 team block → four categories, each caption matching its own cover ──
    ("The people doing it", "A closer look"),
    ("Small on purpose.", "Four categories, open to browse."),
    ("Name one", "Million-view shorts"),
    ("Design lead", "Three shorts · 29M impressions"),
    ("Name two", "Personal branding"),
    ("Film &amp; motion", "Founder &amp; talking-head films"),
    ("Name three", "UI animation"),
    (">Engineering<", ">After Effects · Product motion<"),
    ("Name four", "Thumbnail designs"),
    ("AI &amp; automation", "Photoshop · Canva"),
    ('data-cursor="Say hi"', 'data-cursor="Open"'),

    # ── 08 results: the three impression figures his profile states ──
    ("finance team likes.", "algorithm liked."),
    ("Averaged across engagements from the last twelve months. Replace with your own audited figures.",
     "Three shorts from the reel, each past a million impressions — the figures my profile reports, nothing rounded up."),
    ("3.4×", "17.7M"),
    ("Pipeline lift", "Mr. Least"),
    ("Median increase in qualified inbound within two quarters of launch.",
     "Impressions on a single short-form edit — the biggest in the reel."),
    ("68%", "10M"),
    ("Less production time", "Double It Up"),
    ("Same output volume, fewer hours, because the boring half runs itself.",
     "Impressions on the second short. Both are cut for the first three seconds."),
    ("11 days", "1.3M"),
    ("Idea to live", "Drive X · TVS Scooty"),
    ("Average time from approved concept to a shipped, measurable page.",
     "Impressions on a mobility short — hook, captions and pace doing the work."),

    # ── 08 quote cards: factual, attributed to the role — not invented praise ──
    ("They replaced four vendors and shipped more in a month than we had all quarter.",
     "Ensured the quality of every video and managed all the editors and content in the company."),
    ("The automations alone paid for the engagement. The film was the part our board kept quoting.",
     "Delivers batches of videos for the studio's clients — short-form, UGC and talking-head edits, on schedule, from India."),

    # ── 09 contact ──
    ("Tell us what", "Tell me what"),
    ("you're building.", "you're making."),
    ("Taking two projects for Q4", "Open to freelance projects"),
    ("Studio time", "Time in India"),
    (">Add your number<", f">{PHONE}<"),
    (">Behance</a>", ">YouTube</a>"),
    ("Bengaluru · working worldwide", "Korba, Chhattisgarh · editing remotely for studios in the UAE and the US"),

    # ── internal: theme storage key ──
    ("'aifloh-theme'", "'ab-theme-legacy'"),
]
# anchors that must be unique, or the swap would brand something else too
UNIQUE = {">Services<", ">Studio<", "built with.", "you're building.", "07 — Studio", "finance team likes.",
          ">+0%<", ">0.0M<", ">#0<"}

missing = []
for old, new in R:
    if old not in tpl:
        missing.append(old)
    elif old in UNIQUE:
        assert tpl.count(old) == 1, f"anchor not unique: {old!r} ×{tpl.count(old)}"
    tpl = tpl.replace(old, new)
if missing:
    sys.exit("copy anchors not found:\n  " + "\n  ".join(repr(m) for m in missing))

# 1a. Hero orbit labels (the eight "services" that circle the core) — positional,
#     because their names also appear as node labels and nav items.
MENU = [
    ("Thumbnails", "Photoshop &amp; Canva"),
    ("Short-form", "Reels, Shorts &amp; UGC"),
    ("AI video", "Generative films"),
    ("Long-form", "Case studies &amp; supercuts"),
    ("Motion", "After Effects &amp; UI"),
    ("Events", "After movies &amp; live shows"),
    ("Branding", "Founder &amp; talking-head films"),
    ("Reach", "29M impressions on three shorts"),
]
menu_re = re.compile(r'(data-name="1"[^>]*>)([^<]*)(</span></div>\s*<span data-sub="1"[^>]*>)([^<]*)(</span>)')
ms = list(menu_re.finditer(tpl))
assert len(ms) == len(MENU), f"orbit labels drifted ({len(ms)})"
for m, (name, sub) in zip(reversed(ms), reversed(MENU)):
    tpl = tpl[:m.start()] + m.group(1) + name + m.group(3) + sub + m.group(5) + tpl[m.end():]

# 1b. Node graph: relabel the eight disciplines and rewire what pulls what.
OS_LABELS = {"brand": "Story", "website": "Shoot", "motion": "Motion", "video": "Edit",
             "ai": "AI video", "automation": "Captions", "seo": "Thumbnails", "perf": "Grade"}
for node, label in OS_LABELS.items():
    i = tpl.index(f'data-os-node="{node}"')
    j = tpl.index("</div>", i)
    seg = tpl[i:j]
    fixed, n = re.subn(r'(white-space:nowrap;">)[^<]*(<)', lambda m: m.group(1) + label + m.group(2), seg, count=1)
    assert n == 1, f"os node {node} label not found"
    tpl = tpl[:i] + fixed + tpl[j:]
OS_LINKS = {
    "brand":      "website,video,seo",            # Story → Shoot, Edit, Thumbnails
    "website":    "brand,video,perf",             # Shoot → Story, Edit, Grade
    "motion":     "video,ai,automation",          # Motion → Edit, AI video, Captions
    "video":      "brand,motion,perf,automation", # Edit → Story, Motion, Grade, Captions
    "ai":         "motion,video",
    "automation": "video,motion,seo",             # Captions → Edit, Motion, Thumbnails
    "seo":        "brand,automation",             # Thumbnails → Story, Captions
    "perf":       "video,website",                # Grade → Edit, Shoot
}
for node, links in OS_LINKS.items():
    pat = re.compile(r'(data-os-node="%s"((?:(?!>).)*?)data-os-link=")[^"]*(")' % re.escape(node))
    tpl, n = pat.subn(lambda m: m.group(1) + links + m.group(3), tpl)
    assert n == 1, f"os node {node} not rewired ({n})"

# The work card renders a static first frame that the carousel JS only
# overwrites on rotation — patch that one instance (the identically-named
# sector chip in the brands section is real and must not change).
STATIC_SECTOR = '<span data-fly-sector="1" style="color:#dbe6ff;">Fintech</span>'
assert tpl.count(STATIC_SECTOR) == 1, "work sector anchor drifted"
tpl = tpl.replace(STATIC_SECTOR, STATIC_SECTOR.replace(">Fintech<", ">Short-form<"))
tpl = tpl.replace("sector: 'Fintech'", "sector: 'Short-form'")
tpl = tpl.replace("sector: 'Consumer app'", "sector: 'Reels'")
tpl = tpl.replace("sector: 'B2B SaaS'", "sector: 'Events'")

# outbound links: every social anchor ships as href="#" in the original, so
# wire them by their link text instead of by URL.
LINKS = {"LinkedIn": LINKEDIN, "YouTube": YOUTUBE, "Instagram": INSTAGRAM}
wired = 0
for label, url in LINKS.items():
    pat = re.compile(r'<a href="#"((?:(?!</a>).)*?)>%s</a>' % re.escape(label))
    tpl, n = pat.subn(
        lambda m: f'<a href="{url}" target="_blank" rel="noopener"{m.group(1)}>{label}</a>', tpl)
    if not n:
        sys.exit(f"social anchor not found: {label}")
    wired += n
# X gets a fourth anchor in the contact row, beside YouTube
yt_anchor = f'<a href="{YOUTUBE}" target="_blank" rel="noopener" style="font-size:15px;">YouTube</a>'
assert yt_anchor in tpl, "contact YouTube anchor not found"
tpl = tpl.replace(yt_anchor, yt_anchor + f'<a href="{X_URL}" target="_blank" rel="noopener" style="font-size:15px;">X</a>', 1)
wired += 1
# hero CTAs ship dead in the original too
for label, target in (("See the work →", "#work"), ("Get in touch", "#contact")):
    pat = re.compile(r'<a href="#"((?:(?!</a>).)*?)>%s</a>' % re.escape(label))
    tpl, n = pat.subn(lambda m: f'<a href="{target}"{m.group(1)}>{label}</a>', tpl)
    if not n:
        sys.exit(f"hero CTA not found: {label}")
tpl = tpl.replace('href="tel:"', f'href="tel:{TEL}"')

# 1c. The three hero lines shared one style, so the name would read as the first
#     clause of a sentence. Name stays in the h1; the tagline sits under it in
#     the serif accent so the hierarchy is obvious.
TAGLINE = ('<p style="margin:10px 0 0; font-family:\'Instrument Serif\',serif; font-style:italic; '
           'font-size:clamp(21px,2.5vw,34px); line-height:1.15; color:#b6f500; '
           'letter-spacing:-.01em;">Every frame, on purpose.</p>')
tpl, n = re.subn(r'(<span data-lines="1">%s</span>\s*</h1>)' % re.escape(NAME),
                 lambda m: m.group(1) + TAGLINE, tpl, count=1)
assert n == 1, "hero h1 close not found"

# 1c-bis. The header's light-mode button becomes the colour-theme picker. Its
#         handler is guarded (`if (tbtn)`), so swapping the element disables the
#         old light mode; parts.THEME_SCRIPT fills the slot at runtime.
m = re.search(r'<button data-chrome="theme-btn".*?</button>', tpl, re.S)
assert m, "theme button not found"
tpl = tpl[:m.start()] + '<div data-ab-picker style="position:relative; display:flex;"></div>' + tpl[m.end():]
# The Three.js globe is retired: without the host ref, the component's _init()
# returns before it builds a scene, binds drag handlers or starts its loop. The
# same box now holds the timeline canvas (parts.HERO_SCRIPT draws into it).
HOST = '<div ref="{{ hostRef }}" style="position:absolute; inset:0; z-index:1;"></div>'
assert tpl.count(HOST) == 1, "hero canvas host drifted"
tpl = tpl.replace(HOST, '<div data-ab-stage style="position:absolute; inset:0; z-index:1;">'
                        '<canvas data-ab-hero aria-hidden="true"></canvas></div>')

# 1c-ter. His portrait opens the About column (anchor is the eyebrow R just renamed).
m = re.search(r'(<div style="display:flex; flex-direction:column; gap:22px;">)(\s*<span[^>]*>07 — About</span>)', tpl)
assert m, "about column opener not found"
tpl = tpl[:m.start()] + m.group(1) + parts.PORTRAIT_HTML + m.group(2) + tpl[m.end():]

# 1d. Rocket travel: the 16:9 card is much shorter than the old 3:4 one, so a
#     52% offset barely moved. Give it a full card-height climb.
tpl = tpl.replace("transform:translateX(-50%) translateY(52%);",
                  "transform:translateX(-50%) translateY(102%);")
tpl = tpl.replace("height:min(34vh,280px)", "height:min(40vh,330px)")

# ── 2. wordmark: swap the raster logo for type ────────────────────────────────
tpl = tpl.replace(
    '<img src="03e043a0-40fe-47cb-b5fc-e180ec524ac2" alt="aifloh" '
    'style="height:24px; width:auto; filter:brightness(0) invert(1);">',
    '<span style="font-family:\'Space Grotesk\',sans-serif; font-size:19px; font-weight:700; '
    f'letter-spacing:-.01em; color:#eaf0ff; white-space:nowrap;">{NAME}</span>')
tpl = tpl.replace(
    '<img src="03e043a0-40fe-47cb-b5fc-e180ec524ac2" alt="aifloh" '
    'style="height:20px; width:auto; filter:brightness(0) invert(1); opacity:.5;">',
    '<span style="font-family:\'Space Grotesk\',sans-serif; font-size:16px; font-weight:700; '
    f'letter-spacing:-.01em; color:#eaf0ff; opacity:.5; white-space:nowrap;">{NAME}</span>')
assert "03e043a0" not in tpl, "wordmark not fully replaced"
del manifest["03e043a0-40fe-47cb-b5fc-e180ec524ac2"]
tpl = tpl.replace('alt="aifloh"', f'alt="{NAME}"')

tpl = tpl.replace("<html>", '<html lang="en">', 1)
assert '<html lang="en">' in tpl, "html lang not set"

# page <title> — the dc runtime swaps the whole document in, so the title has to
# live inside the template head, not just the outer bundle shell.
SITE = "https://vikasbanjare.github.io/avinash-banjare-portfolio/"
PAGE_TITLE = "Avinash Banjare — Video Editor"
DESC = ("Avinash Chandra Banjare — video editor. Short-form, personal-brand and UGC videos, "
        "motion graphics and AI films for studios in India, the UAE and the US. "
        "Three shorts past a million impressions each.")
TITLE = (
    f"<title>{PAGE_TITLE}</title>\n"
    f'<meta name="description" content="{DESC}">\n'
    f'<meta name="author" content="{NAME}">\n'
    f'<meta name="theme-color" content="{palette.THEMES[palette.DEFAULT]["bg"]}">\n'
    f'<link rel="canonical" href="{SITE}">\n'
    '<link rel="icon" type="image/svg+xml" href="assets/favicon.svg">\n'
    # share preview: without these, a link pasted into LinkedIn or WhatsApp
    # renders as a bare URL with no title, image or blurb
    '<meta property="og:type" content="website">\n'
    f'<meta property="og:title" content="{PAGE_TITLE}">\n'
    f'<meta property="og:description" content="{DESC}">\n'
    f'<meta property="og:url" content="{SITE}">\n'
    f'<meta property="og:image" content="{SITE}assets/og-card.jpg">\n'
    '<meta property="og:image:width" content="1200">\n'
    '<meta property="og:image:height" content="630">\n'
    '<meta name="twitter:card" content="summary_large_image">\n'
    f'<meta name="twitter:title" content="{PAGE_TITLE}">\n'
    f'<meta name="twitter:description" content="{DESC}">\n'
    f'<meta name="twitter:image" content="{SITE}assets/og-card.jpg">'
)
if "<title>" in tpl:
    tpl = re.sub(r"<title>.*?</title>", TITLE, tpl, flags=re.S)
else:
    anchor = '<meta name="viewport" content="width=device-width, initial-scale=1">'
    assert anchor in tpl, "viewport meta missing"
    tpl = tpl.replace(anchor, anchor + "\n" + TITLE, 1)

# ── 3. fill every image-slot ──────────────────────────────────────────────────
SLOTS = {
    "fly-01": "viral-shorts", "fly-02": "short-form", "fly-03": "event-films",
    "ln-01": "viral-shorts", "ln-02": "short-form", "ln-03": "event-films",
    "team-01": "viral-shorts", "team-02": "personal-branding",
    "team-03": "ui-animation", "team-04": "thumbnail-designs",
    "work-01": "viral-shorts",
}
# employer monograms (assets/logos, drawn by render_assets.py) become manifest
# assets: the star cards, the experience list and nothing else reference them
LOGO_UUIDS = {}
for key, (name, _mono) in parts.EMPLOYERS.items():
    uid = asset_uuid("logo", name)
    add_png(uid, ROOT / "assets" / "logos" / f"{parts.slugify(name)}.png")
    LOGO_UUIDS[key] = uid
STAR_LOGOS = {"star-01": LOGO_UUIDS["__NEWFORM__"],
              "star-02": LOGO_UUIDS["__KNOCKOUT__"],
              "star-03": LOGO_UUIDS["__HUB__"]}
slot_uuid = next(r["uuid"] for r in json.loads(grab("ext_resources")[0])
                 if r["id"] == "imageSlotsState")
slot_state = {sid: {"u": data_uri(cover_jpeg(slug))} for sid, slug in SLOTS.items()}
for sid, uid in STAR_LOGOS.items():
    e = manifest[uid]
    slot_state[sid] = {"u": f"data:{e['mime']};base64,{e['data']}"}
manifest[slot_uuid] = {"mime": "application/json", "compressed": False,
                       "data": base64.b64encode(json.dumps(slot_state).encode()).decode()}

# ── 4. geometry + structural fixes ───────────────────────────────────────────
# 4a. launch rockets and team tiles ship as 3:4 portrait; every cover here is
#     landscape, so a portrait frame crops the middle out of the artwork.
n = tpl.count("width:66%; aspect-ratio:3/4;")
assert n == 3, f"launch rocket frames drifted ({n})"
tpl = tpl.replace("width:66%; aspect-ratio:3/4;", "width:80%; aspect-ratio:16/9;")
tpl = tpl.replace("height:min(44vh,360px)", "height:min(34vh,280px)")

n = tpl.count("width:100%; aspect-ratio:3/4;")
assert n == 4, f"team tile frames drifted ({n})"
tpl = tpl.replace("width:100%; aspect-ratio:3/4;", "width:100%; aspect-ratio:16/9;")

tpl = tpl.replace('placeholder="Million-view shorts imagery (3:4)"', 'placeholder="Category cover"')

# 4b. the pinned flyby ran 340vh, which is what read as dead space
tpl = tpl.replace('data-fly-pin="1" style="position:relative; height:340vh;"',
                  'data-fly-pin="1" style="position:relative; height:235vh;"')

# 4c. experience cards: monograms need containing on white, not cover-cropping
for sid in STAR_LOGOS:
    old = f'<image-slot id="{sid}" shape="rect"'
    assert old in tpl, f"{sid} missing"
    tpl = tpl.replace(old, f'<image-slot id="{sid}" shape="rect" fit="contain"')
tpl = tpl.replace(
    '<div style="position:relative; aspect-ratio:16/9; border-radius:8px; overflow:hidden; background:#080d1a;">',
    '<div style="position:relative; aspect-ratio:16/9; border-radius:8px; overflow:hidden; '
    'background:#fff; padding:14px 18px;">')

# 4d. experience dossiers: the three star cards are the three studios
CAREER = [
    ("Newform", "Video Editor · USA, remote", "Batches of client videos · 2025 — present"),
    ("Knockout Media", "Senior Video Editor · UAE", "Quality and the whole edit team · Feb — May 2025"),
    ("The Hub Bengaluru", "Senior Video Producer · Bengaluru", "Shot and edited the studio's films · 2023 — 2024"),
]
# the pin labels sit outside the cards and picked up the global project-name
# swap, so name the studios there too
tag_positions = [m.start() for m in re.finditer(r'data-star-tag="1"', tpl)]
assert len(tag_positions) == len(CAREER), f"star tags drifted ({len(tag_positions)})"
for pos, (name, _role, _note) in zip(reversed(tag_positions), reversed(CAREER)):
    end = tpl.index("</div>", pos)
    tag = tpl[pos:end]
    fixed, n = re.subn(r'(font-size:13\.5px; font-weight:600; color:#f6f9ff; white-space:nowrap;">)[^<]*<',
                       lambda m: m.group(1) + name + "<", tag, count=1)
    assert n == 1, "star tag anchor drifted"
    tpl = tpl[:pos] + fixed + tpl[end:]

# all three dossier cards share data-star-card="1"; walk them in document order
positions = [m.start() for m in re.finditer(r'data-star-card="1"', tpl)]
assert len(positions) == len(CAREER), f"star cards drifted ({len(positions)})"
for pos, (name, role, note) in zip(reversed(positions), reversed(CAREER)):
    end = tpl.index("</div>", tpl.index('color:#b6f500;">', pos))
    card = tpl[pos:end]
    fixed, n1 = re.subn(r'(font-size:16px; font-weight:600; color:#f6f9ff;">)[^<]*<',
                        lambda m: m.group(1) + name + "<", card, count=1)
    fixed, n2 = re.subn(r'(font-size:12px; color:#8da0c4;">)[^<]*<',
                        lambda m: m.group(1) + role + "<", fixed, count=1)
    fixed, n3 = re.subn(r'(font-size:12\.5px; font-weight:700; color:#b6f500;">)[^<]*<',
                        lambda m: m.group(1) + note + "<", fixed, count=1)
    assert n1 == n2 == n3 == 1, "star card anchors drifted"
    tpl = tpl[:pos] + fixed + tpl[end:]

# 4e. Brand wall: the bundle ships 17 of aifloh's/Vikas's client logos, each
#     repeated per marquee track. Replace every tile with a generated wordmark
#     from parts.WALL and feed the hover readout the same names.
sec_start = tpl.rfind("<section", 0, tpl.index('id="clients"'))
sec_end = tpl.index("</section>", sec_start)
sec = tpl[sec_start:sec_end]
tile_re = re.compile(r'<div style="flex:0 0 auto; width:clamp\(150px,15vw,210px\);[^"]*" style-hover="[^"]*">'
                     r'<img src="[0-9a-f-]{36}" alt="[^"]*"[^>]*></div>')
tiles = list(tile_re.finditer(sec))
assert len(tiles) == 51, f"wall tiles drifted ({len(tiles)})"
old_logo_uuids = set(re.findall(r'<img src="([0-9a-f-]{36})"', sec))
proto = tiles[0].group(0)
WALL_UUIDS = {}
for name, _did in parts.WALL:
    uid = asset_uuid("wall", name)
    add_png(uid, ROOT / "assets" / "wall" / f"{parts.slugify(name)}.png")
    WALL_UUIDS[name] = uid


def wall_tile(name):
    return re.sub(r'<img src="[0-9a-f-]{36}" alt="[^"]*"',
                  f'<img src="{WALL_UUIDS[name]}" alt="{html.escape(name, quote=True)}"', proto, count=1)


# Tiles come in contiguous runs, one per marquee group: three tracks × three
# identical groups, and the keyframes translate exactly one third of the track,
# so the groups inside a track MUST stay identical or the loop jumps at the seam.
# Each track gets its own slice of the brand list, like the original's rows.
runs, cur = [], [tiles[0]]
for a, b in zip(tiles, tiles[1:]):
    if sec[a.end():b.start()].strip() == "":
        cur.append(b)
    else:
        runs.append(cur)
        cur = [b]
runs.append(cur)
assert len(runs) == 9, f"marquee groups drifted ({len(runs)})"
_per = -(-len(parts.WALL) // 3)                                   # ceil: 10 brands → 4, 3, 3
_rows = [parts.WALL[:_per], parts.WALL[_per:2 * _per - 1], parts.WALL[2 * _per - 1:]]
for k, run in enumerate(reversed(runs)):
    row = _rows[(len(runs) - 1 - k) // 3]
    sec = sec[:run[0].start()] + " ".join(wall_tile(nm) for nm, _ in row) + sec[run[-1].end():]
tpl = tpl[:sec_start] + sec + tpl[sec_end:]
for uid in old_logo_uuids:            # the old logos are unreferenced now — drop the bytes
    manifest.pop(uid, None)
m = re.search(r"const did = \{.*?\};", tpl, re.S)
assert m, "wall readout map not found"
tpl = tpl[:m.start()] + "const did = " + json.dumps(dict(parts.WALL), ensure_ascii=False) + ";" + tpl[m.end():]
assert "|| 'Creative partner'" in tpl, "wall readout fallback drifted"
tpl = tpl.replace("|| 'Creative partner'", "|| 'In the reel'")
# wordmarks want more of the tile than the old marks did
n = tpl.count("max-width:72%; max-height:44px;")
assert n >= 1, "wall logo sizing anchor missing"
tpl = tpl.replace("max-width:72%; max-height:44px;", "max-width:86%; max-height:58px;")

# 4f. launch cards carry the global project-name swap too; name them for the
#     three categories their own artwork shows.
LAUNCH_CARDS = [
    ("Million-view shorts", "Mr. Least · Double It Up · Drive X"),
    ("Short-form videos", "Reels · Shorts · UGC"),
    ("Event films", "After movie · Live show supercut"),
]
pad_positions = [m.start() for m in re.finditer(r'data-launch="1"', tpl)]
assert len(pad_positions) == len(LAUNCH_CARDS), f"launch pads drifted ({len(pad_positions)})"
for pos, (name, sub) in zip(reversed(pad_positions), reversed(LAUNCH_CARDS)):
    end = tpl.index("data-launch-alt", pos)
    card = tpl[pos:end]
    fixed, n1 = re.subn(r'(font-size:18px; font-weight:600; letter-spacing:-\.02em; color:#f6f9ff;">)[^<]*<',
                        lambda m: m.group(1) + name + "<", card, count=1)
    fixed, n2 = re.subn(r'(<span style="font-size:12px; color:#8da0c4;">)[^<]*<',
                        lambda m: m.group(1) + sub + "<", fixed, count=1)
    assert n1 == n2 == 1, "launch card anchors drifted"
    tpl = tpl[:pos] + fixed + tpl[end:]

# 4g. Both testimonial cards ship the same placeholder name and the same "C"
#     avatar, so one global swap would brand both the same. Attribute each
#     card positionally to the role it describes.
QUOTES = [
    ("q1", "Knockout Media", "Senior Video Editor · UAE", "K"),
    ("q2", "Newform", "Video Editor · USA, remote", "N"),
]
for key, name, role, initial in QUOTES:
    start = tpl.index(f'data-reveal="{key}"')
    end = tpl.index("</blockquote>", start)
    card = tpl[start:end]
    fixed, n1 = re.subn(r'(font-size:14\.5px; font-weight:600; color:#f6f9ff;">)[^<]*<',
                        lambda m: m.group(1) + name + "<", card, count=1)
    fixed, n2 = re.subn(r'(<span style="font-size:13px; color:#8da0c4;">)[^<]*<',
                        lambda m: m.group(1) + role + "<", fixed, count=1)
    fixed, n3 = re.subn(r'(font-size:20px; line-height:1; color:#b6f500;">)[^<]*<',
                        lambda m: m.group(1) + initial + "<", fixed, count=1)
    assert n1 == n2 == n3 == 1, f"quote card {key} anchors drifted"
    tpl = tpl[:start] + fixed + tpl[end:]

# 4h. Cross-platform hardening. 100vw counts the scrollbar, so on any platform
#     that reserves gutter space the hero sat ~15px wider than the viewport.
n = tpl.count("width:100vw;")
assert n == 1, f"hero width anchor drifted ({n})"
tpl = tpl.replace("width:100vw;", "width:100%;")


# ── 5. section 02 + gallery viewer ───────────────────────────────────────────
def poster_paths(pr):
    """One real YouTube frame per film, served as a file (vertical Shorts keep 9:16)."""
    return {vid: f"assets/posters/{vid}.jpg" for vid in pr["videos"]
            if (ROOT / "assets" / "posters" / f"{vid}.jpg").exists()}


def cover_path(pr):
    hit = sorted((ROOT / "assets" / "img" / pr["slug"]).glob("cover.*"))
    return f"assets/img/{pr['slug']}/{hit[0].name}" if hit else pr["cover"]


def frame_paths(pr):
    """Light 760px stills of a design category's pieces, for the work monitor."""
    return [f"assets/frames/{f.name}"
            for f in sorted((ROOT / "assets" / "frames").glob(f"{pr['slug']}-*.jpg"))]


def gallery_srcs(pr):
    base = ROOT / "assets" / "img" / pr["slug"]
    out = []
    for i, url in enumerate(pr["images"], 1):
        hit = sorted(base.glob(f"{i:02d}.*"))
        out.append(f"assets/img/{pr['slug']}/{hit[0].name}" if hit else url)
    return out


WORKDATA = [{
    "slug": p["slug"], "title": p["title"], "tags": p["tags"],
    "kind": p["kind"], "cover": cover_path(p),
    "images": gallery_srcs(p), "videos": p["videos"],
    "posters": poster_paths(p), "frames": frame_paths(p),
    "meta": p.get("meta", {}), "captions": p.get("captions", []),
} for p in projects]
_missing_posters = [(p["slug"], v) for p in WORKDATA for v in p["videos"] if v not in p["posters"]]
assert not _missing_posters, f"films without a poster: {_missing_posters}"

# The circular flyby is replaced by one component: a curated category list with
# a docked "program monitor" (components/work-section.html). The host's
# _setupWork() bails when the flyby markup is absent, so removing it is safe.
comp = (ROOT / "components" / "work-section.html").read_text(encoding="utf-8")
m_css = re.search(r"<style>\s*(/\*.*?)</style>", comp, re.S) or re.search(r"<style>(.*?\[data-vbwork2\].*?)</style>", comp, re.S)
m_sec = re.search(r"(<section data-vbwork2.*?</section>)", comp, re.S)
_scripts = re.findall(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", comp, re.S)
assert m_css and m_sec and _scripts, "work-section component is missing its style/section/script"
WORK_CSS, WORK_HTML, WORK_IIFE = m_css.group(1), m_sec.group(1), max(_scripts, key=len).strip()
assert "[data-vbwork2]" in WORK_CSS and "VB_WORK" in WORK_IIFE

w_open = tpl.rfind("<section", 0, tpl.index('id="work"'))
w_close = tpl.index("</section>", w_open) + len("</section>")
assert 'data-fly-pin' in tpl[w_open:w_close], "expected to be replacing the flyby section"
tpl = tpl[:w_open] + WORK_HTML + tpl[w_close:]

# Inline <script> in the template does NOT run: the loader only executes
# scripts it can resolve through the manifest, so ship behaviour as bundle
# assets and reference them by uuid exactly like React/Three/Babel are.
LAUNCH = ["viral-shorts", "short-form", "event-films"]                      # = ln-01..03 above
TEAM = ["viral-shorts", "personal-branding", "ui-animation", "thumbnail-designs"]  # = team-01..04
script_js = (parts.SCRIPT.replace("__WORKDATA__", json.dumps(WORKDATA, separators=(",", ":")))
                          .replace("__LAUNCH__", json.dumps(LAUNCH))
                          .replace("__TEAM__", json.dumps(TEAM)))
GAL_UUID = "9f2c7d14-3b6a-4e18-9c52-71d0a4e8f230"  # fixed: loader matches a strict uuid shape


def add_js(uid, src):
    manifest[uid] = {"mime": "text/javascript", "compressed": False,
                     "data": base64.b64encode(palette.tokenize(src).encode()).decode()}


add_js(GAL_UUID, script_js)
assert "</body>" in tpl
tpl = tpl.replace("</body>", parts.GALLERY + "</body>", 1)

# Only scripts in <head> get re-executed by the loader, so the tag goes beside
# React/Three there; each script polls for its own nodes before wiring.
head_anchor = '<script src="eb552694-613e-47d3-9baa-773be587dd3e"></script>'
assert head_anchor in tpl, "head script anchor missing"
tpl = tpl.replace(head_anchor, head_anchor + f'\n<script src="{GAL_UUID}"></script>', 1)

# 5b. Work-section behaviour: poll for the root, then run the component verbatim.
VB_WORK = [{k: w[k] for k in ("slug", "title", "tags", "kind", "cover", "images", "videos", "posters", "frames")}
           for w in WORKDATA]
work_js = """
(function () {
  "use strict";
  window.VB_WORK = __VBWORK__;
  var tries = 0;
  (function poll() {
    if (document.querySelector('[data-vbwork2]')) { run(); watchdog(); return; }
    if (++tries > 150) return;
    setTimeout(poll, 100);
  })();

  function run() {
__IIFE__
  }

  // Entrance relies on IntersectionObserver. If a callback is ever late or
  // never arrives, rows would sit invisible at translateY(105%). Anything that
  // is on screen and still un-entered gets revealed; stops once all are in.
  function watchdog() {
    var timer = setInterval(function () {
      var root = document.querySelector('[data-vbwork2]');
      if (!root || !root.classList.contains('vw2-anim')) { clearInterval(timer); return; }
      var els = root.querySelectorAll('.vw2-head-top, .vw2-bar, .vw2-row, .vw2-mon-in');
      var pending = 0, vh = window.innerHeight || 800, i, e, box, r;
      for (i = 0; i < els.length; i++) {
        e = els[i];
        if (e.classList.contains('vw2-in')) continue;
        box = e.classList.contains('vw2-row') && e.parentNode ? e.parentNode : e;
        r = box.getBoundingClientRect();
        if (!r.width && !r.height) continue;            // filtered out / hidden
        if (r.top < vh && r.bottom > 0) { e.classList.add('vw2-in'); } else { pending++; }
      }
      if (!pending) clearInterval(timer);
    }, 1200);
  }
})();
"""
work_js = (work_js.replace("__VBWORK__", json.dumps(VB_WORK, separators=(",", ":")))
                  .replace("__IIFE__", WORK_IIFE))
WORK_UUID = "c83a1f56-2e7d-4b09-a4c1-5d96e0f7b312"
add_js(WORK_UUID, work_js)
tpl = tpl.replace(head_anchor, head_anchor + f'\n<script src="{WORK_UUID}"></script>', 1)
tpl = tpl.replace("</head>", "<style>" + WORK_CSS + "</style></head>", 1)

# 5c. Process section — inserted after 03, so 04..09 shift down by one.
#     Renumber in reverse so "04 → 05" can't then be caught by "05 → 06".
for n in range(9, 3, -1):
    old_lbl, new_lbl = f"0{n} &mdash; ", f"0{n + 1} &mdash; "
    old_txt, new_txt = f"0{n} — ", f"0{n + 1} — "
    if old_txt in tpl:
        tpl = tpl.replace(old_txt, new_txt)
    elif old_lbl in tpl:
        tpl = tpl.replace(old_lbl, new_lbl)

process_html = parts.PROCESS_SECTION.replace("__NODES__", parts.pipeline_nodes())
close_os = tpl.index("</section>", tpl.index('id="os"')) + len("</section>")
tpl = tpl[:close_os] + process_html + tpl[close_os:]

PROCESS_UUID = "5d81be27-0c44-4f7b-a3e9-8ab1c62d47f5"
add_js(PROCESS_UUID, parts.PROCESS_SCRIPT.replace(
    "__PROCESSDATA__", json.dumps(parts.PROCESS_DATA, separators=(",", ":"))))
tpl = tpl.replace(head_anchor, head_anchor + f'\n<script src="{PROCESS_UUID}"></script>', 1)
tpl = tpl.replace("</head>", parts.PROCESS_CSS + "</head>", 1)

# touch screens cannot hover: hide that half of the hero hint (label + its separator)
m = re.search(r'(<span style="display:flex; align-items:center; gap:7px;">)(<span style="width:13px;[^>]*></span>Hover to scrub</span>)(\s*<span style="opacity:\.4;">·</span>)', tpl)
assert m, "hero hint markup drifted"
tpl = (tpl[:m.start()] + '<span data-ab-hint="hover" style="display:flex; align-items:center; gap:7px;">' + m.group(2)
       + m.group(3).replace('<span style="opacity:.4;">', '<span data-ab-hint="sep" style="opacity:.4;">') + tpl[m.end():])
tpl = tpl.replace("</head>", '<style>@media (pointer:coarse){[data-ab-hint]{display:none !important;}}</style></head>', 1)

# the nav's second entry pointed at the node graph; it now reads "Process"
assert '<a href="#os"' in tpl, "nav link to #os missing"
tpl = tpl.replace('<a href="#os"', '<a href="#process"', 1)

# 5d. Experience gets substance: monogram, dates, scope, expandable detail.
#     The software stack lands in the Process section.
exp = []
for e in parts.EXPERIENCE:
    e = dict(e)
    m_ = manifest[LOGO_UUIDS[e["logo"]]]
    e["logo"] = f"data:{m_['mime']};base64,{m_['data']}"
    exp.append(e)

close_chart = tpl.index("</section>", tpl.index('id="starchart"'))
tpl = tpl[:close_chart] + parts.EXPERIENCE_BLOCK + tpl[close_chart:]

close_proc = tpl.index("</section>", tpl.index('id="process"'))
tpl = tpl[:close_proc] + parts.STACK_BLOCK + tpl[close_proc:]


# Real brand marks (simple-icons, CC0) get inlined and tinted.
def brand_svg(key, ink):
    if key is None:
        return None
    f = ROOT / "assets" / "icons" / f"{key}.svg"
    if not f.exists():
        return None
    d = re.search(r'<path[^>]*\bd="([^"]+)"', f.read_text())
    if not d:
        return None
    return (f'<svg viewBox="0 0 24 24" width="15" height="15" style="display:block;" '
            f'aria-hidden="true"><path fill="{ink}" d="{d.group(1)}"/></svg>')


stack_payload = []
for group, items in parts.STACK:
    rows = []
    for name, key, mono, ink, bg, level in items:
        rows.append([name, brand_svg(key, ink), mono, ink, bg, level])
    stack_payload.append([group, rows])
real_marks = sum(1 for _, rows in stack_payload for r in rows if r[1])

EXP_UUID = "a71f4c92-6d0b-4e55-8f31-2c94b7e0d18a"
add_js(EXP_UUID, parts.EXP_SCRIPT
       .replace("__EXPDATA__", json.dumps(exp, separators=(",", ":")))
       .replace("__STACKDATA__", json.dumps(stack_payload, separators=(",", ":"))))
tpl = tpl.replace(head_anchor, head_anchor + f'\n<script src="{EXP_UUID}"></script>', 1)

# 5e. Analytics, if configured. data/analytics.json ships empty, so by default
#     the page carries no tracking at all.
_acfg = json.loads((ROOT / "data" / "analytics.json").read_text())
ANALYTICS = {"provider": _acfg.get("provider", ""), "id": _acfg.get("id", "")}
AN_UUID = "b4e9d370-51ac-4a62-9d18-7f0c3e5ab926"
if ANALYTICS["provider"] and ANALYTICS["id"]:
    add_js(AN_UUID, parts.ANALYTICS_SCRIPT.replace(
        "__ANALYTICS__", json.dumps(ANALYTICS, separators=(",", ":"))))
    tpl = tpl.replace(head_anchor, head_anchor + f'\n<script src="{AN_UUID}"></script>', 1)
    print(f"  analytics          : {ANALYTICS['provider']} ({ANALYTICS['id']})")
else:
    print("  analytics          : none configured (no tracking shipped)")

# 5f. Colour themes: the variable table for every theme goes in <head>, the
#     picker script beside the other injected scripts. It is added last so it
#     lands first after the anchor and sets <html data-theme> before anything paints.
tpl = tpl.replace("</head>", palette.theme_css() + parts.THEME_CSS + "</head>", 1)
THEME_UUID = "e2c7a9d4-6f1b-4c83-9a5e-3d8b7f2c1a64"
add_js(THEME_UUID, parts.THEME_SCRIPT
       .replace("__THEMES__", json.dumps(palette.theme_list(), separators=(",", ":")))
       .replace("__DEFAULT__", json.dumps(palette.DEFAULT)))
tpl = tpl.replace(head_anchor, head_anchor + f'\n<script src="{THEME_UUID}"></script>', 1)

# 5g. Hero timeline: every film (and the two thumbnails) as a clip, with its
#     320px frame from assets/thumbs; vertical Shorts go on the upper track.
HERO = []
for p in projects:
    for vid in p["videos"]:
        m_ = p.get("meta", {}).get(vid, {})
        thumb = f"assets/thumbs/{vid}.jpg"
        HERO.append({"t": m_.get("title", p["title"]), "c": p["title"],
                     "s": thumb if (ROOT / thumb).exists() else "", "p": bool(m_.get("portrait"))})
    for i, cap in enumerate(p.get("captions", []), 1):
        thumb = f"assets/thumbs/thumb-{i:02d}.jpg"
        if (ROOT / thumb).exists():
            HERO.append({"t": cap.split(" — ")[0], "c": p["title"], "s": thumb, "p": False})
HERO_UUID = "7b3d9e21-4a6c-4f58-b2d1-8e5c0a7f3d96"
add_js(HERO_UUID, parts.HERO_SCRIPT.replace("__HERODATA__", json.dumps(HERO, separators=(",", ":"))))
tpl = tpl.replace(head_anchor, head_anchor + f'\n<script src="{HERO_UUID}"></script>', 1)
tpl = tpl.replace("</head>", parts.HERO_CSS + "</head>", 1)

# ── 6. palette: every remaining aifloh colour becomes a theme variable ───────
# Runs after every anchor above (several of them match on the old colours).
# Three.js literals get the default theme's real hex; THEME_SCRIPT re-sets them live.
_lime = tpl.lower().count("#b6f500")
tpl = palette.tokenize(tpl)
assert "#b6f500" not in tpl.lower() and "#04060d" not in tpl.lower(), "palette pass incomplete"
assert "THREE.Color('var(" not in tpl and "col: 'var(" not in tpl, "a shader colour became a CSS variable"
print(f"  palette            : {_lime} lime tokens → var(--accent); {len(palette.THEMES)} themes, default {palette.DEFAULT}")

# Safari (iOS and macOS) needs -webkit-backdrop-filter or every frosted panel —
# header, menu, viewer bar, badges — renders flat. Run this last so it also
# covers the markup injected above.
_plain = len(re.findall(r'(?<!-webkit-)backdrop-filter:', tpl))
tpl = re.sub(r'(?<!-webkit-)backdrop-filter:\s*([^;"]+)',
             lambda m: f"-webkit-backdrop-filter:{m.group(1)}; backdrop-filter:{m.group(1)}", tpl)
assert len(re.findall(r'(?<!-webkit-)backdrop-filter:', tpl)) == _plain, "prefix pass incomplete"
print(f"  safari prefixes    : {_plain} backdrop-filter rules")

# ── 7. write the bundle back out ─────────────────────────────────────────────
out = raw
# The original escapes every "/" as \\u002F so a literal </script> inside the
# template cannot terminate the host <script> tag early. Match that exactly.
tpl_json = json.dumps(tpl).replace("/", "\\u002F")
out = re.sub(r'(<script type="__bundler/template">).*?(</script>)',
             lambda m: m.group(1) + tpl_json + m.group(2), out, count=1, flags=re.S)
out = re.sub(r'(<script type="__bundler/manifest">).*?(</script>)',
             lambda m: m.group(1) + json.dumps(manifest, separators=(",", ":")) + m.group(2),
             out, count=1, flags=re.S)
out = out.replace("<title>Bundled Page</title>", f"<title>{PAGE_TITLE}</title>")

# Injected JS is only exercised in a browser, so a quoting slip used to ship
# silently as a dead section. Fail the build instead.
if shutil.which("node"):
    import tempfile
    for uid in (GAL_UUID, WORK_UUID, PROCESS_UUID, EXP_UUID, THEME_UUID, HERO_UUID):
        src = base64.b64decode(manifest[uid]["data"]).decode()
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
            fh.write(src)
            probe = fh.name
        r = subprocess.run(["node", "--check", probe], capture_output=True, text=True)
        os.unlink(probe)
        if r.returncode:
            sys.exit(f"injected script {uid[:8]} has a syntax error:\n{r.stderr}")
    print("  injected js        : syntax OK")
else:
    print("  injected js        : node not found — skipped syntax check")

leftovers = [w for w in ("aifloh", "Project title", "Name one", "Client name", "Vikas", "Behance", "Mirae")
             if w in tpl]
OUT.write_text(out, encoding="utf-8")
print(f"wrote {OUT.name}  {len(out)/1024/1024:.2f} MB")
print(f"  copy swaps applied : {len(R)} + {len(MENU)} orbit labels + {len(OS_LABELS)} nodes")
print(f"  image-slots filled : {len(slot_state)}")
print(f"  social links wired : {wired}")
print(f"  wall tiles         : {len(parts.WALL)} brands over 3 tracks ({[len(r) for r in _rows]}), was 17")
print(f"  brand marks inlined: {real_marks}/{sum(len(r) for _, r in stack_payload)}")
print(f"  reel               : {len(projects)} categories · {N_VID} films · {N_IMG} thumbnails")
print(f"  hero timeline      : {len(HERO)} clips ({sum(1 for h in HERO if h['p'])} vertical)")
if leftovers:
    print("  ⚠ leftover placeholder text:", leftovers)
