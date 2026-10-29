"""Procedural Studio Archetypes for Executive Motion Graphics.

Implements world-class, 100% original, copyright-safe procedural vector components
inspired by top-tier motion design studios (Cloud X Berry, ByteByteGo, Fireship, Vox):
  1. Data Center Grid: 48-rack server facility with LED status lights.
  2. Tooling Mockups: Tri-pane Browser Console, Terminal CLI, and Python Boto3 Code Editor.
  3. Comparison Split: Two-column CapEx vs OpEx comparative matrix.
  4. Region Topology: AWS Region master card containing 3 isolated Availability Zones and fiber links.
  5. Squircle Brand Badges: Apple/macOS superellipse icons with diffuse shadows and vector emblems.
  6. Feature Callout Pills: Floating pill badges with colored icons (Power, Network, Cooling, SLA).
"""
from __future__ import annotations
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]
_MONO_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
]


def get_font(size: int, bold: bool = False, mono: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    cands = _MONO_CANDIDATES if mono else _FONT_CANDIDATES
    for c in cands:
        if bold and "bold" not in c.lower():
            continue
        if not bold and "bold" in c.lower():
            continue
        if os.path.isfile(c):
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                pass
    for c in cands:
        if os.path.isfile(c):
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                pass
    return ImageFont.load_default()


def apply_drop_shadow(img: Image.Image, x0: int, y0: int, x1: int, y1: int, radius: int = 16, blur: int = 14, alpha: int = 28) -> None:
    """Adds a soft diffuse drop shadow onto an RGBA canvas."""
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow, "RGBA")
    sdraw.rounded_rectangle([x0, y0 + 8, x1, y1 + 16], radius=radius, fill=(0, 0, 0, alpha))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=blur))
    img.alpha_composite(shadow)


# ---------------------------------------------------------------------------
# 1. DATA CENTER SERVER RACK GRID
# ---------------------------------------------------------------------------
def draw_datacenter_grid(draw: ImageDraw.ImageDraw, img: Image.Image, cw: int, ch: int, el, u: float, style: str) -> None:
    """Draws a clean white Data Center card with 48 server racks and LED lights."""
    card_x, card_y = int(20 * u), int(16 * u)
    card_w, card_h = cw - int(40 * u), ch - int(32 * u)

    apply_drop_shadow(img, card_x, card_y, card_x + card_w, card_y + card_h, radius=int(26 * u), blur=int(14 * u), alpha=24)
    draw.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h], radius=int(24 * u), fill=(255, 255, 255, 255), outline=(226, 232, 240, 255), width=2)

    # Header: Server Rack Icon + "DATA CENTER"
    hdr_x, hdr_y = card_x + int(36 * u), card_y + int(30 * u)
    draw.rounded_rectangle([hdr_x, hdr_y, hdr_x + int(56 * u), hdr_y + int(56 * u)], radius=int(14 * u), fill=(30, 41, 59, 255))
    draw.rounded_rectangle([hdr_x + int(14 * u), hdr_y + int(12 * u), hdr_x + int(42 * u), hdr_y + int(44 * u)], radius=int(3 * u), outline=(255, 255, 255, 255), width=2)
    draw.line([(hdr_x + int(18 * u), hdr_y + int(21 * u)), (hdr_x + int(38 * u), hdr_y + int(21 * u))], fill=(255, 255, 255, 255), width=2)
    draw.line([(hdr_x + int(18 * u), hdr_y + int(30 * u)), (hdr_x + int(38 * u), hdr_y + int(30 * u))], fill=(255, 255, 255, 255), width=2)
    draw.ellipse([hdr_x + int(34 * u), hdr_y + int(37 * u), hdr_x + int(38 * u), hdr_y + int(41 * u)], fill=(34, 197, 94, 255))

    f_hdr = get_font(max(18, int(24 * u)), bold=True)
    title = (el.label or "DATA CENTER").strip().upper()
    draw.text((hdr_x + int(72 * u), hdr_y + int(12 * u)), title, fill=(15, 23, 42, 255), font=f_hdr)

    # Server Rack Grid: 4 rows x 12 columns
    grid_top_y = card_y + int(105 * u)
    rows, cols = 4, 12
    rack_w = max(24, int(46 * u))
    rack_h = max(45, int(98 * u))
    spacing_x = max(12, int(26 * u))
    spacing_y = max(10, int(22 * u))
    grid_start_x = card_x + (card_w - (cols * rack_w + (cols - 1) * spacing_x)) // 2

    for r in range(rows):
        ry = grid_top_y + r * (rack_h + spacing_y)
        for c in range(cols):
            rx = grid_start_x + c * (rack_w + spacing_x)
            draw.rounded_rectangle([rx, ry, rx + rack_w, ry + rack_h], radius=int(5 * u), fill=(51, 65, 85, 255), outline=(71, 85, 105, 255), width=1)
            slot_h = max(8, int(rack_h / 3.6))
            for s in range(3):
                sy = ry + int(6 * u) + s * slot_h
                draw.rounded_rectangle([rx + int(3 * u), sy, rx + rack_w - int(3 * u), sy + slot_h - int(4 * u)], radius=int(2 * u), fill=(30, 41, 59, 255))
                draw.line([(rx + int(6 * u), sy + int(slot_h / 2) - 2), (rx + int(rack_w / 2), sy + int(slot_h / 2) - 2)], fill=(71, 85, 105, 255), width=1)
                led_c = (34, 197, 94, 255) if (r + c + s) % 5 != 0 else (56, 189, 248, 255)
                draw.ellipse([rx + rack_w - int(9 * u), sy + int(3 * u), rx + rack_w - int(5 * u), sy + int(7 * u)], fill=led_c)


