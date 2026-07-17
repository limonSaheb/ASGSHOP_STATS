from __future__ import annotations

import math
import os
from pathlib import Path

from reportlab.lib.colors import HexColor, Color, white, black
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "output" / "pdf"
TMP_DIR = ROOT / "tmp" / "pdfs"
PDF_PATH = OUTPUT_DIR / "asgshop-investor-report-q1-2026.pdf"
LOGO_PATH = ROOT / "asgshop.png"

PAGE_W, PAGE_H = A4

COLORS = {
    "ink": HexColor("#14110f"),
    "muted": HexColor("#5d5752"),
    "soft": HexColor("#8a837c"),
    "line": HexColor("#ddd5cc"),
    "paper": HexColor("#f7f2eb"),
    "paper_2": HexColor("#efe8df"),
    "card": HexColor("#fffdfa"),
    "accent": HexColor("#ff5a2a"),
    "accent_2": HexColor("#0d7c6b"),
    "accent_3": HexColor("#1955b3"),
    "gold": HexColor("#b9770e"),
    "good": HexColor("#2f7d32"),
}

DATA = {
    "active_students": 499_000,
    "new_students": 631_000,
    "engagement_seconds": 874,
    "total_events": 54_300_000,
    "transactions": 36_000,
    "cdn_bandwidth_tb": 1_132,
    "cdn_requests_m": 1_886.1,
    "mau_data": [
        201638, 199653, 197628, 196308, 194916, 192670, 190972, 190301, 189796,
        189524, 188671, 186879, 187799, 188207, 188171, 187588, 187360, 189366,
        190732, 190121, 190903, 193395, 197079, 198638, 201092, 203028, 204438,
        207640, 212915, 217326, 220473, 222760, 223783, 225311, 229473, 232962,
        234493, 237451, 241643, 245494, 247393, 248514, 246857, 246535, 246851,
        248176, 249860, 249851, 249694, 249662, 250574, 249128, 248602, 249236,
        248004, 247667, 248530, 246037, 241642, 239582, 238277, 236864, 236369,
        236089, 234042, 231581, 229660, 226989, 224316, 220729, 218678, 217441,
        217092, 216697, 215226, 212228, 210204, 207030, 203803, 199375, 196347,
        193717, 191894, 188900, 186966, 187056, 191153, 193780, 196433, 197098,
    ],
    "dau_ratio": [
        5.72, 5.63, 5.87, 6.25, 6.33, 6.26, 6.23, 6.0, 5.61, 5.63, 5.43, 5.63,
        10.17, 12.62, 11.87, 11.54, 11.2, 12.75, 12.39, 12.15, 11.11, 12.04,
        11.83, 11.31, 11.59, 10.91, 10.38, 11.3, 11.97, 11.81, 11.25, 10.94,
        10.25, 10.26, 11.53, 11.57, 10.73, 10.95, 11.41, 11.4, 11.08, 10.25,
        6.87, 9.1, 9.98, 11.09, 11.04, 11.24, 11.21, 12.3, 12.4, 12.22, 12.68,
        12.86, 12.5, 12.48, 11.92, 11.49, 12.24, 13.31, 13.76, 12.95, 12.56,
        11.96, 12.2, 12.64, 12.14, 12.4, 12.44, 12.06, 11.87, 11.28, 11.11,
        10.97, 9.94, 10.0, 9.62, 8.84, 6.4, 4.05, 6.83, 8.45, 10.04, 11.26,
        12.32, 15.27, 18.64, 17.95, 19.82, 19.08,
    ],
    "returning_daily": [
        8428, 8199, 8462, 8825, 9000, 8909, 8474, 8110, 7557, 7431, 7168, 7418,
        11063, 16475, 16748, 16906, 16702, 18997, 18814, 18743, 17155, 18010,
        17606, 17794, 18052, 17203, 16525, 17263, 18218, 18749, 19223, 19381,
        18657, 18207, 20841, 21591, 20810, 20964, 21667, 21721, 22184, 21968,
        14402, 19155, 21317, 23267, 23553, 24154, 24149, 26863, 27225, 26994,
        27228, 27235, 26880, 26460, 25386, 24656, 25435, 27223, 27993, 26783,
        26262, 25171, 25623, 26215, 25157, 25526, 25137, 24252, 23487, 22349,
        22097, 21365, 18986, 19024, 18026, 16317, 11469, 6950, 11473, 14323,
        17003, 18921, 20555, 24825, 30575, 30191, 34164, 33482,
    ],
    "new_daily": [
        3374, 3294, 3476, 3670, 3669, 3543, 3816, 3675, 3467, 3468, 3322, 3414,
        13996, 13642, 9087, 7610, 6710, 7618, 6819, 6587, 5783, 6973, 7592,
        6536, 7262, 7020, 6452, 7998, 9400, 8818, 7669, 6996, 6393, 6863, 8490,
        11148, 8338, 7608, 9386, 9730, 8531, 6534, 3486, 5552, 5977, 6704, 6852,
        6310, 6507, 6780, 6707, 5981, 6894, 7243, 6529, 6438, 6303, 5929, 5903,
        8193, 7589, 6468, 5632, 5021, 5251, 5099, 4647, 4786, 4567, 4102, 4033,
        3729, 3369, 3746, 3279, 3347, 3106, 2757, 2034, 1408, 2436, 2757, 3523,
        3850, 4018, 6449, 9794, 8360, 8987, 8001,
    ],
    "top_pages": [
        ("FRB-26 Final Revision", 15.78, "12.4%"),
        ("HSC Academic Program", 5.83, "16.6%"),
        ("Admission Special", 2.92, "31.1%"),
        ("Shop | Apar's Classroom", 0.588, "12.1%"),
        ("HSC 27 Academic Cycles", 0.416, "6.6%"),
        ("FRB-26 Full Syllabus", 0.348, "34.8%"),
    ],
    "acquisition": [
        ("Direct", 42.8),
        ("Google Organic", 40.0),
        ("Paid Social", 13.0),
        ("Apars Referral", 4.3),
    ],
    "cities": [
        ("Dhaka", 164.0),
        ("Chattogram", 48.3),
        ("Rajshahi", 29.0),
        ("Khulna", 25.9),
        ("Cumilla", 13.8),
        ("Sylhet", 13.8),
    ],
    "cdn_months": [
        ("January 2026", 352, 601.3, 92.98, 344, 16.9),
        ("February 2026", 345, 588.2, 92.82, 327, 17.3),
        ("March 2026", 435, 696.6, 91.63, 253, 19.2),
    ],
    "geo_traffic": [
        ("Singapore", 1030),
        ("Frankfurt", 66),
        ("Paris", 31),
        ("Chicago", 6),
        ("Los Angeles", 1),
    ],
}


