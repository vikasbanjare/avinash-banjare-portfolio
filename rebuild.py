#!/usr/bin/env python3
"""
Rebuild the AI Flow bundle as Vikas Banjare's portfolio.

Keeps the original design 1:1 — same markup, inline styles, Three.js hero,
React/dc runtime, fonts, scroll and hover behaviour. Only the *content* changes:
copy, the 13 image-slots, the 17 logo-wall images and the site wordmark.

Sources of truth:
  - Resume redesign review.pdf  (career, contact, capabilities, metrics)
  - data/projects.json          (scraped Behance categories + covers)
"""
import base64, json, mimetypes, os, pathlib, re, shutil, subprocess, sys

ROOT = pathlib.Path(__file__).parent
# The original bundle now lives in the repo: it used to be read straight out of
# ~/Downloads and the build broke the moment that file was moved.
SRC = ROOT / "source" / "ai-flow-source.html"
if not SRC.exists():                       # fall back to wherever it was last seen
    for alt in (pathlib.Path.home() / "Downloads" / "Code" / "AI Floh Site.html",
                pathlib.Path.home() / "Downloads" / "AI Floh Site.html"):
        if alt.exists():
            SRC = alt
            break
    else:
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
for _p in projects:
    _p["url_behance"] = f'https://www.behance.net/gallery/{_p["id"]}/{_p["behanceSlug"]}'
BY = {p["slug"]: p for p in projects}
N_IMG = sum(len(p["images"]) for p in projects)
N_VID = sum(len(p["videos"]) for p in projects)

# ── image prep ────────────────────────────────────────────────────────────────
OPT.mkdir(parents=True, exist_ok=True)


def cover_jpeg(slug, px=900, q=68):
    """Downscaled JPEG bytes for a project cover."""
    dst = OPT / f"{slug}-{px}.jpg"
    if not dst.exists():
        src = sorted((ROOT / "assets" / "img" / slug).glob("cover.*"))[0]
        subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", str(q),
                        "-Z", str(px), str(src), "--out", str(dst)],
                       capture_output=True, check=True)
    return dst.read_bytes()


def data_uri(b):
    return "data:image/jpeg;base64," + base64.b64encode(b).decode()


# ── 1. copy replacements ──────────────────────────────────────────────────────
# Every pair is asserted to hit at least once, so a template change fails loudly
# rather than silently leaving aifloh's copy on the page.
EMAIL = "vikas.banjare@gmail.com"
PHONE = "+91 79874 11328"
LINKEDIN = "https://www.linkedin.com/in/vikasbanjare/"
BEHANCE = "https://www.behance.net/vikas-banjare"

