#!/usr/bin/env python3
"""Generate premium MP4 video for Agent-World demo — 2x supersampled."""
import os, math
import numpy as np
import imageio
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Output resolution
W, H = 1920, 1080
S = 2  # supersampling factor
RW, RH = W * S, H * S
FPS = 15
CPF = 12
DIR = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(DIR, "agent_demo.mp4")
LOGO_PATH = os.path.join(DIR, "..", "logo.png")

# ── Premium muted palette ───────────────────────────────────────────
BG       = (250, 250, 252)
WHITE    = (255, 255, 255)
CARD_BG  = (246, 247, 249)
TEXT     = (20, 20, 28)
TEXT2    = (82, 82, 100)
TEXT3    = (150, 150, 165)
BORDER   = (230, 230, 236)

PRI      = (55, 65, 81)
PRI_L    = (71, 85, 105)
GREEN    = (45, 125, 100)
PURPLE   = (88, 80, 120)
PURP_L   = (108, 98, 140)
AMBER    = (150, 120, 70)

THK_BG   = (245, 244, 250)
THK_BD   = (228, 225, 238)
THK_TX   = (80, 70, 110)
THK_BAR  = (130, 120, 170)
TOOL_BG  = (247, 246, 243)
TOOL_BD  = (225, 220, 210)
TOOL_TX  = (100, 85, 60)
ANS_BG   = (244, 249, 247)
ANS_BD   = (180, 210, 195)
ANS_TX   = (35, 85, 65)
FN_BG    = (248, 249, 252)
FN_BD    = (220, 222, 230)
USR_BG   = PRI
CURSOR_C = (160, 160, 175)
ENV_AV   = (240, 237, 230)
SHADOW_C = (0, 0, 0, 18)  # very subtle black shadow

# ── Fonts (all at 2x for supersampled rendering) ────────────────────
TNR      = "/System/Library/Fonts/Supplemental/Times New Roman.ttf"
TNR_BOLD = "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf"

def get_font(sz, bold=False):
    if bold and os.path.exists(TNR_BOLD):
        try: return ImageFont.truetype(TNR_BOLD, sz)
        except: pass
    if os.path.exists(TNR):
        try: return ImageFont.truetype(TNR, sz)
        except: pass
    for p in ["/System/Library/Fonts/Helvetica.ttc", "/Library/Fonts/Arial Unicode.ttf"]:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, sz)
            except: continue
    return ImageFont.load_default()

F     = get_font(26*S)
FS    = get_font(22*S)
FB    = get_font(26*S, True)
FT    = get_font(28*S, True)
FM    = get_font(20*S)
FG    = get_font(15*S, True)
FTAG  = get_font(17*S, True)
FTAG2 = get_font(16*S, True)
FH    = get_font(56*S, True)
FAV   = get_font(24*S, True)
FCODE = get_font(18*S)
FHDR  = get_font(20*S, True)
FSTAT = get_font(13*S)

# ── Logo ────────────────────────────────────────────────────────────
logo_img = None
logo_icon = None
logo_cache = {}
if os.path.exists(LOGO_PATH):
    logo_img = Image.open(LOGO_PATH).convert("RGBA")
    iw = int(logo_img.width * 0.48)
    logo_icon = logo_img.crop((0, 0, iw, logo_img.height))

