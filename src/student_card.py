"""
OLYMPIAD INTELLIGENCE
Premium Student Card System

Collectible olympiad student cards with:
- Shield silhouette
- Symmetrical FIFA-style stats
- Rarity-specific visual themes
- Event-specific designs
- Transparent background outside the card
"""

import math
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageChops

from card_events import determine_events


# ============================================================
# CONFIG
# ============================================================

WIDTH = 1024
HEIGHT = 1536

PROFILE_PATH = Path("data/processed/student_profile.json")
OUTPUT_DIR = Path("data/processed/cards")
PHOTO_PATH = Path("data/raw/student_photo.png")


# ============================================================
# FONTS
# ============================================================

def load_font(size, bold=False):

    if bold:
        paths = [
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/segoeuib.ttf",
            "C:/Windows/Fonts/calibrib.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]
    else:
        paths = [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/segoeui.ttf",
            "C:/Windows/Fonts/calibri.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]

    for path in paths:
        if Path(path).exists():
            return ImageFont.truetype(path, size)

    return ImageFont.load_default()


# ============================================================
# PROFILE
# ============================================================

def load_profile():

    if not PROFILE_PATH.exists():
        raise FileNotFoundError(
            "student_profile.json not found.\n"
            "Run:\n"
            "python src/student_profile.py"
        )

    with open(PROFILE_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


# ============================================================
# CARD RARITY
# ============================================================

def get_card_type(rating):

    if rating >= 95:
        return "ICON"
    if rating >= 90:
        return "ELITE"
    if rating >= 85:
        return "SPECIAL"
    if rating >= 80:
        return "RARE"
    if rating >= 70:
        return "SILVER"

    return "BRONZE"


# ============================================================
# BASE CARD THEMES
# ============================================================

CARD_THEMES = {

    "BRONZE": {
        "bg_top": (38, 20, 15),
        "bg_bottom": (116, 63, 34),
        "gold": (220, 147, 80),
        "light": (255, 222, 176),
        "accent": (160, 82, 42),
        "dark": (22, 11, 8),
        "pattern": "bronze",
    },

    "SILVER": {
        "bg_top": (30, 34, 42),
        "bg_bottom": (111, 118, 132),
        "gold": (211, 218, 229),
        "light": (255, 255, 255),
        "accent": (138, 147, 163),
        "dark": (18, 20, 25),
        "pattern": "silver",
    },

    "RARE": {
        "bg_top": (9, 20, 50),
        "bg_bottom": (40, 87, 157),
        "gold": (127, 184, 255),
        "light": (233, 247, 255),
        "accent": (60, 123, 223),
        "dark": (5, 11, 28),
        "pattern": "rare",
    },

    "SPECIAL": {
        "bg_top": (11, 7, 36),
        "bg_bottom": (82, 40, 145),
        "gold": (211, 162, 255),
        "light": (247, 235, 255),
        "accent": (158, 74, 239),
        "dark": (5, 4, 20),
        "pattern": "special",
    },

    "ELITE": {
        "bg_top": (27, 7, 47),
        "bg_bottom": (109, 47, 148),
        "gold": (255, 207, 88),
        "light": (255, 248, 190),
        "accent": (225, 141, 48),
        "dark": (18, 5, 30),
        "pattern": "elite",
    },

    "ICON": {
        "bg_top": (35, 21, 4),
        "bg_bottom": (151, 97, 16),
        "gold": (255, 220, 73),
        "light": (255, 250, 191),
        "accent": (218, 163, 36),
        "dark": (23, 13, 3),
        "pattern": "icon",
    },
}


# ============================================================
# EVENT STYLE OVERRIDES
# ============================================================

EVENT_STYLES = {

    "standard": {},

    "proof_master": {
        "gold": (209, 149, 255),
        "light": (246, 228, 255),
        "accent": (133, 72, 211),
        "pattern": "proof",
    },

    "geometry_master": {
        "gold": (80, 233, 207),
        "light": (226, 255, 250),
        "accent": (31, 156, 143),
        "pattern": "geometry",
    },

    "olympiad_elite": {
        "gold": (232, 213, 255),
        "light": (255, 249, 255),
        "accent": (139, 95, 219),
        "pattern": "elite",
    },

    "champion": {
        "gold": (255, 220, 77),
        "light": (255, 247, 181),
        "accent": (210, 143, 20),
        "pattern": "champion",
    },
}


EVENT_NAMES = {
    "standard": "SPECIAL",
    "proof_master": "PROOF MASTER",
    "geometry_master": "GEOMETRY MASTER",
    "olympiad_elite": "OLYMPIAD ELITE",
    "champion": "CHAMPION",
}


# ============================================================
# EXACT 3-LETTER STAT LABELS
# ============================================================

STAT_LABELS = {
    "algebra": "ALG",
    "geometry": "GEO",
    "number_theory": "NTH",
    "discrete_mathematics": "DMC",
    "proof": "PRO",
    "reasoning": "REA",
    "calculation": "CAL",
    "case_analysis": "CAS",
}


# ============================================================
# CARD SILHOUETTE
# ============================================================

def card_polygon():

    return [
        (178, 45), (846, 45),
        (906, 88), (939, 156), (952, 300), (941, 455),
        (948, 635), (936, 825),
        (925, 985), (895, 1128),
        (850, 1235), (795, 1327),
        (735, 1392), (655, 1445),
        (590, 1484), (512, 1512),
        (434, 1484), (369, 1445),
        (289, 1392), (229, 1327),
        (174, 1235), (129, 1128),
        (99, 985), (88, 825),
        (76, 635), (83, 455),
        (72, 300), (85, 156), (118, 88),
    ]


def create_mask():

    mask = Image.new("L", (WIDTH, HEIGHT), 0)
    ImageDraw.Draw(mask).polygon(card_polygon(), fill=255)

    return mask


def shield_bounds_at_y(y):
    """
    Returns (left_x, right_x) of the shield silhouette at a given
    horizontal scanline, by intersecting the polygon edges with y.
    Used to keep text/lines from ever crossing the card border,
    no matter how the silhouette is tuned later.
    """

    polygon = card_polygon()
    n = len(polygon)
    xs = []

    for i in range(n):

        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % n]

        if y1 == y2:
            continue

        if min(y1, y2) <= y <= max(y1, y2):
            t = (y - y1) / (y2 - y1)
            xs.append(x1 + t * (x2 - x1))

    if not xs:
        return None

    return min(xs), max(xs)


# Half the visual width of the drawn border band (outer dark stroke
# is 32px wide, centered on the polygon path) plus a little breathing
# room, so nothing we place ever touches or crosses the frame.
FRAME_MARGIN = 26


def safe_bounds_for_range(y0, y1, margin=FRAME_MARGIN, samples=14):
    """
    Content-safe (left, right) x-bounds that clear the frame for
    every scanline between y0 and y1 - i.e. the tightest window
    across that whole vertical span, not just its endpoints.
    """

    lefts = []
    rights = []

    for i in range(samples):
        y = y0 + (y1 - y0) * i / (samples - 1)
        bounds = shield_bounds_at_y(y)
        if bounds:
            lefts.append(bounds[0])
            rights.append(bounds[1])

    return max(lefts) + margin, min(rights) - margin


# ============================================================
# GRADIENT
# ============================================================

def gradient_background(theme):

    image = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(image)

    top = theme["bg_top"]
    bottom = theme["bg_bottom"]

    for y in range(HEIGHT):

        ratio = y / (HEIGHT - 1)

        r = int(top[0] * (1 - ratio) + bottom[0] * ratio)
        g = int(top[1] * (1 - ratio) + bottom[1] * ratio)
        b = int(top[2] * (1 - ratio) + bottom[2] * ratio)

        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # subtle top sheen so the card reads as glossy / premium
    sheen = Image.new("L", (WIDTH, HEIGHT), 0)
    sheen_draw = ImageDraw.Draw(sheen)
    sheen_draw.ellipse(
        [WIDTH // 2 - 520, -420, WIDTH // 2 + 520, 420],
        fill=40
    )
    white = Image.new("RGB", (WIDTH, HEIGHT), (255, 255, 255))
    image = Image.composite(white, image, sheen)

    return image


# ============================================================
# RARITY-SPECIFIC PATTERNS (drawn on their own layer, then
# vertically faded so they only ever live behind the portrait
# and never collide with the name / stats / footer text)
# ============================================================

PATTERN_TOP = 85
PATTERN_FADE_START = 660
PATTERN_FADE_END = 800


def _rgba(color):
    return (color[0], color[1], color[2], 255)


def draw_patterns(draw, theme, pattern):

    gold = _rgba(theme["gold"])
    light = _rgba(theme["light"])
    accent = _rgba(theme["accent"])
    dark = _rgba(theme["dark"])

    # --------------------------------------------------------
    # BRONZE - plain, understated (lowest tier)
    # --------------------------------------------------------

    if pattern == "bronze":

        for i in range(7):
            x = 130 + i * 115
            draw.line([(x, 130), (x + 150, 460)], fill=light, width=3)

    # --------------------------------------------------------
    # SILVER - clean crossed hatch
    # --------------------------------------------------------

    elif pattern == "silver":

        for i in range(6):
            y = 110 + i * 95
            draw.line([(90, y), (700, y + 300)], fill=light, width=3)
            draw.line([(920, y), (320, y + 300)], fill=accent, width=2)

    # --------------------------------------------------------
    # RARE - diagonal stripes + facets
    # --------------------------------------------------------

    elif pattern == "rare":

        for i in range(12):
            x = 60 + i * 78
            draw.line([(x, 90), (x + 230, 400)], fill=light, width=3)

        for i in range(8):
            draw.polygon(
                [
                    (120 + i * 110, 500),
                    (175 + i * 110, 445),
                    (230 + i * 110, 500),
                    (175 + i * 110, 555),
                ],
                outline=accent,
                width=3,
            )

    # --------------------------------------------------------
    # SPECIAL - diagonal ribbons + stars
    # --------------------------------------------------------

    elif pattern == "special":

        draw.polygon([(0, 220), (1024, 20), (1024, 120), (0, 350)], fill=accent)
        draw.polygon([(0, 390), (1024, 150), (1024, 205), (0, 450)], fill=dark)

        for i in range(28):
            x = 90 + ((i * 139) % 825)
            y = 110 + ((i * 197) % 560)
            size = 3 + (i % 4)
            draw.line([(x - size, y), (x + size, y)], fill=light, width=2)
            draw.line([(x, y - size), (x, y + size)], fill=light, width=2)

    # --------------------------------------------------------
    # ELITE - sunburst behind the portrait
    # --------------------------------------------------------

    elif pattern == "elite":

        center = (512, 470)

        for angle in range(0, 360, 20):
            rad = math.radians(angle)
            end = (
                int(center[0] + math.cos(rad) * 430),
                int(center[1] + math.sin(rad) * 430),
            )
            draw.line([center, end], fill=gold, width=3)

        for i in range(7):
            x = 165 + i * 100
            draw.polygon(
                [(x, 545), (x + 40, 505), (x + 80, 545), (x + 40, 585)],
                outline=light,
                width=3,
            )

    # --------------------------------------------------------
    # ICON - concentric legend rings
    # --------------------------------------------------------

    elif pattern == "icon":

        center = (512, 470)

        for radius in [95, 175, 255, 335]:
            draw.ellipse(
                [
                    center[0] - radius, center[1] - radius,
                    center[0] + radius, center[1] + radius,
                ],
                outline=gold,
                width=4,
            )

        for angle in range(0, 360, 20):
            rad = math.radians(angle)
            end = (
                int(center[0] + math.cos(rad) * 335),
                int(center[1] + math.sin(rad) * 335),
            )
            draw.line([center, end], fill=light, width=2)

    # --------------------------------------------------------
    # PROOF MASTER - construction graph
    # --------------------------------------------------------

    elif pattern == "proof":

        points = [(190, 470), (430, 370), (760, 480), (600, 690), (330, 700)]

        for i in range(len(points)):
            a = points[i]
            b = points[(i + 1) % len(points)]
            draw.line([a, b], fill=light, width=4)

        for x, y in points:
            draw.ellipse([x - 9, y - 9, x + 9, y + 9], fill=gold)

    # --------------------------------------------------------
    # GEOMETRY MASTER - triangle row
    # --------------------------------------------------------

    elif pattern == "geometry":

        for i in range(5):
            x = 150 + i * 165
            draw.polygon(
                [(x, 560), (x + 80, 435), (x + 160, 560)],
                outline=light,
                width=5,
            )
            draw.line([(x, 560), (x + 160, 560)], fill=gold, width=4)

    # --------------------------------------------------------
    # CHAMPION - starburst
    # --------------------------------------------------------

    elif pattern == "champion":

        center_x, center_y = 512, 480

        for angle in range(0, 360, 24):
            rad = math.radians(angle)
            end_x = center_x + math.cos(rad) * 400
            end_y = center_y + math.sin(rad) * 400
            draw.line([(center_x, center_y), (end_x, end_y)], fill=light, width=3)


def apply_patterns(background, theme):
    """
    Draws the rarity pattern onto a transparent layer, then fades
    it out vertically so it always stays behind the portrait and
    never overlaps the name, stats or footer.
    """

    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw_patterns(ImageDraw.Draw(layer), theme, theme["pattern"])

    fade = Image.new("L", (WIDTH, HEIGHT), 0)
    fade_draw = ImageDraw.Draw(fade)

    for y in range(HEIGHT):

        if y < PATTERN_TOP:
            alpha = 0
        elif y < PATTERN_FADE_START:
            alpha = 255
        elif y < PATTERN_FADE_END:
            ratio = (y - PATTERN_FADE_START) / (PATTERN_FADE_END - PATTERN_FADE_START)
            alpha = int(255 * (1 - ratio))
        else:
            alpha = 0

        fade_draw.line([(0, y), (WIDTH, y)], fill=alpha)

    r, g, b, a = layer.split()
    a = ImageChops.multiply(a, fade)
    layer = Image.merge("RGBA", (r, g, b, a))

    background.paste(layer, (0, 0), layer)


# ============================================================
# FRAME
# ============================================================

def draw_frame(draw, theme):

    polygon = card_polygon()

    draw.line(polygon + [polygon[0]], fill=theme["dark"], width=32, joint="curve")
    draw.line(polygon + [polygon[0]], fill=theme["gold"], width=16, joint="curve")
    draw.line(polygon + [polygon[0]], fill=theme["light"], width=5, joint="curve")


# ============================================================
# PLAYER / PHOTO
# ============================================================

def draw_student_image(image, profile, theme):

    draw = ImageDraw.Draw(image)
    center_x = 512

    if PHOTO_PATH.exists():

        try:
            photo = Image.open(PHOTO_PATH).convert("RGBA")
            photo.thumbnail((390, 460))

            x = center_x - photo.width // 2
            y = 325

            image.paste(photo, (x, y), photo)
            return

        except Exception:
            pass

    head_box = [center_x - 105, 350, center_x + 105, 580]
    draw.ellipse(head_box, fill=theme["dark"])

    draw.polygon(
        [
            (285, 850), (325, 635), (395, 580), (512, 565),
            (629, 580), (699, 635), (739, 850),
        ],
        fill=theme["dark"],
    )

    draw.arc(head_box, 0, 360, fill=theme["light"], width=5)


# ============================================================
# HEADER
# ============================================================

def draw_header(draw, profile, theme, event_id):

    rating_font = load_font(112, True)
    ovr_font = load_font(30, True)
    event_font = load_font(25, True)
    name_font = load_font(47, True)

    rating = int(profile["overall_rating"])
    rating_text = str(rating)

    # --------------------------------------------------------
    # Rating plate - sized to fit "85 / OVR" exactly, not a
    # fixed oversized box
    # --------------------------------------------------------

    r_box = draw.textbbox((0, 0), rating_text, font=rating_font)
    o_box = draw.textbbox((0, 0), "OVR", font=ovr_font)

    r_w, r_h = r_box[2] - r_box[0], r_box[3] - r_box[1]
    o_w, o_h = o_box[2] - o_box[0], o_box[3] - o_box[1]

    pad_x, pad_top, gap, pad_bottom = 32, 26, 8, 22

    plate_w = max(r_w, o_w) + pad_x * 2
    plate_h = pad_top + r_h + gap + o_h + pad_bottom
    plate_x, plate_y = 92, 90

    safe_left, _ = safe_bounds_for_range(plate_y, plate_y + plate_h)
    plate_x = max(plate_x, safe_left)

    draw.rounded_rectangle(
        [plate_x, plate_y, plate_x + plate_w, plate_y + plate_h],
        radius=22,
        fill=theme["dark"],
    )

    draw.text(
        (plate_x + pad_x - r_box[0], plate_y + pad_top - r_box[1]),
        rating_text,
        font=rating_font,
        fill=theme["light"],
    )

    draw.text(
        (plate_x + pad_x - o_box[0], plate_y + pad_top + r_h + gap - o_box[1]),
        "OVR",
        font=ovr_font,
        fill=theme["gold"],
    )

    # --------------------------------------------------------
    # Event badge - a pill that hugs the label text, so long
    # names like "GEOMETRY MASTER" never spill outside it
    # --------------------------------------------------------

    event_name = EVENT_NAMES.get(event_id, "SPECIAL")

    e_box = draw.textbbox((0, 0), event_name, font=event_font)
    e_w, e_h = e_box[2] - e_box[0], e_box[3] - e_box[1]

    badge_pad_x, badge_pad_y = 24, 14
    badge_right = 900
    badge_top = 90
    badge_h = e_h + badge_pad_y * 2
    badge_w = e_w + badge_pad_x * 2

    _, safe_right = safe_bounds_for_range(badge_top, badge_top + badge_h)
    badge_right = min(badge_right, safe_right)
    badge_left = badge_right - badge_w

    draw.rounded_rectangle(
        [badge_left, badge_top, badge_right, badge_top + badge_h],
        radius=badge_h / 2,
        fill=theme["dark"],
    )

    draw.text(
        (badge_right - badge_pad_x, badge_top + badge_h / 2),
        event_name,
        anchor="rm",
        font=event_font,
        fill=theme["light"],
    )

    # --------------------------------------------------------
    # Name - shrinks to fit so long names can't cross the frame
    # --------------------------------------------------------

    name_text = profile["student_name"].upper()
    left_bound, right_bound = shield_bounds_at_y(870)
    max_name_width = (right_bound - left_bound) - 100

    name_size = 47
    while name_size > 24:
        name_font = load_font(name_size, True)
        box = draw.textbbox((0, 0), name_text, font=name_font)
        if box[2] - box[0] <= max_name_width:
            break
        name_size -= 2

    draw.text(
        (512, 870),
        name_text,
        anchor="mm",
        font=name_font,
        fill=theme["light"],
    )

    divider_left, divider_right = safe_bounds_for_range(900, 910)
    draw.line([(divider_left, 905), (divider_right, 905)], fill=theme["light"], width=3)


# ============================================================
# SKILLS
# ============================================================

def draw_skills(draw, profile, theme):

    label_font = load_font(29, True)
    value_font = load_font(34, True)

    left_x = 165
    right_x = 540

    start_y = 965
    row_gap = 72
    bar_width = 112
    bar_height = 7

    # The card narrows as it goes down, so the last row (CAL / CAS)
    # is the tightest fit against the frame. Clamp both columns - and
    # shrink the bar if needed - against the safe window for the
    # whole block, not just the top row.
    block_bottom = start_y + 3 * row_gap + 40
    safe_left, safe_right = safe_bounds_for_range(start_y, block_bottom)

    left_x = max(left_x, safe_left)
    right_edge = right_x + 160 + bar_width
    if right_edge > safe_right:
        bar_width = max(60, bar_width - (right_edge - safe_right))

    left_skills = [
        ("ALG", "algebra"),
        ("NTH", "number_theory"),
        ("PRO", "proof"),
        ("CAL", "calculation"),
    ]

    right_skills = [
        ("GEO", "geometry"),
        ("DMC", "discrete_mathematics"),
        ("REA", "reasoning"),
        ("CAS", "case_analysis"),
    ]

    def draw_stat(label, key, x, y):

        value = int(profile.get(key, 0))
        value_text = str(value)

        draw.text((x, y), label, font=label_font, fill=theme["gold"])
        draw.text((x + 100, y - 3), value_text, font=value_font, fill=theme["light"])

        value_box = draw.textbbox((x + 100, y - 3), value_text, font=value_font)
        bar_x = max(x + 160, value_box[2] + 14)
        bar_y = y + 24

        draw.rounded_rectangle(
            [bar_x, bar_y, bar_x + bar_width, bar_y + bar_height],
            radius=4,
            fill=theme["dark"],
        )

        draw.rounded_rectangle(
            [bar_x, bar_y, bar_x + int(bar_width * value / 100), bar_y + bar_height],
            radius=4,
            fill=theme["light"],
        )

    for row in range(4):

        y = start_y + row * row_gap

        draw_stat(*left_skills[row], left_x, y)
        draw_stat(*right_skills[row], right_x, y)


# ============================================================
# FOOTER
# ============================================================

def draw_footer(draw, profile, theme):

    label_font = load_font(19, True)
    value_font = load_font(32, True)

    attempted = profile.get("problems_attempted", 0)
    solved = profile.get("problems_solved", 0)
    success = round(solved / attempted * 100) if attempted else 0

    items = [
        ("PROBLEMS", str(attempted)),
        ("SOLVED", str(solved)),
        ("SUCCESS", f"{success}%"),
    ]

    footer_y = 1222
    label_y = footer_y + 26
    value_y = footer_y + 54

    # Divider line: width taken from the actual shield edge at
    # this y, with a safety margin, so it can never poke outside
    # the card frame.
    left_bound, right_bound = shield_bounds_at_y(footer_y)
    draw.line(
        [(left_bound + 34, footer_y), (right_bound - 34, footer_y)],
        fill=theme["light"],
        width=3,
    )

    # Item positions: computed from the narrowest point the text
    # actually reaches (bottom of the value row), split into three
    # equal slots, so nothing can ever cross the border - no matter
    # how long the numbers get.
    probe_left, probe_right = shield_bounds_at_y(value_y + 26)
    usable_left = probe_left + 26
    usable_right = probe_right - 26
    slot_w = (usable_right - usable_left) / 3

    for i, (label, value) in enumerate(items):

        cx = usable_left + slot_w * (i + 0.5)

        draw.text((cx, label_y), label, anchor="ma", font=label_font, fill=theme["gold"])
        draw.text((cx, value_y), value, anchor="ma", font=value_font, fill=theme["light"])


# ============================================================
# CREATE ONE CARD
# ============================================================

def create_card(profile, event_id):

    rating = int(profile["overall_rating"])
    card_type = get_card_type(rating)

    theme = CARD_THEMES[card_type].copy()
    theme.update(EVENT_STYLES.get(event_id, {}))

    background = gradient_background(theme)
    apply_patterns(background, theme)

    mask = create_mask()

    card = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    card.paste(background, (0, 0), mask)

    draw = ImageDraw.Draw(card)

    draw_frame(draw, theme)
    draw_student_image(card, profile, theme)
    draw_header(draw, profile, theme, event_id)
    draw_skills(draw, profile, theme)
    draw_footer(draw, profile, theme)

    return card, card_type


# ============================================================
# MAIN
# ============================================================

def main():

    profile = load_profile()
    events = determine_events(profile)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("OLYMPIAD INTELLIGENCE - PREMIUM STUDENT CARDS")
    print("=" * 70)
    print()
    print(f"Student: {profile['student_name']}")
    print(f"Overall: {profile['overall_rating']}")
    print(f"Tier: {profile.get('tier', 'Unknown')}")
    print()
    print("Generating cards...")
    print()

    for event_id in events:

        event_name = EVENT_NAMES.get(event_id, event_id.upper())
        card, card_type = create_card(profile, event_id)

        output_path = OUTPUT_DIR / f"{profile['student_id']}_{event_id}.png"
        card.save(output_path)

        print(f"{event_name:<22} | {card_type:<8} | {output_path}")

    print()
    print("=" * 70)
    print("CARD GENERATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