R = [
    # ── identity ──
    ("aifloh — assembling the system", "vikas banjare — assembling the reel"),
    ("hello@aifloh.com", EMAIL),
    ("© 2026 aifloh — designed, filmed, built and automated in-house.",
     "© 2026 Vikas Chandra Banjare — directed, designed, edited and automated in-house."),

    # ── hero ──
    ("Creative studio · AI-native", "Creative lead · 8 years · Video · Design · AI"),
    ("One core.<br>Every craft<br>in orbit.", "Vikas Banjare"),
    ("aifloh designs, films, builds and automates — video, websites, SEO and AI working as one system that revolves around your brand.",
     "I direct, shoot, cut and automate — eight years building content engines end to end for fintech and edtech brands, "
     "with custom AI workflows that take up to 70% of the production load."),

    ("Start a project →", "See the work →"),
    (">See the work<", ">Get in touch<"),
    (">Start a project<", ">Get in touch<"),

    # ── menu: service pairs ──
    ("Brand &amp; UI", "UI/UX &amp; systems"),
    ("Motion &amp; edit", "Direction &amp; edit"),
    ("Custom agents", "Edit automation"),
    ("Rank &amp; grow", "YouTube SEO"),
    ("Ops on autopilot", "70% of output"),
    (">Apps<", ">Studio<"),
    ("Product builds", "Shoots &amp; lighting"),
    (">Websites<", ">Podcasts<"),
    ("Sites that convert", "Series production"),

    # ── 02 selected work ──
    ("Proof, not a", "Selected work,"),
    ("portfolio grid.", "end to end."),
    ("Three engagements where design, film, build and automation shipped as one system.",
     "Direction, edit, motion and design — across wealth-tech, broking and edtech. "
     "Open any project below to see everything inside it."),
    ("Project title one", "Podcast Videos"),
    ("Project title two", "Wealthy YT Ads"),
    ("Project title three", "Social Media Designs"),
    ("Brand · Website · Film", "Direction · Edit · Motion"),
    ("Motion · AI · Automation", "Performance creative · Edit"),
    ("SEO · Content · Website", "Design system · Social"),
    ("+240% qualified signups", "9 episodes shipped"),
    ("4.1M organic views", "4 campaign films"),
    ("#1 for 40 target terms", "22 published pieces"),

    # ── 03 operating system ──
    ("Hover any capability to see what it pulls with it. Nothing here operates alone.",
     "Every one of these shows up in the work below. Nothing here is aspirational."),
    (">Website<", ">UI/UX<"),

    # ── 04 brand wall — never framed as "clients" ──
    ("04 — Clients", "04 — Brands"),
    # The 17 logos in the bundle are real accounts (m.Stock by Mirae Asset,
    # Unacademy, Wealthy, Purple Finance, DataFlow, Novo Nordisk, ...), so the
    # wall and its sector labels stay exactly as they are. Pronoun only.
    ("Brands we've", "Brands I've"),

    # ── 05 sector map → career ──
    ("05 — Sector map", "05 — Experience"),
    ("Every mission on the map.", "Three studios. Eight years."),
    ("Hover a star to read its case dossier.",
     "Hover a company to read what I owned there."),
    ("Hover a star to read its dossier", "Hover a company to read the detail"),
    ("AIF sector map · epoch 2026.6", "Career map · 2019 — 2026"),
    ("RA 04h 12m · DEC −08° · FINTECH", "MUMBAI · 2025 — PRESENT"),
    ("RA 11h 47m · DEC +22° · CONSUMER APP", "BENGALURU · 2022 — 2025"),
    ("RA 19h 03m · DEC −31° · B2B SAAS", "BENGALURU · 2019 — 2022"),

    # ── 06 launches ──
    ("Recent missions off the pad — each one counted down, launched, and left in orbit.",
     "What the last eight years actually produced — counted, not estimated."),
    ("Pad 01 — Fintech", "Pad 01 — Film"),
    ("Pad 02 — Consumer app", "Pad 02 — Motion"),
    ("Pad 03 — B2B SaaS", "Pad 03 — Design"),
    ("qualified signups", "films in the set"),
    ("organic views", "motion pieces"),
    ("for 40 target terms", "thumbnails shipped"),
    # the animated count-up target lives in data-launch-fig, not the label
    ('data-launch-fig="+240%"', 'data-launch-fig="7"'),
    ('data-launch-fig="4.1M"', 'data-launch-fig="4"'),
    ('data-launch-fig="#1"', 'data-launch-fig="10"'),

    # ── 07 studio ──
    ("aifloh is one team that designs, films, builds and automates. No handoffs, no three vendors blaming each other, no six-week wait for a deck nobody reads.",
     "I run the whole creative function — brand films, product demos, podcasts, performance creatives, newsletters and landing pages. "
     "No handoffs between three vendors, no six-week wait for a deck nobody reads."),
    ("Work with us →", "Work with me →"),
    ("strategy. We ship", "strategy. I ship"),
    ("Numbers the", "The numbers"),
    ("finance team likes.", "behind the work."),
    ("One team, one loop", "One hand, end to end"),
    ("The person who writes it edits it, and the person who designs it ships it. Feedback lands in hours, not sprints.",
     "I join the briefing, build the storyboard, shoot it, cut it and ship it. Feedback lands in hours, not sprints."),
    ("You do not get a folder of files. You get the machine that keeps producing them after we leave.",
     "Templated systems and design libraries, so the tenth asset costs a fraction of the first."),
    ("Automation takes the repetitive eighty percent. Humans keep the twenty percent that people actually remember.",
     "Custom AI automation cut a full day of podcast editing to roughly 30 minutes. The judgement calls stay human."),

    # ── 07 team block → four projects, each caption matching its own image ──
    ("The people doing it", "A closer look"),
    ("Small on purpose.", "Four projects, open to browse."),
    ("Name one", "Creative Designs"),
    ("Design lead", "Graphic design · Illustration"),
    ("Name two", "Wealthy YT Ads"),
    ("Film &amp; motion", "Performance creative · Edit"),
    ("Name three", "Podcast Videos"),
    (">Engineering<", ">Direction · Edit · Motion<"),
    ("Name four", "Thumbnail Designs"),
    ("AI &amp; automation", "CTR-led thumbnail systems"),
    ('data-cursor="Say hi"', 'data-cursor="Open"'),

    # ── 08 results ──
    ("Averaged across engagements from the last twelve months. Replace with your own audited figures.",
     "Straight off the record — eight years across Mirae Asset, Wealthy and Unacademy."),
    ("3.4×", "2,000+"),
    ("Pipeline lift", "Videos produced"),
    ("Median increase in qualified inbound within two quarters of launch.",
     "Led a team of editors producing 2,000+ educational videos at Unacademy."),
    ("68%", "70%"),
    ("Less production time", "Design work automated"),
    ("Same output volume, fewer hours, because the boring half runs itself.",
     "AI-assisted workflows and templated systems raised throughput without adding headcount."),
    ("11 days", "1M+"),
    ("Idea to live", "Subs in one month"),
    ("Average time from approved concept to a shipped, measurable page.",
     "New YouTube subscribers in a single month across the channels I produced for."),

    # ── 08 quote cards: factual, attributed to the role — not invented praise ──
    ("They replaced four vendors and shipped more in a month than we had all quarter.",
     "Built custom AI automation for podcast and social editing — a full day of manual work cut to roughly 30 minutes."),

    ("The automations alone paid for the engagement. The film was the part our board kept quoting.",
     "Designed studio setups for 150+ channels and re-engineered workflows — productivity up 25%, output up 35%."),

    # ── 09 contact ──
    ("Tell us what", "Tell me what"),
    ("Taking two projects for Q4", "Open to freelance"),
    (">Add your number<", f">{PHONE}<"),
    (">Instagram<", ">Email<"),
    (">Services<", ">Tools<"),

    # ── internal: theme storage key ──
    ("'aifloh-theme'", "'vb-theme'"),
]