# ---------------------------------------------------------------------------
# 2. APPLICATION TOOLING MOCKUPS (CONSOLE, CLI, SDK)
# ---------------------------------------------------------------------------
def draw_tooling_mockups(draw: ImageDraw.ImageDraw, img: Image.Image, cw: int, ch: int, el, u: float, style: str) -> None:
    """Draws 3 side-by-side floating windows: Browser Console, Terminal CLI, VS Code Python SDK."""
    pane_w = int((cw - int(120 * u)) / 3.0)
    pane_h = ch - int(40 * u)
    pane_y = int(20 * u)
    gap = int(36 * u)
    start_x = int(24 * u)

    # Pane 1: Browser Console
    px1 = start_x
    apply_drop_shadow(img, px1, pane_y, px1 + pane_w, pane_y + pane_h, radius=int(20 * u), blur=int(12 * u), alpha=22)
    draw.rounded_rectangle([px1, pane_y, px1 + pane_w, pane_y + pane_h], radius=int(18 * u), fill=(255, 255, 255, 255), outline=(226, 232, 240, 255), width=2)
    draw.rounded_rectangle([px1, pane_y, px1 + pane_w, pane_y + int(52 * u)], radius=int(18 * u), fill=(241, 245, 249, 255))
    draw.rectangle([px1, pane_y + int(36 * u), px1 + pane_w, pane_y + int(52 * u)], fill=(241, 245, 249, 255))
    for i, col in enumerate([(239, 68, 68, 255), (245, 158, 11, 255), (34, 197, 94, 255)]):
        draw.ellipse([px1 + int((16 + i * 18) * u), pane_y + int(20 * u), px1 + int((26 + i * 18) * u), pane_y + int(30 * u)], fill=col)
    draw.rounded_rectangle([px1 + int(78 * u), pane_y + int(14 * u), px1 + pane_w - int(16 * u), pane_y + int(38 * u)], radius=int(12 * u), fill=(255, 255, 255, 255), outline=(203, 213, 225, 255), width=1)
    f_url = get_font(max(10, int(11 * u)), mono=True)
    draw.text((px1 + int(94 * u), pane_y + int(19 * u)), "console.aws.amazon.com", fill=(100, 116, 139, 255), font=f_url)

    # Console Hero Box inside Browser
    draw.rounded_rectangle([px1 + int(20 * u), pane_y + int(70 * u), px1 + pane_w - int(20 * u), pane_y + int(125 * u)], radius=int(12 * u), fill=(249, 115, 22, 255))
    f_cb = get_font(max(13, int(16 * u)), bold=True)
    draw.text((px1 + int(36 * u), pane_y + int(82 * u)), "AWS Management Console", fill=(255, 255, 255, 255), font=f_cb)
    f_cs = get_font(max(10, int(11 * u)))
    draw.text((px1 + int(36 * u), pane_y + int(104 * u)), "Interactive Web UI & Navigation", fill=(255, 255, 255, 210), font=f_cs)

    services = [("EC2", "Virtual Servers", (249, 115, 22, 255)), ("S3", "Object Storage", (16, 185, 129, 255)), ("RDS", "SQL Databases", (37, 99, 235, 255)), ("Lambda", "Serverless Code", (234, 88, 12, 255))]
    for idx, (sn, sd, sc) in enumerate(services):
        sy = pane_y + int(140 * u) + idx * int(95 * u)
        draw.rounded_rectangle([px1 + int(20 * u), sy, px1 + pane_w - int(20 * u), sy + int(82 * u)], radius=int(12 * u), fill=(248, 250, 252, 255), outline=(226, 232, 240, 255), width=1)
        draw.rounded_rectangle([px1 + int(32 * u), sy + int(14 * u), px1 + int(80 * u), sy + int(64 * u)], radius=int(10 * u), fill=sc)
        draw.text((px1 + int(42 * u), sy + int(30 * u)), sn[:3], fill=(255, 255, 255, 255), font=get_font(max(11, int(13 * u)), bold=True))
        draw.text((px1 + int(94 * u), sy + int(20 * u)), sn, fill=(15, 23, 42, 255), font=get_font(max(13, int(15 * u)), bold=True))
        draw.text((px1 + int(94 * u), sy + int(44 * u)), sd, fill=(100, 116, 139, 255), font=get_font(max(10, int(12 * u))))

    # Pane 2: Dark Terminal CLI
    px2 = start_x + pane_w + gap
    apply_drop_shadow(img, px2, pane_y, px2 + pane_w, pane_y + pane_h, radius=int(20 * u), blur=int(12 * u), alpha=22)
    draw.rounded_rectangle([px2, pane_y, px2 + pane_w, pane_y + pane_h], radius=int(18 * u), fill=(15, 23, 42, 255), outline=(51, 65, 85, 255), width=2)
    draw.rounded_rectangle([px2, pane_y, px2 + pane_w, pane_y + int(52 * u)], radius=int(18 * u), fill=(30, 41, 59, 255))
    draw.rectangle([px2, pane_y + int(36 * u), px2 + pane_w, pane_y + int(52 * u)], fill=(30, 41, 59, 255))
    for i, col in enumerate([(239, 68, 68, 255), (245, 158, 11, 255), (34, 197, 94, 255)]):
        draw.ellipse([px2 + int((16 + i * 18) * u), pane_y + int(20 * u), px2 + int((26 + i * 18) * u), pane_y + int(30 * u)], fill=col)
    draw.text((px2 + int(140 * u), pane_y + int(18 * u)), "aws-cli — zsh", fill=(148, 163, 184, 255), font=get_font(max(11, int(12 * u)), bold=True, mono=True))

    f_code = get_font(max(10, int(12 * u)), mono=True)
    ty = pane_y + int(76 * u)
    draw.text((px2 + int(24 * u), ty), "$", fill=(34, 197, 94, 255), font=get_font(max(10, int(12 * u)), bold=True, mono=True))
    draw.text((px2 + int(40 * u), ty), "aws ec2 describe-instances \\", fill=(241, 245, 249, 255), font=f_code)
    ty += int(24 * u)
    draw.text((px2 + int(56 * u), ty), "--region us-east-1", fill=(56, 189, 248, 255), font=f_code)
    ty += int(36 * u)
    lines = ['{', '  "Reservations": [', '    {', '      "InstanceId": "i-09f12ab34c",', '      "InstanceType": "t3.medium",', '      "State": "running",', '      "PublicIp": "54.210.82.14"', '    }', '  ]', '}', '', '$ aws s3 sync ./dist s3://prod']
    for lt in lines:
        col = (34, 197, 94, 255) if lt.startswith("$") else ((251, 191, 36, 255) if "Instance" in lt else (148, 163, 184, 255))
        draw.text((px2 + int(24 * u), ty), lt, fill=col, font=f_code)
        ty += int(22 * u)

    # Pane 3: Code Editor SDK
    px3 = start_x + (pane_w + gap) * 2
    apply_drop_shadow(img, px3, pane_y, px3 + pane_w, pane_y + pane_h, radius=int(20 * u), blur=int(12 * u), alpha=22)
    draw.rounded_rectangle([px3, pane_y, px3 + pane_w, pane_y + pane_h], radius=int(18 * u), fill=(30, 30, 46, 255), outline=(69, 71, 90, 255), width=2)
    draw.rounded_rectangle([px3, pane_y, px3 + pane_w, pane_y + int(52 * u)], radius=int(18 * u), fill=(24, 24, 37, 255))
    draw.rectangle([px3, pane_y + int(36 * u), px3 + pane_w, pane_y + int(52 * u)], fill=(24, 24, 37, 255))
    for i, col in enumerate([(239, 68, 68, 255), (245, 158, 11, 255), (34, 197, 94, 255)]):
        draw.ellipse([px3 + int((16 + i * 18) * u), pane_y + int(20 * u), px3 + int((26 + i * 18) * u), pane_y + int(30 * u)], fill=col)
    draw.rounded_rectangle([px3 + int(76 * u), pane_y + int(14 * u), px3 + int(210 * u), pane_y + int(46 * u)], radius=int(6 * u), fill=(30, 30, 46, 255))
    draw.text((px3 + int(90 * u), pane_y + int(24 * u)), "deploy_infra.py", fill=(205, 214, 244, 255), font=get_font(max(10, int(11 * u)), mono=True))

    py_lines = [('# AWS SDK Boto3 Python', (108, 112, 134, 255)), ('import boto3', (203, 166, 247, 255)), ('', (0,0,0,0)), ('ec2 = boto3.client("ec2")', (137, 180, 250, 255)), ('s3  = boto3.client("s3")', (137, 180, 250, 255)), ('', (0,0,0,0)), ('def launch_nodes():', (249, 226, 175, 255)), ('    resp = ec2.run_instances(', (205, 214, 244, 255)), ('        ImageId="ami-0c55b1",', (166, 227, 161, 255)), ('        InstanceType="t3.med",', (166, 227, 161, 255)), ('        MinCount=1, MaxCount=5', (250, 179, 135, 255)), ('    )', (205, 214, 244, 255)), ('    return resp["Nodes"]', (203, 166, 247, 255))]
    py_y = pane_y + int(76 * u)
    for idx, (ct, cc) in enumerate(py_lines):
        draw.text((px3 + int(18 * u), py_y), f"{idx+1:2d}", fill=(108, 112, 134, 255), font=get_font(max(10, int(11 * u)), mono=True))
        draw.text((px3 + int(50 * u), py_y), ct, fill=cc, font=f_code)
        py_y += int(25 * u)


