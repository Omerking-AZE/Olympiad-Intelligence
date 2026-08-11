"""
OLYMPIAD INTELLIGENCE
FIFA-Style Student Card System

Generates decorative collectible-style student cards
based on olympiad performance, rarity and events.
"""

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from card_events import determine_events, CARD_EVENTS


WIDTH = 900
HEIGHT = 1250


# ============================================================
# FONTS
# ============================================================

def load_font(size, bold=False):

    if bold:
        font_paths = [
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/segoeuib.ttf",
            "C:/Windows/Fonts/calibrib.ttf",
        ]
    else:
        font_paths = [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/segoeui.ttf",
            "C:/Windows/Fonts/calibri.ttf",
        ]

    for path in font_paths:
        if Path(path).exists():
            return ImageFont.truetype(path, size)

    return ImageFont.load_default()


# ============================================================
# PROFILE
# ============================================================

def load_profile():

    path = Path(
        "data/processed/student_profile.json"
    )

    if not path.exists():
        raise FileNotFoundError(
            "student_profile.json not found. "
            "Run student_profile.py first."
        )

    with open(path, "r", encoding="utf-8") as file:
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
# CARD THEMES
# ============================================================

CARD_THEMES = {

    "BRONZE": {
        "bg": (62, 35, 22),
        "bg2": (117, 69, 39),
        "primary": (224, 157, 100),
        "light": (255, 207, 160),
        "dark": (47, 25, 16),
        "glow": (190, 105, 52),
    },

    "SILVER": {
        "bg": (52, 57, 67),
        "bg2": (125, 132, 145),
        "primary": (218, 224, 234),
        "light": (255, 255, 255),
        "dark": (38, 42, 49),
        "glow": (174, 187, 204),
    },

    "RARE": {
        "bg": (20, 38, 70),
        "bg2": (45, 92, 160),
        "primary": (116, 178, 255),
        "light": (226, 244, 255),
        "dark": (12, 25, 48),
        "glow": (72, 143, 229),
    },

    "SPECIAL": {
        "bg": (28, 30, 75),
        "bg2": (85, 42, 143),
        "primary": (102, 225, 255),
        "light": (231, 248, 255),
        "dark": (18, 18, 50),
        "glow": (178, 90, 255),
    },

    "ELITE": {
        "bg": (42, 25, 67),
        "bg2": (110, 58, 155),
        "primary": (237, 195, 92),
        "light": (255, 244, 185),
        "dark": (31, 17, 48),
        "glow": (255, 210, 78),
    },

    "ICON": {
        "bg": (66, 40, 10),
        "bg2": (156, 105, 22),
        "primary": (255, 213, 77),
        "light": (255, 248, 188),
        "dark": (51, 29, 6),
        "glow": (255, 226, 103),
    },
}


# ============================================================
# EVENT THEMES
# ============================================================

EVENT_THEMES = {

    "champion": {
        "primary": (255, 215, 75),
        "light": (255, 248, 180),
        "accent": (211, 145, 30),
    },

    "geometry_master": {
        "primary": (77, 229, 208),
        "light": (208, 255, 248),
        "accent": (25, 157, 146),
    },

    "proof_master": {
        "primary": (199, 140, 255),
        "light": (241, 218, 255),
        "accent": (111, 62, 183),
    },

    "olympiad_elite": {
        "primary": (232, 205, 255),
        "light": (255, 248, 255),
        "accent": (135, 95, 218),
    },
}


# ============================================================
# CARD SHAPE
# ============================================================

def card_polygon():

    return [
        (145, 45),
        (755, 45),

        (825, 105),
        (842, 220),

        (855, 355),
        (842, 515),

        (850, 705),
        (835, 900),

        (810, 1055),
        (760, 1145),

        (680, 1180),
        (600, 1210),

        (500, 1235),
        (450, 1260),

        (400, 1235),
        (300, 1210),
        (220, 1180),
        (140, 1145),

        (90, 1055),
        (65, 900),

        (50, 705),
        (58, 515),

        (45, 355),
        (58, 220),

        (75, 105),
    ]


# ============================================================
# MASK
# ============================================================

def create_card_mask():

    mask = Image.new(
        "L",
        (WIDTH, HEIGHT),
        0
    )

    draw = ImageDraw.Draw(mask)

    draw.polygon(
        card_polygon(),
        fill=255
    )

    return mask


# ============================================================
# BACKGROUND
# ============================================================