missing = []
for old, new in R:
    if old not in tpl:
        missing.append(old)
    tpl = tpl.replace(old, new)
if missing:
    sys.exit("copy anchors not found:\n  " + "\n  ".join(repr(m) for m in missing))

# The work card renders a static first frame that the carousel JS only
# overwrites on rotation — patch that one instance (the identically-named
# sector chip in the clients section is real and must not change).
STATIC_SECTOR = '<span data-fly-sector="1" style="color:#dbe6ff;">Fintech</span>'
assert tpl.count(STATIC_SECTOR) == 1, "work sector anchor drifted"
tpl = tpl.replace(STATIC_SECTOR, STATIC_SECTOR.replace(">Fintech<", ">Podcast<"))

# work-carousel DATA array (drives the 3D scan labels)
tpl = tpl.replace("sector: 'Fintech'", "sector: 'Podcast'")
tpl = tpl.replace("sector: 'Consumer app'", "sector: 'Campaign'")
tpl = tpl.replace("sector: 'B2B SaaS'", "sector: 'Social'")

# outbound links: every social anchor ships as href="#" in the original, so
# wire them by their link text instead of by URL.
LINKS = {"LinkedIn": LINKEDIN, "Behance": BEHANCE, "Email": f"mailto:{EMAIL}"}
wired = 0
for label, url in LINKS.items():
    pat = re.compile(r'<a href="#"((?:(?!</a>).)*?)>%s</a>' % re.escape(label))
    tpl, n = pat.subn(
        lambda m: f'<a href="{url}" target="_blank" rel="noopener"{m.group(1)}>{label}</a>', tpl)
    if not n:
        sys.exit(f"social anchor not found: {label}")
    wired += n
# hero CTAs ship dead in the original too
for label, target in (("See the work →", "#work"), ("Get in touch", "#contact")):
    pat = re.compile(r'<a href="#"((?:(?!</a>).)*?)>%s</a>' % re.escape(label))
    tpl, n = pat.subn(lambda m: f'<a href="{target}"{m.group(1)}>{label}</a>', tpl)
    if not n:
        sys.exit(f"hero CTA not found: {label}")

# the empty tel: href
tpl = tpl.replace('href="tel:"', 'href="tel:+917987411328"')

# the email address itself, wherever it is shown as plain text
tpl = re.sub(r'<a href="#"((?:(?!</a>).)*?)>%s</a>' % re.escape(EMAIL),
             lambda m: f'<a href="mailto:{EMAIL}"{m.group(1)}>{EMAIL}</a>', tpl)

# 1b. The three hero lines shared one style, so the name read as the first
#     clause of a sentence. Name stays in the h1; the tagline moves out below
#     it in the serif accent so the hierarchy is obvious.
TAGLINE = ('<p style="margin:10px 0 0; font-family:\'Instrument Serif\',serif; font-style:italic; '
           'font-size:clamp(21px,2.5vw,34px); line-height:1.15; color:#b6f500; '
           'letter-spacing:-.01em;">Every craft in orbit.</p>')
h1_close = '<span data-lines="1">Vikas Banjare</span>\n      </h1>'
assert h1_close in tpl, "hero h1 close not found"
tpl = tpl.replace(h1_close, h1_close + TAGLINE, 1)

# 1c. Availability was noise — drop the whole contact cell.
avail_start = tpl.index('<span style="font-size:10.5px; font-weight:600; letter-spacing:.18em; '
                        'text-transform:uppercase; color:#5d6e8e;">Availability</span>')
cell_start = tpl.rindex('<div style="display:flex; flex-direction:column; gap:9px;">', 0, avail_start)
cell_end = tpl.index('</div>', tpl.index('</span>', tpl.index('Open to freelance', avail_start))) + len('</div>')
tpl = tpl[:cell_start] + tpl[cell_end:]
assert "Open to freelance" not in tpl, "availability cell not fully removed"

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
    'letter-spacing:-.01em; color:#eaf0ff; white-space:nowrap;">Vikas Banjare</span>')
