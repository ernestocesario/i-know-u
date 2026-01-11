import random

class HeaderTaglines:
    TAGLINES = [
        "Nothing stays private forever",
        "Digital anonymity is a comfortable lie",
        "Every click leaves a scar",
        "Privacy died with your first post",
        "In the web we trust, until we don't",
        "Every post tells a story you didn't mean to share",
        "We see what you're hiding in plain sight",
        "The truth is in the pixels",
        "What you share reveals what you hide",
    ]

    @staticmethod
    def get_random_tagline() -> str:
        return f"{random.choice(HeaderTaglines.TAGLINES)}..."