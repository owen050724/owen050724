#!/usr/bin/env python3
"""Build the local profile banner (Python 3 + ImageMagick; no network).

Typography stays still. A short line moves around the original Y monogram.
Set PROFILE_FONT_DIR if Arial fonts are installed in a nonstandard location.
All intermediate frames are kept outside the repository in a temporary folder.
"""

from concurrent.futures import ThreadPoolExecutor
from html import escape
from math import hypot
from pathlib import Path
import os
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
WIDTH, HEIGHT = 1200, 420
FRAMES = 40
Y_POINTS = [
    (760, 105), (799, 105), (849, 184), (899, 105), (938, 105),
    (868, 218), (868, 293), (830, 293), (830, 218), (760, 105),
]


def points_string(points):
    return " ".join(f"{x:.2f},{y:.2f}" for x, y in points)


def moving_segment(fraction, length=110):
    segments = list(zip(Y_POINTS, Y_POINTS[1:]))
    lengths = [hypot(b[0] - a[0], b[1] - a[1]) for a, b in segments]
    perimeter = sum(lengths)
    start = fraction * perimeter
    result = []
    traversed = 0
    for (a, b), segment_length in zip(segments * 2, lengths * 2):
        left = max(start, traversed)
        right = min(start + length, traversed + segment_length)
        if right >= left:
            for distance in (left, right):
                progress = (distance - traversed) / segment_length
                result.append((a[0] + (b[0] - a[0]) * progress,
                               a[1] + (b[1] - a[1]) * progress))
        traversed += segment_length
    return result


def linework(points, color, width=1):
    """Outline with filled quads for consistent browser / MSVG rendering."""
    result = []
    for a, b in zip(points, points[1:]):
        length = hypot(b[0] - a[0], b[1] - a[1])
        if not length:
            continue
        dx = -(b[1] - a[1]) / length * width / 2
        dy = (b[0] - a[0]) / length * width / 2
        corners = [(a[0] + dx, a[1] + dy), (b[0] + dx, b[1] + dy),
                   (b[0] - dx, b[1] - dy), (a[0] - dx, a[1] - dy)]
        result.append(f'<polygon points="{points_string(corners)}" fill="{color}"/>')
    return "\n".join(result)


def svg(frame=0, browser_fonts=True):
    body_font = "Arial, Helvetica, sans-serif" if browser_fonts else "Arial"
    name_font = "Arial Black, Arial, Helvetica, sans-serif" if browser_fonts else "Arial Black"
    highlight = moving_segment((0.16 + frame / FRAMES) % 1)
    p_outer = [(964,105),(1063,105),(1102,143),(1102,191),(1063,229),
               (1002,229),(1002,293),(964,293),(964,105)]
    p_inner = [(1002,141),(1047,141),(1064,157),(1064,177),(1047,193),
               (1002,193),(1002,141)]
    depth = "".join(linework([(x+19,y-18) for x,y in outline], "#363e31")
                    for outline in (Y_POINTS,p_outer,p_inner))
    edges = "".join(linework([(x,y),(x+19,y-18)], "#363e31") for x,y in
                    [(760,105),(799,105),(899,105),(938,105),(868,293),
                     (964,105),(1063,105),(1102,143),(1102,191),(1002,293)])
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">
  <title id="title">Yeonoh Park — Security Researcher</title>
  <desc id="desc">Graphite, ivory, and lime editorial banner with oversized lettering and an original angular YP monogram. SeoulTech / CIS Lab. Owen050724.</desc>
  <rect width="1200" height="420" rx="20" fill="#151719"/>
  <path d="M690 1H1180Q1199 1 1199 20V400Q1199 419 1180 419H612Z" fill="#191c1d"/>
  <rect x="1" y="1" width="1198" height="418" rx="19" fill="none" stroke="#303331"/>
  <rect x="60" y="46" width="9" height="9" fill="#d6f77a"/>
  <text x="84" y="56" fill="#d5d8cd" font-family="{body_font}" font-size="16" font-weight="700" letter-spacing="1.1">SECURITY RESEARCHER</text>
  <g fill="#f4f1e8" font-family="{name_font}" font-size="114" font-weight="900">
    <text x="55" y="173">YEONOH</text>
    <text x="55" y="280" fill="#d6f77a">PARK</text>
  </g>
  {linework([(451,260),(515,260),(502,247)], "#d6f77a", 3)}
  {linework([(515,260),(502,273)], "#d6f77a", 3)}
  <text x="61" y="323" fill="#adb3a7" font-family="{body_font}" font-size="15" letter-spacing="0.2">VULNERABILITY RESEARCH / SYSTEM SECURITY</text>
  {depth}
  {edges}
  <polygon points="{points_string(Y_POINTS)}" fill="#242b20"/>
  <polygon points="{points_string(p_outer)}" fill="#202423"/>
  <polygon points="{points_string(p_inner)}" fill="#191c1d"/>
  {linework(Y_POINTS, "#788b4e", 1.2)}
  {linework(p_outer, "#747b6a", 1.2)}
  {linework(p_inner, "#747b6a", 1.2)}
  {linework(highlight, "#d6f77a", 3.2)}
  {linework([(736,120),(736,82),(774,82)], "#464f3d", 1)}
  {linework([(1128,272),(1128,310),(1090,310)], "#464f3d", 1)}
  <text x="744" y="339" fill="#88917f" font-family="{body_font}" font-size="11" letter-spacing="0.3">IDENTITY. AUTHORITY. TRUST.</text>
  <rect x="60" y="363" width="1080" height="1" fill="#373c35"/>
  <text x="61" y="392" fill="#b4baad" font-family="{body_font}" font-size="13" font-weight="700" letter-spacing="0.5">SEOULTECH / CIS LAB</text>
  <text x="1140" y="392" text-anchor="end" fill="#d6f77a" font-family="{body_font}" font-size="13" font-weight="700" letter-spacing="0.7">OWEN050724</text>