def fmt_int(n: float) -> str:
    return f"{int(round(n)):,}"


def fmt_compact(n: float) -> str:
    if n >= 1_000_000_000:
        return f"{n / 1_000_000_000:.2f}B"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.0f}K"
    return str(int(round(n)))


def wrap_text(text: str, font: str, size: int, width: float) -> list[str]:
    words = text.split()
    if not words:
        return []
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = current + " " + word
        if stringWidth(candidate, font, size) <= width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def draw_wrapped(
    c: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    width: float,
    font: str,
    size: int,
    color=black,
    leading: float | None = None,
) -> float:
    leading = leading or size * 1.35
    lines = wrap_text(text, font, size, width)
    t = c.beginText(x, y)
    t.setFont(font, size)
    t.setLeading(leading)
    t.setFillColor(color)
    for line in lines:
        t.textLine(line)
    c.drawText(t)
    return y - len(lines) * leading


def add_footer(c: canvas.Canvas, page_num: int) -> None:
    c.setStrokeColor(COLORS["line"])
    c.line(40, 30, PAGE_W - 40, 30)
    c.setFont("Helvetica", 8)
    c.setFillColor(COLORS["soft"])
    c.drawString(40, 18, "ASG Shop Investor Report | Q1 2026 | Confidential")
    c.drawRightString(PAGE_W - 40, 18, f"Page {page_num}")