tpl = tpl.replace(
    '<img src="03e043a0-40fe-47cb-b5fc-e180ec524ac2" alt="aifloh" '
    'style="height:20px; width:auto; filter:brightness(0) invert(1); opacity:.5;">',
    '<span style="font-family:\'Space Grotesk\',sans-serif; font-size:16px; font-weight:700; '
    'letter-spacing:-.01em; color:#eaf0ff; opacity:.5; white-space:nowrap;">Vikas Banjare</span>')
assert "03e043a0" not in tpl, "wordmark not fully replaced"
tpl = tpl.replace('alt="aifloh"', 'alt="Vikas Banjare"')

tpl = tpl.replace("<html>", '<html lang="en">', 1)
assert '<html lang="en">' in tpl, "html lang not set"

# page <title> — the dc runtime swaps the whole document in, so the title has to
# live inside the template head, not just the outer bundle shell.
SITE = "https://vikasbanjare.github.io/vikas-portfolio/"
DESC = ("Vikas Banjare — Creative Lead in Mumbai. Eight years of video direction, "
        "editing, motion and design for fintech and edtech, plus the in-house tools "
        "that automate the production.")
TITLE = (
    "<title>Vikas Banjare — Creative Lead, Video &amp; Design</title>\n"
    f'<meta name="description" content="{DESC}">\n'
    '<meta name="author" content="Vikas Banjare">\n'
    '<meta name="theme-color" content="#04060d">\n'
    f'<link rel="canonical" href="{SITE}">\n'
    '<link rel="icon" type="image/svg+xml" href="assets/favicon.svg">\n'
    # share preview: without these, a link pasted into LinkedIn or WhatsApp
    # renders as a bare URL with no title, image or blurb
    '<meta property="og:type" content="website">\n'
    '<meta property="og:title" content="Vikas Banjare — Creative Lead, Video &amp; Design">\n'
    f'<meta property="og:description" content="{DESC}">\n'
    f'<meta property="og:url" content="{SITE}">\n'
    f'<meta property="og:image" content="{SITE}assets/og-card.jpg">\n'
    '<meta property="og:image:width" content="1200">\n'
    '<meta property="og:image:height" content="630">\n'
    '<meta name="twitter:card" content="summary_large_image">\n'
    '<meta name="twitter:title" content="Vikas Banjare — Creative Lead, Video &amp; Design">\n'
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
    "fly-01": "podcast-videos",   "fly-02": "wealthy-yt-ads",  "fly-03": "social-media-designs",
    "ln-01": "trailer-video",     "ln-02": "motion-graphic",   "ln-03": "thumbnail-designs",
    "team-01": "creative-designs", "team-02": "wealthy-yt-ads",
    "team-03": "podcast-videos",   "team-04": "thumbnail-designs",
    "work-01": "podcast-videos",
}
# star-01..03 are the experience cards — they carry the real company logos
# already shipped in the bundle, not project artwork.
STAR_LOGOS = {
    "star-01": "01f4091d-be8b-4550-be7f-a35230217bdf",  # m.Stock by Mirae Asset
    "star-02": "4f18b6ad-811b-4858-ab83-d38301b5eb71",  # Wealthy
    "star-03": "fb3ba0d9-e4ae-4ff5-8a02-1fdd1119941a",  # Unacademy
}
slot_uuid = next(r["uuid"] for r in json.loads(grab("ext_resources")[0])
                 if r["id"] == "imageSlotsState")
slot_state = {sid: {"u": data_uri(cover_jpeg(slug))} for sid, slug in SLOTS.items()}
for sid, uuid in STAR_LOGOS.items():
    e = manifest[uuid]
    slot_state[sid] = {"u": f"data:{e['mime']};base64,{e['data']}"}
manifest[slot_uuid] = {"mime": "application/json", "compressed": False,
                       "data": base64.b64encode(json.dumps(slot_state).encode()).decode()}

# ── 4. geometry + structural fixes ───────────────────────────────────────────
import parts

# 4a. launch rockets and team tiles ship as 3:4 portrait; every cover here is
#     landscape, so a portrait frame crops the middle out of the artwork.
n = tpl.count("width:66%; aspect-ratio:3/4;")
assert n == 3, f"launch rocket frames drifted ({n})"
tpl = tpl.replace("width:66%; aspect-ratio:3/4;", "width:80%; aspect-ratio:16/9;")
tpl = tpl.replace("height:min(44vh,360px)", "height:min(34vh,280px)")

n = tpl.count("width:100%; aspect-ratio:3/4;")
assert n == 4, f"team tile frames drifted ({n})"
tpl = tpl.replace("width:100%; aspect-ratio:3/4;", "width:100%; aspect-ratio:16/9;")

