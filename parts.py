"""Markup + scripts injected into the AI Flow template by rebuild.py.

Everything *added* to the bundle lives here: the YouTube gallery viewer, the
Process section (pipeline + four craft cards), the experience cards, the
software stack, the brand-wall data and the optional analytics loader.
Colours are the role variables from palette.py (var(--accent) etc.). Strict ES5 only — the dc runtime
re-executes these as plain scripts, and they poll for their own root nodes
because head scripts run before the document is mounted.
"""


def slugify(s):
    """'The Hub Bengaluru' -> 'the-hub-bengaluru' (file names for generated tiles)."""
    return "".join(c if c.isalnum() else "-" for c in s.lower()).strip("-")

# ── full-screen category viewer ──────────────────────────────────────────────
GALLERY = """
<div data-vbgal style="position:fixed; inset:0; z-index:140; background:rgba(var(--bg-rgb),.985); backdrop-filter:blur(20px); opacity:0; pointer-events:none; transition:opacity .38s ease; overflow-y:auto; overscroll-behavior:contain; font-family:'Onest',system-ui,sans-serif;">
  <div style="position:sticky; top:0; z-index:3; display:flex; align-items:center; justify-content:space-between; gap:18px; padding:16px clamp(20px,6vw,90px); background:rgba(var(--bg-rgb),.93); border-bottom:1px solid rgba(255,255,255,.12); backdrop-filter:blur(14px);">
    <div style="min-width:0;">
      <h3 data-vbgal-title style="font-family:'Space Grotesk',sans-serif; font-size:clamp(17px,2.4vw,26px); font-weight:600; letter-spacing:-.02em; color:var(--text); white-space:nowrap; overflow:hidden; text-overflow:ellipsis;"></h3>
      <span data-vbgal-meta style="display:block; font-size:10.5px; font-weight:600; letter-spacing:.16em; text-transform:uppercase; color:var(--faint); margin-top:5px;"></span>
    </div>
    <button data-vbgal-close aria-label="Close" style="flex:0 0 auto; width:44px; height:44px; border-radius:50%; border:1px solid rgba(255,255,255,.16); background:rgba(255,255,255,.05); color:var(--body); cursor:pointer; display:flex; align-items:center; justify-content:center; padding:0; transition:background .3s ease, color .3s ease, border-color .3s ease;">
      <svg width="15" height="15" viewBox="0 0 15 15" style="display:block;"><path d="M2 2l11 11M13 2L2 13" stroke="currentColor" stroke-width="1.7" fill="none" stroke-linecap="round"></path></svg>
    </button>
  </div>
  <div data-vbgal-body style="max-width:1240px; margin:0 auto; padding:clamp(22px,4vh,44px) clamp(20px,6vw,90px) clamp(60px,10vh,120px);"></div>
</div>
"""

