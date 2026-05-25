"""
pdf_report.py
Dark-theme PDF report generator for Business Idea Novelty Analyzer.
Called from app.py's /download_report route.
"""

import math
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors

# ── Colour palette ────────────────────────────────────────────────────────────
BG          = colors.HexColor("#0d1117")
CARD        = colors.HexColor("#161b22")
CARD2       = colors.HexColor("#1c2128")
GREEN       = colors.HexColor("#39d353")
GREEN_DIM   = colors.HexColor("#1a4a2e")
GOLD        = colors.HexColor("#e3a008")
ORANGE      = colors.HexColor("#f97316")
RED_C       = colors.HexColor("#ef4444")
TEXT        = colors.HexColor("#e6edf3")
TEXT_DIM    = colors.HexColor("#8b949e")
TEXT_DIMMER = colors.HexColor("#484f58")
BORDER      = colors.HexColor("#30363d")

W, H = A4  # 595 x 842 pt


# ── Helpers ───────────────────────────────────────────────────────────────────

def rr(c, x, y, w, h, r, fill, stroke=None, sw=0.5):
    """Draw a rounded rectangle."""
    c.saveState()
    c.setFillColor(fill)
    if stroke:
        c.setStrokeColor(stroke)
        c.setLineWidth(sw)
    else:
        c.setStrokeColor(fill)
        c.setLineWidth(0)
    p = c.beginPath()
    p.moveTo(x + r, y)
    p.lineTo(x + w - r, y)
    p.arcTo(x + w - 2*r, y,        x + w,     y + 2*r, -90, 90)
    p.lineTo(x + w,      y + h - r)
    p.arcTo(x + w - 2*r, y + h - 2*r, x + w, y + h,   0,   90)
    p.lineTo(x + r,      y + h)
    p.arcTo(x,           y + h - 2*r, x + 2*r, y + h,  90,  90)
    p.lineTo(x,          y + r)
    p.arcTo(x,           y,        x + 2*r,   y + 2*r, 180, 90)
    p.close()
    c.drawPath(p, fill=1, stroke=1 if stroke else 0)
    c.restoreState()


def wrap_text(c, text, font, size, max_w):
    """Return list of lines that fit within max_w."""
    c.setFont(font, size)
    words = text.split()
    lines, line = [], ""
    for word in words:
        test = (line + " " + word).strip()
        if c.stringWidth(test, font, size) <= max_w:
            line = test
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def sim_color(sim):
    if sim >= 55:
        return GREEN
    elif sim >= 45:
        return GOLD
    else:
        return ORANGE


def verdict_color(score):
    if score >= 75:
        return GREEN
    elif score >= 50:
        return GOLD
    elif score >= 30:
        return ORANGE
    else:
        return RED_C


# ── Section drawers ───────────────────────────────────────────────────────────

def draw_page_bg(c):
    c.setFillColor(BG)
    c.rect(0, 0, W, H, fill=1, stroke=0)


def draw_header(c):
    """Returns y cursor after header."""
    # Ticker strip
    c.setFillColor(GREEN_DIM)
    c.rect(0, H - 20, W, 20, fill=1, stroke=0)
    ticker = "SEMANTIC SIMILARITY ENGINE  ·  REAL-TIME WEB ANALYSIS  ·  SENTENCE-BERT POWERED  ·  MCA FINAL YEAR PROJECT  ·  "
    c.setFont("Helvetica", 6)
    c.setFillColor(GREEN)
    c.drawCentredString(W/2, H - 13, ticker)

    # Vol / Issue
    y = H - 34
    c.setFont("Helvetica", 7)
    c.setFillColor(TEXT_DIM)
    c.drawString(30, y, "VOL. 1  ·  APRIL 3, 2026")
    c.drawRightString(W - 30, y, "ISSUE NO. 01  ·  ANALYSIS DESK")

    c.setStrokeColor(BORDER)
    c.setLineWidth(0.3)
    c.line(30, y - 5, W - 30, y - 5)

    # Title
    c.setFont("Helvetica-Bold", 30)
    c.setFillColor(TEXT)
    c.drawCentredString(W/2, H - 70, "Business Idea")
    c.setFont("Helvetica-BoldOblique", 30)
    c.setFillColor(GREEN)
    c.drawCentredString(W/2, H - 98, "Novelty")
    c.setFont("Helvetica", 7.5)
    c.setFillColor(TEXT_DIM)
    c.drawCentredString(W/2, H - 112, "I N T E L L I G E N C E   R E P O R T")

    # Nav bar
    nav_y = H - 132
    c.setFillColor(CARD)
    c.rect(0, nav_y - 10, W, 24, fill=1, stroke=0)
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.3)
    c.line(0, nav_y - 10, W, nav_y - 10)
    c.line(0, nav_y + 14, W, nav_y + 14)
    nav_items = ["IDEA ANALYSIS", "MARKET INTELLIGENCE", "SIMILARITY REPORT", "INNOVATION INDEX", "STARTUP DESK"]
    gap = W / len(nav_items)
    c.setFont("Helvetica", 6)
    c.setFillColor(TEXT_DIM)
    for i, item in enumerate(nav_items):
        c.drawCentredString(gap*i + gap/2, nav_y - 1, item)

    return H - 158