tpl = tpl.replace('placeholder="Project title one imagery (3:4)"', 'placeholder="Project imagery"')

# 4b. the pinned flyby ran 340vh, which is what read as dead space
tpl = tpl.replace('data-fly-pin="1" style="position:relative; height:340vh;"',
                  'data-fly-pin="1" style="position:relative; height:235vh;"')

# 4c. experience cards: logos need containing on white, not cover-cropping on navy
for sid in STAR_LOGOS:
    old = f'<image-slot id="{sid}" shape="rect"'
    assert old in tpl, f"{sid} missing"
    tpl = tpl.replace(old, f'<image-slot id="{sid}" shape="rect" fit="contain"')
tpl = tpl.replace(
    '<div style="position:relative; aspect-ratio:16/9; border-radius:8px; overflow:hidden; background:#080d1a;">',
    '<div style="position:relative; aspect-ratio:16/9; border-radius:8px; overflow:hidden; '
    'background:#fff; padding:14px 18px;">')

# 4d. experience dossiers: rewrite the three star cards to the three employers
CAREER = [
    ("Mirae Asset Capital Markets", "Design Studio Lead · Mumbai",
     "Owns the end-to-end creative function"),
    ("Wealthy", "Associate Creative Head · Bengaluru",
     "Video + design across every channel"),
    ("Unacademy", "Studio Operations Specialist · Bengaluru",
     "2,000+ videos · 100+ channels"),
]
# the pin labels sit outside the cards and picked up the global project-name
# swap, so name the companies there too
tag_positions = [m.start() for m in re.finditer(r'data-star-tag="1"', tpl)]
assert len(tag_positions) == len(CAREER), f"star tags drifted ({len(tag_positions)})"
for pos, (name, _role, _note) in zip(reversed(tag_positions), reversed(CAREER)):
    end = tpl.index("</div>", pos)
    tag = tpl[pos:end]
    fixed = re.sub(r'(font-size:13\.5px; font-weight:600; color:#f6f9ff; white-space:nowrap;">)[^<]*<',
                   lambda m: m.group(1) + name + "<", tag, count=1)
    assert fixed != tag, "star tag unchanged"
    tpl = tpl[:pos] + fixed + tpl[end:]

# all three dossier cards share data-star-card="1"; walk them in document order
positions = [m.start() for m in re.finditer(r'data-star-card="1"', tpl)]
assert len(positions) == len(CAREER), f"star cards drifted ({len(positions)})"
for pos, (name, role, note) in zip(reversed(positions), reversed(CAREER)):
    end = tpl.index("</div>", tpl.index('color:#b6f500;">', pos))
    card = tpl[pos:end]
    fixed = re.sub(r'(font-size:16px; font-weight:600; color:#f6f9ff;">)[^<]*<',
                   lambda m: m.group(1) + name + "<", card, count=1)
    fixed = re.sub(r'(font-size:12px; color:#8da0c4;">)[^<]*<',
                   lambda m: m.group(1) + role + "<", fixed, count=1)
    fixed = re.sub(r'(font-size:12\.5px; font-weight:700; color:#b6f500;">)[^<]*<',
                   lambda m: m.group(1) + note + "<", fixed, count=1)
    assert fixed != card, "star card content unchanged"
    tpl = tpl[:pos] + fixed + tpl[end:]

# 4c-bis. Several wall marks (DataFlow, Purple Finance, The Hub, i30) render
#         tiny inside the tile — give them more of it.
n = tpl.count("max-width:72%; max-height:44px;")
assert n >= 1, "wall logo sizing anchor missing"
tpl = tpl.replace("max-width:72%; max-height:44px;", "max-width:86%; max-height:58px;")

# 4d-bis. launch cards carry the global project-name swap too; name them for
# the three projects their own artwork actually shows.
LAUNCH_CARDS = [
    ("Trailer Video", "Branding · Motion · Grade"),
    ("Motion Graphic", "After Effects · Motion"),
    ("Thumbnail Designs", "CTR-led thumbnail systems"),
]
pad_positions = [m.start() for m in re.finditer(r'data-launch="1"', tpl)]
assert len(pad_positions) == len(LAUNCH_CARDS), f"launch pads drifted ({len(pad_positions)})"
for pos, (name, sub) in zip(reversed(pad_positions), reversed(LAUNCH_CARDS)):
    end = tpl.index("data-launch-alt", pos)
    card = tpl[pos:end]
    fixed = re.sub(r'(font-size:18px; font-weight:600; letter-spacing:-\.02em; color:#f6f9ff;">)[^<]*<',
                   lambda m: m.group(1) + name + "<", card, count=1)
    fixed = re.sub(r'(<span style="font-size:12px; color:#8da0c4;">)[^<]*<',
                   lambda m: m.group(1) + sub + "<", fixed, count=1)
    assert fixed != card, "launch card unchanged"
    tpl = tpl[:pos] + fixed + tpl[end:]