def draw_header(c: canvas.Canvas, section: str, title: str, subtitle: str, page_num: int) -> None:
    c.setFillColor(COLORS["paper"])
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    c.setFillColor(COLORS["paper_2"])
    c.roundRect(32, PAGE_H - 85, PAGE_W - 64, 38, 12, stroke=0, fill=1)
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(COLORS["accent"])
    c.drawString(48, PAGE_H - 70, section.upper())
    title_lines = wrap_text(title, "Helvetica-Bold", 26, PAGE_W - 96)
    title_text = c.beginText(48, PAGE_H - 118)
    title_text.setFont("Helvetica-Bold", 26)
    title_text.setLeading(30)
    title_text.setFillColor(COLORS["ink"])
    for line in title_lines:
        title_text.textLine(line)
    c.drawText(title_text)
    add_footer(c, page_num)


def card(c: canvas.Canvas, x: float, y: float, w: float, h: float, fill, stroke=None, radius: int = 16) -> None:
    c.setFillColor(fill)
    c.setStrokeColor(stroke or fill)
    c.roundRect(x, y, w, h, radius, stroke=1 if stroke else 0, fill=1)


def draw_metric_card(
    c: canvas.Canvas,
    x: float,
    y: float,
    w: float,
    h: float,
    label: str,
    value: str,
    note: str,
    accent,
) -> None:
    card(c, x, y, w, h, COLORS["card"], COLORS["line"])
    c.setFillColor(accent)
    c.roundRect(x + 14, y + h - 22, 34, 6, 3, stroke=0, fill=1)
    c.setFillColor(COLORS["soft"])
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x + 16, y + h - 40, label.upper())
    c.setFillColor(COLORS["ink"])
    c.setFont("Helvetica-Bold", 22)
    c.drawString(x + 16, y + h - 62, value)
    draw_wrapped(c, note, x + 16, y + 16, w - 32, "Helvetica", 8, COLORS["muted"], 10)


def draw_bullet_list(c: canvas.Canvas, items: list[str], x: float, y: float, width: float, size: int = 11) -> float:
    current_y = y
    for item in items:
        c.setFillColor(COLORS["accent"])
        c.circle(x + 4, current_y - 4, 2.3, stroke=0, fill=1)
        current_y = draw_wrapped(c, item, x + 14, current_y, width - 14, "Helvetica", size, COLORS["ink"], size * 1.4)
        current_y -= 8
    return current_y


def draw_line_chart(
    c: canvas.Canvas,
    x: float,
    y: float,
    w: float,
    h: float,
    data: list[float],
    color,
    title: str,
    y_labels: tuple[str, str, str],
) -> None:
    card(c, x, y, w, h, COLORS["card"], COLORS["line"])
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(COLORS["ink"])
    c.drawString(x + 16, y + h - 24, title)

    plot_x = x + 16
    plot_y = y + 22
    plot_w = w - 32
    plot_h = h - 56

    min_v = min(data)
    max_v = max(data)
    spread = max(max_v - min_v, 1)

    c.setStrokeColor(COLORS["line"])
    c.setLineWidth(0.8)
    for i in range(3):
        gy = plot_y + (plot_h * i / 2)
        c.line(plot_x, gy, plot_x + plot_w, gy)
        c.setFont("Helvetica", 8)
        c.setFillColor(COLORS["soft"])
        c.drawRightString(plot_x - 4, gy - 2, y_labels[i])

    pts = []
    for idx, value in enumerate(data):
        px = plot_x + (plot_w * idx / (len(data) - 1))
        py = plot_y + ((value - min_v) / spread) * plot_h
        pts.append((px, py))

    c.setStrokeColor(color)
    c.setLineWidth(2.2)
    p = c.beginPath()
    p.moveTo(*pts[0])
    for px, py in pts[1:]:
        p.lineTo(px, py)
    c.drawPath(p, stroke=1, fill=0)

    c.setFillColor(Color(color.red, color.green, color.blue, alpha=0.08))
    area = c.beginPath()
    area.moveTo(plot_x, plot_y)
    for px, py in pts:
        area.lineTo(px, py)
    area.lineTo(plot_x + plot_w, plot_y)
    area.close()
    c.drawPath(area, stroke=0, fill=1)