</svg>
'''


def main():
    magick = shutil.which("magick")
    if not magick:
        raise SystemExit("ImageMagick 7 (magick) is required.")
    font_dir = Path(os.environ.get("PROFILE_FONT_DIR", "/System/Library/Fonts/Supplemental"))
    fonts = [("Arial", "Arial.ttf", 400), ("Arial", "Arial Bold.ttf", 700),
             ("Arial Black", "Arial Black.ttf", 900)]
    if any(not (font_dir / filename).exists() for _, filename, _ in fonts):
        raise SystemExit("Set PROFILE_FONT_DIR to a folder containing Arial.ttf, Arial Bold.ttf, and Arial Black.ttf.")
    ASSETS.mkdir(exist_ok=True)
    (ASSETS / "profile-header.svg").write_text(svg(), encoding="utf-8")
    temp = Path(tempfile.mkdtemp(prefix="owen-profile-", dir="/private/tmp"))
    (temp / "type.xml").write_text(
        '<?xml version="1.0"?><typemap>' + ''.join(
            f'<type name="{escape(name)}-{weight}" fullname="{escape(name)}" family="{escape(name)}" '
            f'weight="{weight}" style="normal" stretch="normal" glyphs="{escape(str(font_dir / filename))}"/>'
            for name, filename, weight in fonts
        ) + '</typemap>', encoding="utf-8")
    env = dict(os.environ, MAGICK_CONFIGURE_PATH=str(temp))

    def render(frame):
        source = temp / f"frame-{frame:03d}.svg"
        output = temp / f"frame-{frame:03d}.png"
        source.write_text(svg(frame, browser_fonts=False), encoding="utf-8")
        subprocess.run([magick, "-background", "none", str(source), str(output)], env=env, check=True)
        return output

    with ThreadPoolExecutor(max_workers=4) as pool:
        frames = list(pool.map(render, range(FRAMES)))
    # A shared palette keeps the stationary text pixel-identical in every frame.
    palette = temp / "palette.png"
    subprocess.run([magick, str(frames[0]), "-colors", "96", "-unique-colors", str(palette)], check=True)
    subprocess.run([
        magick, "-delay", "12", "-loop", "0", *map(str, frames),
        "+dither", "-remap", str(palette), "-layers", "Optimize", str(ASSETS / "profile-header.gif"),
    ], check=True)
    print(f"SVG: {ASSETS / 'profile-header.svg'}")
    print(f"GIF: {ASSETS / 'profile-header.gif'} ({(ASSETS / 'profile-header.gif').stat().st_size:,} bytes)")
    print(f"Preview: {frames[0]}")
    print(f"Animation: {FRAMES} frames, 4.8 seconds, {WIDTH} × {HEIGHT}; text stays still.")


if __name__ == "__main__":
    main()
