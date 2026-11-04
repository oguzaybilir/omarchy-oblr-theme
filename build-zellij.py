#!/usr/bin/env python3
"""Render oblr/zellij.kdl from colors.toml using the omarchy-zellij-theme template.

The stock template puts emphasis text on a light color7 ribbon, which hides
oblr's muted hues, so ribbons and selected text get dark backgrounds here.
Re-run after editing colors.toml, then `omarchy theme set oblr`.
Needs ~/.config/omarchy/themed/zellij.kdl.tpl from omarchy-zellij-theme.
"""
import os, re, subprocess

theme = os.path.expanduser("~/.config/omarchy/themes/oblr")
tpl = os.path.expanduser("~/.config/omarchy/themed/zellij.kdl.tpl")

out = subprocess.run(["omarchy-theme-color", "--file", f"{theme}/colors.toml", "--all"],
                     capture_output=True, text=True, check=True).stdout
c = dict(line.split("\t", 1) for line in out.splitlines() if "\t" in line)
rgb = lambda k: ",".join(str(int(c[k].lstrip("#")[i:i + 2], 16)) for i in (0, 2, 4))

def sub(m):
    key = m.group(1)
    if key not in c:
        raise SystemExit(f"unknown color key in template: {key}")
    return rgb(key)

s = re.sub(r"\{\{\s*([a-z0-9_]+)_rgb\s*\}\}", sub, open(tpl).read())
assert "{{" not in s, "unrendered template token"

overrides = {
    "text_selected": dict(base="bright_foreground", background="#2a2b2b",
                          emphasis_0="bright_yellow", emphasis_1="bright_blue",
                          emphasis_2="bright_green", emphasis_3="bright_magenta"),
    "ribbon_selected": dict(base="bright_foreground", background="accent",
                            emphasis_0="bright_foreground", emphasis_1="bright_yellow",
                            emphasis_2="bright_foreground", emphasis_3="bright_foreground"),
    "ribbon_unselected": dict(base="foreground", background="#1f2020",
                              emphasis_0="bright_red", emphasis_1="bright_foreground",
                              emphasis_2="bright_blue", emphasis_3="bright_magenta"),
}
for block, fields in overrides.items():
    def patch(m):
        b = m.group(0)
        for field, val in fields.items():
            v = rgb(val) if not val.startswith("#") else ",".join(str(int(val[i:i + 2], 16)) for i in (1, 3, 5))
            b, n = re.subn(rf"(\n\s+{field} ).*", rf"\g<1>{v}", b, count=1)
            assert n == 1, (block, field)
        return b
    s, n = re.subn(rf"\n        {block} \{{\n.*?\n        \}}", patch, s, flags=re.S)
    assert n == 1, block

open(f"{theme}/zellij.kdl", "w").write(s)
print(f"wrote {theme}/zellij.kdl")
