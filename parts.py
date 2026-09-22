"""Markup + script injected into the AI Flow template by rebuild.py.

Kept in its own module so rebuild.py stays readable: this is all *new* UI
(the all-work index and the project gallery overlay), written to match the
bundle's existing inline-style, Space-Grotesk/Onest visual language.
"""

# ── the clickable index of every project, appended inside section 02 ─────────
INDEX_GRID = """
<div style="position:relative; z-index:4; max-width:1240px; margin:0 auto; padding:clamp(28px,5vh,60px) clamp(20px,6vw,90px) clamp(56px,8vh,100px);">
  <div style="display:flex; align-items:flex-end; justify-content:space-between; gap:20px; flex-wrap:wrap; margin-bottom:clamp(20px,3vh,32px);">
    <div style="display:flex; flex-direction:column; gap:6px;">
      <span style="font-size:10.5px; font-weight:600; letter-spacing:.18em; text-transform:uppercase; color:#b6f500;">All work</span>
      <h3 style="font-family:'Space Grotesk',sans-serif; font-size:clamp(20px,2.4vw,30px); font-weight:600; letter-spacing:-.025em; color:#f6f9ff;">__NPROJ__ projects. Open any one.</h3>
    </div>
    <span style="font-size:12.5px; color:#8da0c4;">__COUNTS__</span>
  </div>
  <div data-vbgrid style="display:grid; grid-template-columns:repeat(auto-fill,minmax(min(100%,270px),1fr)); gap:clamp(12px,1.5vw,20px);"></div>
</div>
"""

# ── full-screen project viewer ───────────────────────────────────────────────
GALLERY = """
<div data-vbgal style="position:fixed; inset:0; z-index:140; background:rgba(4,6,13,.985); backdrop-filter:blur(20px); opacity:0; pointer-events:none; transition:opacity .38s ease; overflow-y:auto; overscroll-behavior:contain; font-family:'Onest',system-ui,sans-serif;">
  <div style="position:sticky; top:0; z-index:3; display:flex; align-items:center; justify-content:space-between; gap:18px; padding:16px clamp(20px,6vw,90px); background:rgba(4,6,13,.93); border-bottom:1px solid rgba(255,255,255,.12); backdrop-filter:blur(14px);">
    <div style="min-width:0;">
      <h3 data-vbgal-title style="font-family:'Space Grotesk',sans-serif; font-size:clamp(17px,2.4vw,26px); font-weight:600; letter-spacing:-.02em; color:#f6f9ff; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;"></h3>
      <span data-vbgal-meta style="display:block; font-size:10.5px; font-weight:600; letter-spacing:.16em; text-transform:uppercase; color:#5d6e8e; margin-top:5px;"></span>
    </div>
    <button data-vbgal-close aria-label="Close" style="flex:0 0 auto; width:44px; height:44px; border-radius:50%; border:1px solid rgba(255,255,255,.16); background:rgba(255,255,255,.05); color:#eaf0ff; cursor:pointer; display:flex; align-items:center; justify-content:center; padding:0; transition:background .3s ease, color .3s ease, border-color .3s ease;">
      <svg width="15" height="15" viewBox="0 0 15 15" style="display:block;"><path d="M2 2l11 11M13 2L2 13" stroke="currentColor" stroke-width="1.7" fill="none" stroke-linecap="round"></path></svg>
    </button>
  </div>
  <div data-vbgal-body style="max-width:1240px; margin:0 auto; padding:clamp(22px,4vh,44px) clamp(20px,6vw,90px) clamp(60px,10vh,120px);"></div>
</div>
"""