# ---------------------------------------------------------------------------
# 3. COMPARISON MATRIX (CAPEX VS OPEX)
# ---------------------------------------------------------------------------
def draw_comparison_split(draw: ImageDraw.ImageDraw, img: Image.Image, cw: int, ch: int, el, u: float, style: str) -> None:
    """Draws 2 comparative columns: On-Premises CapEx vs AWS Cloud OpEx."""
    col_w = int((cw - int(80 * u)) / 2.0)
    col_h = ch - int(40 * u)
    col_y = int(20 * u)
    x_left = int(24 * u)
    x_right = x_left + col_w + int(32 * u)

    # Left: On-Premises (CapEx)
    apply_drop_shadow(img, x_left, col_y, x_left + col_w, col_y + col_h, radius=int(22 * u), blur=int(14 * u), alpha=22)
    draw.rounded_rectangle([x_left, col_y, x_left + col_w, col_y + col_h], radius=int(20 * u), fill=(255, 255, 255, 255), outline=(226, 232, 240, 255), width=2)
    draw.rounded_rectangle([x_left + int(20 * u), col_y + int(20 * u), x_left + col_w - int(20 * u), col_y + int(90 * u)], radius=int(14 * u), fill=(241, 245, 249, 255))
    draw.rounded_rectangle([x_left + int(32 * u), col_y + int(28 * u), x_left + int(84 * u), col_y + int(80 * u)], radius=int(10 * u), fill=(100, 116, 139, 255))
    draw.text((x_left + int(100 * u), col_y + int(32 * u)), "ON-PREMISES (CapEx)", fill=(15, 23, 42, 255), font=get_font(max(15, int(20 * u)), bold=True))
    draw.text((x_left + int(100 * u), col_y + int(60 * u)), "Capital Expenditure · Fixed Cost", fill=(100, 116, 139, 255), font=get_font(max(11, int(13 * u))))

    capex_rows = [("Upfront Hardware Investment", "Heavy budget locked into physical servers & SANs.", (239, 68, 68, 255)), ("Capacity Guessing & Waste", "Must provision for peak load; 60-80% idle capacity.", (245, 158, 11, 255)), ("Slow Hardware Procurement", "Weeks waiting for hardware shipping, racking & cables.", (245, 158, 11, 255)), ("Facility Overhead & Power", "Real estate, diesel backup, cooling & datacenter rent.", (100, 116, 139, 255))]
    for idx, (t, d, c) in enumerate(capex_rows):
        fy = col_y + int(110 * u) + idx * int(105 * u)
        draw.rounded_rectangle([x_left + int(20 * u), fy, x_left + col_w - int(20 * u), fy + int(92 * u)], radius=int(12 * u), fill=(248, 250, 252, 255), outline=(226, 232, 240, 255), width=1)
        draw.rounded_rectangle([x_left + int(32 * u), fy + int(14 * u), x_left + int(37 * u), fy + int(78 * u)], radius=int(2 * u), fill=c)
        draw.text((x_left + int(52 * u), fy + int(18 * u)), t, fill=(15, 23, 42, 255), font=get_font(max(13, int(15 * u)), bold=True))
        draw.text((x_left + int(52 * u), fy + int(48 * u)), d, fill=(71, 85, 105, 255), font=get_font(max(10, int(12 * u))))

    # Right: AWS Cloud (OpEx)
    apply_drop_shadow(img, x_right, col_y, x_right + col_w, col_y + col_h, radius=int(22 * u), blur=int(14 * u), alpha=22)
    draw.rounded_rectangle([x_right, col_y, x_right + col_w, col_y + col_h], radius=int(20 * u), fill=(255, 255, 255, 255), outline=(226, 232, 240, 255), width=2)
    draw.rounded_rectangle([x_right + int(20 * u), col_y + int(20 * u), x_right + col_w - int(20 * u), col_y + int(90 * u)], radius=int(14 * u), fill=(255, 247, 237, 255), outline=(254, 215, 170, 255), width=1)
    draw.rounded_rectangle([x_right + int(32 * u), col_y + int(28 * u), x_right + int(84 * u), col_y + int(80 * u)], radius=int(10 * u), fill=(249, 115, 22, 255))
    draw.text((x_right + int(100 * u), col_y + int(32 * u)), "AWS CLOUD (OpEx)", fill=(15, 23, 42, 255), font=get_font(max(15, int(20 * u)), bold=True))
    draw.text((x_right + int(100 * u), col_y + int(60 * u)), "Operational Expenditure · Pay-As-You-Go", fill=(234, 88, 12, 255), font=get_font(max(11, int(13 * u)), bold=True))

    opex_rows = [("Zero Upfront Capital", "No servers to buy. Pay only for what you consume.", (16, 185, 129, 255)), ("Elastic Auto-Scaling", "Scale instances with traffic; shut down and pay $0.", (16, 185, 129, 255)), ("Instant Global Provisioning", "Spin up 100 EC2 virtual machines in under 60 seconds.", (14, 165, 233, 255)), ("Massive Economies of Scale", "AWS lowers pricing regularly; pass savings to business.", (124, 58, 237, 255))]
    for idx, (t, d, c) in enumerate(opex_rows):
        fy = col_y + int(110 * u) + idx * int(105 * u)
        draw.rounded_rectangle([x_right + int(20 * u), fy, x_right + col_w - int(20 * u), fy + int(92 * u)], radius=int(12 * u), fill=(248, 250, 252, 255), outline=(226, 232, 240, 255), width=1)
        draw.rounded_rectangle([x_right + int(32 * u), fy + int(14 * u), x_right + int(37 * u), fy + int(78 * u)], radius=int(2 * u), fill=c)
        draw.text((x_right + int(52 * u), fy + int(18 * u)), t, fill=(15, 23, 42, 255), font=get_font(max(13, int(15 * u)), bold=True))
        draw.text((x_right + int(52 * u), fy + int(48 * u)), d, fill=(71, 85, 105, 255), font=get_font(max(10, int(12 * u))))