# ── viewer behaviour ─────────────────────────────────────────────────────────
SCRIPT = """
(function () {
  "use strict";
  var WORK = __WORKDATA__;
  var BY = {};
  WORK.forEach(function (p) { BY[p.slug] = p; });

  function el(sel, root) { return (root || document).querySelector(sel); }

  // Titles come from YouTube's oEmbed and the Super.site scrape — outside-the-
  // build data concatenated into innerHTML. Escape every interpolation.
  function esc(v) {
    return String(v == null ? '' : v)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }
  function countLabel(p) {
    var bits = [];
    if (p.images.length) bits.push(p.images.length + (p.images.length === 1 ? ' piece' : ' pieces'));
    if (p.videos.length) bits.push(p.videos.length + (p.videos.length === 1 ? ' film' : ' films'));
    return bits.join(' · ') || 'no items';
  }
  function metaOf(p, id) { return (p.meta && p.meta[id]) || {}; }
  function watchUrl(id, portrait) {
    return (portrait ? 'https://www.youtube.com/shorts/' : 'https://www.youtube.com/watch?v=') + encodeURIComponent(id);
  }

  // The dc runtime swaps the document in and React renders after this file
  // executes, so wait for our own nodes to exist before wiring anything.
  function ready(cb) {
    var tries = 0;
    (function poll() {
      if (el('[data-vbgal]')) return cb();
      if (++tries > 120) return;            // ~12s, then give up quietly
      setTimeout(poll, 100);
    })();
  }

  ready(function () {
    var gal = el('[data-vbgal]'), body = el('[data-vbgal-body]');
    var lastFocus = null;

    // one video: its own real frame, the impression badge when the site states one,
    // a caption with the title and a plain link out to YouTube
    function tile(p, id) {
      var m = metaOf(p, id), portrait = !!m.portrait;
      var poster = (p.posters && p.posters[id]) || p.cover;
      var title = m.title || p.title;
      return '<figure style="margin:0; display:flex; flex-direction:column; gap:10px; min-width:0;">' +
        '<div data-yt="' + esc(id) + '" role="button" tabindex="0" data-cursor="Play" aria-label="Play ' + esc(title) + '" style="position:relative; aspect-ratio:' + (portrait ? '9/16' : '16/9') + '; border-radius:12px; overflow:hidden; border:1px solid rgba(255,255,255,.12); background:var(--panel-2); cursor:pointer;">' +
          '<img src="' + esc(poster) + '" alt="" loading="lazy" style="width:100%; height:100%; object-fit:cover; opacity:.82; display:block;">' +
          (m.views ? '<span style="position:absolute; top:12px; left:12px; font-family:\\'Space Grotesk\\',sans-serif; font-size:12px; font-weight:700; letter-spacing:.04em; padding:6px 10px; border-radius:100px; background:rgba(var(--bg-rgb),.78); border:1px solid rgba(var(--accent-rgb),.45); color:var(--accent); -webkit-backdrop-filter:blur(8px); backdrop-filter:blur(8px);">' + esc(m.views) + ' impressions</span>' : '') +
          '<span style="position:absolute; inset:0; display:flex; align-items:center; justify-content:center; pointer-events:none;">' +
            '<span style="width:60px; height:60px; border-radius:50%; background:var(--accent); display:flex; align-items:center; justify-content:center; box-shadow:0 12px 40px rgba(var(--accent-rgb),.38);">' +
              '<svg width="16" height="18" viewBox="0 0 16 18" style="margin-left:3px; display:block;"><path d="M0 0l16 9L0 18z" style="fill:var(--on-accent);"></path></svg>' +
            '</span>' +
          '</span>' +
        '</div>' +
        '<figcaption style="display:flex; align-items:baseline; justify-content:space-between; gap:12px; font-size:13px; line-height:1.4; color:var(--muted);">' +
          '<span style="color:var(--body); font-weight:500; min-width:0;">' + esc(title) + '</span>' +
          '<a href="' + esc(watchUrl(id, portrait)) + '" target="_blank" rel="noopener" style="flex:0 0 auto; color:var(--muted); text-decoration:none; white-space:nowrap;">YouTube &#8599;</a>' +
        '</figcaption>' +
      '</figure>';
    }

    function open(slug) {
      var p = BY[slug];
      if (!p || !gal) return;
      lastFocus = document.activeElement;
      el('[data-vbgal-title]').textContent = p.title;
      el('[data-vbgal-meta]').textContent = p.tags.join(' · ') + ' — ' + countLabel(p);

      var h = '', land = [], port = [];
      p.videos.forEach(function (id) { (metaOf(p, id).portrait ? port : land).push(id); });
      if (land.length) {
        h += '<div style="display:grid; grid-template-columns:repeat(auto-fill,minmax(min(100%,430px),1fr)); gap:clamp(14px,1.8vw,22px);">';
        land.forEach(function (id) { h += tile(p, id); });
        h += '</div>';
      }
      if (port.length) {
        if (land.length) h += '<div style="height:clamp(20px,3vh,34px);"></div>';
        // vertical films sit side by side at their own ratio instead of letterboxed in 16:9
        h += '<div style="display:grid; grid-template-columns:repeat(auto-fill,minmax(min(100%,230px),1fr)); gap:clamp(14px,1.8vw,22px);">';
        port.forEach(function (id) { h += tile(p, id); });
        h += '</div>';
      }
      if (p.images.length) {
        if (p.videos.length) h += '<div style="height:clamp(20px,3vh,34px);"></div>';
        var cols = p.images.length === 1 ? 1 : 2;
        h += '<div style="columns:' + cols + '; column-gap:clamp(12px,1.6vw,20px);" data-vbcols>';
        p.images.forEach(function (src, i) {
          var cap = (p.captions && p.captions[i]) || '';
          h += '<figure style="break-inside:avoid; margin:0 0 clamp(12px,1.6vw,20px); border-radius:12px; overflow:hidden; border:1px solid rgba(255,255,255,.1); background:var(--panel-2);">' +
                 '<img src="' + esc(src) + '" alt="' + esc(cap || p.title) + '" loading="lazy" style="width:100%; display:block;">' +
                 (cap ? '<figcaption style="padding:12px 14px; font-size:13px; color:var(--muted);">' + esc(cap) + '</figcaption>' : '') +
               '</figure>';
        });
        h += '</div>';
      }
      body.innerHTML = h;

      if (window.matchMedia('(max-width: 820px)').matches) {
        var c = el('[data-vbcols]', body); if (c) c.style.columns = '1';
      }
      body.querySelectorAll('[data-yt]').forEach(function (t) {
        function play() {
          if (t.querySelector('iframe')) return;
          // ponytail: iframe only on demand — 18 eager players would stall the overlay
          var vid = encodeURIComponent(t.getAttribute('data-yt'));
          t.innerHTML = '<iframe src="https://www.youtube-nocookie.com/embed/' + vid +
            '?autoplay=1&rel=0&playsinline=1&modestbranding=1" allow="autoplay; fullscreen; picture-in-picture; encrypted-media" allowfullscreen ' +
            'loading="lazy" title="' + esc(t.getAttribute('aria-label')) + '" ' +
            'style="position:absolute; inset:0; width:100%; height:100%; border:0; display:block;"></iframe>';
          t.style.cursor = 'default';
          t.removeAttribute('data-cursor');
        }
        t.addEventListener('click', play);
        t.addEventListener('keydown', function (e) {
          if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); play(); }
        });
      });

      gal.style.opacity = '1';
      gal.style.pointerEvents = 'auto';
      gal.scrollTop = 0;
      document.documentElement.style.overflow = 'hidden';
      var cl = el('[data-vbgal-close]'); if (cl) cl.focus();
    }

    function close() {
      if (!gal) return;
      gal.style.opacity = '0';
      gal.style.pointerEvents = 'none';
      document.documentElement.style.overflow = '';
      setTimeout(function () { body.innerHTML = ''; }, 420);  // stops any playing embed
      if (lastFocus && lastFocus.focus) lastFocus.focus();
    }

    // The host page owns wheel events (window listener, passive:false, always
    // preventDefault) for its custom smooth scroll. Keep those off the overlay
    // so a trackpad scrolls it the normal way.
    if (gal) {
      ['wheel', 'touchmove'].forEach(function (evt) {
        gal.addEventListener(evt, function (e) { e.stopPropagation(); }, { passive: true });
      });
    }

    var closeBtn = el('[data-vbgal-close]');
    if (closeBtn) {
      closeBtn.addEventListener('click', close);
      closeBtn.addEventListener('mouseenter', function () {
        closeBtn.style.background = 'var(--accent)'; closeBtn.style.color = 'var(--on-accent)'; closeBtn.style.borderColor = 'var(--accent)';
      });
      closeBtn.addEventListener('mouseleave', function () {
        closeBtn.style.background = 'rgba(255,255,255,.05)'; closeBtn.style.color = 'var(--body)';
        closeBtn.style.borderColor = 'rgba(255,255,255,.16)';
      });
    }
    if (gal) gal.addEventListener('click', function (e) { if (e.target === gal) close(); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && gal && gal.style.pointerEvents === 'auto') close();
    });

    // ── launch pads and the four "closer look" tiles open their category ──
    var LAUNCH = __LAUNCH__, TEAM = __TEAM__;
    document.querySelectorAll('[data-launch]').forEach(function (node, i) {
      if (!LAUNCH[i] || !BY[LAUNCH[i]]) return;
      node.style.cursor = 'pointer';
      node.setAttribute('data-cursor', 'Open');
      node.addEventListener('click', function () { open(LAUNCH[i]); });
    });
    TEAM.forEach(function (slug, i) {
      var slot = document.getElementById('team-0' + (i + 1));
      var card = slot;
      while (card && !(card.getAttribute && card.getAttribute('data-cursor'))) card = card.parentNode;
      if (!card || !BY[slug]) return;
      card.style.cursor = 'pointer';
      card.setAttribute('role', 'button');
      card.setAttribute('tabindex', '0');
      card.setAttribute('aria-label', 'Open ' + BY[slug].title);
      card.addEventListener('click', function () { open(slug); });
      card.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(slug); }
      });
    });

    window.__vbOpenProject = open;
  });
})();
"""