# ── behaviour ────────────────────────────────────────────────────────────────
# Plain script in the template body; the bundler re-executes these on mount.
SCRIPT = """
(function () {
  "use strict";
  var WORK = __WORKDATA__;
  var CCV = 'https://www-ccv.adobe.io/v1/player/ccv/';
  var BY = {};
  WORK.forEach(function (p) { BY[p.slug] = p; });

  function el(sel, root) { return (root || document).querySelector(sel); }

  // Titles, tags and image paths come from a scrape of Behance — outside-the-
  // build data concatenated into innerHTML. Escape every interpolation rather
  // than trusting the source stays well-behaved.
  // "1 pieces" read wrong, and a project holding both images and films only
  // ever reported one of them.
  function countLabel(p) {
    var bits = [];
    if (p.images.length) bits.push(p.images.length + (p.images.length === 1 ? ' piece' : ' pieces'));
    if (p.videos.length) bits.push(p.videos.length + (p.videos.length === 1 ? ' film' : ' films'));
    return bits.join(' · ') || 'no items';
  }

  function esc(v) {
    return String(v == null ? '' : v)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  // The dc runtime swaps the document in and React renders after this file
  // executes, so wait for our own nodes to exist before wiring anything.
  function ready(cb) {
    var tries = 0;
    (function poll() {
      if (el('[data-vbgal]')) return cb();   // the index grid was replaced by the work-section component
      if (++tries > 120) return;            // ~12s, then give up quietly
      setTimeout(poll, 100);
    })();
  }

  ready(function () {
    // ── the all-work index ──
    var grid = el('[data-vbgrid]');
    if (grid) {
      WORK.forEach(function (p) {
        var n = countLabel(p);
        var card = document.createElement('button');
        card.type = 'button';
        card.setAttribute('data-cursor', 'Open');
        card.setAttribute('aria-label', 'Open ' + p.title);
        card.style.cssText = 'position:relative; display:block; width:100%; padding:0; text-align:left; border:1px solid rgba(255,255,255,.1); border-radius:16px; overflow:hidden; background:#080d1a; cursor:pointer; font-family:inherit; transition:transform .5s cubic-bezier(.2,.7,.3,1), border-color .4s ease, box-shadow .4s ease;';
        card.innerHTML =
          '<div style="position:relative; aspect-ratio:16/9; overflow:hidden; background:#0a1226;">' +
            '<img src="' + esc(p.cover) + '" alt="' + esc(p.title) + '" loading="lazy" style="width:100%; height:100%; object-fit:cover; display:block; transition:transform .8s cubic-bezier(.2,.7,.3,1);">' +
            '<span style="position:absolute; top:11px; left:11px; font-size:9.5px; font-weight:700; letter-spacing:.14em; text-transform:uppercase; padding:5px 10px; border-radius:100px; background:rgba(4,6,13,.72); border:1px solid ' + (p.kind === 'video' ? 'rgba(182,245,0,.45); color:#b6f500;' : 'rgba(255,255,255,.16); color:#cfe0ff;') + ' -webkit-backdrop-filter:blur(8px); backdrop-filter:blur(8px);">' + (p.kind === 'video' ? 'Film' : 'Design') + '</span>' +
            '<span style="position:absolute; inset:0; background:linear-gradient(to top, rgba(4,6,13,.9), rgba(4,6,13,0) 58%);"></span>' +
          '</div>' +
          '<div style="display:flex; align-items:flex-end; justify-content:space-between; gap:12px; padding:14px 16px 16px; margin-top:-46px; position:relative;">' +
            '<span style="display:flex; flex-direction:column; gap:4px; min-width:0;">' +
              '<span style="font-family:\\'Space Grotesk\\',sans-serif; font-size:16.5px; font-weight:600; letter-spacing:-.02em; color:#f6f9ff;">' + esc(p.title) + '</span>' +
              '<span style="font-size:12px; color:#8da0c4;">' + esc(p.tags.join(' · ')) + '</span>' +
            '</span>' +
            '<span style="flex:0 0 auto; font-family:\\'Space Grotesk\\',sans-serif; font-size:12px; color:#b6f500;">' + esc(n) + '</span>' +
          '</div>';
        card.addEventListener('mouseenter', function () {
          card.style.transform = 'translateY(-6px)';
          card.style.borderColor = 'rgba(182,245,0,.5)';
          card.style.boxShadow = '0 22px 50px rgba(0,0,0,.55)';
          var im = card.querySelector('img'); if (im) im.style.transform = 'scale(1.06)';
        });
        card.addEventListener('mouseleave', function () {
          card.style.transform = '';
          card.style.borderColor = 'rgba(255,255,255,.1)';
          card.style.boxShadow = '';
          var im = card.querySelector('img'); if (im) im.style.transform = '';
        });
        card.addEventListener('click', function () { open(p.slug); });
        grid.appendChild(card);
      });
    }

    // ── viewer ──
    var gal = el('[data-vbgal]'), body = el('[data-vbgal-body]');
    var lastFocus = null;

    function open(slug) {
      var p = BY[slug];
      if (!p || !gal) return;
      lastFocus = document.activeElement;
      el('[data-vbgal-title]').textContent = p.title;
      el('[data-vbgal-meta]').textContent = p.tags.join(' · ') + ' — ' + countLabel(p);

      var h = '';
      if (p.videos.length) {
        h += '<div style="display:grid; grid-template-columns:repeat(auto-fill,minmax(min(100%,430px),1fr)); gap:clamp(14px,1.8vw,22px);">';
        p.videos.forEach(function (id) {
          // a real frame from THIS video, not the shared project cover
          var poster = (p.posters && p.posters[id]) || p.cover;
          h += '<div data-ccv="' + esc(id) + '" data-cursor="Play" style="position:relative; aspect-ratio:16/9; border-radius:12px; overflow:hidden; border:1px solid rgba(255,255,255,.12); background:#0a1226; cursor:pointer;">' +
                 '<img src="' + esc(poster) + '" alt="" loading="lazy" style="width:100%; height:100%; object-fit:cover; opacity:.75; display:block;">' +
                 '<span style="position:absolute; inset:0; display:flex; align-items:center; justify-content:center; pointer-events:none;">' +
                   '<span style="width:60px; height:60px; border-radius:50%; background:#b6f500; display:flex; align-items:center; justify-content:center; box-shadow:0 12px 40px rgba(182,245,0,.38);">' +
                     '<svg width="16" height="18" viewBox="0 0 16 18" style="margin-left:3px; display:block;"><path d="M0 0l16 9L0 18z" fill="#06140a"></path></svg>' +
                   '</span>' +
                 '</span>' +
               '</div>';
        });
        h += '</div>';
      }
      if (p.images.length) {
        if (p.videos.length) h += '<div style="height:clamp(20px,3vh,34px);"></div>';
        // one piece reads full-width; a set reads as two columns
        var cols = p.images.length === 1 ? 1 : 2;
        h += '<div style="columns:' + cols + '; column-gap:clamp(12px,1.6vw,20px);" data-vbcols>';
        p.images.forEach(function (src) {
          h += '<figure style="break-inside:avoid; margin:0 0 clamp(12px,1.6vw,20px); border-radius:12px; overflow:hidden; border:1px solid rgba(255,255,255,.1); background:#0a1226;">' +
                 '<img src="' + esc(src) + '" alt="' + esc(p.title) + '" loading="lazy" style="width:100%; display:block;">' +
               '</figure>';
        });
        h += '</div>';
      }
      body.innerHTML = h;

      if (window.matchMedia('(max-width: 820px)').matches) {
        var c = el('[data-vbcols]', body); if (c) c.style.columns = '1';
      }
      body.querySelectorAll('[data-ccv]').forEach(function (tile) {
        tile.addEventListener('click', function () {
          // ponytail: iframe only on click — 33 eager players would stall the page
          var vid = encodeURIComponent(tile.getAttribute('data-ccv'));
          tile.innerHTML = '<iframe src="' + CCV + vid +
            '/embed?api_key=behance1&bgcolor=%2304060d" allow="autoplay; fullscreen" allowfullscreen ' +
            'referrerpolicy="no-referrer" loading="lazy" title="Project video" ' +
            'style="width:100%; height:100%; border:0; display:block;"></iframe>';
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
        closeBtn.style.background = '#b6f500'; closeBtn.style.color = '#06140a'; closeBtn.style.borderColor = '#b6f500';
      });
      closeBtn.addEventListener('mouseleave', function () {
        closeBtn.style.background = 'rgba(255,255,255,.05)'; closeBtn.style.color = '#eaf0ff';
        closeBtn.style.borderColor = 'rgba(255,255,255,.16)';
      });
    }
    if (gal) gal.addEventListener('click', function (e) { if (e.target === gal) close(); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && gal && gal.style.pointerEvents === 'auto') close();
    });

    // ── wire the flyby + launch cards ──
    // The three planets hold fixed artwork, but the scan card rotates through
    // projects as you scroll. Clicking the card must open whatever the card is
    // *currently naming* — read the live index instead of a fixed one.
    var LAUNCH = ['trailer-video', 'motion-graphic', 'thumbnail-designs'];

    document.querySelectorAll('[data-launch]').forEach(function (node, i) {
      if (!LAUNCH[i] || !BY[LAUNCH[i]]) return;
      node.style.cursor = 'pointer';
      node.setAttribute('data-cursor', 'Open');
      node.addEventListener('click', function () { open(LAUNCH[i]); });
    });

    // ── stagger the index grid in on scroll ──
    var cards = [].slice.call(grid ? grid.children : []);
    cards.forEach(function (c) { c.style.opacity = '0'; c.style.transform = 'translateY(26px)'; });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        var d = cards.indexOf(e.target) % 3;
        e.target.style.transition =
          'opacity .8s cubic-bezier(.2,.7,.3,1) ' + (d * 0.09) + 's, ' +
          'transform .8s cubic-bezier(.2,.7,.3,1) ' + (d * 0.09) + 's, ' +
          'border-color .4s ease, box-shadow .4s ease';
        e.target.style.opacity = '1';
        e.target.style.transform = 'none';
        io.unobserve(e.target);
      });
    }, { threshold: 0.15, rootMargin: '0px 0px -6% 0px' });
    cards.forEach(function (c) { io.observe(c); });

    window.__vbOpenProject = open;
  });
})();
"""


