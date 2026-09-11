#!/usr/bin/env python3
"""Generate the illustrated README from profile.json using Python's standard library.

Run: python3 scripts/render-profile.py
The existing animated header is maintained by render-profile-header.py.
No network, external fonts, JavaScript, or foreignObject is used in the SVGs.
"""

from html import escape
from pathlib import Path
import json
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "panels"
DATA = json.loads((ROOT / "profile.json").read_text(encoding="utf-8"))
INK, CARD, BORDER = "#151719", "#1b1f1d", "#353d32"
WHITE, MUTED, LIME, GOLD = "#f4f1e8", "#b9c0b2", "#d6f77a", "#e7be76"
FONT = "Arial, Helvetica, Apple SD Gothic Neo, Noto Sans KR, sans-serif"


def text_width(text, size, bold=False):
    """Conservative layout estimate, checked against actual SVG text in preview."""
    width = 0
    for char in text:
        if unicodedata.east_asian_width(char) in ("W", "F"):
            factor = 1.0
        elif char in "MW@%&":
            factor = .94
        elif char in "mw":
            factor = .82
        elif char in "ijlI.,:;'!| ":
            factor = .30
        elif char.isupper():
            factor = .72
        else:
            factor = .57
        width += factor * size
    return width * (1.03 if bold else 1)


def wrap(text, width, size, bold=False):
    lines, current = [], ""
    for word in text.split():
        trial = f"{current} {word}".strip()
        if current and text_width(trial, size, bold) > width:
            lines.append(current)
            current = word
        else:
            current = trial
    if current:
        lines.append(current)
    return lines