# ---------------------------------------------------------------------------
# 4. REGION AND AVAILABILITY ZONE TOPOLOGY
# ---------------------------------------------------------------------------
def draw_region_topology(draw: ImageDraw.ImageDraw, img: Image.Image, cw: int, ch: int, el, u: float, style: str) -> None:
    """Draws master Region container holding 3 Availability Zones linked by low-latency fiber."""
    reg_x, reg_y = int(20 * u), int(16 * u)
    reg_w, reg_h = cw - int(40 * u), ch - int(32 * u)

    apply_drop_shadow(img, reg_x, reg_y, reg_x + reg_w, reg_y + reg_h, radius=int(26 * u), blur=int(16 * u), alpha=22)
    draw.rounded_rectangle([reg_x, reg_y, reg_x + reg_w, reg_y + reg_h], radius=int(24 * u), fill=(255, 255, 255, 255), outline=(191, 219, 254, 255), width=3)

    # Region Header Banner
    draw.rounded_rectangle([reg_x + int(32 * u), reg_y + int(24 * u), reg_x + reg_w - int(32 * u), reg_y + int(82 * u)], radius=int(14 * u), fill=(239, 246, 255, 255), outline=(219, 234, 254, 255), width=1)
    draw.rounded_rectangle([reg_x + int(44 * u), reg_y + int(32 * u), reg_x + int(96 * u), reg_y + int(74 * u)], radius=int(10 * u), fill=(37, 99, 235, 255))
    draw.ellipse([reg_x + int(56 * u), reg_y + int(40 * u), reg_x + int(84 * u), reg_y + int(66 * u)], outline=(255, 255, 255, 255), width=2)
    draw.line([(reg_x + int(56 * u), reg_y + int(53 * u)), (reg_x + int(84 * u), reg_y + int(53 * u))], fill=(255, 255, 255, 255), width=2)

    f_rt = get_font(max(15, int(20 * u)), bold=True)
    draw.text((reg_x + int(110 * u), reg_y + int(34 * u)), "AWS REGION: us-east-1 (N. Virginia)", fill=(15, 23, 42, 255), font=f_rt)
    f_rs = get_font(max(10, int(12 * u)))
    draw.text((reg_x + int(110 * u), reg_y + int(58 * u)), "Cluster of 3 or more Isolated Availability Zones · Independent Utilities & Floodplains", fill=(71, 85, 105, 255), font=f_rs)

    # 3 AZ Cards
    az_w = int((reg_w - int(100 * u)) / 3.0)
    az_h = reg_h - int(120 * u)
    az_y = reg_y + int(100 * u)
    azs = [("us-east-1a", "Availability Zone A", (249, 115, 22, 255)), ("us-east-1b", "Availability Zone B", (16, 185, 129, 255)), ("us-east-1c", "Availability Zone C", (147, 51, 234, 255))]

    for idx, (code, name, col) in enumerate(azs):
        ax = reg_x + int(28 * u) + idx * (az_w + int(22 * u))
        apply_drop_shadow(img, ax, az_y, ax + az_w, az_y + az_h, radius=int(18 * u), blur=int(10 * u), alpha=18)
        draw.rounded_rectangle([ax, az_y, ax + az_w, az_y + az_h], radius=int(16 * u), fill=(255, 255, 255, 255), outline=(226, 232, 240, 255), width=2)

        # Header Pill inside AZ
        draw.rounded_rectangle([ax + int(16 * u), az_y + int(16 * u), ax + az_w - int(16 * u), az_y + int(70 * u)], radius=int(12 * u), fill=(248, 250, 252, 255), outline=(226, 232, 240, 255), width=1)
        draw.rounded_rectangle([ax + int(24 * u), az_y + int(24 * u), ax + int(68 * u), az_y + int(62 * u)], radius=int(8 * u), fill=col)
        draw.text((ax + int(34 * u), az_y + int(34 * u)), code[-2:].upper(), fill=(255, 255, 255, 255), font=get_font(max(12, int(15 * u)), bold=True))
        draw.text((ax + int(80 * u), az_y + int(28 * u)), code, fill=(15, 23, 42, 255), font=get_font(max(13, int(16 * u)), bold=True))
        draw.text((ax + int(80 * u), az_y + int(48 * u)), name, fill=(100, 116, 139, 255), font=get_font(max(10, int(11 * u))))

        # Data Center Mini Racks
        for dc_i in range(2):
            dcy = az_y + int(88 * u) + dc_i * int(110 * u)
            draw.rounded_rectangle([ax + int(16 * u), dcy, ax + az_w - int(16 * u), dcy + int(98 * u)], radius=int(10 * u), fill=(241, 245, 249, 255))
            for rk in range(5):
                rkx = ax + int(30 * u) + rk * int((az_w - int(60 * u)) / 5.0)
                draw.rounded_rectangle([rkx, dcy + int(12 * u), rkx + int(42 * u), dcy + int(86 * u)], radius=int(4 * u), fill=(51, 65, 85, 255))
                for sl in range(3):
                    draw.rounded_rectangle([rkx + 2, dcy + int(16 * u) + sl * int(22 * u), rkx + int(40 * u), dcy + int(34 * u) + sl * int(22 * u)], radius=1, fill=(30, 41, 59, 255))
                    draw.ellipse([rkx + int(32 * u), dcy + int(19 * u) + sl * int(22 * u), rkx + int(36 * u), dcy + int(23 * u) + sl * int(22 * u)], fill=(34, 197, 94, 255))

        draw.rounded_rectangle([ax + int(16 * u), az_y + az_h - int(48 * u), ax + az_w - int(16 * u), az_y + az_h - int(14 * u)], radius=int(8 * u), fill=(254, 243, 199, 255))
        draw.text((ax + int(28 * u), az_y + az_h - int(36 * u)), "🛡️ Isolated Utility & Floodplain", fill=(180, 83, 9, 255), font=get_font(max(10, int(11 * u)), bold=True))