# ── 04 · Tools ───────────────────────────────────────────────────────────────
# An animated production pipeline: the stages of the job, with the software
# Vikas wrote sitting on the stages it actually automates. Hovering a card
# lights its node. Pure CSS motion + a little JS for the hover link.
TOOLS_CSS = """
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
.vb-tcard:hover { border-color: rgba(182,245,0,.5) !important; transform: translateY(-5px); }
@media (prefers-reduced-motion: reduce) {
  [data-vbpipe] .vb-wire, [data-vbpipe] .vb-tool > circle:first-child, .vb-tcard { animation: none !important; }
}
</style>
"""

TOOLS_SECTION = """
<section id="tools" style="position:relative; padding:clamp(70px,11vh,140px) clamp(20px,6vw,90px); background:#04060d;">
  <div style="max-width:1240px; margin:0 auto;">
    <div style="margin-bottom:clamp(30px,5vh,54px);">
      <span style="display:block; font-size:10.5px; font-weight:600; letter-spacing:.18em; text-transform:uppercase; color:#b6f500; margin-bottom:15px;">04 &mdash; Tools</span>
      <h2 style="font-family:'Space Grotesk',sans-serif; font-size:clamp(30px,5vw,64px); line-height:1.04; font-weight:500; letter-spacing:-.035em; color:#f6f9ff; max-width:17ch;">Software I built to <span style="font-family:'Instrument Serif',serif; font-style:italic; font-weight:400; color:#b6f500;">do the work.</span></h2>
      <p style="margin-top:18px; max-width:58ch; font-size:clamp(14.5px,1.4vw,17px); line-height:1.62; color:#8da0c4;">This is where the 70% automation number comes from. Each one sits on a stage of the pipeline below and takes the repetitive pass off a real production schedule.</p>
    </div>

    <div style="position:relative; border:1px solid rgba(255,255,255,.1); border-radius:18px; background:linear-gradient(180deg, rgba(12,23,54,.5), rgba(4,6,13,0)); padding:clamp(20px,3vw,38px) clamp(14px,2vw,30px); margin-bottom:clamp(20px,3vh,34px); overflow-x:auto;">
      <svg data-vbpipe viewBox="0 0 1020 178" preserveAspectRatio="xMidYMid meet" style="display:block; width:100%; min-width:620px; height:auto; overflow:visible;" role="img" aria-label="Production pipeline: idea, ContentIntel, CutPilot, Pulse, Daxio, live">
        <line class="vb-wire" x1="70" y1="62" x2="950" y2="62" stroke="#2f6bff" stroke-opacity=".55" stroke-width="1.6"></line>
        __NODES__
      </svg>
    </div>

    <div data-vbtools style="display:grid; grid-template-columns:repeat(auto-fit,minmax(min(100%,250px),1fr)); gap:clamp(12px,1.6vw,20px);"></div>
  </div>
</section>
"""