# ── 04 · Process ─────────────────────────────────────────────────────────────
# The stages every film in the reel goes through, with the four crafts Avinash
# owns sitting on the stages they drive. Hovering a card lights its node;
# clicking it opens the category the craft comes from.
PROCESS_CSS = """
<style>
@keyframes vbFlow { to { stroke-dashoffset: -28; } }
@keyframes vbPing { 0%,100% { r:5; opacity:1; } 50% { r:8.5; opacity:.55; } }
@keyframes vbRise { from { opacity:0; transform:translateY(16px); } to { opacity:1; transform:none; } }
[data-vbpipe] .vb-wire { stroke-dasharray: 6 8; animation: vbFlow 1.1s linear infinite; }
[data-vbpipe] .vb-tool > circle:first-child { animation: vbPing 2.6s ease-in-out infinite; }
[data-vbpipe] .vb-tool:nth-of-type(2) > circle:first-child { animation-delay:.5s; }
[data-vbpipe] .vb-tool:nth-of-type(3) > circle:first-child { animation-delay:1s; }
[data-vbpipe] .vb-tool:nth-of-type(4) > circle:first-child { animation-delay:1.5s; }
[data-vbpipe] g[data-node] { transition: opacity .35s ease; cursor: default; }
[data-vbpipe].vb-focus g[data-node]:not(.vb-on) { opacity:.25; }
.vb-tcard { animation: vbRise .7s cubic-bezier(.2,.7,.3,1) both; }
.vb-tcard:hover { border-color: rgba(var(--accent-rgb),.5) !important; transform: translateY(-5px); }
.vb-tcard:focus-visible { outline:2px solid var(--accent); outline-offset:3px; }
@media (prefers-reduced-motion: reduce) {
  [data-vbpipe] .vb-wire, [data-vbpipe] .vb-tool > circle:first-child, .vb-tcard { animation: none !important; }
}
</style>
"""

PROCESS_SECTION = """
<section id="process" style="position:relative; padding:clamp(70px,11vh,140px) clamp(20px,6vw,90px); background:var(--bg);">
  <div style="max-width:1240px; margin:0 auto;">
    <div style="margin-bottom:clamp(30px,5vh,54px);">
      <span style="display:block; font-size:10.5px; font-weight:600; letter-spacing:.18em; text-transform:uppercase; color:var(--accent); margin-bottom:15px;">04 &mdash; Process</span>
      <h2 style="font-family:'Space Grotesk',sans-serif; font-size:clamp(30px,5vw,64px); line-height:1.04; font-weight:500; letter-spacing:-.035em; color:var(--text); max-width:17ch;">How a video gets <span style="font-family:'Instrument Serif',serif; font-style:italic; font-weight:400; color:var(--accent);">made.</span></h2>
      <p style="margin-top:18px; max-width:58ch; font-size:clamp(14.5px,1.4vw,17px); line-height:1.62; color:var(--muted);">Every film in the reel runs through the same six stages. Hover a card to light the stage it owns, and open it to see the category that craft comes from.</p>
    </div>

    <div style="position:relative; border:1px solid rgba(255,255,255,.1); border-radius:18px; background:linear-gradient(180deg, rgba(var(--panel-2-rgb),.55), rgba(var(--bg-rgb),0)); padding:clamp(20px,3vw,38px) clamp(14px,2vw,30px); margin-bottom:clamp(20px,3vh,34px); overflow-x:auto;">
      <svg data-vbpipe viewBox="0 0 1020 178" preserveAspectRatio="xMidYMid meet" style="display:block; width:100%; min-width:620px; height:auto; overflow:visible;" role="img" aria-label="Production pipeline: brief, cut, motion, AI video, thumbnail, publish">
        <line class="vb-wire" x1="70" y1="62" x2="950" y2="62" style="stroke:var(--glow);" stroke-opacity=".55" stroke-width="1.6"></line>
        __NODES__
      </svg>
    </div>

    <div data-vbtools style="display:grid; grid-template-columns:repeat(auto-fit,minmax(min(100%,250px),1fr)); gap:clamp(12px,1.6vw,20px);"></div>
  </div>
</section>
"""

# x, label, kind ('tool' | 'step'), slug
PIPELINE = [
    (90,  "Brief",     "step", None),
    (262, "Cut",       "tool", "cut"),
    (434, "Motion",    "tool", "motion"),
    (606, "AI video",  "tool", "ai"),
    (778, "Thumbnail", "tool", "thumbs"),
    (930, "Publish",   "step", None),
]

PIPE_SUB = {
    "Brief": "hook + structure",
    "cut": "Premiere Pro",
    "motion": "After Effects",
    "ai": "generative shots",
    "thumbs": "Photoshop · Canva",
    "Publish": "Shorts · Reels · YouTube",
}


def pipeline_nodes():
    out = []
    for x, label, kind, slug in PIPELINE:
        tool = kind == "tool"
        fill = "var(--accent)" if tool else "var(--glow-2)"     # style="", not fill="": attributes cannot take var()
        sub = PIPE_SUB[slug or label]
        cls = ' class="vb-tool"' if tool else ""
        out.append(
            f'<g data-node="{slug or label.lower()}"{cls}>'
            f'<circle cx="{x}" cy="62" r="{6 if tool else 4.5}" style="fill:{fill};"></circle>'
            f'<circle cx="{x}" cy="62" r="15" style="fill:none; stroke:{fill};" '
            f'stroke-opacity="{".45" if tool else ".22"}" stroke-width="1"></circle>'
            f'<text x="{x}" y="106" text-anchor="middle" style="fill:{"var(--text)" if tool else "var(--muted)"};" '
            f'font-family="Space Grotesk, sans-serif" font-size="{14 if tool else 12.5}" '
            f'font-weight="{600 if tool else 500}">{label}</text>'
            f'<text x="{x}" y="127" text-anchor="middle" style="fill:var(--faint);" '
            f'font-family="Onest, sans-serif" font-size="11">{sub}</text>'
            f"</g>"
        )
    return "".join(out)


