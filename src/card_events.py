"""
OLYMPIAD INTELLIGENCE
Student Card Event System

Creates event metadata for student cards.
"""


CARD_EVENTS = {
    "standard": {
        "name": "Standard",
        "description": "Standard Olympiad Intelligence card",
        "rarity": "Standard",
    },

    "champion": {
        "name": "Champion",
        "description": "Awarded for exceptional olympiad performance",
        "rarity": "Special",
    },

    "geometry_master": {
        "name": "Geometry Master",
        "description": "Special card for outstanding geometry performance",
        "rarity": "Special",
    },

    "proof_master": {
        "name": "Proof Master",
        "description": "Special card for outstanding proof performance",
        "rarity": "Special",
    },

    "olympiad_elite": {
        "name": "Olympiad Elite",
        "description": "Elite-level olympiad performance",
        "rarity": "Elite",
    },
}


def get_available_events():
    """Return all available card events."""

    return CARD_EVENTS


def get_event(event_id):
    """Return information about a specific event."""

    return CARD_EVENTS.get(event_id)


def determine_events(profile):
    """
    Automatically determine events based on
    the student's performance.
    """

    events = ["standard"]

    rating = profile.get("overall_rating", 0)

    geometry = profile.get("geometry", 0)
    proof = profile.get("proof", 0)

    if rating >= 90:
        events.append("olympiad_elite")

    if rating >= 95:
        events.append("champion")

    if geometry >= 90:
        events.append("geometry_master")

    if proof >= 90:
        events.append("proof_master")

    return events


def print_events(profile):

    events = determine_events(profile)

    print()
    print("=" * 70)
    print("OLYMPIAD INTELLIGENCE - CARD EVENTS")
    print("=" * 70)
    print()

    print("Available Events:")
    print()

    for event_id in events:

        event = CARD_EVENTS[event_id]

        print(
            f"{event_id:<20} "
            f"{event['name']:<20} "
            f"{event['rarity']}"
        )

    print()
    print("=" * 70)


if __name__ == "__main__":

    test_profile = {
        "overall_rating": 85,
        "geometry": 84,
        "proof": 92,
    }

    print_events(test_profile)