# x, label, kind ('tool' | 'step'), slug
PIPELINE = [
    (90,  "Idea",         "step", None),
    (262, "VoiceFlow",    "tool", "voiceflow"),
    (434, "ContentIntel", "tool", "contentintel"),
    (606, "Pulse",        "tool", "pulse"),
    (778, "Daxio",        "tool", "daxio"),
    (930, "Live",         "step", None),
]

PIPE_SUB = {
    "Idea": "brief",
    "voiceflow": "dictate it",
    "contentintel": "grade it",
    "pulse": "cut + caption it",
    "daxio": "review it",
    "Live": "published",
}


def pipeline_nodes():
    out = []
    for x, label, kind, slug in PIPELINE:
        tool = kind == "tool"
        fill = "#b6f500" if tool else "#7fd4ff"
        sub = PIPE_SUB[slug or label]
        cls = ' class="vb-tool"' if tool else ""
        out.append(
            f'<g data-node="{slug or label.lower()}"{cls}>'
            f'<circle cx="{x}" cy="62" r="{6 if tool else 4.5}" fill="{fill}"></circle>'
            f'<circle cx="{x}" cy="62" r="15" fill="none" stroke="{fill}" '
            f'stroke-opacity="{".45" if tool else ".22"}" stroke-width="1"></circle>'
            f'<text x="{x}" y="106" text-anchor="middle" fill="{"#f6f9ff" if tool else "#8da0c4"}" '
            f'font-family="Space Grotesk, sans-serif" font-size="{14 if tool else 12.5}" '
            f'font-weight="{600 if tool else 500}">{label}</text>'
            f'<text x="{x}" y="127" text-anchor="middle" fill="#5d6e8e" '
            f'font-family="Onest, sans-serif" font-size="11">{sub}</text>'
            f"</g>"
        )
    return "".join(out)


