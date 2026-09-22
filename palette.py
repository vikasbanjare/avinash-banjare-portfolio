"""Colour themes, and the pass that turns the bundle's hard-coded colours into CSS variables.

The AI Flow bundle hard-codes aifloh's palette in ~900 inline styles, a handful
of JS style assignments and the hero's shader uniforms. `tokenize()` rewrites
every one of those colours to a role variable — `var(--accent)`,
`rgba(var(--accent-rgb),.3)` — so the whole page re-inks the instant
`<html data-theme>` changes. The only consumer that needs real colours is
Three.js: its `THREE.Color('#…')` literals and the orbit items' `col:` values
get the DEFAULT theme's hex at build time, and parts.THEME_SCRIPT re-sets those
uniforms at runtime when the visitor picks another theme.

New components should use the variables directly: var(--accent), var(--panel),
rgba(var(--glow-rgb),.4) and so on. Roles:

  bg / bg-2 / panel / panel-2 / panel-3   backgrounds, light to dark chrome
  hero-top / hero-fill                     the hero nebula's shader colours
  text / body / body-2 / muted / faint     type, display to hairline labels
  accent / accent-hover / on-accent        ink + CTA and the text on it
  glow / glow-2 / glow-deep                wires, dots, planet, section glows
  flame                                    the launch pad's LIFTOFF label
"""
import re

ROLES = ("bg", "bg-2", "panel", "panel-2", "panel-3", "hero-top", "hero-fill",
         "text", "body", "body-2", "muted", "faint",
         "accent", "accent-hover", "on-accent", "glow", "glow-2", "glow-deep", "flame")

# Five dark themes. Every accent clears 4.5:1 on its background and every
# on-accent clears 4.5:1 on the accent; faint labels are ~3.8:1 like the original.
# Electric is the default: #004fff glows, a lighter #4d86ff where blue has to be read.
THEMES = {
    "electric": {"name": "Electric", "bg": "#05070f", "bg-2": "#080b16", "panel": "#0f1526", "panel-2": "#141b33",
                 "panel-3": "#1e2848", "hero-top": "#0a1f6b", "hero-fill": "#12275c",
                 "text": "#f2f5ff", "body": "#e3e9fb", "body-2": "#c3cdea", "muted": "#93a0c4", "faint": "#66728f",
                 "accent": "#4d86ff", "accent-hover": "#7aa6ff", "on-accent": "#04102e",
                 "glow": "#004fff", "glow-2": "#8db3ff", "glow-deep": "#0033b3", "flame": "#ff9a3d"},
    "violet": {"name": "Violet", "bg": "#0a0812", "bg-2": "#0e0b18", "panel": "#171226", "panel-2": "#1d1730",
               "panel-3": "#2a2340", "hero-top": "#1a1040", "hero-fill": "#2a1f4d",
               "text": "#f6f3ff", "body": "#ece7fa", "body-2": "#cfc6e8", "muted": "#a196bd", "faint": "#6f6688",
               "accent": "#a58bff", "accent-hover": "#bca8ff", "on-accent": "#150a2e",
               "glow": "#ff4fa3", "glow-2": "#ff9ad1", "glow-deep": "#b3167a", "flame": "#ff7a45"},
    "ember":  {"name": "Ember", "bg": "#0b0908", "bg-2": "#100d0b", "panel": "#161210", "panel-2": "#1b1613",
               "panel-3": "#2c2521", "hero-top": "#12211f", "hero-fill": "#1c3330",
               "text": "#faf7f2", "body": "#efe9e1", "body-2": "#dccfc0", "muted": "#a0958a", "faint": "#736a61",
               "accent": "#ffb020", "accent-hover": "#ffc75c", "on-accent": "#1c1200",
               "glow": "#1fb2a0", "glow-2": "#5ee6d0", "glow-deep": "#0f7a6c", "flame": "#ff7a45"},
    "mint":   {"name": "Mint", "bg": "#07090c", "bg-2": "#0b0e12", "panel": "#12181c", "panel-2": "#171f24",
               "panel-3": "#243035", "hero-top": "#0e2a2a", "hero-fill": "#1b3a3a",
               "text": "#f2f7f5", "body": "#e4ecea", "body-2": "#c3d0cc", "muted": "#93a5a0", "faint": "#66756f",
               "accent": "#5cf2c2", "accent-hover": "#8cf7d6", "on-accent": "#04201a",
               "glow": "#7c5cff", "glow-2": "#b7a6ff", "glow-deep": "#4a2fd6", "flame": "#ff6a4d"},
    "coral":  {"name": "Coral", "bg": "#0c0a0a", "bg-2": "#110d0d", "panel": "#1a1414", "panel-2": "#201818",
               "panel-3": "#302424", "hero-top": "#2a1614", "hero-fill": "#3a1f1c",
               "text": "#faf4f2", "body": "#efe6e3", "body-2": "#d4c8c4", "muted": "#a4958f", "faint": "#756a66",
               "accent": "#ff6a4d", "accent-hover": "#ff8a72", "on-accent": "#1c0803",
               "glow": "#38d1f0", "glow-2": "#8ae6f7", "glow-deep": "#1487a3", "flame": "#ffd34d"},
}
DEFAULT = "electric"

