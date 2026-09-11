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
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets"
DATA = json.loads((ROOT / "profile.json").read_text(encoding="utf-8"))
PANELS = {}
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
        self.parts.append(f'<g data-card="true" transform="translate({x} {y})">{"".join(drawing.parts)}</g>')


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
        PANELS[f"{name}{'-mobile' if self.mobile else ''}"] = svg


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
    return " ".join([data["purpose"] + ".", data["note"], data["email"] + ".", *[s["label"] + ": " + s["url"] for s in data["social"]]])


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
        tag = Drawing()
        tag.rect(0, 0, width, 94)
        tag.text(interest, 18, 20, 25 if mobile else 23, LIME, True, width-36)
        p.group(tag,x,y)
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
    height = max(117 + len(wrap(m["label"],width-44,24,True))*24*1.28 + 12
                 + len(wrap(m["note"],width-44,21))*21*1.3 + 22
                 for m in data["metrics"])
    for i, metric in enumerate(data["metrics"]):
        x, y = p.pad+(i%cols)*(width+gap), p.y+(i//cols)*(height+gap)
        card = Drawing()
        card.rect(0,0,width,height)
        card.text(metric["value"],22,20,76,LIME,True)
        yy = card.text(metric["label"],22,117,24,WHITE,True,width-44,1.28)+12
        card.text(metric["note"],22,yy,21,MUTED,False,width-44,1.3)
        p.group(card,x,y)
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
    p.rule(p.pad,p.y,p.width-p.pad)
    p.y += 30
    for social in data["social"]:
        handle = social["url"].removeprefix("https://").removeprefix("www.").rstrip("/")
        p.label(social["label"].upper())
        p.paragraph(handle,WHITE,26,gap=24)
    p.finish("contact")


SECTIONS = ("about","research","method","published","coordinated","publication","background","contact")
SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("",SVG_NS)


def full_alt():
    return " ".join(DATA[name]["title"]+". "+content_alt(name) for name in SECTIONS)


def compose(mobile):
    """Merge the header and sections into one canvas, without card seams."""
    width = 600 if mobile else 1200
    scale = width / 1200
    header = ET.parse(OUT/"profile-header.svg").getroot()
    for child in list(header):
        tag = child.tag.rsplit("}",1)[-1]
        # One shared canvas supplies the background and outer border.
        if tag in ("title","desc") or (tag=="rect" and float(child.get("width","0"))>1100):
            header.remove(child)
        elif tag=="polygon" and child.get("fill")==LIME:
            points = child.get("points","").split()
            if points and min(float(point.split(",")[0]) for point in points)>=736:
                header.remove(child)
    header.append(ET.Element(f"{{{SVG_NS}}}path",{
        "class":"header-trace", "d":"M760 105H799L849 184L899 105H938L868 218V293H830V218Z",
        "fill":"none", "stroke":LIME, "stroke-width":"3.2", "pathLength":"1000",
        "stroke-dasharray":"110 890", "stroke-linejoin":"round",
    }))
    body = [f'<g id="profile-header" transform="scale({scale})">'+"".join(ET.tostring(child,encoding="unicode") for child in header)+"</g>"]
    y = 420*scale
    for name in SECTIONS:
        part = ET.fromstring(PANELS[name+("-mobile" if mobile else "")])
        # Reuse drawing content, replacing each panel's outer background.
        group = next(child for child in part if child.tag.rsplit("}",1)[-1]=="g")
        if name!="about":
            pad = 32 if mobile else 60
            body.append(f'<path d="M{pad} {y}H{width-pad}" stroke="{BORDER}"/>')
        body.append(f'<g id="section-{name}" role="group" aria-label="{escape(DATA[name]["title"],quote=True)}" transform="translate(0 {y})">'+ET.tostring(group,encoding="unicode")+"</g>")
        y += float(part.get("height"))-24
    height = round(y+24)
    content = "\n".join(body)
    svg = f'''<svg xmlns="{SVG_NS}" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">Yeonoh Park · 박연오 — Security Researcher</title>
<desc id="desc">{escape(full_alt())}</desc>
<defs><clipPath id="profile-canvas"><rect width="{width}" height="{height}" rx="20"/></clipPath></defs>
<style>
@keyframes trace {{ to {{ stroke-dashoffset: -1000; }} }}
.header-trace {{ animation: trace 4.8s linear infinite; }}
@media (prefers-reduced-motion: reduce) {{ .header-trace {{ animation: none; }} }}
</style>
<g clip-path="url(#profile-canvas)">
<rect width="{width}" height="{height}" fill="{INK}"/>
{content}
</g>
<rect x=".5" y=".5" width="{width-1}" height="{height-1}" rx="20" fill="none" stroke="{BORDER}"/>
</svg>
'''
    (OUT/f'profile{"-mobile" if mobile else ""}.svg').write_text(svg,encoding="utf-8")


def render_readme():
    readme = f'''<!-- Generated from profile.json. To update: python3 scripts/render-profile.py -->

<p align="center">
  <picture>
    <source media="(max-width: 600px)" srcset="./assets/profile-mobile.svg">
    <img src="./assets/profile.svg" alt="{escape(full_alt(),quote=True)}" width="100%">
  </picture>
</p>

<p align="center">
  <a href="mailto:{DATA['contact']['email']}">Email</a> ·
  {' · '.join(f'<a href="{s["url"]}">{s["label"]}</a>' for s in DATA['contact']['social'])}<br>
  <sub>
    <a href="{DATA['published']['items'][0]['link']}">Jenkins advisory</a> ·
    <a href="{DATA['published']['items'][1]['link']}">ToolJet CVE</a> ·
    <a href="{DATA['publication']['link']}">Conference proceedings</a>
  </sub>
</p>
'''
    (ROOT/"README.md").write_text(readme,encoding="utf-8")


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
        compose(mobile)
    render_readme()
    print("Generated README.md, assets/profile.svg, and assets/profile-mobile.svg from profile.json.")


if __name__ == "__main__":
    main()