# Only tools with evidence on this machine. Every claim below traces to a file:
# the VoiceFlow kickoff brief, the CutPilot/Pulse extension READMEs, the Daxio
# site copy, and contentintel.in itself.
TOOLS_DATA = [
    {"slug": "contentintel", "name": "ContentIntel", "tag": "Live · contentintel.in",
     "url": "https://contentintel.in", "accent": True,
     "logo": None, "glyph": "\u25c8",
     "one": "Checks a post before you publish it.",
     "desc": "Paste a script, thumbnail or title and it grades them the way the algorithm would \u2014 then rewrites the weak parts."},
    {"slug": "voiceflow", "name": "VoiceFlow", "tag": "Mac app (internal tool)",
     "url": None, "accent": False,
     "logo": "voiceflow-mark.svg", "glyph": None,
     "one": "Talk, and it types.",
     "desc": "Dictation for the Mac. Runs Whisper on-device, cleans the text up, and types it into whatever app you are already in."},
    {"slug": "pulse", "name": "Pulse", "tag": "Premiere extension (internal tool)",
     "url": None, "accent": False,
     "logo": "pulse-logo-primary.svg", "glyph": None,
     "one": "Cuts and captions inside Premiere.",
     "desc": "Transcribes the footage, builds the rough cut from the transcript, then adds the subtitles \u2014 without leaving the timeline."},
    {"slug": "daxio", "name": "Daxio", "tag": "Review tool (internal tool)",
     "url": None, "accent": False,
     "logo": "daxio-mark-white.svg", "glyph": None,
     "one": "Notes that stick to the frame.",
     "desc": "Review that is tied to the timeline. A comment lands on the exact frame it is about, so feedback is never ambiguous and nothing gets lost in a thread."},
]

TOOLS_SCRIPT = """
(function () {
  "use strict";
  var TOOLS = __TOOLSDATA__;
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
    TOOLS.forEach(function (t, i) {
      var card = document.createElement(t.url ? 'a' : 'div');
      if (t.url) { card.href = t.url; card.target = '_blank'; card.rel = 'noopener'; }
      card.className = 'vb-tcard';
      card.setAttribute('data-tool', t.slug);
      card.setAttribute('data-cursor', t.url ? 'Visit' : 'Built');
      card.style.cssText =
        'display:flex; flex-direction:column; gap:10px; padding:22px 20px 20px; border-radius:16px; ' +
        'border:1px solid ' + (t.accent ? 'rgba(182,245,0,.34)' : 'rgba(255,255,255,.1)') + '; ' +
        'background:' + (t.accent ? 'rgba(182,245,0,.055)' : 'rgba(255,255,255,.035)') + '; ' +
        'text-decoration:none; transition:transform .45s cubic-bezier(.2,.7,.3,1), border-color .4s ease; ' +
        'animation-delay:' + (i * 0.09) + 's;';
      var mark = t.logo
        ? '<img src="' + t.logo + '" alt="' + t.name + '" style="width:54px; height:54px; object-fit:contain; display:block; border-radius:13px;">'
        : '<span style="width:54px; height:54px; border-radius:13px; display:flex; align-items:center; justify-content:center; font-size:25px; background:' + (t.accent ? 'rgba(182,245,0,.13)' : 'rgba(127,212,255,.11)') + '; color:' + (t.accent ? '#b6f500' : '#7fd4ff') + ';">' + (t.glyph || t.name[0]) + '</span>';
      card.innerHTML =
        '<span style="display:flex; align-items:center; gap:13px; margin-bottom:2px;">' +
          mark +
          '<span style="font-size:10px; font-weight:700; letter-spacing:.15em; text-transform:uppercase; color:' + (t.accent ? '#b6f500' : '#5d6e8e') + ';">' + t.tag + '</span>' +
        '</span>' +
        '<span style="font-family:\\'Space Grotesk\\',sans-serif; font-size:20px; font-weight:600; letter-spacing:-.02em; color:#f6f9ff;">' + t.name + '</span>' +
        '<span style="font-family:\\'Space Grotesk\\',sans-serif; font-size:14.5px; font-weight:500; line-height:1.4; color:' + (t.accent ? '#b6f500' : '#cfe0ff') + ';">' + t.one + '</span>' +
        '<span style="font-size:13px; line-height:1.6; color:#8da0c4;">' + t.desc + '</span>' +
        (t.url ? '<span style="margin-top:4px; font-size:13px; font-weight:600; color:#b6f500;">Visit contentintel.in &#8599;</span>' : '');

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
      // touch has no hover, so the pipeline highlight was dead on phones
      card.addEventListener('touchstart', focusNode, { passive: true });
      wrap.appendChild(card);
    });
  });
})();
"""