def create_background(theme, event_id):

    image = Image.new(
        "RGB",
        (WIDTH, HEIGHT),
        theme["bg"]
    )

    draw = ImageDraw.Draw(image)

    # Gradient
    for y in range(HEIGHT):

        ratio = y / HEIGHT

        r = int(
            theme["bg"][0] * (1 - ratio)
            + theme["bg2"][0] * ratio
        )

        g = int(
            theme["bg"][1] * (1 - ratio)
            + theme["bg2"][1] * ratio
        )

        b = int(
            theme["bg"][2] * (1 - ratio)
            + theme["bg2"][2] * ratio
        )

        draw.line(
            [(0, y), (WIDTH, y)],
            fill=(r, g, b)
        )

    # Large diagonal bands
    draw.polygon(
        [
            (0, 300),
            (WIDTH, 40),
            (WIDTH, 190),
            (0, 480),
        ],
        fill=theme["primary"]
    )

    draw.polygon(
        [
            (0, 520),
            (WIDTH, 180),
            (WIDTH, 220),
            (0, 610),
        ],
        fill=theme["dark"]
    )

    draw.polygon(
        [
            (0, 800),
            (WIDTH, 580),
            (WIDTH, 680),
            (0, 920),
        ],
        fill=theme["primary"]
    )

    # Geometric pattern
    for i in range(18):

        x = 100 + i * 48
        y = 100 + (i % 5) * 155

        draw.line(
            [
                (x, y),
                (x + 120, y - 70)
            ],
            fill=theme["light"],
            width=2
        )

        draw.line(
            [
                (x + 120, y - 70),
                (x + 170, y + 20)
            ],
            fill=theme["primary"],
            width=2
        )

    # Event-specific geometry
    if event_id == "geometry_master":

        for i in range(6):

            x = 120 + i * 130

            draw.polygon(
                [
                    (x, 650),
                    (x + 65, 540),
                    (x + 130, 650),
                ],
                outline=theme["light"],
                width=4
            )

    elif event_id == "proof_master":

        for i in range(7):

            x = 90 + i * 125

            draw.line(
                [
                    (x, 650),
                    (x + 100, 820),
                ],
                fill=theme["light"],
                width=3
            )

            draw.line(
                [
                    (x + 100, 820),
                    (x + 40, 940),
                ],
                fill=theme["primary"],
                width=3
            )

    elif event_id == "champion":

        # Decorative rays
        center = (450, 750)

        for angle in range(0, 360, 30):

            rad = math.radians(angle)

            x = center[0] + math.cos(rad) * 420
            y = center[1] + math.sin(rad) * 420

            draw.line(
                [
                    center,
                    (x, y)
                ],
                fill=theme["light"],
                width=3
            )

    return image


# ============================================================
# FRAME
# ============================================================

def draw_frame(image, theme):

    draw = ImageDraw.Draw(image)

    polygon = card_polygon()

    draw.line(
        polygon + [polygon[0]],
        fill=theme["dark"],
        width=28,
        joint="curve"
    )

    draw.line(
        polygon + [polygon[0]],
        fill=theme["primary"],
        width=13,
        joint="curve"
    )

    draw.line(
        polygon + [polygon[0]],
        fill=theme["light"],
        width=4,
        joint="curve"
    )


# ============================================================
# PLAYER AREA
# ============================================================

def draw_student_area(
    image,
    profile,
    theme,
):

    draw = ImageDraw.Draw(image)

    # Decorative player silhouette area

    center_x = 450

    draw.ellipse(
        [
            center_x - 115,
            360,
            center_x + 115,
            590
        ],
        fill=theme["dark"]
    )

    draw.polygon(
        [
            (270, 850),
            (310, 640),
            (380, 590),
            (520, 590),
            (590, 640),
            (630, 850),
        ],
        fill=theme["dark"]
    )

    # Light silhouette outline

    draw.arc(
        [
            center_x - 115,
            360,
            center_x + 115,
            590
        ],
        0,
        360,
        fill=theme["primary"],
        width=5
    )

    # Future photo placeholder

    draw.text(
        (450, 625),
        "STUDENT",
        anchor="mm",
        font=load_font(24, True),
        fill=theme["primary"]
    )


# ============================================================
# HEADER
# ============================================================