def draw_idea_block(c, y, idea):
    """Exclusive analysis tag + idea text. Returns new y."""
    # Tag
    c.setStrokeColor(GREEN)
    c.setLineWidth(1.2)
    c.line(30, y, 48, y)
    c.setFont("Helvetica", 6.5)
    c.setFillColor(GREEN)
    c.drawString(52, y - 3, "EXCLUSIVE ANALYSIS")
    y -= 16

    # Idea text
    lines = wrap_text(c, f'"{idea}"', "Helvetica-BoldOblique", 10.5, W - 60)
    c.setFillColor(TEXT)
    for line in lines:
        c.setFont("Helvetica-BoldOblique", 10.5)
        c.drawString(30, y, line)
        y -= 14

    c.setStrokeColor(BORDER)
    c.setLineWidth(0.3)
    c.line(30, y - 3, W - 30, y - 3)
    return y - 14


def draw_score_radar(c, y, novelty_score, verdict, category, radar, avg_similarity):
    """Score card left + radar right. Returns new y."""
    sh = 178
    pad = 10

    # ── Left: Score card ──────────────────────────────────────────
    lx, lw = 30, 238
    rr(c, lx, y - sh, lw, sh, 8, CARD, BORDER, 0.5)

    vc = verdict_color(novelty_score)

    # Big number
    c.setFont("Helvetica-Bold", 54)
    c.setFillColor(vc)
    c.drawString(lx + 18, y - 62, str(int(novelty_score)))

    # Verdict
    c.setFont("Helvetica-BoldOblique", 12)
    c.setFillColor(vc)
    c.drawString(lx + 18, y - 80, verdict)

    # Category badge
    bx, by = lx + 18, y - 100
    badge_label = f"◆ {category}"
    bw = c.stringWidth(badge_label, "Helvetica-Bold", 7.5) + 14
    rr(c, bx, by - 2, bw, 15, 4, GREEN_DIM)
    c.setFont("Helvetica-Bold", 7.5)
    c.setFillColor(GREEN)
    c.drawString(bx + 7, by + 5, badge_label)

    # Score bar
    bary = y - 128
    barx = lx + 18
    barw = lw - 36
    rr(c, barx, bary, barw, 5, 2, CARD2)
    rr(c, barx, bary, barw * novelty_score / 100, 5, 2, vc)

    # Bar labels
    c.setFont("Helvetica", 5.5)
    c.setFillColor(TEXT_DIMMER)
    c.drawString(barx, bary - 9, "HIGHLY SIMILAR")
    c.drawCentredString(barx + barw/2, bary - 9, "MODERATELY NOVEL")
    c.drawRightString(barx + barw, bary - 9, "HIGHLY NOVEL")

    # Avg similarity line
    c.setFont("Helvetica", 6.5)
    c.setFillColor(TEXT_DIM)
    c.drawString(lx + 18, y - 155, f"Avg Similarity: {avg_similarity:.1f}%")

    # "NOVELTY SCORE" label bottom
    c.setFont("Helvetica", 6.5)
    c.setFillColor(TEXT_DIMMER)
    c.drawString(lx + 18, y - sh + 12, "NOVELTY SCORE")

    # ── Right: Radar card ─────────────────────────────────────────
    rx = 278
    rw = W - rx - 30
    rr(c, rx, y - sh, rw, sh, 8, CARD, BORDER, 0.5)

    # Title
    c.setFont("Helvetica-BoldOblique", 9.5)
    c.setFillColor(TEXT)
    c.drawCentredString(rx + rw/2, y - 16, "Innovation Radar")

    # Radar pentagon
    chart_cx = rx + rw * 0.36
    chart_cy = y - sh/2 - 4
    _draw_radar(c, chart_cx, chart_cy, 46, radar)

    # Score list
    sx = rx + rw * 0.64
    item_y = y - 28
    for label, val in radar.items():
        c.setFont("Helvetica", 6.5)
        c.setFillColor(TEXT_DIM)
        c.drawString(sx, item_y, label.upper())
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(GREEN)
        c.drawRightString(rx + rw - 10, item_y, str(int(val)))
        mb_w = rw * 0.32
        rr(c, sx, item_y - 7, mb_w, 3, 1, CARD2)
        rr(c, sx, item_y - 7, mb_w * val/100, 3, 1, GREEN)
        item_y -= 26

    return y - sh - 14


