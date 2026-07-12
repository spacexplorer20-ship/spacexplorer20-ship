"""
build_stats_card.py — regenerates dark_mode.svg and light_mode.svg from the
config below.

WHY THIS EXISTS
----------------
The raw SVG uses absolute y="..." coordinates for every line. If you hand-edit
the SVG and delete a section, every line below it stays exactly where it was —
you'd get a blank gap instead of the layout closing up. This script removes
that problem: everything below is described as data (not coordinates), and
the y-position of every row is computed automatically when you run it.

HOW TO EDIT
-----------
1. Add / remove / reorder entries in CUSTOM_SECTIONS below.
   - Each section is (header_or_None, [ (label, value), ... ]).
   - `header=None` means "no header line" (used for the top intro block).
   - To delete a whole section (e.g. "Skills"), just delete its tuple from
     the list.
   - To add a field, add a ("Label", "Value") tuple to a section's list.
2. The "GitHub Stats" block at the bottom is generated separately (function
   `github_stats_section`) because its fields are filled in automatically by
   today.py via element ids (commit_data, star_data, etc.) — don't rename
   those ids or today.py's justify_format() will silently stop updating them.
3. Run:
       pip install --break-system-packages -r cache/requirements.txt  # if lxml/etc missing is not needed here, just stdlib
       python build_stats_card.py
   This overwrites dark_mode.svg and light_mode.svg in the current directory.
4. Commit the regenerated files.

today.py does NOT need to change — it finds elements by id regardless of
where this script places them.
"""

import textwrap

WIDTH = 760
PAD_X = 30
PAD_TOP = 46          # y of the first content row below the title
ROW_H = 20             # vertical spacing between rows
SECTION_GAP = 30       # extra spacing consumed by a section header row
BOTTOM_PAD = 30
VALUE_X = 300          # fixed column where values start (dot leaders fill the gap)
CHAR_W = 7.6           # approx monospace char width at this font-size, used only for dot-leader math
TITLE = "spacexplorer20-ship"

# ---------------------------------------------------------------------------
# EDIT BELOW: add/remove sections or fields freely.
# ---------------------------------------------------------------------------

CUSTOM_SECTIONS = [
    (None, [
        ("Role", "Associate Engineer Hire, Accenture (App Dev Primer)"),
        ("University", "Jadavpur University (Civil Eng.) · IIT Madras (Research)"),
        ("Focus", "KG-RAG, PINNs, MLOps, HEC-RAS"),
        ("Member since", {"dynamic_id": "age_data", "placeholder": "-- years, -- months, -- days"}),
    ]),
    ("Skills", [
        ("Languages.Research", "Python, Cypher"),
        ("Languages.Systems", "C++, Java, GDScript, JavaScript"),
        ("Tools.Game Dev", "Godot 4, RPG Maker MZ, Kaboom.js"),
        ("Interests", "AR/VR/XR, Football (UCL)"),
    ]),
    # ("Contact", [
    #     ("Email", "YOUR_EMAIL"),
    #     ("LinkedIn", "YOUR_LINKEDIN"),
    #     ("Portfolio", "YOUR_PORTFOLIO_URL"),
    # ]),
]

PALETTES = {
    "dark": {
        "bg": "#0d1117",
        "border": "#30363d",
        "title": "#58A6FF",
        "key": "#58A6FF",
        "value": "#e6edf3",
        "cc": "#4b5563",
        "hdr": "#BC8CFF",
        "add": "#3fb950",
        "del": "#f85149",
        "text": "#c9d1d9",
    },
    "light": {
        "bg": "#ffffff",
        "border": "#d0d7de",
        "title": "#0969da",
        "key": "#0969da",
        "value": "#1f2328",
        "cc": "#8c959f",
        "hdr": "#8250df",
        "add": "#1a7f37",
        "del": "#cf222e",
        "text": "#1f2328",
    },
}

# ---------------------------------------------------------------------------
# Rendering — you shouldn't need to touch anything below this line.
# ---------------------------------------------------------------------------


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def dot_leader(label_end_x, target_x=VALUE_X):
    gap = target_x - label_end_x
    n = max(1, int(gap / CHAR_W))
    return " " + ("." * n) + " "


def field_row(y, label, value):
    """value is either a plain string, or {"dynamic_id": ..., "placeholder": ...}"""
    label_tag = f'<tspan class="key">{esc(label)}</tspan>:'
    label_end_x = PAD_X + 2 + (len(label) + 1) * CHAR_W  # rough estimate incl ". " prefix + label + ":"

    if isinstance(value, dict):
        dyn_id = value["dynamic_id"]
        placeholder = esc(value["placeholder"])
        dots_span = f'<tspan class="cc" id="{dyn_id}_dots">{dot_leader(label_end_x)}</tspan>'
        value_span = f'<tspan class="value" id="{dyn_id}">{placeholder}</tspan>'
    else:
        dots_span = f'<tspan class="cc">{dot_leader(label_end_x)}</tspan>'
        value_span = f'<tspan class="value">{esc(value)}</tspan>'

    return (
        f'<tspan x="{PAD_X}" y="{y}" class="cc">. </tspan>{label_tag}'
        f'{dots_span}{value_span}\n'
    )