# ── 06 · Experience detail ───────────────────────────────────────────────────
# The star chart alone carried no substance. This sits under it: real logos,
# real dates, and the actual scope from the resume. Click a card to expand.
EXPERIENCE = [
    {"slug": "mirae", "name": "Mirae Asset Capital Markets", "role": "Design Studio Lead",
     "place": "Mumbai", "dates": "Oct 2025 — Present", "logo": "__MIRAE__", "now": True,
     "lead": "Own the end-to-end creative function — brand films, product demos, podcasts, performance creatives, newsletters and landing pages.",
     "points": [
        "Produce event-ready films from script and use-case inputs: sit in the briefing, build the storyboard, then shoot and cut the final piece.",
        "Combine screen recordings, product demos, graphics and callouts with synced VO, subtitles and captions — exported for event screens, web and social.",
        "Built custom AI automation for podcast and social editing, cutting a full day of manual work to roughly 30 minutes.",
        "Automated 60–70% of daily design production with AI-assisted and templated workflows, raising throughput without adding headcount.",
        "Lead UI/UX for app and web journeys, and maintain the design system across platforms.",
     ]},
    {"slug": "wealthy", "name": "Wealthy", "role": "Associate Creative Head",
     "place": "Bengaluru", "dates": "Apr 2022 — Sep 2025", "logo": "__WEALTHY__", "now": False,
     "lead": "Led video and design across YouTube, Instagram, LinkedIn, Facebook and Twitter under one identity.",
     "points": [
        "Directed professional shoots — talking heads, explainers, reels, partner testimonials — running lighting, camera and sound.",
        "Conceptualised and launched Bulls Eye, a weekly stock-market publication adopted across the investor and advisor network.",
        "Led UX/UI for the internal CRM dashboard, improving usability and workflow efficiency.",
        "Ran Welocity, the company's largest event, from content production through logistics and live delivery.",
     ]},
    {"slug": "unacademy", "name": "Unacademy", "role": "Studio Operations Specialist",
     "place": "Bengaluru", "dates": "Dec 2019 — Mar 2022", "logo": "__UNACADEMY__", "now": False,
     "lead": "Led a team of editors producing 2,000+ educational videos, contributing to 1M+ new YouTube subscribers in a single month.",
     "points": [
        "Helped grow and optimise 100+ channels including Unacademy JEE, NEET and Let's Crack UPSC CSE, with daily quality audits at scale.",
        "Designed studio setups for 150+ channels and re-engineered workflows — productivity up 25%, output up 35%.",
        "Collaborated with 100+ creators on production standards and delivery.",
     ]},
]