# The four crafts, each pointing at the category in section 02 that shows it.
# Software named here is what his own profile names (Premiere Pro, After
# Effects) plus what the thumbnails were made in.
PROCESS_DATA = [
    {"slug": "cut", "name": "Cut", "tag": "Premiere Pro", "open": "short-form", "accent": True,
     "glyph": "▶",
     "one": "Story first, then the cut.",
     "desc": "Selects, structure and pacing — the assembly that makes a 30-second short or a live-show supercut hold to the last frame."},
    {"slug": "motion", "name": "Motion", "tag": "After Effects", "open": "ui-animation", "accent": False,
     "glyph": "◈",
     "one": "Type, UI and data that move.",
     "desc": "Kinetic captions, UI animation and visual explainers, timed to the rhythm of the cut rather than laid on top of it."},
    {"slug": "ai", "name": "AI video", "tag": "Generative tools", "open": "ai-video", "accent": False,
     "glyph": "✧",
     "one": "New shots without a new shoot.",
     "desc": "Generative video where it earns its place — the Shopdeck AI film in the reel is one example."},
    {"slug": "thumbs", "name": "Thumbnails", "tag": "Photoshop · Canva", "open": "thumbnail-designs", "accent": False,
     "glyph": "▣",
     "one": "The frame that gets the click.",
     "desc": "Title, subject and colour built for a decision made at 160 pixels wide. Two of them are in the reel."},
]

PROCESS_SCRIPT = """
(function () {
  "use strict";
  var CARDS = __PROCESSDATA__;
  function ready(cb) {
    var n = 0;
    (function poll() {
      if (document.querySelector('[data-vbtools]')) return cb();
      if (++n > 120) return;
      setTimeout(poll, 100);
    })();
  }
  ready(function () {
    var wrap = document.querySelector('[data-vbtools]');
    var pipe = document.querySelector('[data-vbpipe]');
    CARDS.forEach(function (t, i) {
      var card = document.createElement('button');
      card.type = 'button';
      card.className = 'vb-tcard';
      card.setAttribute('data-tool', t.slug);
      card.setAttribute('data-cursor', 'Open');
      card.setAttribute('aria-label', 'Open ' + t.name + ' \\u2014 ' + t.one);
      card.style.cssText =
        'display:flex; flex-direction:column; align-items:flex-start; gap:10px; padding:22px 20px 20px; border-radius:16px; text-align:left; font:inherit; color:inherit; cursor:pointer; ' +
        'border:1px solid ' + (t.accent ? 'rgba(var(--accent-rgb),.34)' : 'rgba(255,255,255,.1)') + '; ' +
        'background:' + (t.accent ? 'rgba(var(--accent-rgb),.055)' : 'rgba(255,255,255,.035)') + '; ' +
        'transition:transform .45s cubic-bezier(.2,.7,.3,1), border-color .4s ease; ' +
        'animation-delay:' + (i * 0.09) + 's;';
      card.innerHTML =
        '<span style="display:flex; align-items:center; gap:13px; margin-bottom:2px;">' +
          '<span style="width:54px; height:54px; border-radius:13px; display:flex; align-items:center; justify-content:center; font-size:23px; background:' + (t.accent ? 'rgba(var(--accent-rgb),.13)' : 'rgba(var(--glow-2-rgb),.11)') + '; color:' + (t.accent ? 'var(--accent)' : 'var(--glow-2)') + ';">' + t.glyph + '</span>' +
          '<span style="font-size:10px; font-weight:700; letter-spacing:.15em; text-transform:uppercase; color:' + (t.accent ? 'var(--accent)' : 'var(--faint)') + ';">' + t.tag + '</span>' +
        '</span>' +
        '<span style="font-family:\\'Space Grotesk\\',sans-serif; font-size:20px; font-weight:600; letter-spacing:-.02em; color:var(--text);">' + t.name + '</span>' +
        '<span style="font-family:\\'Space Grotesk\\',sans-serif; font-size:14.5px; font-weight:500; line-height:1.4; color:' + (t.accent ? 'var(--accent)' : 'var(--body-2)') + ';">' + t.one + '</span>' +
        '<span style="font-size:13px; line-height:1.6; color:var(--muted);">' + t.desc + '</span>' +
        '<span style="margin-top:4px; font-size:13px; font-weight:600; color:var(--accent);">Open the category &rarr;</span>';

      function focusNode() {
        if (!pipe) return;
        pipe.classList.add('vb-focus');
        pipe.querySelectorAll('g[data-node]').forEach(function (g) { g.classList.remove('vb-on'); });
        var g = pipe.querySelector('g[data-node="' + t.slug + '"]');
        if (g) g.classList.add('vb-on');
      }
      function blurNode() {
        if (!pipe) return;
        pipe.classList.remove('vb-focus');
        pipe.querySelectorAll('g[data-node]').forEach(function (g) { g.classList.remove('vb-on'); });
      }
      card.addEventListener('mouseenter', focusNode);
      card.addEventListener('mouseleave', blurNode);
      card.addEventListener('focus', focusNode);
      card.addEventListener('blur', blurNode);
      // touch has no hover, so the pipeline highlight was dead on phones
      card.addEventListener('touchstart', focusNode, { passive: true });
      card.addEventListener('click', function () {
        if (typeof window.__vbOpenProject === 'function') window.__vbOpenProject(t.open);
      });
      wrap.appendChild(card);
    });
  });
})();
"""