# 4c-ter. Both testimonial cards ship the same placeholder name and the same
#         "C" avatar, so one global swap branded the Unacademy quote as Mirae
#         Asset. Attribute each card positionally.
QUOTES = [
    ("q1", "Mirae Asset Capital Markets", "Design Studio Lead · Mumbai", "M"),
    ("q2", "Unacademy", "Studio Operations Specialist · Bengaluru", "U"),
]
for key, name, role, initial in QUOTES:
    start = tpl.index(f'data-reveal="{key}"')
    end = tpl.index("</blockquote>", start)
    card = tpl[start:end]
    fixed = re.sub(r'(font-size:14\.5px; font-weight:600; color:#f6f9ff;">)[^<]*<',
                   lambda m: m.group(1) + name + "<", card, count=1)
    fixed = re.sub(r'(<span style="font-size:13px; color:#8da0c4;">)[^<]*<',
                   lambda m: m.group(1) + role + "<", fixed, count=1)
    fixed = re.sub(r'(font-size:20px; line-height:1; color:#b6f500;">)[^<]*<',
                   lambda m: m.group(1) + initial + "<", fixed, count=1)
    assert fixed != card, f"quote card {key} unchanged"
    tpl = tpl[:start] + fixed + tpl[end:]

# 4d-ter. The node graph still carried aifloh's wiring, so after "Website" was
#         relabelled "UI/UX" it claimed UI/UX links to SEO. Rewire it to match
#         what these disciplines actually feed in this portfolio.
OS_LINKS = {
    "brand":      "website,motion",     # identity drives product UI and brand motion
    "website":    "brand,motion",       # UI/UX — no longer wired to SEO
    "motion":     "video,brand,website",
    "video":      "motion,ai,seo",      # edits carry motion, AI assist, YouTube SEO
    "ai":         "automation,video",
    "automation": "ai,perf",
    "seo":        "video,perf",
    "perf":       "seo,automation,video",
}
for node, links in OS_LINKS.items():
    pat = re.compile(r'(data-os-node="%s"((?:(?!>).)*?)data-os-link=")[^"]*(")' % re.escape(node))
    tpl, n = pat.subn(lambda m: m.group(1) + links + m.group(3), tpl)
    assert n == 1, f"os node {node} not rewired ({n})"

# 4c-quater. Cross-platform hardening.
# 100vw counts the scrollbar, so on any platform that reserves gutter space
# (Windows especially, where scrollbars are always visible) the hero sat ~15px
# wider than the viewport and the whole page scrolled sideways. macOS overlay
# scrollbars hide the bug entirely.
n = tpl.count("width:100vw;")
assert n == 1, f"hero width anchor drifted ({n})"
tpl = tpl.replace("width:100vw;", "width:100%;")

# 4e. all-work index + gallery viewer + behaviour
def poster_paths(pr):
    """Each video gets its own real frame. Served as files: the site self-hosts
    its assets now, so inlining them as base64 only bloated the page (~1.3 MB)."""
    return {vid: f"assets/posters/{vid}.jpg" for vid in pr["videos"]
            if (ROOT / "assets" / "posters" / f"{vid}.jpg").exists()}


def cover_path(pr):
    hit = sorted((ROOT / "assets" / "img" / pr["slug"]).glob("cover.*"))
    return f"assets/img/{pr['slug']}/{hit[0].name}" if hit else pr["cover"]


def frame_paths(pr):
    """Light 760px stills of the first gallery images, for the work monitor."""
    return [f"assets/frames/{f.name}"
            for f in sorted((ROOT / "assets" / "frames").glob(f"{pr['slug']}-*.jpg"))]


def gallery_srcs(pr):
    """Local files when they exist, Behance CDN as the fallback.

    Self-hosting means a deleted Behance project or a hotlink block can't
    blank out a gallery.
    """
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
    "url": p["url_behance"],
} for p in projects]
_local = sum(1 for p in WORKDATA for s in p["images"] if not s.startswith("http"))
_total = sum(len(p["images"]) for p in WORKDATA)

# The circular flyby and the 13-card grid are both replaced by one component:
# a curated project list with a docked "program monitor" (components/work-section.html,
# chosen from four judged prototypes and hardened by a three-lens review).
# The host's _setupWork() bails when the flyby markup is absent, so removing it is safe.
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
# scripts it can resolve through the manifest, so ship this as a bundle asset
# and reference it by uuid exactly like React/Three/Babel are referenced.
script_js = parts.SCRIPT.replace("__WORKDATA__", json.dumps(WORKDATA, separators=(",", ":")))
GAL_UUID = "9f2c7d14-3b6a-4e18-9c52-71d0a4e8f230"  # fixed: loader matches a strict uuid shape
manifest[GAL_UUID] = {"mime": "text/javascript", "compressed": False,
                      "data": base64.b64encode(script_js.encode()).decode()}