def draw_stacked_bar_chart(
    c: canvas.Canvas,
    x: float,
    y: float,
    w: float,
    h: float,
    returning: list[int],
    new: list[int],
    title: str,
) -> None:
    card(c, x, y, w, h, COLORS["card"], COLORS["line"])
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(COLORS["ink"])
    c.drawString(x + 16, y + h - 24, title)
    plot_x = x + 16
    plot_y = y + 22
    plot_w = w - 32
    plot_h = h - 60

    sample_idx = list(range(0, len(returning), 3))
    vals = [(returning[i], new[i]) for i in sample_idx]
    max_total = max(r + n for r, n in vals)
    bar_gap = 2
    bar_w = max((plot_w / len(vals)) - bar_gap, 1)

    c.setStrokeColor(COLORS["line"])
    for i in range(4):
        gy = plot_y + (plot_h * i / 3)
        c.line(plot_x, gy, plot_x + plot_w, gy)

    for pos, (r_val, n_val) in enumerate(vals):
        bx = plot_x + pos * (bar_w + bar_gap)
        r_h = (r_val / max_total) * plot_h
        n_h = (n_val / max_total) * plot_h
        c.setFillColor(Color(COLORS["ink"].red, COLORS["ink"].green, COLORS["ink"].blue, alpha=0.72))
        c.rect(bx, plot_y, bar_w, r_h, stroke=0, fill=1)
        c.setFillColor(Color(COLORS["accent"].red, COLORS["accent"].green, COLORS["accent"].blue, alpha=0.78))
        c.rect(bx, plot_y + r_h, bar_w, n_h, stroke=0, fill=1)

    c.setFillColor(COLORS["ink"])
    c.circle(x + 18, y + h - 42, 3, stroke=0, fill=1)
    c.setFont("Helvetica", 8)
    c.drawString(x + 26, y + h - 45, "Returning")
    c.setFillColor(COLORS["accent"])
    c.circle(x + 86, y + h - 42, 3, stroke=0, fill=1)
    c.drawString(x + 94, y + h - 45, "New")


def draw_hbar_list(
    c: canvas.Canvas,
    x: float,
    y: float,
    w: float,
    h: float,
    title: str,
    items: list[tuple[str, float]],
    suffix: str,
    color,
) -> None:
    card(c, x, y, w, h, COLORS["card"], COLORS["line"])
    c.setFillColor(COLORS["ink"])
    c.setFont("Helvetica-Bold", 11)
    c.drawString(x + 16, y + h - 24, title)

    inner_y = y + h - 54
    max_v = max(v for _, v in items)
    row_h = (h - 72) / len(items)
    for idx, (label, value) in enumerate(items):
        ry = inner_y - idx * row_h
        c.setFont("Helvetica", 9)
        c.setFillColor(COLORS["ink"])
        c.drawString(x + 16, ry, label)
        c.setFillColor(COLORS["paper_2"])
        c.roundRect(x + 16, ry - 14, w - 120, 8, 4, stroke=0, fill=1)
        c.setFillColor(color)
        fill_w = (w - 120) * (value / max_v)
        c.roundRect(x + 16, ry - 14, fill_w, 8, 4, stroke=0, fill=1)
        c.setFillColor(COLORS["muted"])
        c.drawRightString(x + w - 16, ry, f"{value:.1f}{suffix}")