# ── 06 · Experience detail ───────────────────────────────────────────────────
# One card per role, from his résumé (Sep 2026) and avinash-portfolio.super.site.
# Bullets restate his own descriptions; nothing is added to them. `logo`
# placeholders are swapped for the generated monogram tiles in rebuild.py.
EXPERIENCE = [
    {"slug": "newform", "name": "Newform", "role": "Video Editor",
     "place": "USA · remote", "dates": "Oct 2025 — Present", "logo": "__NEWFORM__", "now": True,
     "lead": "Deliver batches of videos for the studio's clients — cut to a brief and a drop date, remotely from Korba.",
     "points": []},
    {"slug": "freelance", "name": "Freelance", "role": "Video Editor",
     "place": "Remote", "dates": "Jun — Sep 2025", "logo": "__FREELANCE__", "now": False,
     "lead": "Independent video editing for clients between the UAE studio and Newform.",
     "points": []},
    {"slug": "knockout", "name": "Knockout Media", "role": "Senior Video Editor",
     "place": "UAE", "dates": "Feb — May 2025", "logo": "__KNOCKOUT__", "now": False,
     "lead": "Owned the quality of every video and managed all the editors and content in the company.",
     "points": [
        "Reviewed the team's cuts and coached the junior editors on where the work could improve.",
        "Led the brainstorms for new client ideas alongside the day-to-day editing.",
     ]},
    {"slug": "hub", "name": "The Hub Bengaluru", "role": "Senior Video Producer",
     "place": "Bengaluru", "dates": "Nov 2023 — Nov 2024", "logo": "__HUB__", "now": False,
     "lead": "Full-time video editor for the studio and its accounts — shot and edited its films, camera and cut on the same projects.",
     "points": []},
    {"slug": "skydo", "name": "Skydo", "role": "Freelance Video Editor",
     "place": "Remote", "dates": "Jan — Sep 2023", "logo": "__SKYDO__", "now": False,
     "lead": "Edited Instagram reels for the company's channel.",
     "points": []},
    {"slug": "korba", "name": "Exploring Korba Camp", "role": "Founder",
     "place": "Korba, Chhattisgarh", "dates": "Nov 2022 — Present", "logo": "__KORBA__", "now": True,
     "lead": "An ecotourism brand and one of the best-known travel Instagram pages in the state — vision, strategy and day-to-day operations, with a small team.",
     "points": [
        "Showcases Chhattisgarh and promotes sustainable travel experiences.",
        "Photography and social posts for the page sit alongside the video work.",
     ]},
    {"slug": "gaurav", "name": "Gaurav's Academy", "role": "Freelance Video Editor",
     "place": "Remote", "dates": "Jan — Dec 2022", "logo": "__GAURAV__", "now": False,
     "lead": "Ran the YouTube account of Gaurav's Academy for Mechanical Engineers — trailers, teasers, shorts and thumbnails for the channel.",
     "points": []},
]

# Company → (display name, monogram). render_assets.py draws the white tiles;
# rebuild.py registers them as manifest assets for the star cards and the list.
EMPLOYERS = {
    "__NEWFORM__":   ("Newform", "NF"),
    "__FREELANCE__": ("Freelance", "FR"),
    "__KNOCKOUT__":  ("Knockout Media", "KM"),
    "__HUB__":       ("The Hub Bengaluru", "HUB"),
    "__SKYDO__":     ("Skydo", "SK"),
    "__KORBA__":     ("Exploring Korba Camp", "EK"),
    "__GAURAV__":    ("Gaurav's Academy", "GA"),
}

# ── 05 · Brand wall ──────────────────────────────────────────────────────────
# (name, what the readout says on hover). The studios come from his profile;
# the brands and channels are the ones named in his own video titles, with the
# film that names them. Edit freely — the tiles are generated wordmarks.
WALL = [
    ("Newform",             "Video editor · batches of client videos, 2025 — present"),
    ("Knockout Media",      "Senior video editor · UAE, 2025"),
    ("The Hub Bengaluru",   "Junior video editor · shot and cut, 2023 — 2024"),
    ("Exploring Korba Camp", "Founder · ecotourism brand and Instagram page"),
    ("Skydo",               "Freelance video editor · Instagram reels, 2023 · corporate film"),
    ("Gaurav's Academy",    "Freelance · YouTube trailers, teasers, shorts and thumbnails, 2022"),
    ("The Souled Store",    "Case study video"),
    ("Barely Opinionated",  "After movie · live-show supercut"),
    ("TVS",                 "Drive X short · 1.3M impressions"),
    ("Shopdeck",            "AI video"),
    ("Bluechew",            "UGC ad"),
]

# Software he names on his résumé and site, grouped by where it sits in the
# job, with the résumé's own skill dots (out of 5; 0 = not rated there).
# Marks are simple-icons (CC0) in assets/icons/<key>.svg.
#   name, icon-key, monogram, ink, background, level
STACK = [
    ("Edit & motion", [
        ("Premiere Pro",  "premiere",     "Pr", "#9999FF", "#2A0634", 4),
        ("After Effects", "aftereffects", "Ae", "#9999FF", "#00005B", 4),
    ]),
    ("Design", [
        ("Photoshop",   "photoshop",   "Ps", "#31A8FF", "#001E36", 4),
        ("Illustrator", "illustrator", "Ai", "#FF9A00", "#330000", 2),
        ("Canva",       "canva",       "C",  "#FFFFFF", "#00C4CC", 0),
    ]),
]

EXPERIENCE_BLOCK = """
<div data-vbexp style="max-width:1240px; margin:clamp(34px,5vh,60px) auto 0; display:grid; grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr)); gap:clamp(14px,1.8vw,22px);"></div>
"""

STACK_BLOCK = """
<div style="max-width:1240px; margin:clamp(30px,5vh,56px) auto 0; padding-top:clamp(24px,4vh,40px); border-top:1px solid rgba(255,255,255,.1);">
  <span style="display:block; font-size:10.5px; font-weight:700; letter-spacing:.18em; text-transform:uppercase; color:var(--faint); margin-bottom:20px;">What I work in</span>
  <div data-vbstack style="display:grid; grid-template-columns:repeat(auto-fit,minmax(min(100%,220px),1fr)); gap:clamp(18px,2.4vw,34px);"></div>
</div>
"""