assert "</body>" in tpl
tpl = tpl.replace("</body>", parts.GALLERY + "</body>", 1)

# Only scripts in <head> get re-executed by the loader, so the tag goes beside
# React/Three there; the script polls for its own nodes before wiring.
head_anchor = '<script src="eb552694-613e-47d3-9baa-773be587dd3e"></script>'
assert head_anchor in tpl, "head script anchor missing"
tpl = tpl.replace(head_anchor, head_anchor + f'\n<script src="{GAL_UUID}"></script>', 1)

# 4e-bis. Work-section behaviour. The component's script expects its root to
# exist and window.VB_WORK to be set, but head scripts run before the dc runtime
# mounts the document — so poll for the root, then run the component verbatim.
VB_WORK = [{
    "slug": w["slug"], "title": w["title"], "tags": w["tags"], "kind": w["kind"],
    "cover": w["cover"], "images": w["images"], "videos": w["videos"],
    "posters": w["posters"], "frames": w["frames"],
} for w in WORKDATA]
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
manifest[WORK_UUID] = {"mime": "text/javascript", "compressed": False,
                       "data": base64.b64encode(work_js.encode()).decode()}
tpl = tpl.replace(head_anchor, head_anchor + f'\n<script src="{WORK_UUID}"></script>', 1)
tpl = tpl.replace("</head>", "<style>" + WORK_CSS + "</style></head>", 1)

# 4f. Tools section — inserted after 03, so 04..09 shift down by one.
#     Renumber in reverse so "04 → 05" can't then be caught by "05 → 06".
for n in range(9, 3, -1):
    old_lbl, new_lbl = f"0{n} &mdash; ", f"0{n + 1} &mdash; "
    old_txt, new_txt = f"0{n} — ", f"0{n + 1} — "
    if old_txt in tpl:
        tpl = tpl.replace(old_txt, new_txt)
    elif old_lbl in tpl:
        tpl = tpl.replace(old_lbl, new_lbl)

# inline each tool logo so the page stays self-contained
tool_data = []
for t in parts.TOOLS_DATA:
    t = dict(t)
    if t["logo"]:
        f = ROOT / "assets" / "tools" / t["logo"]
        assert f.exists(), f"missing logo {f}"
        t["logo"] = "data:image/svg+xml;base64," + base64.b64encode(f.read_bytes()).decode()
    tool_data.append(t)

tools_html = parts.TOOLS_SECTION.replace("__NODES__", parts.pipeline_nodes())
close_os = tpl.index("</section>", tpl.index('id="os"')) + len("</section>")
tpl = tpl[:close_os] + tools_html + tpl[close_os:]

tools_js = parts.TOOLS_SCRIPT.replace(
    "__TOOLSDATA__", json.dumps(tool_data, separators=(",", ":")))
TOOLS_UUID = "5d81be27-0c44-4f7b-a3e9-8ab1c62d47f5"
manifest[TOOLS_UUID] = {"mime": "text/javascript", "compressed": False,
                        "data": base64.b64encode(tools_js.encode()).decode()}
tpl = tpl.replace(head_anchor, head_anchor + f'\n<script src="{TOOLS_UUID}"></script>', 1)
tpl = tpl.replace("</head>", parts.TOOLS_CSS + "</head>", 1)

# menu gets a Tools entry pointing at the new section
tpl = tpl.replace('<a href="#os"', '<a href="#tools"', 1) if '<a href="#os"' in tpl else tpl

# 4g. Experience gets substance: logo, dates, scope, expandable detail.
#     The stack row lands in the Tools section.
exp = []
for e in parts.EXPERIENCE:
    e = dict(e)
    uuid = {"__MIRAE__": STAR_LOGOS["star-01"],
            "__WEALTHY__": STAR_LOGOS["star-02"],
            "__UNACADEMY__": STAR_LOGOS["star-03"]}[e["logo"]]
    m = manifest[uuid]
    e["logo"] = f"data:{m['mime']};base64,{m['data']}"
    exp.append(e)

close_chart = tpl.index("</section>", tpl.index('id="starchart"'))
tpl = tpl[:close_chart] + parts.EXPERIENCE_BLOCK + tpl[close_chart:]

close_tools = tpl.index("</section>", tpl.index('id="tools"'))
tpl = tpl[:close_tools] + parts.STACK_BLOCK + tpl[close_tools:]

# Real brand marks (simple-icons, CC0) get inlined and tinted; the five with no
# mark available keep their monogram tile.
def brand_svg(key, ink):
    if key is None:
        return None
    if key == "__figma__":
        return parts.FIGMA_MARK
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
    for name, key, mono, ink, bg in items:
        rows.append([name, brand_svg(key, ink), mono, ink, bg])
    stack_payload.append([group, rows])