# ── Steps data ──────────────────────────────────────────────────────
STEPS = [
    ("user", "I have a page list in my note system.\nPlease use the first page title to search\nfor a same-name page in the database.\nThen check nested to-do blocks vs plain\nparagraph blocks for consistency.\n\nRules: missing=50, incomplete=30, mismatch=20\nTotal>=50 -> High Risk"),
    ("think", "Plan:\n1. Get the first page title from the list\n2. Search the database for same-name pages\n3. Check nested to-do vs plain paragraph\n4. Calculate risk score, output JSON\n\nStep 1: Call get_example_page for the title."),
    ("fn", "get_example_page()"),
    ("tool", '{"object":"page",\n "properties":{\n  "Name":{"title":[{"plain_text":"Tuscan kale"}]},\n  "Price":{"number":2.5},\n  "In stock":{"checkbox":true}\n }}'),
    ("think", 'Extracted page title: Name -> "Tuscan kale"\n\nNext: query_example_database for same-name pages.'),
    ("fn", 'query_example_database(\n  property_name="Name",\n  value="Tuscan kale"\n)'),
    ("tool", "[]"),
    ("think", "Empty array -> no same-name page found\ndb_same_name_count = 0\nMarked as missing, +50 pts\n\nNext: get nested to-do block."),
    ("fn", "get_example_block_todo_nested()"),
    ("tool", '{"type":"paragraph",\n "has_children":true,\n "paragraph":{"children":[\n  {"type":"to_do",\n   "to_do":{"checked":false}}]}}'),
    ("think", "to_do.checked = false\n-> Incomplete item found, +30 pts\n\nFinally: get plain paragraph for comparison."),
    ("fn", "get_example_block_paragraph()"),
    ("tool", '{"type":"paragraph",\n "has_children":false,\n "paragraph":{"text":[]}}'),
    ("think", "Comparing two paragraph blocks:\n  Nested: has_children = true\n  Plain: has_children = false\n-> Consistency mismatch, +20 pts\n\nTotal = 50+30+20 = 100 >= 50\nConclusion: High Risk"),
    ("answer", '{\n  "page_title": "Tuscan kale",\n  "db_same_name_count": 0,\n  "risk_score": 100,\n  "risk_level": "High Risk"\n}'),
]

VIDEO_TITLE = "Travel Planning"

AV_SZ = 72 * S

# ── Shadow helper ───────────────────────────────────────────────────
_shadow_cache = {}

def make_shadow(w, h, radius, blur_r=8):
    """Create a soft drop shadow image (RGBA)."""
    key = (w, h, radius, blur_r)
    if key in _shadow_cache:
        return _shadow_cache[key]
    pad = blur_r * 3
    sw, sh = w + pad*2, h + pad*2
    shadow = Image.new('RGBA', (sw, sh), (0,0,0,0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle([pad, pad, pad+w, pad+h], radius=radius, fill=(0,0,0,22))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=blur_r))
    _shadow_cache[key] = shadow
    return shadow

def paste_shadow(img, x, y, w, h, radius=16, blur_r=8, offset_y=4):
    """Paste a soft shadow behind a rectangle area."""
    shadow = make_shadow(w, h, radius*S, blur_r*S)
    pad = blur_r * 3 * S
    sx = x*S - pad
    sy = y*S - pad + offset_y*S
    img.paste(Image.alpha_composite(
        Image.new('RGBA', img.size, (0,0,0,0)),
        _paste_at(shadow, sx, sy, img.size)
    ), (0,0), _paste_at(shadow, sx, sy, img.size))

def _paste_at(overlay, x, y, canvas_size):
    """Place an overlay image at (x,y) on a canvas-sized RGBA."""
    c = Image.new('RGBA', canvas_size, (0,0,0,0))
    c.paste(overlay, (x, y))
    return c

# ── Drawing helpers (all at 2x coordinates) ─────────────────────────
def rr(draw, xy, r, fill=None, outline=None, w=1):
    """Rounded rectangle using Pillow's built-in method."""
    x0, y0, x1, y1 = [v*S for v in xy]
    r2 = r * S
    if fill and outline:
        draw.rounded_rectangle([x0,y0,x1,y1], radius=r2, fill=fill, outline=outline, width=w*S)
    elif fill:
        draw.rounded_rectangle([x0,y0,x1,y1], radius=r2, fill=fill)
    elif outline:
        draw.rounded_rectangle([x0,y0,x1,y1], radius=r2, outline=outline, width=w*S)

def tag_badge(draw, x, y, text, fg, bg):
    bb = draw.textbbox((0,0), text, font=FTAG2)
    tw = bb[2] - bb[0] + 18*S
    th = bb[3] - bb[1] + 10*S
    draw.rounded_rectangle([x, y, x+tw, y+th], radius=6*S, fill=bg)
    draw.text((x+9*S, y+4*S), text, fill=fg, font=FTAG2)
    return tw