EXP_SCRIPT = """
(function () {
  "use strict";
  var EXP = __EXPDATA__, STACK = __STACKDATA__;
  function ready(cb) {
    var n = 0;
    (function poll() {
      if (document.querySelector('[data-vbexp]') && document.querySelector('[data-vbstack]')) return cb();
      if (++n > 120) return;
      setTimeout(poll, 100);
    })();
  }
  ready(function () {
    // ── experience cards ──
    var wrap = document.querySelector('[data-vbexp]');
    EXP.forEach(function (e, i) {
      var more = e.points.length > 0;
      var card = document.createElement('div');
      card.setAttribute('data-exp', e.slug);
      if (more) card.setAttribute('data-cursor', 'Read');
      card.style.cssText =
        'display:flex; flex-direction:column; gap:14px; padding:24px 22px; border-radius:16px; ' + (more ? 'cursor:pointer; ' : '') +
        'border:1px solid ' + (e.now ? 'rgba(var(--accent-rgb),.32)' : 'rgba(255,255,255,.1)') + '; ' +
        'background:' + (e.now ? 'rgba(var(--accent-rgb),.05)' : 'rgba(255,255,255,.035)') + '; ' +
        'transition:border-color .4s ease, transform .45s cubic-bezier(.2,.7,.3,1); ' +
        'opacity:0; transform:translateY(24px);';
      var bullets = e.points.map(function (t) {
        return '<li style="position:relative; padding-left:16px; margin-top:9px; font-size:13px; line-height:1.6; color:var(--muted); list-style:none;">' +
               '<span style="position:absolute; left:0; top:8px; width:5px; height:5px; border-radius:50%; background:' + (e.now ? 'var(--accent)' : 'var(--glow-2)') + ';"></span>' + t + '</li>';
      }).join('');
      card.innerHTML =
        '<span style="display:flex; align-items:center; gap:13px;">' +
          '<span style="width:52px; height:52px; border-radius:12px; background:#fff; display:flex; align-items:center; justify-content:center; padding:6px; flex:0 0 auto;">' +
            '<img src="' + e.logo + '" alt="' + e.name + '" style="max-width:100%; max-height:100%; object-fit:contain; display:block;">' +
          '</span>' +
          '<span style="display:flex; flex-direction:column; gap:3px; min-width:0;">' +
            '<span style="font-family:\\'Space Grotesk\\',sans-serif; font-size:16.5px; font-weight:600; letter-spacing:-.02em; color:var(--text);">' + e.name + '</span>' +
            '<span style="font-size:11.5px; letter-spacing:.04em; color:' + (e.now ? 'var(--accent)' : 'var(--faint)') + ';">' + e.dates + ' · ' + e.place + '</span>' +
          '</span>' +
        '</span>' +
        '<span style="font-family:\\'Space Grotesk\\',sans-serif; font-size:13.5px; font-weight:600; color:var(--body-2);">' + e.role + '</span>' +
        '<span style="font-size:13.5px; line-height:1.62; color:var(--muted);">' + e.lead + '</span>' +
        (more
          ? '<ul data-exp-more style="max-height:0; overflow:hidden; transition:max-height .55s cubic-bezier(.2,.7,.3,1); margin:0; padding:0;">' + bullets + '</ul>' +
            '<span data-exp-toggle style="font-size:12px; font-weight:600; color:' + (e.now ? 'var(--accent)' : 'var(--glow-2)') + ';">Read the detail +</span>'
          : '');

      if (more) {
        var open = false;
        card.setAttribute('role', 'button');
        card.setAttribute('tabindex', '0');
        card.setAttribute('aria-expanded', 'false');
        function toggle() {
          open = !open;
          var ul = card.querySelector('[data-exp-more]');
          var tg = card.querySelector('[data-exp-toggle]');
          ul.style.maxHeight = open ? ul.scrollHeight + 'px' : '0';
          tg.textContent = open ? 'Close \\u2212' : 'Read the detail +';
          card.setAttribute('aria-expanded', open ? 'true' : 'false');
        }
        card.addEventListener('click', toggle);
        card.addEventListener('keydown', function (ev) {
          if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); toggle(); }
        });
      }
      card.addEventListener('mouseenter', function () {
        card.style.transform = 'translateY(-5px)';
        card.style.borderColor = 'rgba(var(--accent-rgb),.5)';
      });
      card.addEventListener('mouseleave', function () {
        card.style.transform = 'none';
        card.style.borderColor = e.now ? 'rgba(var(--accent-rgb),.32)' : 'rgba(255,255,255,.1)';
      });
      wrap.appendChild(card);

      var io = new IntersectionObserver(function (en) {
        en.forEach(function (x) {
          if (!x.isIntersecting) return;
          x.target.style.transition += ', opacity .8s ease ' + (i * 0.1) + 's, transform .8s cubic-bezier(.2,.7,.3,1) ' + (i * 0.1) + 's';
          x.target.style.opacity = '1';
          x.target.style.transform = 'none';
          io.unobserve(x.target);
        });
      }, { threshold: 0.12 });
      io.observe(card);
    });

    // ── software stack ──
    document.querySelector('[data-vbstack]').innerHTML = STACK.map(function (g) {
      return '<div>' +
        '<span style="display:block; font-family:\\'Space Grotesk\\',sans-serif; font-size:13px; font-weight:600; color:var(--accent); margin-bottom:14px;">' + g[0] + '</span>' +
        '<span style="display:flex; flex-wrap:wrap; gap:8px;">' +
          g[1].map(function (t) {
            var name = t[0], svg = t[1], mono = t[2], ink = t[3], bg = t[4], level = t[5] || 0;
            var dots = '', d;
            for (d = 0; d < 5; d++) {
              dots += '<i style="width:5px; height:5px; border-radius:50%; background:' + (d < level ? 'var(--accent)' : 'rgba(255,255,255,.18)') + ';"></i>';
            }
            var badge = svg
              ? svg
              : '<span style="font-family:\\'Space Grotesk\\',sans-serif; font-size:' + (mono.length > 2 ? 9 : 12) + 'px; font-weight:700; letter-spacing:.01em; color:' + ink + ';">' + mono + '</span>';
            return '<span data-sw style="display:inline-flex; align-items:center; gap:9px; padding:6px 13px 6px 6px; border:1px solid rgba(255,255,255,.12); border-radius:100px; cursor:default; transition:border-color .35s ease, transform .35s cubic-bezier(.2,.7,.3,1), background .35s ease;">' +
                     '<span style="width:28px; height:28px; border-radius:8px; background:' + bg + '; display:flex; align-items:center; justify-content:center; flex:0 0 auto;">' + badge + '</span>' +
                     '<span style="font-size:12.5px; color:var(--body-2); white-space:nowrap;">' + name + '</span>' +
                     (level ? '<span aria-label="' + level + ' of 5" style="display:inline-flex; gap:3px; margin-left:2px;">' + dots + '</span>' : '') +
                   '</span>';
          }).join('') +
        '</span>' +
      '</div>';
    }).join('');

    document.querySelectorAll('[data-sw]').forEach(function (chip) {
      chip.addEventListener('mouseenter', function () {
        chip.style.borderColor = 'rgba(var(--accent-rgb),.5)';
        chip.style.background = 'rgba(var(--accent-rgb),.06)';
        chip.style.transform = 'translateY(-3px)';
      });
      chip.addEventListener('mouseleave', function () {
        chip.style.borderColor = 'rgba(255,255,255,.12)';
        chip.style.background = 'transparent';
        chip.style.transform = 'none';
      });
    });
  });
})();
"""