def draw_table(c: canvas.Canvas, x: float, y: float, w: float, row_h: float, headers: list[str], rows: list[list[str]]) -> None:
    total_h = row_h * (len(rows) + 1)
    card(c, x, y - total_h, w, total_h, COLORS["card"], COLORS["line"])
    col_widths = [0.48 * w, 0.16 * w, 0.16 * w, 0.20 * w]
    cursor = x
    c.setFillColor(COLORS["paper_2"])
    c.roundRect(x, y - row_h, w, row_h, 14, stroke=0, fill=1)
    for i, header in enumerate(headers):
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(COLORS["muted"])
        c.drawString(cursor + 10, y - 18, header.upper())
        cursor += col_widths[i]

    for row_idx, row in enumerate(rows):
        top = y - row_h * (row_idx + 1)
        c.setStrokeColor(COLORS["line"])
        c.line(x + 8, top - row_h + 2, x + w - 8, top - row_h + 2)
        cursor = x
        for i, cell in enumerate(row):
            c.setFont("Helvetica-Bold" if i == 0 else "Helvetica", 9)
            c.setFillColor(COLORS["ink"])
            align_right = i > 0
            if align_right:
                c.drawRightString(cursor + col_widths[i] - 10, top - 18, cell)
            else:
                c.drawString(cursor + 10, top - 18, cell)
            cursor += col_widths[i]


def cover_page(c: canvas.Canvas) -> None:
    c.setFillColor(COLORS["ink"])
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    c.setFillColor(Color(1, 1, 1, alpha=0.05))
    c.circle(PAGE_W - 80, PAGE_H - 120, 160, stroke=0, fill=1)
    c.circle(90, 100, 140, stroke=0, fill=1)
    c.setFillColor(COLORS["accent"])
    c.rect(48, PAGE_H - 112, 120, 8, stroke=0, fill=1)

    if LOGO_PATH.exists():
        logo = ImageReader(str(LOGO_PATH))
        c.drawImage(logo, 48, PAGE_H - 94, width=112, height=48, mask="auto", preserveAspectRatio=True)

    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(48, PAGE_H - 140, "Investor Presentation Report")
    c.setFont("Helvetica-Bold", 31)
    c.drawString(48, PAGE_H - 208, "ASG Shop")
    c.setFont("Times-Italic", 28)
    c.drawString(48, PAGE_H - 245, "Q1 2026 traction, scale and readiness")
    draw_wrapped(
        c,
        "A print-first briefing designed for investor conversations. Built from internal platform analytics covering Jan 1 to Mar 31, 2026.",
        48,
        PAGE_H - 292,
        360,
        "Helvetica",
        12,
        Color(1, 1, 1, alpha=0.82),
        18,
    )

    highlights = [
        ("499K", "active students"),
        ("54.3M", "total learning events"),
        ("36K+", "transactions in the quarter"),
        ("1.89B", "edge requests served"),
    ]
    base_y = PAGE_H - 430
    for idx, (value, label) in enumerate(highlights):
        box_x = 48 + (idx % 2) * 250
        box_y = base_y - (idx // 2) * 112
        card(c, box_x, box_y, 220, 86, Color(1, 1, 1, alpha=0.06), Color(1, 1, 1, alpha=0.10))
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 24)
        c.drawString(box_x + 16, box_y + 48, value)
        c.setFillColor(Color(1, 1, 1, alpha=0.76))
        c.setFont("Helvetica", 10)
        c.drawString(box_x + 16, box_y + 24, label.upper())

    c.setFillColor(Color(1, 1, 1, alpha=0.68))
    c.setFont("Helvetica", 9)
    c.drawString(48, 32, "Prepared from ASG Shop internal analytics and infrastructure telemetry.")