# ---------------------------------------------------------------------------
# 5. SQUIRCLE BRAND BADGE
# ---------------------------------------------------------------------------
def draw_squircle_brand(draw: ImageDraw.ImageDraw, img: Image.Image, cw: int, ch: int, title: str, low: str, u: float, style: str) -> None:
    """Draws an Apple/macOS squircle icon (110x110) with diffuse shadow and brand emblem."""
    size = min(cw, ch) - int(36 * u)
    cx, cy = cw // 2, (ch - int(24 * u)) // 2
    r = size // 2

    apply_drop_shadow(img, cx - r, cy - r, cx + r, cy + r, radius=int(26 * u), blur=int(10 * u), alpha=32)
    draw.rounded_rectangle([cx - r, cy - r, cx + r, cy + r], radius=int(24 * u), fill=(255, 255, 255, 255), outline=(226, 232, 240, 255), width=2)

    # Draw Emblem
    if "amazon" in low or "aws" in low:
        f_a = get_font(max(28, int(46 * u)), bold=True)
        draw.text((cx - int(14 * u), cy - int(30 * u)), "a", fill=(15, 23, 42, 255), font=f_a)
        draw.arc([cx - int(20 * u), cy - 2, cx + int(20 * u), cy + int(20 * u)], start=25, end=155, fill=(249, 115, 22, 255), width=max(3, int(4 * u)))
    elif "microsoft" in low or "azure" in low:
        g = int(14 * u)
        draw.rectangle([cx - g - 2, cy - g - 2, cx - 2, cy - 2], fill=(242, 80, 34, 255))
        draw.rectangle([cx + 2, cy - g - 2, cx + g + 2, cy - 2], fill=(127, 186, 0, 255))
        draw.rectangle([cx - g - 2, cy + 2, cx - 2, cy + g + 2], fill=(0, 164, 239, 255))
        draw.rectangle([cx + 2, cy + 2, cx + g + 2, cy + g + 2], fill=(255, 185, 0, 255))
    elif "google" in low or "gcp" in low:
        f_g = get_font(max(28, int(44 * u)), bold=True)
        draw.text((cx - int(16 * u), cy - int(28 * u)), "G", fill=(66, 133, 244, 255), font=f_g)
    else:
        # Generic Tech Cloud / Shield
        draw.ellipse([cx - int(18 * u), cy - int(14 * u), cx + int(18 * u), cy + int(14 * u)], fill=(37, 99, 235, 255))

    # Bold tracking label underneath
    f_lbl = get_font(max(12, int(15 * u)), bold=True)
    lbl = (title or "CLOUD").strip().upper()[:16]
    tb = draw.textbbox((0, 0), lbl, font=f_lbl)
    lw = tb[2] - tb[0]
    draw.text((cx - lw // 2, cy + r + int(10 * u)), lbl, fill=(15, 23, 42, 255), font=f_lbl)


# ---------------------------------------------------------------------------
# 6. FEATURE CALLOUT PILL
# ---------------------------------------------------------------------------
def draw_callout_pill(draw: ImageDraw.ImageDraw, img: Image.Image, cw: int, ch: int, title: str, low: str, u: float, style: str) -> None:
    """Draws a floating pill badge with colored icon box and uppercase tracking label."""
    pad_x, pad_y = int(8 * u), int(6 * u)
    pw, ph = cw - pad_x * 2, ch - pad_y * 2

    apply_drop_shadow(img, pad_x, pad_y, pad_x + pw, pad_y + ph, radius=int(18 * u), blur=int(8 * u), alpha=20)
    draw.rounded_rectangle([pad_x, pad_y, pad_x + pw, pad_y + ph], radius=int(16 * u), fill=(255, 255, 255, 255), outline=(241, 245, 249, 255), width=2)

    # Icon Color & Type
    col = (124, 58, 237, 255)
    if any(k in low for k in ("power", "energy", "watt", "volt")):
        col = (245, 158, 11, 255)
    elif any(k in low for k in ("cooling", "chiller", "hvac", "cold")):
        col = (2, 132, 199, 255)
    elif any(k in low for k in ("security", "shield", "iam", "compliance")):
        col = (220, 38, 38, 255)

    bx_sz = ph - int(12 * u)
    bx_x = pad_x + int(6 * u)
    bx_y = pad_y + int(6 * u)
    draw.rounded_rectangle([bx_x, bx_y, bx_x + bx_sz, bx_y + bx_sz], radius=int(12 * u), fill=col)

    # Text
    f_txt = get_font(max(13, int(18 * u)), bold=True)
    draw.text((bx_x + bx_sz + int(16 * u), pad_y + int(ph / 2) - int(10 * u)), (title or "FEATURE").strip().upper()[:22], fill=(15, 23, 42, 255), font=f_txt)


# ---------------------------------------------------------------------------
# 7. 4-TIER HIERARCHY STACK (GLOBAL INFRASTRUCTURE BLUEPRINT)
# ---------------------------------------------------------------------------
def draw_hierarchy_stack(draw: ImageDraw.ImageDraw, img: Image.Image, cw: int, ch: int, el, u: float, style: str) -> None:
    """Draws 4 connected tiers: Regions -> Availability Zones -> Data Centers -> Edge Locations."""
    card_x, card_y = int(20 * u), int(16 * u)
    card_w, card_h = cw - int(40 * u), ch - int(32 * u)

    apply_drop_shadow(img, card_x, card_y, card_x + card_w, card_y + card_h, radius=int(26 * u), blur=int(14 * u), alpha=24)
    draw.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h], radius=int(24 * u), fill=(255, 255, 255, 255), outline=(226, 232, 240, 255), width=2)

    # Header Banner
    hdr_x, hdr_y = card_x + int(32 * u), card_y + int(24 * u)
    draw.rounded_rectangle([hdr_x, hdr_y, card_x + card_w - int(32 * u), hdr_y + int(64 * u)], radius=int(14 * u), fill=(248, 250, 252, 255), outline=(226, 232, 240, 255), width=1)
    
    # Header Icon Box
    draw.rounded_rectangle([hdr_x + int(12 * u), hdr_y + int(10 * u), hdr_x + int(56 * u), hdr_y + int(54 * u)], radius=int(10 * u), fill=(30, 41, 59, 255))
    draw.rounded_rectangle([hdr_x + int(20 * u), hdr_y + int(18 * u), hdr_x + int(48 * u), hdr_y + int(46 * u)], radius=int(3 * u), outline=(255, 255, 255, 255), width=2)
    draw.line([(hdr_x + int(24 * u), hdr_y + int(26 * u)), (hdr_x + int(44 * u), hdr_y + int(26 * u))], fill=(255, 255, 255, 255), width=2)
    draw.line([(hdr_x + int(24 * u), hdr_y + int(34 * u)), (hdr_x + int(44 * u), hdr_y + int(34 * u))], fill=(255, 255, 255, 255), width=2)

    f_title = get_font(max(15, int(20 * u)), bold=True)
    draw.text((hdr_x + int(70 * u), hdr_y + int(12 * u)), "AWS GLOBAL INFRASTRUCTURE: 4-TIER BLUEPRINT", fill=(15, 23, 42, 255), font=f_title)
    f_sub = get_font(max(10, int(12 * u)))
    draw.text((hdr_x + int(70 * u), hdr_y + int(38 * u)), "Planetary physical architecture organized from geographic clusters down to the edge", fill=(100, 116, 139, 255), font=f_sub)

    # 4 Tier Cards
    tiers = [
        ("01", "AWS REGIONS", "34+ Geographic Clusters Worldwide", ["Complete Fault Domain Isolation", "Sovereign Compliance Boundaries", "Independent Utility Power Grids"], (37, 99, 235, 255)),
        ("02", "AVAILABILITY ZONES", "3+ Isolated Locations per Region", ["Discrete Physical Data Centers", "Separated 100-Year Floodplains", "< 1-2 ms Low-Latency Metro Fiber"], (249, 115, 22, 255)),
        ("03", "PHYSICAL DATA CENTERS", "Hyperscale Server Facilities", ["50,000–80,000 Custom Servers", "2N Power Redundancy & Diesel Backup", "CRAH Cooling & Nitro Custom Silicon"], (16, 185, 129, 255)),
        ("04", "EDGE LOCATIONS (PoPs)", "Global Low-Latency Perimeter Network", ["600+ Points of Presence Worldwide", "Amazon CloudFront Edge Caching", "Route 53 Anycast DNS & Shield DDoS"], (147, 51, 234, 255)),
    ]

    tier_start_y = card_y + int(105 * u)
    tier_h = int((card_h - int(125 * u)) / 4.0) - int(10 * u)
    t_gap = int(10 * u)

    for i, (num, name, subtitle, tags, col) in enumerate(tiers):
        ty = tier_start_y + i * (tier_h + t_gap)
        tx = card_x + int(32 * u)
        tw = card_w - int(64 * u)

        # Background tier card
        apply_drop_shadow(img, tx, ty, tx + tw, ty + tier_h, radius=int(14 * u), blur=int(8 * u), alpha=16)
        draw.rounded_rectangle([tx, ty, tx + tw, ty + tier_h], radius=int(14 * u), fill=(255, 255, 255, 255), outline=(226, 232, 240, 255), width=1.5)

        # Number badge on left
        badge_w = int(72 * u)
        draw.rounded_rectangle([tx + int(12 * u), ty + int(12 * u), tx + int(12 * u) + badge_w, ty + tier_h - int(12 * u)], radius=int(10 * u), fill=col)
        f_num = get_font(max(16, int(22 * u)), bold=True)
        draw.text((tx + int(30 * u), ty + int(tier_h / 2) - int(13 * u)), num, fill=(255, 255, 255, 255), font=f_num)

        # Title & Subtitle
        f_tname = get_font(max(13, int(17 * u)), bold=True)
        draw.text((tx + badge_w + int(28 * u), ty + int(14 * u)), name, fill=(15, 23, 42, 255), font=f_tname)
        f_tsub = get_font(max(10, int(12 * u)))
        draw.text((tx + badge_w + int(28 * u), ty + int(38 * u)), subtitle, fill=(100, 116, 139, 255), font=f_tsub)

        # Feature tags on right
        tag_x = tx + int(tw * 0.46)
        for tag_text in tags:
            f_tag = get_font(max(9, int(11 * u)), bold=True)
            tb = draw.textbbox((0, 0), tag_text, font=f_tag)
            tag_w = tb[2] - tb[0] + int(20 * u)
            if tag_x + tag_w > tx + tw - int(12 * u):
                break
            draw.rounded_rectangle([tag_x, ty + int(tier_h / 2) - int(14 * u), tag_x + tag_w, ty + int(tier_h / 2) + int(14 * u)], radius=int(6 * u), fill=(241, 245, 249, 255), outline=(226, 232, 240, 255), width=1)
            draw.text((tag_x + int(10 * u), ty + int(tier_h / 2) - int(7 * u)), tag_text, fill=(51, 65, 85, 255), font=f_tag)
            tag_x += tag_w + int(8 * u)