# ── aifloh's colours → roles ────────────────────────────────────────────────
ROLE_OF = {
    # navy blacks
    "#04060d": "bg", "#04060f": "bg", "#03050b": "bg", "#060912": "bg-2", "#060a14": "bg-2", "#070b16": "bg-2",
    "#070d1c": "panel", "#080d1a": "panel", "#071026": "panel", "#0a1124": "panel-2", "#0a1226": "panel-2",
    "#131a30": "panel-2", "#0d1f16": "panel-2", "#243357": "panel-3", "#0c1736": "hero-top", "#1b2b4d": "hero-fill",
    # blues
    "#0052cc": "glow-deep", "#0a4cc0": "glow-deep", "#13409a": "glow-deep", "#1b3b86": "glow-deep",
    "#1f5fd6": "glow", "#3d6bd6": "glow", "#2f6bff": "glow", "#7fd4ff": "glow-2", "#8fb4ff": "glow-2",
    "#5b7fa8": "muted",
    # blue-tinted greys and whites
    "#f6f9ff": "text", "#f3f7ff": "text", "#f0f5ff": "text", "#f4f6fb": "text", "#eaf0ff": "body",
    "#dbe6ff": "body-2", "#cfe0ff": "body-2", "#c9d5ee": "body-2", "#c2cee6": "body-2",
    "#a9bcdd": "muted", "#9fb6e6": "muted", "#9fb4e0": "muted", "#9fb0d0": "muted", "#8da0c4": "muted",
    "#6f7f9e": "faint", "#5d6e8e": "faint",
    # lime
    "#b6f500": "accent", "#cbff3d": "accent-hover", "#06140a": "on-accent", "#ff9d3d": "flame",
}
# triples that only ever appear inside rgb()/rgba(): frosted panels and lime derivatives
_RGB_ROLE = {
    (9, 14, 28): "panel", (3, 5, 12): "bg", (4, 8, 18): "bg", (12, 22, 44): "panel-2", (8, 12, 24): "bg-2",
    (6, 10, 20): "bg-2", (7, 11, 22): "bg-2", (6, 9, 18): "bg-2", (10, 17, 36): "panel-2", (11, 19, 41): "panel-2",
    (7, 13, 28): "panel", (8, 13, 26): "panel",
    (140, 190, 0): "accent", (96, 134, 0): "accent", (235, 250, 190): "accent-hover", (20, 32, 10): "on-accent",
}


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


RGB_ROLE = dict(_RGB_ROLE)
RGB_ROLE.update({rgb(k): v for k, v in ROLE_OF.items()})

_HEX = re.compile(r"#([0-9a-fA-F]{6})\b")
_RGB = re.compile(r"(rgba?\()(\d{1,3}),(\d{1,3}),(\d{1,3})")          # no spaces: skips the dead light-mode table
_THREE = re.compile(r"THREE\.Color\('(#[0-9a-fA-F]{6})'\)")
_ORBIT = re.compile(r"col:\s*'(#[0-9a-fA-F]{6})'")


def tokenize(text, default=DEFAULT):
    """Rewrite every aifloh colour in `text` to its role variable. Three.js
    literals get the default theme's real hex instead (shaders cannot read CSS)."""
    T = THEMES[default]

    def literal(m):
        role = ROLE_OF.get(m.group(1).lower())
        return m.group(0).replace(m.group(1), T[role]) if role else m.group(0)
    text = _THREE.sub(literal, text)
    text = _ORBIT.sub(literal, text)

    def var(m):
        role = ROLE_OF.get("#" + m.group(1).lower())
        return f"var(--{role})" if role else m.group(0)
    text = _HEX.sub(var, text)

    def rgbvar(m):
        role = RGB_ROLE.get((int(m.group(2)), int(m.group(3)), int(m.group(4))))
        return f"{m.group(1)}var(--{role}-rgb)" if role else m.group(0)
    return _RGB.sub(rgbvar, text)


def _block(t):
    return "".join(f"--{r}:{t[r]};--{r}-rgb:{','.join(map(str, rgb(t[r])))};" for r in ROLES)


def theme_css():
    """One <style> with every theme: the default on :root, each theme under its data-theme."""
    css = ":root{" + _block(THEMES[DEFAULT]) + "}"
    for slug, t in THEMES.items():
        css += f':root[data-theme="{slug}"]{{' + _block(t) + "}"
    return "<style data-ab-themes>" + css + "</style>"


def theme_list():
    """What the picker script needs: slug, name and every role's hex."""
    return [{"slug": slug, "name": t["name"], "vars": {r: t[r] for r in ROLES}} for slug, t in THEMES.items()]


if __name__ == "__main__":   # the smallest checks that fail if the pass or the tables break
    for slug, t in THEMES.items():
        for r in ROLES:
            assert r in t, f"{slug} lacks {r}"
            assert t[r].lower() not in ROLE_OF, f"{slug}.{r} = {t[r]} collides with an aifloh colour"
    out = tokenize("color:#B6F500; box-shadow:0 0 10px rgba(182,245,0,.3); background:#04060d; "
                   "new THREE.Color('#0a4cc0'); col: '#7fd4ff'; rgb(4, 6, 13)")
    assert out == ("color:var(--accent); box-shadow:0 0 10px rgba(var(--accent-rgb),.3); background:var(--bg); "
                   f"new THREE.Color('{THEMES[DEFAULT]['glow-deep']}'); col: '{THEMES[DEFAULT]['glow-2']}'; rgb(4, 6, 13)"), out
    assert tokenize("#fff #000 rgba(255,255,255,.1) #9999FF") == "#fff #000 rgba(255,255,255,.1) #9999FF"
    assert theme_css().count(":root") == len(THEMES) + 1
    print(f"palette ok: {len(THEMES)} themes, {len(ROLE_OF)} hex + {len(_RGB_ROLE)} rgb-only mappings, default {DEFAULT}")