def page_one(c: canvas.Canvas) -> None:
    draw_header(
        c,
        "Executive Summary",
        "Why this quarter matters",
        "The platform shows evidence of scale, demand durability, and infrastructure discipline - three signals investors care about early.",
        2,
    )
    draw_metric_card(c, 48, 620, 156, 96, "Active Students", "499K", "A large engaged learner base in one quarter.", COLORS["accent"])
    draw_metric_card(c, 218, 620, 156, 96, "New Students", "631K", "Top of funnel is still expanding beyond the active base.", COLORS["accent_2"])
    draw_metric_card(c, 388, 620, 156, 96, "Engagement", "14m 34s", "High-intent usage rather than low-value browsing.", COLORS["accent_3"])

    card(c, 48, 400, 496, 188, COLORS["card"], COLORS["line"])
    c.setFillColor(COLORS["ink"])
    c.setFont("Helvetica-Bold", 14)
    c.drawString(64, 560, "Investor takeaway")
    bullets = [
        "ASG Shop is not just attracting visits; it is sustaining deep study behavior, with 54.3 million tracked events and nearly 15 minutes of average engagement per active student.",
        "Growth quality looks strong. More than 80% of first-touch acquisition came from direct and organic channels, indicating brand pull and efficient demand generation.",
        "The product is serving national scale already, with 1.13 PB of bandwidth and 1.89 billion requests delivered in Q1 while maintaining cache hit rates above 91%.",
        "Content concentration around flagship programs creates visible monetization and brand leverage, especially around FRB-26 and broader HSC preparation pathways.",
    ]
    draw_bullet_list(c, bullets, 68, 532, 452, 11)

    card(c, 48, 178, 240, 190, COLORS["card"], COLORS["line"])
    c.setFillColor(COLORS["ink"])
    c.setFont("Helvetica-Bold", 13)
    c.drawString(64, 340, "What this report is designed to prove")
    draw_bullet_list(
        c,
        [
            "There is already meaningful demand at national scale.",
            "Learner behavior suggests trust, habit and repeat usage.",
            "Core infrastructure can absorb very large spikes efficiently.",
            "The business has the foundations for investor-backed acceleration.",
        ],
        68,
        314,
        200,
        10,
    )

    card(c, 304, 178, 240, 190, COLORS["ink"], None)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(320, 340, "Important note")
    draw_wrapped(
        c,
        "This deck uses operating and usage metrics already present in the codebase. It is intentionally investor-facing, but it is not a financial statement or a valuation memo.",
        320,
        314,
        200,
        "Helvetica",
        10,
        Color(1, 1, 1, alpha=0.82),
        14,
    )


def page_two(c: canvas.Canvas) -> None:
    draw_header(
        c,
        "Traction",
        "Platform adoption has reached visible scale",
        "The topline metrics suggest a product that is already operating beyond prototype stage and into repeatable demand.",
        3,
    )
    draw_metric_card(c, 48, 610, 156, 88, "Transactions", "36K+", "Commercial activity is already present on the platform.", COLORS["gold"])
    draw_metric_card(c, 218, 610, 156, 88, "Total Events", "54.3M", "Usage depth creates strong internal feedback loops.", COLORS["accent"])
    draw_metric_card(c, 388, 610, 156, 88, "Edge Bandwidth", "1.13 PB", "Usage is heavy enough to stress real infrastructure.", COLORS["accent_2"])

    draw_line_chart(c, 48, 352, 322, 228, DATA["mau_data"], COLORS["accent"], "Rolling 30-day active students", ("187K", "219K", "251K"))
    draw_stacked_bar_chart(c, 382, 352, 162, 228, DATA["returning_daily"], DATA["new_daily"], "Returning vs new mix")

    card(c, 48, 116, 496, 210, COLORS["card"], COLORS["line"])
    c.setFillColor(COLORS["ink"])
    c.setFont("Helvetica-Bold", 13)
    c.drawString(64, 296, "How to read the quarter")
    bullets = [
        "The active-student curve peaked near 250K in February and held much of that scale through the remainder of the quarter, ending above the January starting base.",
        "Returning users dominate most of the quarter, a useful sign that the product is building learning habits rather than one-time curiosity traffic.",
        "A 631K inflow of new students on top of a 499K active base implies continued market expansion rather than simple recycling of the same cohort.",
    ]
    draw_bullet_list(c, bullets, 68, 270, 452, 11)