# ── analytics ────────────────────────────────────────────────────────────────
# GitHub Pages keeps no visitor logs, so counting visits needs a script on the
# page. The bundler rewrites <script src> in the template into its own blob
# URLs, so the vendor tag has to be created at runtime instead of written into
# the markup. All three providers below are cookieless — no consent banner.
ANALYTICS_SCRIPT = """
(function () {
  "use strict";
  var P = __ANALYTICS__;
  if (!P || !P.provider || !P.id) return;          // nothing configured: ship nothing
  if (document.querySelector('[data-vb-analytics]')) return;

  var s = document.createElement('script');
  s.setAttribute('data-vb-analytics', P.provider);
  s.defer = true;

  if (P.provider === 'cloudflare') {
    s.src = 'https://static.cloudflareinsights.com/beacon.min.js';
    s.setAttribute('data-cf-beacon', JSON.stringify({ token: P.id }));
  } else if (P.provider === 'goatcounter') {
    s.src = 'https://gc.zgo.at/count.js';
    s.setAttribute('data-goatcounter', 'https://' + P.id + '.goatcounter.com/count');
  } else if (P.provider === 'plausible') {
    s.src = 'https://plausible.io/js/script.js';
    s.setAttribute('data-domain', P.id);
  } else {
    return;
  }

  (document.head || document.documentElement).appendChild(s);
})();
"""


# ── colour themes: picker + live hero recolour ───────────────────────────────
# palette.theme_css() defines every role variable per <html data-theme>. This
# script picks the stored theme before first paint, builds the picker where the
# old light-mode button sat, and re-sets the hero's shader uniforms (the one
# place CSS variables cannot reach) whenever the theme changes.
THEME_CSS = """
<style>
@keyframes abSpin { to { transform:rotate(360deg); } }
@keyframes abBlink { 50% { opacity:.25; } }
.ab-spin { animation:abSpin 40s linear infinite; }
.ab-blink { animation:abBlink 1.4s ease-in-out infinite; }
.ab-grain { background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='160' height='160'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='2' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 .55 0'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>"); }
[data-ab-menu] button:focus-visible, [data-ab-picker] button:focus-visible { outline:2px solid var(--accent); outline-offset:3px; }
@media (prefers-reduced-motion: reduce) { .ab-spin, .ab-blink { animation:none !important; } }
</style>
"""

THEME_SCRIPT = """
(function () {
  "use strict";
  var THEMES = __THEMES__, DEFAULT = __DEFAULT__, KEY = 'ab-palette';
  var UNI = { uBot: 'bg', uTop: 'hero-top', uGlow: 'glow-deep', uCore: 'glow-deep', uRim: 'accent', uFill: 'hero-fill' };
  var ORBIT = ['accent', 'glow', 'glow-2'];   // the eight orbit dots use these three roles
  var BY = {};
  THEMES.forEach(function (t) { BY[t.slug] = t; });
  function html() { return document.documentElement; }
  function stored() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  var current = BY[stored()] ? stored() : DEFAULT;
  html().setAttribute('data-theme', current);

  function hex2rgb(h) { return [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)]; }
  function nearestRole(hex, vars) {
    var a = hex2rgb(hex), best = ORBIT[0], bd = 1e9, i, b, d;
    for (i = 0; i < ORBIT.length; i++) {
      b = hex2rgb(vars[ORBIT[i]]);
      d = (a[0] - b[0]) * (a[0] - b[0]) + (a[1] - b[1]) * (a[1] - b[1]) + (a[2] - b[2]) * (a[2] - b[2]);
      if (d < bd) { bd = d; best = ORBIT[i]; }
    }
    return best;
  }
  // The scene is built with DEFAULT's colours. Uniforms are THREE.Color objects,
  // so setting them in place is enough; orbit colours are matched by nearest role.
  function recolorScene(prevSlug, slug) {
    var scene = window.__abScene, P = BY[prevSlug].vars, N = BY[slug].vars;
    if (!scene || !scene.traverse) return false;
    scene.traverse(function (o) {
      var u = o.material && o.material.uniforms, k;
      if (!u) return;
      for (k in UNI) { if (u[k] && u[k].value && u[k].value.set) u[k].value.set(N[UNI[k]]); }
      if (u.uColor && u.uColor.value && u.uColor.value.getHexString) {
        u.uColor.value.set(N[nearestRole('#' + u.uColor.value.getHexString(), P)]);
      }
    });
    return true;
  }
  if (current !== DEFAULT) {
    var tries = 0;
    (function poll() {
      if (recolorScene(DEFAULT, current)) return;
      if (++tries < 200) setTimeout(poll, 100);
    })();
  }
  function setMeta(slug) {
    var m = document.querySelector('meta[name="theme-color"]');
    if (m) m.setAttribute('content', BY[slug].vars.bg);
  }
  setMeta(current);

  var btn = null, menu = null, items = [];
  function apply(slug) {
    if (!BY[slug] || slug === current) return;
    var prev = current;
    current = slug;
    html().setAttribute('data-theme', slug);
    try { localStorage.setItem(KEY, slug); } catch (e) {}
    setMeta(slug);
    recolorScene(prev, slug);
    refresh();
  }
  function swatch(t, size) {
    return '<span aria-hidden="true" style="width:' + size + 'px; height:' + size + 'px; border-radius:50%; flex:0 0 auto; ' +
      'background:linear-gradient(135deg,' + t.vars.accent + ' 0 50%,' + t.vars.glow + ' 50% 100%); box-shadow:0 0 0 1px rgba(255,255,255,.18);"></span>';
  }
  function refresh() {
    if (!btn) return;
    btn.setAttribute('aria-label', 'Colour theme: ' + BY[current].name);
    btn.innerHTML = swatch(BY[current], 15);
    items.forEach(function (it) {
      var on = it.getAttribute('data-theme-pick') === current;
      it.setAttribute('aria-checked', on ? 'true' : 'false');
      it.style.background = on ? 'rgba(255,255,255,.08)' : 'transparent';
      it.querySelector('[data-check]').style.opacity = on ? '1' : '0';
    });
  }
  function place() {
    var r = btn.getBoundingClientRect();
    menu.style.top = (r.bottom + 10) + 'px';
    menu.style.right = Math.max(12, window.innerWidth - r.right) + 'px';
  }
  function open(v) {
    menu.hidden = !v;
    btn.setAttribute('aria-expanded', v ? 'true' : 'false');
    if (v) { place(); if (items[0]) items[0].focus(); }
  }
  function build(slot) {
    btn = document.createElement('button');
    btn.type = 'button';
    btn.setAttribute('data-cursor', 'Colours');
    btn.setAttribute('aria-haspopup', 'true');
    btn.setAttribute('aria-expanded', 'false');
    btn.style.cssText = 'display:flex; align-items:center; justify-content:center; width:41px; height:41px; border-radius:50%; ' +
      'background:rgba(255,255,255,.05); border:1px solid rgba(255,255,255,.14); color:var(--body); cursor:pointer; padding:0; ' +
      '-webkit-backdrop-filter:blur(10px); backdrop-filter:blur(10px);';
    slot.appendChild(btn);

    // the menu lives on <body>: the header translates itself on scroll, which would drag a nested fixed panel along
    menu = document.createElement('div');
    menu.setAttribute('data-ab-menu', '');
    menu.setAttribute('role', 'menu');
    menu.setAttribute('aria-label', 'Colour theme');
    menu.hidden = true;
    menu.style.cssText = 'position:fixed; z-index:120; min-width:210px; padding:8px; border-radius:16px; ' +
      'background:rgba(var(--bg-2-rgb),.94); border:1px solid rgba(255,255,255,.12); box-shadow:0 24px 60px rgba(0,0,0,.55); ' +
      '-webkit-backdrop-filter:blur(16px); backdrop-filter:blur(16px); font-family:\\'Onest\\',system-ui,sans-serif;';
    var h = '<span style="display:block; padding:6px 10px 8px; font-size:10.5px; font-weight:700; letter-spacing:.18em; text-transform:uppercase; color:var(--faint);">Colour theme</span>';
    THEMES.forEach(function (t) {
      h += '<button type="button" role="menuitemradio" data-theme-pick="' + t.slug + '" aria-checked="false" ' +
        'style="display:flex; align-items:center; gap:11px; width:100%; min-height:44px; padding:8px 10px; border:0; border-radius:10px; ' +
        'background:transparent; color:var(--text); font:500 14px \\'Onest\\',system-ui,sans-serif; cursor:pointer; text-align:left;">' +
        swatch(t, 18) + '<span style="flex:1;">' + t.name + '</span>' +
        '<span data-check style="opacity:0; color:var(--accent); font-weight:700;">&#10003;</span></button>';
    });
    menu.innerHTML = h;
    document.body.appendChild(menu);
    items = [].slice.call(menu.querySelectorAll('[data-theme-pick]'));
    items.forEach(function (it) {
      it.addEventListener('click', function () { apply(it.getAttribute('data-theme-pick')); open(false); btn.focus(); });
      it.addEventListener('mouseenter', function () { if (it.getAttribute('aria-checked') !== 'true') it.style.background = 'rgba(255,255,255,.05)'; });
      it.addEventListener('mouseleave', function () { if (it.getAttribute('aria-checked') !== 'true') it.style.background = 'transparent'; });
    });
    btn.addEventListener('click', function (e) { e.stopPropagation(); open(menu.hidden); });
    document.addEventListener('click', function (e) { if (!menu.hidden && !menu.contains(e.target) && e.target !== btn) open(false); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !menu.hidden) { open(false); btn.focus(); } });
    window.addEventListener('scroll', function () { if (!menu.hidden) open(false); }, { passive: true });
    window.addEventListener('resize', function () { if (!menu.hidden) place(); });
    // the host owns wheel events for its smooth scroll; keep them off the panel
    ['wheel', 'touchmove'].forEach(function (evt) {
      menu.addEventListener(evt, function (e) { e.stopPropagation(); }, { passive: true });
    });
    refresh();
  }
  var n = 0;
  (function poll() {
    var slot = document.querySelector('[data-ab-picker]');
    if (slot) { html().setAttribute('data-theme', current); build(slot); return; }
    if (++n < 200) setTimeout(poll, 100);
  })();
})();
"""