def _draw_radar(c, cx, cy, radius, radar):
    labels = list(radar.keys())
    values = list(radar.values())
    n = len(labels)
    angles = [math.pi/2 + 2*math.pi*i/n for i in range(n)]

    # Rings
    for frac in [0.25, 0.5, 0.75, 1.0]:
        pts = [(cx + radius*frac*math.cos(a), cy + radius*frac*math.sin(a)) for a in angles]
        c.saveState()
        c.setStrokeColor(BORDER)
        c.setLineWidth(0.35)
        path = c.beginPath()
        path.moveTo(*pts[0])
        for p in pts[1:]:
            path.lineTo(*p)
        path.close()
        c.drawPath(path, fill=0, stroke=1)
        c.restoreState()

    # Spokes
    c.saveState()
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.35)
    for a in angles:
        c.line(cx, cy, cx + radius*math.cos(a), cy + radius*math.sin(a))
    c.restoreState()

    # Data polygon
    dpts = [(cx + radius*v/100*math.cos(a), cy + radius*v/100*math.sin(a))
            for v, a in zip(values, angles)]
    c.saveState()
    c.setFillColor(colors.HexColor("#39d35338"))
    c.setStrokeColor(GREEN)
    c.setLineWidth(1.4)
    path = c.beginPath()
    path.moveTo(*dpts[0])
    for p in dpts[1:]:
        path.lineTo(*p)
    path.close()
    c.drawPath(path, fill=1, stroke=1)
    c.restoreState()

    # Dots
    for p in dpts:
        c.setFillColor(GREEN)
        c.circle(p[0], p[1], 2.2, fill=1, stroke=0)

    # Labels
    c.setFont("Helvetica", 5.5)
    c.setFillColor(TEXT_DIM)
    for label, a in zip(labels, angles):
        lx = cx + (radius + 9)*math.cos(a)
        ly = cy + (radius + 9)*math.sin(a)
        c.drawCentredString(lx, ly - 2.5, label)


def draw_matches(c, y, matches):
    """Draw similar ventures section. Returns new y."""
    # Section header
    c.setFont("Helvetica-BoldOblique", 10.5)
    c.setFillColor(TEXT)
    c.drawCentredString(W/2, y, "Similar Ventures Found")
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.3)
    c.line(30, y + 7, W/2 - 85, y + 7)
    c.line(W/2 + 85, y + 7, W - 30, y + 7)
    y -= 18

    # Filter tabs
    tab_x = W/2 - 85
    for label, active in [("ALL", True), ("IN INDIA", False), ("GLOBAL", False)]:
        tw = 10 + len(label) * 5.5
        if active:
            rr(c, tab_x, y - 4, tw, 15, 4, GREEN)
            c.setFont("Helvetica-Bold", 6.5)
            c.setFillColor(BG)
        else:
            rr(c, tab_x, y - 4, tw, 15, 4, CARD2, BORDER, 0.4)
            c.setFont("Helvetica", 6.5)
            c.setFillColor(TEXT_DIM)
        c.drawString(tab_x + 5, y + 4, label)
        tab_x += tw + 7
    y -= 22

    for m in matches:
        sc = sim_color(m["similarity"])
        card_h = 58

        rr(c, 30, y - card_h, W - 60, card_h, 6, CARD, BORDER, 0.4)
        rr(c, 30, y - card_h, 3, card_h, 1, sc)  # left accent

        # Rank + country
        flag = m.get("flag", "🌐")
        country = m.get("country", "Global").upper()
        c.setFont("Helvetica", 6)
        c.setFillColor(TEXT_DIMMER)
        c.drawString(42, y - 13, f"MATCH #{m.get('rank', '')}  {flag}  {country}")

        # Name
        c.setFont("Helvetica-Bold", 9.5)
        c.setFillColor(sc)
        name = m.get("name", "")[:45]
        c.drawString(42, y - 26, name)

        # Description
        desc = m.get("description", "")
        desc_lines = wrap_text(c, desc, "Helvetica", 7, W - 130)
        c.setFillColor(TEXT_DIM)
        dl_y = y - 38
        for line in desc_lines[:2]:
            c.setFont("Helvetica", 7)
            c.drawString(42, dl_y, line)
            dl_y -= 10

        # Similarity %
        c.setFont("Helvetica-Bold", 15)
        c.setFillColor(sc)
        c.drawRightString(W - 40, y - 20, f"{m['similarity']:.2f}%")
        c.setFont("Helvetica", 6.5)
        c.setFillColor(TEXT_DIMMER)
        c.drawRightString(W - 40, y - 32, "SIMILARITY")

        # Bottom bar
        pb_x, pb_y, pb_w = 42, y - card_h + 7, W - 100
        rr(c, pb_x, pb_y, pb_w, 2, 1, CARD2)
        rr(c, pb_x, pb_y, pb_w * m["similarity"]/100, 2, 1, sc)

        y -= card_h + 7

    return y - 8