# ---------------------------------------------------------------------------
# 8. GLOBAL EDGE NETWORK & DDOS SHIELD MAP
# ---------------------------------------------------------------------------
def draw_edge_network_map(draw: ImageDraw.ImageDraw, img: Image.Image, cw: int, ch: int, el, u: float, style: str) -> None:
    """Draws Global Edge Network mesh: 600+ PoPs, CloudFront CDN, Route 53, and Shield DDoS."""
    card_x, card_y = int(20 * u), int(16 * u)
    card_w, card_h = cw - int(40 * u), ch - int(32 * u)

    apply_drop_shadow(img, card_x, card_y, card_x + card_w, card_y + card_h, radius=int(26 * u), blur=int(14 * u), alpha=24)
    draw.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h], radius=int(24 * u), fill=(255, 255, 255, 255), outline=(226, 232, 240, 255), width=2)

    # Header Banner
    hdr_x, hdr_y = card_x + int(32 * u), card_y + int(24 * u)
    draw.rounded_rectangle([hdr_x, hdr_y, card_x + card_w - int(32 * u), hdr_y + int(68 * u)], radius=int(14 * u), fill=(248, 250, 252, 255), outline=(226, 232, 240, 255), width=1)
    
    # Left Header Icon
    draw.rounded_rectangle([hdr_x + int(14 * u), hdr_y + int(12 * u), hdr_x + int(58 * u), hdr_y + int(56 * u)], radius=int(10 * u), fill=(147, 51, 234, 255))
    draw.ellipse([hdr_x + int(24 * u), hdr_y + int(22 * u), hdr_x + int(48 * u), hdr_y + int(46 * u)], outline=(255, 255, 255, 255), width=2)
    draw.line([(hdr_x + int(24 * u), hdr_y + int(34 * u)), (hdr_x + int(48 * u), hdr_y + int(34 * u))], fill=(255, 255, 255, 255), width=2)

    f_title = get_font(max(15, int(20 * u)), bold=True)
    draw.text((hdr_x + int(72 * u), hdr_y + int(14 * u)), "EDGE LOCATIONS & POINTS OF PRESENCE (PoPs)", fill=(15, 23, 42, 255), font=f_title)
    f_sub = get_font(max(10, int(12 * u)))
    draw.text((hdr_x + int(72 * u), hdr_y + int(40 * u)), "600+ Global Edge Nodes delivering ultra-low-latency caching and automated DDoS mitigation", fill=(100, 116, 139, 255), font=f_sub)

    # Right metric badge in header
    f_stat = get_font(max(11, int(14 * u)), bold=True)
    draw.rounded_rectangle([card_x + card_w - int(240 * u), hdr_y + int(16 * u), card_x + card_w - int(48 * u), hdr_y + int(52 * u)], radius=int(18 * u), fill=(243, 232, 255, 255), outline=(216, 180, 254, 255), width=1)
    draw.text((card_x + card_w - int(225 * u), hdr_y + int(24 * u)), "⚡ 600+ GLOBAL POPS", fill=(126, 34, 206, 255), font=f_stat)

    # 3 Column Pillar Cards
    pillars = [
        ("Amazon CloudFront CDN", "Content Delivery Network", (37, 99, 235, 255), [
            ("Edge Caching", "Caches static assets (images, videos, HTML) closest to viewers."),
            ("API Acceleration", "Maintains persistent TCP/TLS connections back to AWS origin."),
            ("Origin Shield", "Centralized caching layer eliminating redundant backend load."),
        ]),
        ("Amazon Route 53 Anycast", "Global DNS & Traffic Management", (249, 115, 22, 255), [
            ("Anycast Network", "Routes DNS requests to the geometrically closest healthy PoP."),
            ("Geo-Proximity Routing", "Serves distinct localized content based on user coordinates."),
            ("Automated Failover", "Monitors health checks and re-routes in under 3 seconds."),
        ]),
        ("AWS Shield & WAF", "Edge Security & DDoS Defense", (220, 38, 38, 255), [
            ("Volumetric Mitigation", "Absorbs multi-terabit SYN/UDP flood attacks at the edge."),
            ("Shield Standard ($0)", "Free automated Layer 3/4 protection for all AWS customers."),
            ("WAF Deep Inspection", "Blocks SQL injection, cross-site scripting, and malicious bots."),
        ]),
    ]

    p_w = int((card_w - int(88 * u)) / 3.0)
    p_h = card_h - int(125 * u)
    p_y = card_y + int(105 * u)

    for idx, (p_title, p_subt, col, features) in enumerate(pillars):
        px = card_x + int(32 * u) + idx * (p_w + int(12 * u))

        apply_drop_shadow(img, px, p_y, px + p_w, p_y + p_h, radius=int(18 * u), blur=int(10 * u), alpha=18)
        draw.rounded_rectangle([px, p_y, px + p_w, p_y + p_h], radius=int(16 * u), fill=(255, 255, 255, 255), outline=(226, 232, 240, 255), width=1.5)

        # Pillar Header
        draw.rounded_rectangle([px + int(16 * u), p_y + int(16 * u), px + p_w - int(16 * u), p_y + int(76 * u)], radius=int(12 * u), fill=(248, 250, 252, 255), outline=(226, 232, 240, 255), width=1)
        draw.rounded_rectangle([px + int(24 * u), p_y + int(24 * u), px + int(70 * u), p_y + int(68 * u)], radius=int(8 * u), fill=col)
        draw.text((px + int(80 * u), p_y + int(26 * u)), p_title, fill=(15, 23, 42, 255), font=get_font(max(12, int(15 * u)), bold=True))
        draw.text((px + int(80 * u), p_y + int(48 * u)), p_subt, fill=(100, 116, 139, 255), font=get_font(max(10, int(11 * u))))

        # Feature rows
        for f_i, (ft, fd) in enumerate(features):
            fy = p_y + int(94 * u) + f_i * int(110 * u)
            draw.rounded_rectangle([px + int(16 * u), fy, px + p_w - int(16 * u), fy + int(98 * u)], radius=int(10 * u), fill=(248, 250, 252, 255), outline=(226, 232, 240, 255), width=1)
            draw.rounded_rectangle([px + int(26 * u), fy + int(14 * u), px + int(30 * u), fy + int(84 * u)], radius=int(2 * u), fill=col)
            draw.text((px + int(42 * u), fy + int(18 * u)), ft, fill=(15, 23, 42, 255), font=get_font(max(11, int(14 * u)), bold=True))
            draw.text((px + int(42 * u), fy + int(46 * u)), fd, fill=(71, 85, 105, 255), font=get_font(max(10, int(11 * u))))