def section_header_row(y, header):
    dash_len = 82  # number of box-drawing dashes after the header text
    return (
        f'<tspan x="{PAD_X}" y="{y}" class="hdr">- {esc(header)}</tspan>'
        f'<tspan class="cc"> {"─" * dash_len}</tspan>\n'
    )


def github_stats_section(y):
    """Fixed block — field ids here are read by today.py, do not rename."""
    lines = []
    lines.append(section_header_row(y, "GitHub Stats"))
    y += ROW_H
    lines.append(
        f'<tspan x="{PAD_X}" y="{y}" class="cc">. </tspan>'
        f'<tspan class="key">Repos</tspan>:<tspan class="cc" id="repo_data_dots"> .... </tspan>'
        f'<tspan class="value" id="repo_data">0</tspan> '
        f'{{<tspan class="key">Contributed</tspan>: <tspan class="value" id="contrib_data">0</tspan>}} | '
        f'<tspan class="key">Stars</tspan>:<tspan class="cc" id="star_data_dots"> ............ </tspan>'
        f'<tspan class="value" id="star_data">0</tspan>\n'
    )
    y += ROW_H
    lines.append(
        f'<tspan x="{PAD_X}" y="{y}" class="cc">. </tspan>'
        f'<tspan class="key">Commits</tspan>:<tspan class="cc" id="commit_data_dots"> .................... </tspan>'
        f'<tspan class="value" id="commit_data">0</tspan> | '
        f'<tspan class="key">Followers</tspan>:<tspan class="cc" id="follower_data_dots"> ........ </tspan>'
        f'<tspan class="value" id="follower_data">0</tspan>\n'
    )
    y += ROW_H
    lines.append(
        f'<tspan x="{PAD_X}" y="{y}" class="cc">. </tspan>'
        f'<tspan class="key">Lines of Code on GitHub</tspan>:<tspan class="cc" id="loc_data_dots">. </tspan>'
        f'<tspan class="value" id="loc_data">0</tspan> ( '
        f'<tspan class="addColor" id="loc_add">0</tspan><tspan class="addColor">++</tspan>, '
        f'<tspan id="loc_del_dots"> </tspan><tspan class="delColor" id="loc_del">0</tspan>'
        f'<tspan class="delColor">--</tspan> )\n'
    )
    return "".join(lines), y


def build_svg(palette_name):
    p = PALETTES[palette_name]
    body = []
    y = PAD_TOP

    for header, fields in CUSTOM_SECTIONS:
        if header is not None:
            body.append(section_header_row(y, header))
            y += ROW_H
        for label, value in fields:
            body.append(field_row(y, label, value))
            y += ROW_H
        y += SECTION_GAP - ROW_H  # breathing room before next section

    stats_block, y_after_stats = github_stats_section(y)
    body.append(stats_block)
    y = y_after_stats

    height = y + BOTTOM_PAD

    svg = f'''<?xml version='1.0' encoding='UTF-8'?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}" font-family="Fira Code,ConsolasFallback,Consolas,monospace" font-size="15px">
<style>
@font-face {{
src: local('Consolas'), local('Consolas Bold');
font-family: 'ConsolasFallback';
font-display: swap;
-webkit-size-adjust: 109%;
size-adjust: 109%;
}}
.key {{fill: {p["key"]};}}
.value {{fill: {p["value"]};}}
.addColor {{fill: {p["add"]};}}
.delColor {{fill: {p["del"]};}}
.cc {{fill: {p["cc"]};}}
.hdr {{fill: {p["hdr"]};}}
.title {{fill: {p["title"]}; font-weight: 600;}}
text, tspan {{white-space: pre;}}
</style>
<rect width="{WIDTH}" height="{height}" fill="{p["bg"]}" rx="15"/>
<rect x="1" y="1" width="{WIDTH - 2}" height="{height - 2}" fill="none" stroke="{p["border"]}" stroke-width="1" rx="14"/>

<text x="{PAD_X}" y="35" class="title" font-size="18px">{esc(TITLE)}</text>
<text x="0" y="0" fill="{p["text"]}">
<tspan x="{PAD_X}" y="{PAD_TOP - 16}" class="cc">{"─" * 96}</tspan>
{"".join(body)}</text>
</svg>
'''
    return svg


if __name__ == "__main__":
    for mode in ("dark", "light"):
        svg = build_svg(mode)
        filename = f"{mode}_mode.svg"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"wrote {filename}")