def page_three(c: canvas.Canvas) -> None:
    draw_header(
        c,
        "Engagement",
        "Behavior suggests trust, utility and repeat learning",
        "Strong engagement matters because it tends to precede better monetization, stronger retention and lower acquisition dependency.",
        4,
    )
    draw_metric_card(c, 48, 614, 156, 88, "Avg Engagement", "14m 34s", "874 seconds per active student in the quarter.", COLORS["accent"])
    draw_metric_card(c, 218, 614, 156, 88, "Peak DAU/MAU", "19.8%", "Healthy short-cycle habit formation at peak.", COLORS["accent_3"])
    draw_metric_card(c, 388, 614, 156, 88, "Peak WAU/MAU", "50.5%", "Usage remains relevant through the week.", COLORS["accent_2"])

    draw_line_chart(c, 48, 348, 248, 238, DATA["dau_ratio"], COLORS["accent_3"], "Daily engagement intensity", ("4%", "12%", "20%"))
    draw_hbar_list(
        c,
        310,
        348,
        234,
        238,
        "Flagship content by views",
        [(name, views) for name, views, _ in DATA["top_pages"][:5]],
        "M",
        COLORS["accent"],
    )

    headers = ["Page", "Views", "Bounce", "Signal"]
    rows = []
    signals = [
        "Flagship",
        "Core program",
        "Campaign-scale",
        "Marketplace",
        "Emerging",
        "High-opportunity",
    ]
    for idx, item in enumerate(DATA["top_pages"]):
        name, views, bounce = item
        rows.append([name, f"{views:.2f}M" if views >= 1 else f"{views * 1000:.0f}K", bounce, signals[idx]])
    draw_table(c, 48, 312, 496, 30, headers, rows)


def page_four(c: canvas.Canvas) -> None:
    draw_header(
        c,
        "Acquisition",
        "Brand pull is carrying most of the growth load",
        "For investors, a channel mix led by direct and organic demand is usually a stronger signal than raw traffic alone.",
        5,
    )
    draw_hbar_list(c, 48, 430, 240, 270, "First-touch acquisition mix", DATA["acquisition"], "%", COLORS["accent_3"])
    draw_hbar_list(c, 304, 430, 240, 270, "Top student cities", DATA["cities"], "K", COLORS["accent_2"])

    card(c, 48, 132, 496, 262, COLORS["card"], COLORS["line"])
    c.setFillColor(COLORS["ink"])
    c.setFont("Helvetica-Bold", 13)
    c.drawString(64, 366, "Why investors should care")
    bullets = [
        "Direct plus organic search account for 82.8% of acquisition, which lowers dependence on paid media and points to rising brand authority.",
        "Paid social still contributes a meaningful 13.0%, showing the team can layer performance marketing on top of organic demand rather than rely on it.",
        "Geographic concentration in Bangladesh's major cities suggests a strong domestic wedge before broader regional expansion.",
        "The combination of strong flagship content and efficient acquisition is exactly the kind of base from which category leaders often compound.",
    ]
    draw_bullet_list(c, bullets, 68, 340, 452, 11)