# Software actually used, grouped by where it sits in the job. Real brand marks
# come from simple-icons (CC0); the five with no mark available fall back to a
# monogram tile. "Growth" is gone: YouTube SEO and Meta Business Suite are
# channels, not tools.
#   name, icon-key (None -> monogram), monogram, ink, background
STACK = [
    ("Edit & post", [
        ("Premiere Pro",    "premiere",     "Pr",  "#9999FF", "#2A0634"),
        ("After Effects",   "aftereffects", "Ae",  "#9999FF", "#00005B"),
        ("DaVinci Resolve", "resolve",      "Dr",  "#E4E9F2", "#1C2530"),
        ("Final Cut Pro",   None,           "Fc",  "#D8D8DD", "#26262B"),
        ("OBS Studio",      "obs",          "OBS", "#FFFFFF", "#302E31"),
    ]),
    ("Design", [
        ("Figma",       "__figma__",   "Fg", "#FFFFFF", "#1E1E1E"),
        ("Photoshop",   "photoshop",   "Ps", "#31A8FF", "#001E36"),
        ("Illustrator", "illustrator", "Ai", "#FF9A00", "#330000"),
        ("Lightroom",   "lightroom",   "Lr", "#31A8FF", "#001E36"),
    ]),
    ("AI", [
        ("Claude",     "claude",     "C",  "#FFFFFF", "#D97757"),
        ("ChatGPT",    "chatgpt",    "G",  "#FFFFFF", "#10A37F"),
        ("Higgsfield", None,         "HF", "#B6F500", "#101418"),
        ("Runway",     None,         "R",  "#FFFFFF", "#0B0B0B"),
        ("MidJourney", None,         "MJ", "#FFFFFF", "#1C1C22"),
        ("HeyGen",     None,         "H",  "#FFFFFF", "#6C4CF1"),
        ("ElevenLabs", "elevenlabs", "11", "#FFFFFF", "#0A0A0A"),
    ]),
]

FIGMA_MARK = (
    '<svg viewBox="0 0 38 57" width="17" height="26" style="display:block;">'
    '<path d="M19 28.5a9.5 9.5 0 1 1 9.5 9.5A9.5 9.5 0 0 1 19 28.5z" fill="#1ABCFE"/>'
    '<path d="M0 47.5A9.5 9.5 0 0 1 9.5 38H19v9.5a9.5 9.5 0 0 1-19 0z" fill="#0ACF83"/>'
    '<path d="M19 0v19h9.5a9.5 9.5 0 0 0 0-19H19z" fill="#FF7262"/>'
    '<path d="M0 9.5A9.5 9.5 0 0 0 9.5 19H19V0H9.5A9.5 9.5 0 0 0 0 9.5z" fill="#F24E1E"/>'
    '<path d="M0 28.5A9.5 9.5 0 0 0 9.5 38H19V19H9.5A9.5 9.5 0 0 0 0 28.5z" fill="#A259FF"/>'
    "</svg>"
)

EXPERIENCE_BLOCK = """
<div data-vbexp style="max-width:1240px; margin:clamp(34px,5vh,60px) auto 0; display:grid; grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr)); gap:clamp(14px,1.8vw,22px);"></div>
"""

STACK_BLOCK = """
<div style="max-width:1240px; margin:clamp(30px,5vh,56px) auto 0; padding-top:clamp(24px,4vh,40px); border-top:1px solid rgba(255,255,255,.1);">
  <span style="display:block; font-size:10.5px; font-weight:700; letter-spacing:.18em; text-transform:uppercase; color:#5d6e8e; margin-bottom:20px;">What I work in</span>
  <div data-vbstack style="display:grid; grid-template-columns:repeat(auto-fit,minmax(min(100%,220px),1fr)); gap:clamp(18px,2.4vw,34px);"></div>
</div>
"""