def draw_header(
    image,
    profile,
    theme,
    event_id,
):

    draw = ImageDraw.Draw(image)

    rating_font = load_font(105, True)
    position_font = load_font(32, True)
    name_font = load_font(45, True)
    event_font = load_font(25, True)

    rating = profile["overall_rating"]

    draw.text(
        (145, 105),
        str(rating),
        font=rating_font,
        fill=theme["light"]
    )

    draw.text(
        (165, 215),
        "MATH",
        font=position_font,
        fill=theme["primary"]
    )

    event = CARD_EVENTS[event_id]

    draw.text(
        (650, 100),
        event["name"].upper(),
        anchor="ra",
        font=event_font,
        fill=theme["light"]
    )

    name = profile["student_name"].upper()

    draw.text(
        (450, 870),
        name,
        anchor="mm",
        font=name_font,
        fill=theme["light"]
    )


def draw_skills(
    image,
    profile,
    theme,
):

    draw = ImageDraw.Draw(image)

    skills = [
        ("ALG", "algebra"),
        ("GEO", "geometry"),
        ("NT", "number_theory"),
        ("DM", "discrete_mathematics"),
        ("PRO", "proof"),
        ("REA", "reasoning"),
        ("CAL", "calculation"),
        ("CASE", "case_analysis"),
    ]

    # Daha içəridə və daha sıx yerləşdirmə
    positions = [
        (170, 945),
        (455, 945),

        (170, 995),
        (455, 995),

        (170, 1045),
        (455, 1045),

        (170, 1095),
        (455, 1095),
    ]

    label_font = load_font(22, True)
    value_font = load_font(26, True)

    for (label, key), (x, y) in zip(
        skills,
        positions
    ):

        value = profile.get(key, 0)

        draw.text(
            (x, y),
            label,
            font=label_font,
            fill=theme["primary"]
        )

        draw.text(
            (x + 85, y - 2),
            str(value),
            font=value_font,
            fill=theme["light"]
        )


def draw_footer(
    image,
    profile,
    theme,
):

    draw = ImageDraw.Draw(image)

    small_font = load_font(15, True)

    attempted = profile.get(
        "problems_attempted",
        0
    )

    solved = profile.get(
        "problems_solved",
        0
    )

    if attempted > 0:
        success = round(
            solved / attempted * 100
        )
    else:
        success = 0

    text = (
        f"{solved}/{attempted} SOLVED   "
        f"{success}% SUCCESS"
    )

    # Bir az yuxarı və mərkəzdə
    draw.text(
        (450, 1165),
        text,
        anchor="mm",
        font=small_font,
        fill=theme["light"]
    )

# ============================================================
# CARD GENERATION
# ============================================================

def create_card(profile, event_id):

    rating = profile["overall_rating"]

    card_type = get_card_type(rating)

    theme = CARD_THEMES[card_type].copy()

    if event_id in EVENT_THEMES:

        event_theme = EVENT_THEMES[event_id]

        theme["primary"] = event_theme["primary"]
        theme["light"] = event_theme["light"]
        theme["glow"] = event_theme["accent"]

    image = create_background(
        theme,
        event_id
    )

    # Apply card mask
    mask = create_card_mask()

    card = Image.new(
        "RGB",
        (WIDTH, HEIGHT),
        theme["bg"]
    )

    card.paste(
        image,
        (0, 0),
        mask
    )

    # Draw frame
    draw_frame(
        card,
        theme
    )

    # Draw components
    draw_student_area(
        card,
        profile,
        theme
    )

    draw_header(
        card,
        profile,
        theme,
        event_id
    )

    draw_skills(
        card,
        profile,
        theme
    )

    draw_footer(
        card,
        profile,
        theme
    )

    return card


# ============================================================
# MAIN
# ============================================================

def main():

    profile = load_profile()

    events = determine_events(profile)

    output_dir = Path(
        "data/processed/cards"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    print("=" * 70)
    print(
        "OLYMPIAD INTELLIGENCE - FIFA STYLE CARDS"
    )
    print("=" * 70)
    print()

    print(
        f"Student: {profile['student_name']}"
    )

    print(
        f"Overall: {profile['overall_rating']}"
    )

    print(
        f"Tier: {profile['tier']}"
    )

    print()

    print("Generating cards...")
    print()

    for event_id in events:

        event = CARD_EVENTS[event_id]

        card = create_card(
            profile,
            event_id
        )

        output_path = (
            output_dir
            / f"{profile['student_id']}_{event_id}.png"
        )

        card.save(
            output_path,
            quality=95
        )

        print(
            f"{event['name']:<25}"
            f" -> {output_path}"
        )

    print()
    print("=" * 70)
    print("CARD GENERATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()