class Drawing:
    def __init__(self):
        self.parts = []

    def rect(self, x, y, width, height, fill=CARD, radius=12, stroke=None):
        border = f' stroke="{stroke}"' if stroke else ""
        self.parts.append(f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{radius}" fill="{fill}"{border}/>')

    def rule(self, x1, y, x2, color=BORDER):
        self.parts.append(f'<path d="M{x1} {y}H{x2}" fill="none" stroke="{color}"/>')

    def text(self, text, x, y, size=26, color=WHITE, bold=False, width=None, leading=1.42):
        lines = wrap(text, width, size, bold) if width else [text]
        for line in lines:
            extra = f' data-max-width="{width}"' if width else ""
            self.parts.append(f'<text x="{x}" y="{y + size * .84:.2f}" font-size="{size}" fill="{color}" font-weight="{700 if bold else 400}"{extra}>{escape(line)}</text>')
            y += size * leading
        return y

    def group(self, drawing, x, y):
        self.parts.append(f'<g transform="translate({x} {y})">{"".join(drawing.parts)}</g>')


class Panel(Drawing):
    def __init__(self, number, title, mobile, description, accent=LIME):
        super().__init__()
        self.mobile = mobile
        self.width = 600 if mobile else 1200
        self.pad = 32 if mobile else 60
        self.inner = self.width - self.pad * 2
        self.body = 28 if mobile else 26
        self.description = description
        self.title = title
        self.accent = accent
        self.text(f"{number:02d} / YEONOH PARK", self.pad, 36, 19, accent, True)
        self.rect(self.width - self.pad - 10, 40, 10, 10, accent, 0)
        y = self.text(title, self.pad, 80, 42 if mobile else 48, WHITE, True, self.inner)
        self.rule(self.pad, y + 12, self.width - self.pad)
        self.y = y + 44

    def paragraph(self, text, color=MUTED, size=None, bold=False, gap=24):
        self.y = self.text(text, self.pad, self.y, size or self.body, color, bold, self.inner) + gap

    def label(self, text):
        self.y = self.text(text, self.pad, self.y, 22, self.accent, True, self.inner) + 20

    def finish(self, name):
        height = round(self.y + self.pad)
        body = "\n".join(self.parts)
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{height}" viewBox="0 0 {self.width} {height}" role="img" aria-labelledby="title desc">
<title id="title">{escape(self.title)}</title>
<desc id="desc">{escape(self.description)}</desc>
<rect x=".5" y=".5" width="{self.width-1}" height="{height-1}" rx="20" fill="{INK}" stroke="{BORDER}"/>
<g font-family="{FONT}">{body}</g>
</svg>
'''
        (OUT / f"{name}{'-mobile' if self.mobile else ''}.svg").write_text(svg, encoding="utf-8")


def grid(panel, blocks, columns=2, gap=24):
    count = 1 if panel.mobile else columns
    width = (panel.inner - gap * (count - 1)) / count
    for offset in range(0, len(blocks), count):
        row = [build(width) for build in blocks[offset:offset+count]]
        row_height = max(height for _, height in row)
        for column, (drawing, height) in enumerate(row):
            drawing.parts[0] = drawing.parts[0].replace(f'height="{height}"', f'height="{row_height}"', 1)
            panel.group(drawing, panel.pad + column * (width + gap), panel.y)
        panel.y += row_height + gap


def block(label, detail, width, mobile, number=None):
    d = Drawing()
    inset, y = 26, 26
    available = width - inset * 2
    if number is not None:
        y = d.text(f"{number:02d}", inset, y, 44, LIME, True) + 14
    y = d.text(label, inset, y, 30, WHITE, True, available) + 12
    y = d.text(detail, inset, y, 27 if mobile else 25, MUTED, width=available) + 26
    d.parts.insert(0, f'<rect width="{width}" height="{y}" rx="12" fill="{CARD}" stroke="{BORDER}"/>')
    return d, y


def record(item, width, mobile):
    d = Drawing()
    inset, y = 28, 26
    available = width - inset * 2
    accent = LIME if item["status"] == "PUBLISHED" else GOLD
    y = d.text(item["status"], inset, y, 20, accent, True) + 16
    y = d.text(item["project"], inset, y, 34 if mobile else 32, WHITE, True, available) + 14
    for identifier in item["ids"]:
        y = d.text(identifier, inset, y, 25, accent, True, available) + 4
    if item["ids"]:
        y += 14
    y = d.text(item["description"], inset, y, 27 if mobile else 25, WHITE, width=available) + 18
    if item.get("note"):
        y = d.text(item["note"], inset, y, 24, MUTED, width=available) + 12
    y += 16
    d.parts.insert(0, f'<rect width="{width}" height="{y}" rx="12" fill="{CARD}" stroke="{BORDER}"/>')
    return d, y


def content_alt(name):
    data = DATA[name]
    if name == "about":
        return " ".join([data["intro"], data["focus"], "Interests: " + "; ".join(data["interests"]) + ".", *[r["label"] + ": " + r["detail"] + "." for r in data["roles"]]])
    if name == "research":
        return " ".join([data["scope"], *[m["value"] + " " + m["label"] + " (" + m["note"] + ")." for m in data["metrics"]], data["note"]])
    if name == "method":
        return " ".join(f'{i}. {s["label"]}. {s["detail"]}' for i,s in enumerate(data["steps"],1))
    if name in ("published", "coordinated"):
        return " ".join(" ".join([i["project"] + ".", ", ".join(i["ids"]), i["status"] + ".", i["description"], i["note"].rstrip(".") + "." if i.get("note") else ""]).strip() for i in data["items"])
    if name == "publication":
        return " ".join([data["award"] + ".", data["paper"] + ".", data["korean"] + ".", data["summary"], "Authors: " + data["authors"] + ".", data["venue"] + ".", data["competition"] + ".", data["date"] + ". Conference proceedings and program book."])
    if name == "background":
        return " ".join([*[" · ".join(filter(None, (e["period"], e["school"], e["detail"]))) + "." for e in data["education"]], *[h["year"] + ": " + "; ".join(h["items"]) + "." for h in data["honors"]]])
    return " ".join([data["purpose"] + ".", data["note"], data["email"]])


def render_about(mobile):
    data = DATA["about"]
    p = Panel(1, data["title"], mobile, content_alt("about"))
    p.paragraph(data["intro"], WHITE)
    p.paragraph(data["focus"], MUTED)
    p.label("RESEARCH INTERESTS")
    columns = 2 if mobile else 4
    width = (p.inner - 16 * (columns - 1)) / columns
    for index, interest in enumerate(data["interests"]):
        x = p.pad + (index % columns) * (width + 16)
        y = p.y + (index // columns) * 110
        p.rect(x, y, width, 94)
        p.text(interest, x+18, y+20, 25 if mobile else 23, LIME, True, width-36)
    p.y += (2 if mobile else 1) * 110 + 20
    p.label("COMMUNITY")
    grid(p, [lambda width, r=r: block(r["detail"], r["label"], width, mobile) for r in data["roles"][1:]])
    p.finish("about")


def render_research(mobile):
    data = DATA["research"]
    p = Panel(2, data["title"], mobile, content_alt("research"))
    p.paragraph(data["scope"])
    cols = 2 if mobile else 4
    gap = 20
    width = (p.inner - gap*(cols-1))/cols
    height = 236 if mobile else 226
    for i, metric in enumerate(data["metrics"]):
        x, y = p.pad+(i%cols)*(width+gap), p.y+(i//cols)*(height+gap)
        p.rect(x,y,width,height)
        p.text(metric["value"],x+22,y+20,76,LIME,True)
        yy = p.text(metric["label"],x+22,y+117,24,WHITE,True,width-44,1.28)+12
        p.text(metric["note"],x+22,yy,21,MUTED,False,width-44,1.3)
    p.y += (2 if mobile else 1)*(height+gap)+12
    p.paragraph(data["note"],size=24,gap=0)
    p.finish("research")


def render_method(mobile):
    p = Panel(3, DATA["method"]["title"], mobile, content_alt("method"))
    grid(p, [lambda width, step=step, i=i: block(step["label"],step["detail"],width,mobile,i) for i,step in enumerate(DATA["method"]["steps"],1)])
    p.finish("method")


def render_records(name, number, mobile):
    p = Panel(number,DATA[name]["title"],mobile,content_alt(name))
    grid(p,[lambda width,item=item: record(item,width,mobile) for item in DATA[name]["items"]])
    p.finish(name)


def render_publication(mobile):
    data = DATA["publication"]
    p = Panel(6,data["title"],mobile,content_alt("publication"),GOLD)
    p.paragraph("GOLD PRIZE",GOLD,60 if mobile else 78,True,16)
    p.paragraph(data["paper"],WHITE,36 if mobile else 44,True,24)
    p.paragraph(data["korean"],MUTED,26,gap=30)
    p.paragraph(data["summary"])
    p.rule(p.pad,p.y,p.width-p.pad)
    p.y += 30
    for label, value in [("AUTHORS",data["authors"]),("VENUE",data["venue"]),("COMPETITION",data["competition"]),("CONFERENCE DATES",data["date"])]:
        p.label(label)
        p.paragraph(value,WHITE,gap=30)
    p.rule(p.pad,p.y,p.width-p.pad)
    p.y += 28
    p.paragraph("Conference proceedings & program book ↗",GOLD,25,True,0)
    p.finish("publication")


def render_background(mobile):
    data = DATA["background"]
    p = Panel(7,data["title"],mobile,content_alt("background"))
    p.label("EDUCATION")
    for entry in data["education"]:
        p.paragraph(entry["period"],LIME,24,True,8)
        p.paragraph(entry["school"],WHITE,30,True,8)
        if entry["detail"]:
            p.paragraph(entry["detail"],MUTED,gap=14)
        p.y += 20
    p.rule(p.pad,p.y,p.width-p.pad)
    p.y += 36
    p.label("HONORS")
    for entry in data["honors"]:
        p.paragraph(entry["year"],LIME,34,True,14)
        for item in entry["items"]:
            p.rect(p.pad,p.y+11,6,6,LIME,0)
            p.y = p.text(item,p.pad+24,p.y,p.body,WHITE,width=p.inner-24)+14
        p.y += 18
    p.finish("background")


def render_contact(mobile):
    data = DATA["contact"]
    p = Panel(8,data["title"],mobile,content_alt("contact"))
    p.paragraph(data["purpose"],WHITE,30,True,14)
    p.paragraph(data["note"],MUTED,gap=28)
    p.paragraph(data["email"],LIME,32 if mobile else 48,True,24)
    p.paragraph("EMAIL ME ↗",LIME,23,True,0)
    p.finish("contact")


def render_button(name, label, mobile, secondary=False):
    width = 240 if mobile else (360 if secondary else 560)
    height = 98 if secondary else 104
    size = (32 if secondary else 25) if mobile else (30 if secondary else 28)
    d = Drawing()
    d.rect(.5,.5,width-1,height-1,INK,12,BORDER)
    available = width-(40 if mobile else 60)
    lines = wrap(label, available, size, True)
    text_height = size * (1 + 1.42 * (len(lines)-1))
    d.text(label,20 if mobile else 30,(height-text_height)/2,size,LIME,True,available)
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title"><title id="title">{escape(label)}</title><g font-family="{FONT}">{"".join(d.parts)}</g></svg>\n'
    (OUT/f'{name}{"-mobile" if mobile else ""}.svg').write_text(svg,encoding="utf-8")


def picture(name, alt, width="100%"):
    return f'''<picture>
    <source media="(max-width: 600px)" srcset="./assets/panels/{name}-mobile.svg">
    <img src="./assets/panels/{name}.svg" alt="{escape(alt,quote=True)}" width="{width}">
  </picture>'''


def render_readme():
    parts = ['''<!-- Generated from profile.json. To update: python3 scripts/render-profile.py -->

<p align="center">
  <picture>
    <source media="(prefers-reduced-motion: reduce)" srcset="./assets/profile-header.svg">
    <img src="./assets/profile-header.gif" alt="Yeonoh Park · 박연오 — Security Researcher, SeoulTech CIS Lab" width="100%">
  </picture>
</p>''']
    for name in ("about","research","method","published","coordinated","publication","background","contact"):
        graphic = picture(name,content_alt(name))
        if name == "publication":
            graphic = f'<a href="{DATA[name]["link"]}">\n  {graphic}\n</a>'
        if name == "contact":
            graphic = f'<a href="mailto:{DATA[name]["email"]}">\n  {graphic}\n</a>'
        parts.append(f'<p align="center">\n  {graphic}\n</p>')
        if name == "published":
            links = []
            for label,item in zip(("Jenkins advisory ↗","ToolJet CVE ↗"),DATA["published"]["items"]):
                key = "link-"+item["project"].lower()
                links.append(f'<a href="{item["link"]}">{picture(key,label,"49%")}</a>')
            parts.append('<p align="center">\n  '+"\n  ".join(links)+'\n</p>')
    links = [f'<a href="{social["url"]}">{picture("link-"+social["label"].lower(),social["label"],"32%")}</a>' for social in DATA["contact"]["social"]]
    parts.append('<p align="center">\n  '+"\n  ".join(links)+'\n</p>')
    (ROOT/"README.md").write_text("\n\n".join(parts)+"\n",encoding="utf-8")


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    for mobile in (False,True):
        render_about(mobile)
        render_research(mobile)
        render_method(mobile)
        render_records("published",4,mobile)
        render_records("coordinated",5,mobile)
        render_publication(mobile)
        render_background(mobile)
        render_contact(mobile)
        render_button("link-jenkins","Jenkins advisory ↗",mobile)
        render_button("link-tooljet","ToolJet CVE ↗",mobile)
        for social in DATA["contact"]["social"]:
            render_button("link-"+social["label"].lower(),social["label"],mobile,True)
    render_readme()
    print(f"Generated README.md and {len(list(OUT.glob('*.svg')))} SVG panels from profile.json.")


if __name__ == "__main__":
    main()