EXP_SCRIPT = """
(function () {
  "use strict";
  var EXP = __EXPDATA__, STACK = __STACKDATA__, FIGMA = __FIGMAMARK__;
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
      var card = document.createElement('div');
      card.setAttribute('data-exp', e.slug);
      card.setAttribute('data-cursor', 'Read');
      card.style.cssText =
        'display:flex; flex-direction:column; gap:14px; padding:24px 22px; border-radius:16px; cursor:pointer; ' +
        'border:1px solid ' + (e.now ? 'rgba(182,245,0,.32)' : 'rgba(255,255,255,.1)') + '; ' +
        'background:' + (e.now ? 'rgba(182,245,0,.05)' : 'rgba(255,255,255,.035)') + '; ' +
        'transition:border-color .4s ease, transform .45s cubic-bezier(.2,.7,.3,1); ' +
        'opacity:0; transform:translateY(24px);';
      var bullets = e.points.map(function (t) {
        return '<li style="position:relative; padding-left:16px; margin-top:9px; font-size:13px; line-height:1.6; color:#8da0c4; list-style:none;">' +
               '<span style="position:absolute; left:0; top:8px; width:5px; height:5px; border-radius:50%; background:' + (e.now ? '#b6f500' : '#7fd4ff') + ';"></span>' + t + '</li>';
      }).join('');
      card.innerHTML =
        '<span style="display:flex; align-items:center; gap:13px;">' +
          '<span style="width:52px; height:52px; border-radius:12px; background:#fff; display:flex; align-items:center; justify-content:center; padding:8px; flex:0 0 auto;">' +
            '<img src="' + e.logo + '" alt="' + e.name + '" style="max-width:100%; max-height:100%; object-fit:contain; display:block;">' +
          '</span>' +
          '<span style="display:flex; flex-direction:column; gap:3px; min-width:0;">' +
            '<span style="font-family:\\'Space Grotesk\\',sans-serif; font-size:16.5px; font-weight:600; letter-spacing:-.02em; color:#f6f9ff;">' + e.name + '</span>' +
            '<span style="font-size:11.5px; letter-spacing:.04em; color:' + (e.now ? '#b6f500' : '#5d6e8e') + ';">' + e.dates + ' · ' + e.place + '</span>' +
          '</span>' +
        '</span>' +
        '<span style="font-family:\\'Space Grotesk\\',sans-serif; font-size:13.5px; font-weight:600; color:#cfe0ff;">' + e.role + '</span>' +
        '<span style="font-size:13.5px; line-height:1.62; color:#8da0c4;">' + e.lead + '</span>' +
        '<ul data-exp-more style="max-height:0; overflow:hidden; transition:max-height .55s cubic-bezier(.2,.7,.3,1); margin:0; padding:0;">' + bullets + '</ul>' +
        '<span data-exp-toggle style="font-size:12px; font-weight:600; color:' + (e.now ? '#b6f500' : '#7fd4ff') + ';">Read the detail +</span>';

      var open = false;
      card.addEventListener('click', function () {
        open = !open;
        var ul = card.querySelector('[data-exp-more]');
        var tg = card.querySelector('[data-exp-toggle]');
        ul.style.maxHeight = open ? ul.scrollHeight + 'px' : '0';
        tg.textContent = open ? 'Close \\u2212' : 'Read the detail +';
      });
      card.addEventListener('mouseenter', function () {
        card.style.transform = 'translateY(-5px)';
        card.style.borderColor = 'rgba(182,245,0,.5)';
      });
      card.addEventListener('mouseleave', function () {
        card.style.transform = 'none';
        card.style.borderColor = e.now ? 'rgba(182,245,0,.32)' : 'rgba(255,255,255,.1)';
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
        '<span style="display:block; font-family:\\'Space Grotesk\\',sans-serif; font-size:13px; font-weight:600; color:#b6f500; margin-bottom:14px;">' + g[0] + '</span>' +
        '<span style="display:flex; flex-wrap:wrap; gap:8px;">' +
          g[1].map(function (t) {
            var name = t[0], svg = t[1], mono = t[2], ink = t[3], bg = t[4];
            var badge = svg
              ? svg
              : '<span style="font-family:\\'Space Grotesk\\',sans-serif; font-size:' + (mono.length > 2 ? 9 : 12) + 'px; font-weight:700; letter-spacing:.01em; color:' + ink + ';">' + mono + '</span>';
            return '<span data-sw style="display:inline-flex; align-items:center; gap:9px; padding:6px 13px 6px 6px; border:1px solid rgba(255,255,255,.12); border-radius:100px; cursor:default; transition:border-color .35s ease, transform .35s cubic-bezier(.2,.7,.3,1), background .35s ease;">' +
                     '<span style="width:28px; height:28px; border-radius:8px; background:' + bg + '; display:flex; align-items:center; justify-content:center; flex:0 0 auto;">' + badge + '</span>' +
                     '<span style="font-size:12.5px; color:#cfe0ff; white-space:nowrap;">' + name + '</span>' +
                   '</span>';
          }).join('') +
        '</span>' +
      '</div>';
    }).join('');

    document.querySelectorAll('[data-sw]').forEach(function (chip) {
      chip.addEventListener('mouseenter', function () {
        chip.style.borderColor = 'rgba(182,245,0,.5)';
        chip.style.background = 'rgba(182,245,0,.06)';
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