real_marks = sum(1 for _, rows in stack_payload for r in rows if r[1])

exp_js = (parts.EXP_SCRIPT
          .replace("__EXPDATA__", json.dumps(exp, separators=(",", ":")))
          .replace("__STACKDATA__", json.dumps(stack_payload, separators=(",", ":")))
          .replace("__FIGMAMARK__", json.dumps(parts.FIGMA_MARK)))
EXP_UUID = "a71f4c92-6d0b-4e55-8f31-2c94b7e0d18a"
manifest[EXP_UUID] = {"mime": "text/javascript", "compressed": False,
                      "data": base64.b64encode(exp_js.encode()).decode()}
tpl = tpl.replace(head_anchor, head_anchor + f'\n<script src="{EXP_UUID}"></script>', 1)

# Safari (iOS and macOS) needs -webkit-backdrop-filter or every frosted panel —
# header, menu, viewer bar, badges — renders flat. Run this last so it also
# covers the markup injected above.
_plain = len(re.findall(r'(?<!-webkit-)backdrop-filter:', tpl))
tpl = re.sub(r'(?<!-webkit-)backdrop-filter:\s*([^;"]+)',
             lambda m: f"-webkit-backdrop-filter:{m.group(1)}; backdrop-filter:{m.group(1)}", tpl)
assert len(re.findall(r'(?<!-webkit-)backdrop-filter:', tpl)) == _plain, "prefix pass incomplete"
print(f"  safari prefixes    : {_plain} backdrop-filter rules")

# 4h. Analytics, if configured. data/analytics.json ships empty, so by default
#     the page carries no tracking at all.
_acfg = json.loads((ROOT / "data" / "analytics.json").read_text())
ANALYTICS = {"provider": _acfg.get("provider", ""), "id": _acfg.get("id", "")}
if ANALYTICS["provider"] and ANALYTICS["id"]:
    an_js = parts.ANALYTICS_SCRIPT.replace(
        "__ANALYTICS__", json.dumps(ANALYTICS, separators=(",", ":")))
    AN_UUID = "b4e9d370-51ac-4a62-9d18-7f0c3e5ab926"
    manifest[AN_UUID] = {"mime": "text/javascript", "compressed": False,
                         "data": base64.b64encode(an_js.encode()).decode()}
    tpl = tpl.replace(head_anchor, head_anchor + f'\n<script src="{AN_UUID}"></script>', 1)
    print(f"  analytics          : {ANALYTICS['provider']} ({ANALYTICS['id']})")
else:
    print("  analytics          : none configured (no tracking shipped)")

# ── 5. write the bundle back out ─────────────────────────────────────────────
out = raw
# The original escapes every "/" as \\u002F so a literal </script> inside the
# template cannot terminate the host <script> tag early. Match that exactly.
tpl_json = json.dumps(tpl).replace("/", "\\u002F")
out = re.sub(r'(<script type="__bundler/template">).*?(</script>)',
             lambda m: m.group(1) + tpl_json + m.group(2), out, count=1, flags=re.S)
out = re.sub(r'(<script type="__bundler/manifest">).*?(</script>)',
             lambda m: m.group(1) + json.dumps(manifest, separators=(",", ":")) + m.group(2),
             out, count=1, flags=re.S)
out = out.replace("<title>Bundled Page</title>", "<title>Vikas Banjare — Creative Lead</title>")

# Injected JS is only exercised in a browser, so a quoting slip used to ship
# silently as a dead section. Fail the build instead.
if shutil.which("node"):
    import tempfile
    for uuid in (GAL_UUID, WORK_UUID, TOOLS_UUID, EXP_UUID):
        src = base64.b64decode(manifest[uuid]["data"]).decode()
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
            fh.write(src)
            probe = fh.name
        r = subprocess.run(["node", "--check", probe], capture_output=True, text=True)
        os.unlink(probe)
        if r.returncode:
            sys.exit(f"injected script {uuid[:8]} has a syntax error:\n{r.stderr}")
    print("  injected js       : syntax OK")
else:
    print("  injected js       : node not found — skipped syntax check")

leftovers = [w for w in ("aifloh", "Project title", "Name one", "Client name") if w in tpl]
OUT.write_text(out, encoding="utf-8")
print(f"wrote {OUT.name}  {len(out)/1024/1024:.2f} MB")
print(f"  copy swaps applied : {len(R)}")
print(f"  image-slots filled : {len(slot_state)}")
print(f"  social links wired : {wired}")
print(f"  brand marks inlined: {real_marks}/{sum(len(r) for _, r in stack_payload)}")
print(f"  gallery self-hosted: {_local}/{_total}")
if leftovers:
    print("  ⚠ leftover placeholder text:", leftovers)