def draw_suggestions(c, y, idea, suggestions):
    """Draw strategic recommendations. Returns new y."""
    c.setFont("Helvetica-BoldOblique", 10.5)
    c.setFillColor(TEXT)
    c.drawCentredString(W/2, y, "Strategic Recommendations")
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.3)
    c.line(30, y + 7, W/2 - 100, y + 7)
    c.line(W/2 + 100, y + 7, W - 30, y + 7)
    y -= 16

    for i, suggestion in enumerate(suggestions, 1):
        lines = wrap_text(c, suggestion, "Helvetica", 7.5, W - 110)
        card_h = 20 + len(lines) * 11

        rr(c, 30, y - card_h, W - 60, card_h, 6, CARD, BORDER, 0.4)

        # Number badge
        rr(c, 38, y - 18, 18, 18, 4, GREEN_DIM)
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(GREEN)
        c.drawCentredString(47, y - 9, str(i).zfill(2))

        # Text
        c.setFillColor(TEXT_DIM)
        line_y = y - 10
        for line in lines:
            c.setFont("Helvetica", 7.5)
            c.drawString(64, line_y, line)
            line_y -= 11

        y -= card_h + 7

    return y


def draw_footer(c, y):
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.3)
    c.line(30, y, W - 30, y)
    c.setFont("Helvetica", 6)
    c.setFillColor(TEXT_DIMMER)
    c.drawCentredString(W/2, y - 11,
        "BUSINESS IDEA NOVELTY  ·  Semantic Similarity Based Analysis  ·  MCA Final Year Project  ·  2026")


# ── Main public function ──────────────────────────────────────────────────────

def generate_dark_pdf(idea, novelty_score, verdict, category,
                      radar, matches, suggestions, avg_similarity):
    """
    Generate a dark-theme PDF report and return it as bytes.

    Parameters
    ----------
    idea            : str   — user's business idea
    novelty_score   : float — 0-100
    verdict         : str   — e.g. "Somewhat Common"
    category        : str   — e.g. "AI/ML"
    radar           : dict  — {"Originality": 46, "Market Gap": 40, ...}
    matches         : list  — list of match dicts from similarity.py
    suggestions     : list  — list of suggestion strings
    avg_similarity  : float — average similarity score

    Returns
    -------
    bytes — PDF file content
    """
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)

    # ── Page 1 ────────────────────────────────────────────────────
    draw_page_bg(c)
    y = draw_header(c)
    y = draw_idea_block(c, y, idea)
    y = draw_score_radar(c, y, novelty_score, verdict, category, radar, avg_similarity)
    y = draw_matches(c, y, matches)

    # ── Page 2 if needed ─────────────────────────────────────────
    if y < 200:
        c.showPage()
        draw_page_bg(c)
        y = H - 40

    y = draw_suggestions(c, y, idea, suggestions)
    draw_footer(c, y - 16)

    c.save()
    buf.seek(0)
    return buf.read()