# ---------------------------------------------------------------------------
# 9. HYBRID EDGE: AWS OUTPOSTS & LOCAL ZONES
# ---------------------------------------------------------------------------
def draw_hybrid_outposts(draw: ImageDraw.ImageDraw, img: Image.Image, cw: int, ch: int, el, u: float, style: str) -> None:
    """Draws 2 comparative hybrid extensions: AWS Local Zones vs AWS Outposts."""
    card_x, card_y = int(20 * u), int(16 * u)
    card_w, card_h = cw - int(40 * u), ch - int(32 * u)

    apply_drop_shadow(img, card_x, card_y, card_x + card_w, card_y + card_h, radius=int(26 * u), blur=int(14 * u), alpha=24)
    draw.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h], radius=int(24 * u), fill=(255, 255, 255, 255), outline=(226, 232, 240, 255), width=2)

    # Header Banner
    hdr_x, hdr_y = card_x + int(32 * u), card_y + int(24 * u)
    draw.rounded_rectangle([hdr_x, hdr_y, card_x + card_w - int(32 * u), hdr_y + int(68 * u)], radius=int(14 * u), fill=(248, 250, 252, 255), outline=(226, 232, 240, 255), width=1)
    
    draw.rounded_rectangle([hdr_x + int(14 * u), hdr_y + int(12 * u), hdr_x + int(58 * u), hdr_y + int(56 * u)], radius=int(10 * u), fill=(14, 165, 233, 255))
    draw.rounded_rectangle([hdr_x + int(22 * u), hdr_y + int(20 * u), hdr_x + int(50 * u), hdr_y + int(48 * u)], radius=int(4 * u), outline=(255, 255, 255, 255), width=2)

    f_title = get_font(max(15, int(20 * u)), bold=True)
    draw.text((hdr_x + int(72 * u), hdr_y + int(14 * u)), "HYBRID EDGE EXTENSIONS: LOCAL ZONES & OUTPOSTS", fill=(15, 23, 42, 255), font=f_title)
    f_sub = get_font(max(10, int(12 * u)))
    draw.text((hdr_x + int(72 * u), hdr_y + int(40 * u)), "Bringing AWS compute and APIs directly into metropolitan centers and on-premise data centers", fill=(100, 116, 139, 255), font=f_sub)

    # 2 Comparison Columns
    col_w = int((card_w - int(80 * u)) / 2.0)
    col_h = card_h - int(120 * u)
    col_y = card_y + int(105 * u)
    x_left = card_x + int(32 * u)
    x_right = x_left + col_w + int(16 * u)

    # Left: AWS Local Zones
    apply_drop_shadow(img, x_left, col_y, x_left + col_w, col_y + col_h, radius=int(18 * u), blur=int(12 * u), alpha=20)
    draw.rounded_rectangle([x_left, col_y, x_left + col_w, col_y + col_h], radius=int(18 * u), fill=(255, 255, 255, 255), outline=(226, 232, 240, 255), width=1.5)

    draw.rounded_rectangle([x_left + int(20 * u), col_y + int(20 * u), x_left + col_w - int(20 * u), col_y + int(82 * u)], radius=int(12 * u), fill=(240, 249, 255, 255), outline=(186, 230, 253, 255), width=1)
    draw.rounded_rectangle([x_left + int(30 * u), col_y + int(28 * u), x_left + int(76 * u), col_y + int(74 * u)], radius=int(8 * u), fill=(2, 132, 199, 255))
    draw.text((x_left + int(90 * u), col_y + int(30 * u)), "AWS LOCAL ZONES", fill=(15, 23, 42, 255), font=get_font(max(14, int(18 * u)), bold=True))
    draw.text((x_left + int(90 * u), col_y + int(54 * u)), "Metropolitan Edge Compute Deployment", fill=(2, 132, 199, 255), font=get_font(max(10, int(12 * u)), bold=True))

    lz_rows = [
        ("Sub-10ms Single-Digit Latency", "Run EC2, EBS, and ECS in major cities (LA, Dallas, Tokyo) for real-time applications."),
        ("Direct Regional VPC Extension", "Subnets in Local Zones extend your primary VPC seamlessly with zero VPN setup."),
        ("Zero Physical Maintenance", "AWS fully manages and operates the underlying physical hardware facility."),
    ]
    for idx, (t, d) in enumerate(lz_rows):
        fy = col_y + int(98 * u) + idx * int(114 * u)
        draw.rounded_rectangle([x_left + int(20 * u), fy, x_left + col_w - int(20 * u), fy + int(102 * u)], radius=int(10 * u), fill=(248, 250, 252, 255), outline=(226, 232, 240, 255), width=1)
        draw.rounded_rectangle([x_left + int(30 * u), fy + int(16 * u), x_left + int(34 * u), fy + int(86 * u)], radius=int(2 * u), fill=(2, 132, 199, 255))
        draw.text((x_left + int(48 * u), fy + int(20 * u)), t, fill=(15, 23, 42, 255), font=get_font(max(12, int(15 * u)), bold=True))
        draw.text((x_left + int(48 * u), fy + int(48 * u)), d, fill=(71, 85, 105, 255), font=get_font(max(10, int(12 * u))))

    # Right: AWS Outposts
    apply_drop_shadow(img, x_right, col_y, x_right + col_w, col_y + col_h, radius=int(18 * u), blur=int(12 * u), alpha=20)
    draw.rounded_rectangle([x_right, col_y, x_right + col_w, col_y + col_h], radius=int(18 * u), fill=(255, 255, 255, 255), outline=(226, 232, 240, 255), width=1.5)

    draw.rounded_rectangle([x_right + int(20 * u), col_y + int(20 * u), x_right + col_w - int(20 * u), col_y + int(82 * u)], radius=int(12 * u), fill=(255, 251, 235, 255), outline=(254, 240, 138, 255), width=1)
    draw.rounded_rectangle([x_right + int(30 * u), col_y + int(28 * u), x_right + int(76 * u), col_y + int(74 * u)], radius=int(8 * u), fill=(217, 119, 6, 255))
    draw.text((x_right + int(90 * u), col_y + int(30 * u)), "AWS OUTPOSTS", fill=(15, 23, 42, 255), font=get_font(max(14, int(18 * u)), bold=True))
    draw.text((x_right + int(90 * u), col_y + int(54 * u)), "Physical 42U Server Rack On-Premises", fill=(180, 83, 9, 255), font=get_font(max(10, int(12 * u)), bold=True))

    out_rows = [
        ("Physical 42U Hardware Rack", "Delivered, assembled, and plugged in directly inside your on-premises datacenter."),
        ("Strict Data Sovereignty", "Processes healthcare, defense, and manufacturing data without leaving your building."),
        ("Unified AWS API & Tooling", "Deploy EC2 and EKS using the exact same Boto3, CLI, and IAM policies you use in cloud."),
    ]
    for idx, (t, d) in enumerate(out_rows):
        fy = col_y + int(98 * u) + idx * int(114 * u)
        draw.rounded_rectangle([x_right + int(20 * u), fy, x_right + col_w - int(20 * u), fy + int(102 * u)], radius=int(10 * u), fill=(248, 250, 252, 255), outline=(226, 232, 240, 255), width=1)
        draw.rounded_rectangle([x_right + int(30 * u), fy + int(16 * u), x_right + int(34 * u), fy + int(86 * u)], radius=int(2 * u), fill=(217, 119, 6, 255))
        draw.text((x_right + int(48 * u), fy + int(20 * u)), t, fill=(15, 23, 42, 255), font=get_font(max(12, int(15 * u)), bold=True))
        draw.text((x_right + int(48 * u), fy + int(48 * u)), d, fill=(71, 85, 105, 255), font=get_font(max(10, int(12 * u))))