def draw_env_icon(draw, x, y, sz, color):
    cx, cy_c = x + sz//2, y + sz//2
    r = sz//2 - 8*S
    draw.ellipse([cx-r, cy_c-r, cx+r, cy_c+r], outline=color, width=4*S)
    draw.line([cx-r, cy_c, cx+r, cy_c], fill=color, width=3*S)
    draw.arc([cx-r*2//3, cy_c-r, cx+r*2//3, cy_c+r], 0, 360, fill=color, width=3*S)
    draw.line([cx, cy_c-r, cx, cy_c+r], fill=color, width=3*S)

def draw_avatar(img, draw, x, y, role):
    sz = AV_SZ
    if role == 'user':
        draw.rounded_rectangle([x,y,x+sz,y+sz], radius=16*S, fill=PRI)
        bb = draw.textbbox((0,0), "U", font=FT)
        draw.text((x+(sz-bb[2]+bb[0])//2, y+(sz-bb[3]+bb[1])//2-S), "U", fill=WHITE, font=FT)
    elif role in ('think','fn','answer'):
        draw.rounded_rectangle([x,y,x+sz,y+sz], radius=16*S, fill=WHITE, outline=BORDER, width=2*S)
        icon = logo_icon or logo_img
        if icon:
            pad = 6*S
            inner = sz - pad*2
            key = ('av_icon', inner)
            if key not in logo_cache:
                r = inner / icon.height
                lw = int(icon.width * r)
                if lw > inner:
                    r = inner / icon.width
                    lh = int(icon.height * r)
                    lw = inner
                else:
                    lh = inner
                logo_cache[key] = icon.resize((lw, lh), Image.LANCZOS)
            resized = logo_cache[key]
            px = x + (sz - resized.width) // 2
            py = y + (sz - resized.height) // 2
            img.paste(resized, (px, py), resized)
    elif role == 'tool':
        draw.rounded_rectangle([x,y,x+sz,y+sz], radius=16*S, fill=ENV_AV, outline=TOOL_BD, width=2*S)
        draw_env_icon(draw, x, y, sz, TOOL_TX)

def wrap(text, font, mw, draw):
    mw2 = mw * S
    lines = []
    for p in text.split('\n'):
        if not p: lines.append(''); continue
        cur = ''
        for ch in p:
            t = cur + ch
            if draw.textbbox((0,0), t, font=font)[2] > mw2 and cur:
                lines.append(cur); cur = ch
            else: cur = t
        if cur: lines.append(cur)
    return lines

def paste_logo_header(img, x, y, h):
    if logo_img is None: return 0
    h2 = h * S
    key = ('hdr', h2)
    if key not in logo_cache:
        r = h2 / logo_img.height
        lw = int(logo_img.width * r)
        logo_cache[key] = logo_img.resize((lw, h2), Image.LANCZOS)
    resized = logo_cache[key]
    img.paste(resized, (x*S, y*S), resized)
    return resized.width

def draw_header(img, draw, step, total):
    HH = 66 * S
    draw.rectangle([0,0,RW,HH], fill=WHITE)
    draw.line([0,HH-1,RW,HH-1], fill=BORDER, width=S)
    lw = paste_logo_header(img, 20, 5, 56)
    tx = 20*S + lw + 12*S
    draw.text((tx, 12*S), "Agent-World", fill=TEXT, font=FT)
    draw.text((tx, 38*S), VIDEO_TITLE, fill=TEXT3, font=FSTAT)
    tag = f"STEP {step}/{total}"
    tb = draw.textbbox((0,0), tag, font=FTAG)
    tw = tb[2] - tb[0] + 20*S
    tx2 = RW - tw - 30*S
    draw.rounded_rectangle([tx2, 19*S, tx2+tw, 45*S], radius=13*S, fill=CARD_BG, outline=PRI, width=S)
    draw.text((tx2+10*S, 24*S), tag, fill=PRI, font=FTAG)

def draw_input_bar(draw, text="", cursor=False, frame_idx=0):
    y = RH - 90*S
    draw.rectangle([0,y,RW,RH], fill=WHITE)
    draw.line([0,y,RW,y], fill=BORDER, width=S)
    cx = (RW - 1200*S) // 2
    ix, iy = cx, y + 10*S
    iw, ih = 1200*S, 34*S
    oc = PRI if text else BORDER
    draw.rounded_rectangle([ix, iy, ix+iw, iy+ih], radius=10*S, fill=WHITE, outline=oc, width=S)
    if text:
        draw.text((ix+10*S, iy+7*S), text, fill=TEXT, font=FM)
        if cursor and (frame_idx // 4) % 2 == 0:
            cw = draw.textbbox((0,0), text, font=FM)[2]
            draw.rectangle([ix+10*S+cw+2*S, iy+8*S, ix+10*S+cw+4*S, iy+ih-10*S], fill=CURSOR_C)
    else:
        draw.text((ix+10*S, iy+7*S), "Type a message...", fill=TEXT3, font=FM)
    bx = ix + iw + 8*S
    draw.rounded_rectangle([bx, iy, bx+34*S, iy+ih], radius=8*S, fill=PRI)
    draw.text((bx+9*S, iy+7*S), "→", fill=WHITE, font=FAV)
    draw.text((ix, iy+ih+5*S), "Auto Demo · Streaming I/O", fill=TEXT3, font=FSTAT)

def get_role_font(role):
    if role in ('fn','tool','answer'): return FM
    if role == 'think': return FS
    return F

def get_role_lh(role):
    if role in ('fn','tool','think'): return 28
    return 32

# ── Main render ─────────────────────────────────────────────────────
def render(visible, step_num, typing_role=None, typing_chars=-1, input_text="", frame_idx=0):
    img = Image.new('RGBA', (RW,RH), BG + (255,))
    d = ImageDraw.Draw(img)
    draw_header(img, d, step_num, len(STEPS))
    draw_input_bar(d, text=input_text, cursor=bool(input_text), frame_idx=frame_idx)

    CW = 1200; BW = CW - 10; TW = BW - 30
    LX = (W - CW) // 2
    RX = LX + CW
    cy = 82

    for si, (role, full_text) in enumerate(visible):
        if cy > H - 170: break
        is_typing = (si == len(visible)-1 and typing_chars >= 0)
        text = full_text[:typing_chars] if is_typing else full_text
        fnt = get_role_font(role)
        full_lines = wrap(full_text, fnt, TW, d)
        lines = wrap(text, fnt, TW, d) if is_typing else full_lines
        lh = get_role_lh(role)
        th_full = len(full_lines) * lh

        # Avatar (in 2x coords)
        if role == 'user':
            av_x = (RX + 10) * S
        else:
            av_x = LX*S - AV_SZ - 12*S
        draw_avatar(img, d, av_x, cy*S, role)

        # Role label — clearly separated from content
        if role == 'user':
            bb_rl = d.textbbox((0,0), "You", font=FHDR)
            d.text(((RX)*S - (bb_rl[2]-bb_rl[0]), cy*S+4*S), "You", fill=TEXT2, font=FHDR)
        elif role in ('think','fn','answer'):
            d.text((LX*S, cy*S+4*S), "Agent-World", fill=TEXT2, font=FHDR)
            aw = d.textbbox((0,0),"Agent-World",font=FHDR)[2]
            tag_badge(d, LX*S + aw + 10*S, cy*S+2*S, "Agent", PRI, (240,240,246))
        elif role == 'tool':
            d.text((LX*S, cy*S+4*S), "Environments", fill=TOOL_TX, font=FHDR)
            ew = d.textbbox((0,0),"Environments",font=FHDR)[2]
            tag_badge(d, LX*S + ew + 10*S, cy*S+2*S, "Tool", TOOL_TX, TOOL_BG)

        cy += 38
        bx = LX

        if role == 'user':
            bh = th_full + 24
            bw = min(BW, TW + 40)
            ubx = RX - bw
            # Shadow
            shadow = make_shadow(bw*S, bh*S, 14*S, 10*S)
            pad = 10*3*S*S
            simg = Image.new('RGBA', img.size, (0,0,0,0))
            simg.paste(shadow, (ubx*S - pad, cy*S - pad + 4*S))
            img = Image.alpha_composite(img, simg)
            d = ImageDraw.Draw(img)
            # Card
            d.rounded_rectangle([ubx*S, cy*S, (ubx+bw)*S, (cy+bh)*S], radius=14*S, fill=USR_BG)
            for i,l in enumerate(lines):
                d.text((ubx*S+14*S, cy*S+12*S+i*lh*S), l, fill=WHITE, font=F)
            if is_typing and lines:
                last = lines[-1]
                cw_t = d.textbbox((0,0), last, font=F)[2]
                if (frame_idx//4)%2==0:
                    ly = cy*S+13*S+(len(lines)-1)*lh*S
                    d.rectangle([ubx*S+14*S+cw_t+2*S, ly, ubx*S+14*S+cw_t+4*S, ly+lh*S-8*S], fill=CURSOR_C)
            cy += bh + 10

        elif role == 'think':
            bh = th_full + 20
            d.text((bx*S+14*S, cy*S), "THINKING", fill=THK_TX, font=FTAG)
            cy += 26
            # Shadow
            shadow = make_shadow(BW*S, bh*S, 8*S, 6*S)
            pad = 6*3*S*S
            simg = Image.new('RGBA', img.size, (0,0,0,0))
            simg.paste(shadow, ((bx+10)*S - pad, cy*S - pad + 3*S))
            img = Image.alpha_composite(img, simg)
            d = ImageDraw.Draw(img)
            # Left accent bar
            d.rounded_rectangle([bx*S, cy*S, bx*S+4*S, (cy+bh)*S], radius=2*S, fill=THK_BAR)
            d.rounded_rectangle([(bx+10)*S, cy*S, (bx+BW)*S, (cy+bh)*S], radius=8*S, fill=THK_BG, outline=THK_BD, width=S)
            for i,l in enumerate(lines):
                d.text((bx*S+22*S, cy*S+10*S+i*lh*S), l, fill=THK_TX, font=FS)
            if is_typing and lines:
                last = lines[-1]
                cw_t = d.textbbox((0,0), last, font=FS)[2]
                if (frame_idx//4)%2==0:
                    ly = cy*S+11*S+(len(lines)-1)*lh*S
                    d.rectangle([bx*S+22*S+cw_t+2*S, ly, bx*S+22*S+cw_t+4*S, ly+lh*S-8*S], fill=THK_BAR)
            cy += bh + 10

        elif role == 'fn':
            bh = th_full + 22
            d.text((bx*S+14*S, cy*S), "FUNCTION CALL", fill=PRI_L, font=FTAG)
            cy += 26
            shadow = make_shadow(BW*S, bh*S, 8*S, 6*S)
            pad = 6*3*S*S
            simg = Image.new('RGBA', img.size, (0,0,0,0))
            simg.paste(shadow, ((bx+10)*S - pad, cy*S - pad + 3*S))
            img = Image.alpha_composite(img, simg)
            d = ImageDraw.Draw(img)
            d.rounded_rectangle([bx*S, cy*S, bx*S+4*S, (cy+bh)*S], radius=2*S, fill=PRI)
            d.rounded_rectangle([(bx+10)*S, cy*S, (bx+BW)*S, (cy+bh)*S], radius=8*S, fill=FN_BG, outline=FN_BD, width=S)
            for i,l in enumerate(lines):
                d.text((bx*S+22*S, cy*S+10*S+i*lh*S), l, fill=TEXT, font=FCODE)
            if is_typing and lines:
                last = lines[-1]
                cw_t = d.textbbox((0,0), last, font=FCODE)[2]
                if (frame_idx//4)%2==0:
                    ly = cy*S+11*S+(len(lines)-1)*lh*S
                    d.rectangle([bx*S+22*S+cw_t+2*S, ly, bx*S+22*S+cw_t+4*S, ly+lh*S-8*S], fill=PRI)
            cy += bh + 8

        elif role == 'tool':
            bh = th_full + 20
            d.text((bx*S+14*S, cy*S), "TOOL RESULT", fill=AMBER, font=FTAG)
            cy += 26
            shadow = make_shadow(BW*S, bh*S, 8*S, 6*S)
            pad = 6*3*S*S
            simg = Image.new('RGBA', img.size, (0,0,0,0))
            simg.paste(shadow, ((bx+10)*S - pad, cy*S - pad + 3*S))
            img = Image.alpha_composite(img, simg)
            d = ImageDraw.Draw(img)
            d.rounded_rectangle([bx*S, cy*S, bx*S+4*S, (cy+bh)*S], radius=2*S, fill=AMBER)
            d.rounded_rectangle([(bx+10)*S, cy*S, (bx+BW)*S, (cy+bh)*S], radius=8*S, fill=TOOL_BG, outline=TOOL_BD, width=S)
            for i,l in enumerate(lines):
                d.text((bx*S+22*S, cy*S+10*S+i*lh*S), l, fill=TOOL_TX, font=FM)
            if is_typing and lines:
                last = lines[-1]
                cw_t = d.textbbox((0,0), last, font=FM)[2]
                if (frame_idx//4)%2==0:
                    ly = cy*S+11*S+(len(lines)-1)*lh*S
                    d.rectangle([bx*S+22*S+cw_t+2*S, ly, bx*S+22*S+cw_t+4*S, ly+lh*S-8*S], fill=AMBER)
            cy += bh + 10

        elif role == 'answer':
            bh = th_full + 26
            d.text((bx*S+14*S, cy*S), "FINAL ANSWER", fill=GREEN, font=FTAG)
            cy += 26
            shadow = make_shadow(BW*S, bh*S, 10*S, 8*S)
            pad = 8*3*S*S
            simg = Image.new('RGBA', img.size, (0,0,0,0))
            simg.paste(shadow, ((bx+10)*S - pad, cy*S - pad + 4*S))
            img = Image.alpha_composite(img, simg)
            d = ImageDraw.Draw(img)
            d.rounded_rectangle([bx*S, cy*S, bx*S+4*S, (cy+bh)*S], radius=2*S, fill=GREEN)
            d.rounded_rectangle([(bx+10)*S, cy*S, (bx+BW)*S, (cy+bh)*S], radius=10*S, fill=ANS_BG, outline=ANS_BD, width=2*S)
            for i,l in enumerate(lines):
                d.text((bx*S+24*S, cy*S+12*S+i*lh*S), l, fill=ANS_TX, font=FM)
            if is_typing and lines:
                last = lines[-1]
                cw_t = d.textbbox((0,0), last, font=FM)[2]
                if (frame_idx//4)%2==0:
                    ly = cy*S+13*S+(len(lines)-1)*lh*S
                    d.rectangle([bx*S+24*S+cw_t+2*S, ly, bx*S+24*S+cw_t+4*S, ly+lh*S-8*S], fill=GREEN)
            cy += bh + 10

    # Downscale 2x → 1x with high-quality LANCZOS
    return img.convert('RGB').resize((W, H), Image.LANCZOS)

# ── Main ────────────────────────────────────────────────────────────
def main():
    print("Generating premium streaming video (2x supersampled)...")
    MAX_VIS = 4

    # Title frame
    ti = Image.new('RGBA', (RW,RH), BG + (255,))
    td = ImageDraw.Draw(ti)
    if logo_img:
        lh = 140*S
        r = lh / logo_img.height
        lw = int(logo_img.width * r)
        resized = logo_img.resize((lw, lh), Image.LANCZOS)
        ti.paste(resized, ((RW-lw)//2, RH//2-140*S), resized)
    t1 = "Agent-World"
    bb1 = td.textbbox((0,0), t1, font=FH)
    tw1 = bb1[2] - bb1[0]
    t2 = " · " + VIDEO_TITLE
    bb2 = td.textbbox((0,0), t2, font=FH)
    tw2 = bb2[2] - bb2[0]
    sx = (RW - tw1 - tw2) // 2
    sy = RH // 2 + 20*S
    td.text((sx, sy), t1, fill=TEXT, font=FH)
    td.text((sx+tw1, sy), t2, fill=PRI, font=FH)
    ly = sy + (bb1[3]-bb1[1]) + 10*S
    for i in range(4):
        fr = i/3.0
        c = tuple(int(PRI[j]+((6,182,212)[j]-PRI[j])*fr) for j in range(3))
        sw = (tw1+tw2)//4
        td.rectangle([sx+i*sw, ly, sx+(i+1)*sw, ly+3*S], fill=c)
    ti_final = ti.convert('RGB').resize((W,H), Image.LANCZOS)

    print(f"Writing MP4 to {OUT} ...")
    writer = imageio.get_writer(OUT, fps=FPS, codec='libx264',
                                pixelformat='yuv420p', macro_block_size=2,
                                quality=8, output_params=['-crf', '18'])

    tnp = np.array(ti_final)
    for _ in range(int(2.0*FPS)):
        writer.append_data(tnp)

    fc = 0
    tf = int(2.0*FPS)

    # Transition: empty chat interface for ~1s before typing starts
    empty_frame = render([], 0, frame_idx=0)
    enp = np.array(empty_frame)
    for _ in range(int(1.0*FPS)):
        writer.append_data(enp)
        fc += 1; tf += 1

    for si in range(len(STEPS)):
        role, full_text = STEPS[si]
        tlen = len(full_text)
        start = max(0, si - MAX_VIS + 1)
        visible = list(STEPS[start:si+1])

        if role == 'user':
            flat_text = full_text.replace('\n', ' ')
            flat_len = len(flat_text)
            inp_cpf = 6
            inp_frames = math.ceil(flat_len / inp_cpf)
            prev_visible = list(STEPS[start:si]) if si > 0 else []
            for tf_i in range(inp_frames):
                chars = min((tf_i+1)*inp_cpf, flat_len)
                inp_text = flat_text[:chars]
                disp = inp_text if len(inp_text) < 60 else "…" + inp_text[-58:]
                frame = render(prev_visible, si, input_text=disp, frame_idx=fc)
                writer.append_data(np.array(frame))
                fc += 1; tf += 1
            for _ in range(3):
                frame = render(prev_visible, si, frame_idx=fc)
                writer.append_data(np.array(frame))
                fc += 1; tf += 1

        n_type = math.ceil(tlen / CPF)
        for tf_i in range(n_type):
            chars = min((tf_i+1)*CPF, tlen)
            frame = render(visible, si+1, typing_role=role, typing_chars=chars, frame_idx=fc)
            writer.append_data(np.array(frame))
            fc += 1; tf += 1

        hold = {'user':0.6, 'think':0.4, 'fn':0.3, 'tool':0.4, 'answer':1.5}.get(role, 0.4)
        complete = render(visible, si+1, frame_idx=fc)
        cnp = np.array(complete)
        for _ in range(max(1, int(hold*FPS))):
            writer.append_data(cnp)
            fc += 1; tf += 1

    for _ in range(int(2.0*FPS)):
        writer.append_data(cnp)
        tf += 1

    writer.close()
    total_sec = tf / FPS
    size_mb = os.path.getsize(OUT) / 1024 / 1024
    print(f"Done! {tf} frames, {total_sec:.1f}s, {size_mb:.1f} MB")

def generate_video_for(title, steps, output_path):
    global VIDEO_TITLE, STEPS, OUT
    VIDEO_TITLE = title
    STEPS = steps
    OUT = output_path
    main()

if __name__ == '__main__':
    main()