# ── portrait: the About section's opener ─────────────────────────────────────
# His photo from the Super.site (cropped to the head-and-shoulders disc; the
# greyscale and the speckled disc are his), with theme-coloured ring, tint,
# grain and two stickers. Everything but the photo follows the theme.
PORTRAIT_HTML = """
<div data-ab-portrait style="position:relative; width:min(240px,58vw); aspect-ratio:1/1; margin:0 0 14px 6px;">
  <span style="position:absolute; inset:14% -10% -12% 10%; border-radius:50%; background:rgba(var(--glow-rgb),.38); filter:blur(32px); pointer-events:none;"></span>
  <span class="ab-spin" style="position:absolute; inset:-13px; border-radius:50%; border:1.5px dashed rgba(var(--accent-rgb),.6); pointer-events:none;"></span>
  <span style="position:relative; display:block; width:100%; height:100%; border-radius:50%; overflow:hidden; border:3px solid var(--accent); box-shadow:0 24px 60px rgba(0,0,0,.5); background:var(--panel);">
    <img src="assets/portrait.jpg" alt="Avinash Banjare" width="490" height="490" loading="lazy" style="display:block; width:100%; height:100%; object-fit:cover; filter:grayscale(1) contrast(1.06);">
    <span style="position:absolute; inset:0; background:rgba(var(--accent-rgb),.26); mix-blend-mode:color; pointer-events:none;"></span>
    <span class="ab-grain" style="position:absolute; inset:0; opacity:.3; mix-blend-mode:overlay; pointer-events:none;"></span>
  </span>
  <span aria-hidden="true" style="position:absolute; right:-8px; top:6%; width:58px; height:58px; border-radius:18px; background:var(--accent); color:var(--on-accent); display:flex; align-items:center; justify-content:center; transform:rotate(9deg); box-shadow:0 14px 30px rgba(0,0,0,.35);"><svg width="20" height="22" viewBox="0 0 16 18" style="display:block; margin-left:3px;"><path d="M0 0l16 9L0 18z" fill="currentColor"></path></svg></span>
  <span aria-hidden="true" style="position:absolute; left:-14px; bottom:9%; display:inline-flex; align-items:center; gap:8px; padding:9px 13px; border-radius:100px; background:var(--panel); border:1px solid rgba(255,255,255,.14); transform:rotate(-6deg); font-family:'Space Grotesk',sans-serif; font-size:11px; font-weight:700; letter-spacing:.14em; color:var(--text); box-shadow:0 10px 24px rgba(0,0,0,.35);"><i class="ab-blink" style="width:8px; height:8px; border-radius:50%; background:#ff3d3d; display:inline-block;"></i>REC · 4K</span>
</div>
"""