def page_five(c: canvas.Canvas) -> None:
    draw_header(
        c,
        "Infrastructure",
        "The platform is already operating like a scaled service",
        "Good investor materials should show not only growth, but the ability to absorb growth without breaking margins or user experience.",
        6,
    )
    month_w = 156
    for idx, month in enumerate(DATA["cdn_months"]):
        name, bandwidth, requests, hit_rate, origin_ms, origin_tb = month
        x = 48 + idx * 170
        card(c, x, 470, month_w, 220, COLORS["card"], COLORS["line"])
        c.setFillColor(COLORS["soft"])
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x + 16, 664, name.upper())
        c.setFillColor(COLORS["accent"] if idx == 2 else COLORS["ink"])
        c.setFont("Helvetica-Bold", 22)
        c.drawString(x + 16, 626, f"{bandwidth} TB")
        c.setFillColor(COLORS["muted"])
        c.setFont("Helvetica", 9)
        rows = [
            ("Requests", f"{requests:.1f}M"),
            ("Cache hit", f"{hit_rate:.2f}%"),
            ("Origin ms", f"{origin_ms}"),
            ("Origin traffic", f"{origin_tb:.1f} TB"),
        ]
        row_y = 590
        for label, value in rows:
            c.drawString(x + 16, row_y, label)
            c.setFillColor(COLORS["ink"])
            c.drawRightString(x + month_w - 16, row_y, value)
            c.setFillColor(COLORS["muted"])
            c.setStrokeColor(COLORS["line"])
            c.line(x + 16, row_y - 10, x + month_w - 16, row_y - 10)
            row_y -= 34

    draw_hbar_list(c, 48, 176, 240, 248, "Traffic by data center", DATA["geo_traffic"], " TB", COLORS["accent"])

    card(c, 304, 176, 240, 248, COLORS["ink"], None)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(320, 398, "Infrastructure signal")
    draw_bullet_list(
        c,
        [
            "1.89 billion requests in a quarter indicate meaningful operational maturity.",
            "Cache hit rates above 91% through all three months suggest disciplined delivery economics.",
            "Singapore handling roughly 98% of traffic is operationally aligned with Bangladesh demand patterns.",
            "March delivered the highest bandwidth and request volume while improving origin response time to 253 ms.",
        ],
        320,
        372,
        200,
        10,
    )


def page_six(c: canvas.Canvas) -> None:
    draw_header(
        c,
        "Investment Case",
        "What this quarter supports in an investor discussion",
        "The strongest argument is not that every number is perfect. It is that the platform already demonstrates scale, habit and operational readiness before outside capital is fully deployed.",
        7,
    )
    card(c, 48, 448, 496, 248, COLORS["card"], COLORS["line"])
    c.setFillColor(COLORS["ink"])
    c.setFont("Helvetica-Bold", 14)
    c.drawString(64, 668, "A concise investor narrative")
    narrative = [
        "ASG Shop appears to have already crossed the hardest early hurdle: proving that a large learner base will repeatedly use the product for serious study, not just sample it.",
        "The flagship content ecosystem is strong enough to pull millions of views, while the acquisition mix suggests that trust and brand memory are doing much of the heavy lifting.",
        "Infrastructure is not hypothetical. The team is already supporting internet-scale traffic patterns with disciplined delivery performance.",
        "That combination creates a credible case for growth capital focused on product expansion, distribution and monetization acceleration.",
    ]
    draw_bullet_list(c, narrative, 68, 640, 452, 11)

    draw_metric_card(c, 48, 292, 156, 116, "Demand", "82.8%", "Of acquisition comes from direct plus organic channels.", COLORS["accent"])
    draw_metric_card(c, 218, 292, 156, 116, "Depth", "15.78M", "Views on the lead flagship program in one quarter.", COLORS["accent_2"])
    draw_metric_card(c, 388, 292, 156, 116, "Readiness", "253 ms", "Best monthly origin response time in March.", COLORS["accent_3"])

    card(c, 48, 120, 496, 140, COLORS["ink"], None)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(64, 230, "Recommended use in the room")
    draw_wrapped(
        c,
        "Use this document as a leave-behind after the live conversation. It is strongest when paired with a spoken founder story, current revenue details, and a clear funding ask tailored to the investor.",
        64,
        206,
        452,
        "Helvetica",
        10,
        Color(1, 1, 1, alpha=0.82),
        14,
    )


def build_pdf() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(PDF_PATH), pagesize=A4)
    c.setTitle("ASG Shop Investor Report - Q1 2026")
    c.setAuthor("Codex for ASG Shop")
    c.setSubject("Investor-grade printed presentation report")

    cover_page(c)
    c.showPage()
    page_one(c)
    c.showPage()
    page_two(c)
    c.showPage()
    page_three(c)
    c.showPage()
    page_four(c)
    c.showPage()
    page_five(c)
    c.showPage()
    page_six(c)
    c.save()


if __name__ == "__main__":
    build_pdf()
