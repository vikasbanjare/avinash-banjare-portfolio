"""Design tokens for Avinash's build, and the re-inking pass that applies them.

The AI Flow bundle hard-codes aifloh's lime-on-navy palette in ~900 inline
styles, a Three.js scene and the light-mode toggle's colour table. Rather than
touch each one, rebuild.py runs `recolor()` over the finished template and over
every injected script: each old colour becomes its warm-charcoal / amber / teal
counterpart, in every textual form the page uses (#hex, rgb(), rgba(), and the
"rgb(r, g, b)" strings the theme toggle compares computed styles against).

New components should use the NEW tokens directly (right-hand side below).
"""
import re

# ── the tokens (new palette) ────────────────────────────────────────────────
BG = "#0b0908"            # page background (warm black)
BG_MENU = "#100d0b"       # menu / overlays
PANEL = "#161210"         # cards, stills
PANEL_2 = "#1b1613"
TEXT = "#faf7f2"          # display
BODY = "#efe9e1"          # body
MUTED = "#a0958a"         # secondary body — 6.7:1 on BG
FAINT = "#736a61"         # eyebrows / hairline labels — 3.8:1, never under 14px body copy
ACCENT = "#ffb020"        # amber: ink + CTA (was lime)
ACCENT_HOVER = "#ffc75c"
ON_ACCENT = "#1c1200"     # text on amber
TEAL = "#1fb2a0"          # glows, wires (was #2f6bff)
TEAL_LIGHT = "#5ee6d0"    # design nodes (was #7fd4ff)
FLAME = "#ff7a45"         # liftoff label (was #ff9d3d)

# ── old → new, hex ──────────────────────────────────────────────────────────
MAP = {
    # navy blacks → warm charcoals (lightness preserved)
    "#04060d": BG, "#04060f": "#0c0a09", "#03050b": "#080706", "#060912": "#0f0c0a",
    "#060a14": BG_MENU, "#070b16": "#120e0c", "#070d1c": "#151110", "#080d1a": PANEL,
    "#071026": "#191411", "#0a1124": "#1a1512", "#0a1226": PANEL_2, "#0c1736": "#12211f",
    "#131a30": "#1f1a17", "#1b2b4d": "#1c3330", "#243357": "#2c2521", "#0d1f16": "#231a0c",
    # blues → teals
    "#0052cc": "#0f7a6c", "#0a4cc0": "#0c6b5e", "#13409a": "#0f5a50", "#1b3b86": "#15514a",
    "#1f5fd6": "#159c8a", "#3d6bd6": "#2aa896", "#2f6bff": TEAL, "#7fd4ff": TEAL_LIGHT,
    "#8fb4ff": "#7fe0d0", "#5b7fa8": "#7a8f8b",
    # blue-tinted greys and whites → warm
    "#f6f9ff": TEXT, "#f3f7ff": "#f6f2ec", "#f0f5ff": "#f3eee6", "#eaf0ff": BODY,
    "#dbe6ff": "#e6ddd1", "#cfe0ff": "#dccfc0", "#c9d5ee": "#d3c9bd", "#c2cee6": "#cdc3b7",
    "#a9bcdd": "#b5aa9d", "#9fb6e6": "#b0a597", "#9fb4e0": "#ada294", "#9fb0d0": "#a89e91",
    "#8da0c4": MUTED, "#6f7f9e": "#7e756c", "#5d6e8e": FAINT, "#f4f6fb": "#faf7f2",
    # lime → amber
    "#b6f500": ACCENT, "#cbff3d": ACCENT_HOVER, "#06140a": ON_ACCENT, "#ff9d3d": FLAME,
}

# triples that only ever appear as rgb()/rgba() — panels, the theme table's
# light-mode targets, and the lime derivatives the toggle uses
RGB_ONLY = {
    (9, 14, 28): (22, 18, 16), (3, 5, 12): (8, 7, 6), (4, 8, 18): (13, 10, 9),
    (12, 22, 44): (28, 23, 20), (8, 12, 24): (20, 16, 14), (6, 10, 20): (16, 13, 11),
    (7, 11, 22): (18, 14, 12), (6, 9, 18): (15, 12, 10), (10, 17, 36): (26, 21, 18),
    (11, 19, 41): (27, 22, 19), (7, 13, 28): (21, 17, 16), (8, 13, 26): (22, 18, 16),
    (10, 15, 30): (24, 20, 17), (12, 18, 34): (28, 23, 20), (16, 25, 46): (36, 30, 26),
    (28, 39, 64): (52, 44, 38), (30, 45, 80): (56, 46, 40), (42, 54, 82): (70, 60, 52),
    (61, 76, 110): (92, 82, 72), (70, 85, 122): (104, 93, 82), (72, 87, 124): (106, 95, 84),
    (86, 102, 140): (120, 108, 96), (102, 115, 146): (134, 122, 110), (108, 120, 150): (140, 128, 116),
    (244, 246, 251): (250, 247, 242), (240, 243, 249): (246, 242, 236), (238, 241, 248): (244, 239, 232),
    (230, 235, 246): (237, 231, 222), (246, 248, 252): (250, 248, 244), (233, 237, 245): (240, 235, 227),
    (247, 249, 253): (251, 249, 245),
    (140, 190, 0): (204, 133, 10), (96, 134, 0): (166, 98, 0), (235, 250, 190): (255, 236, 196),
    (20, 32, 10): (28, 18, 0),
}


def _rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


RGB = dict(RGB_ONLY)
RGB.update({_rgb(o): _rgb(n) for o, n in MAP.items()})
_HEX = re.compile(r"#([0-9a-fA-F]{6})\b")
_RGB = re.compile(r"(rgba?\(\s*)(\d{1,3})(\s*,\s*)(\d{1,3})(\s*,\s*)(\d{1,3})")


def recolor(text):
    """Re-ink every old palette colour in `text`; anything not in the map is untouched."""
    text = _HEX.sub(lambda m: MAP.get("#" + m.group(1).lower(), m.group(0)), text)

    def rgb(m):
        old = (int(m.group(2)), int(m.group(4)), int(m.group(6)))
        new = RGB.get(old)
        if not new:
            return m.group(0)
        return m.group(1) + str(new[0]) + m.group(3) + str(new[1]) + m.group(5) + str(new[2])
    return _RGB.sub(rgb, text)


if __name__ == "__main__":   # smallest check that fails if the pass breaks
    assert recolor("color:#B6F500; box-shadow:0 0 10px rgba(182,245,0,.3); rgb(4, 6, 13)") == \
        f"color:{ACCENT}; box-shadow:0 0 10px rgba(255,176,32,.3); rgb(11, 9, 8)"
    assert recolor("#fff #000 rgba(255,255,255,.1) #9999FF") == "#fff #000 rgba(255,255,255,.1) #9999FF"
    print("palette ok:", len(MAP), "hex +", len(RGB_ONLY), "rgb-only pairs")
