"""Build the Russian on-screen keyboard layout for reMarkable.

Usage: python3 make_layout.py <output json>

Letters are the standard ЙЦУКЕН arrangement. Everything not defined here
(space bar row, symbols popup) is inherited from the tablet's en_US layout.
"""
import json
import sys

ROW1 = "йцукенгшщзх"
ROW2 = "фывапролджэ"
ROW3 = "ячсмитьбю"
# Extra characters offered on long-press, keyed by the character on the key.
ALTERNATES = {
    "е": ["ё"],
    "ь": ["ъ"],
    "-": ["–", "—"],
    "$": ["₽"],
    '"': ["«", "»", "„", "“"],
    "#": ["№"],
}

# Symbols page: (default, shifted) per key. Empty strings are spacer keys.
SYMBOLS1 = list(zip("1234567890", "[]{}#%^*+="))
SYMBOLS2 = list(zip('-/:;()$&@"', "_\\|~<>€£¥•"))
SYMBOLS3 = [("", ""), ("", ""), ("?", "¿"), ("!", "¡"), ("'", "'"), ("", ""), ("", "")]

SHIFT = {"special": "shift"}


def variants(ch):
    return [ch] + ALTERNATES.get(ch, [])


def letter(ch):
    return {"default": variants(ch), "shifted": [v.upper() for v in variants(ch)]}


def symbol(pair):
    default, shifted = pair
    return {"default": variants(default), "shifted": variants(shifted)}


def main():
    layout = {
        "inherits": "en_US",
        "alphabetic": [
            [letter(c) for c in ROW1],
            [letter(c) for c in ROW2],
            [SHIFT] + [letter(c) for c in ROW3] + [{"special": "backspace", "width": 1}],
        ],
        "symbolic": [
            [symbol(p) for p in SYMBOLS1],
            [symbol(p) for p in SYMBOLS2],
            [SHIFT] + [symbol(p) for p in SYMBOLS3] + [{"special": "backspace"}],
        ],
    }
    with open(sys.argv[1], "w", encoding="utf-8") as f:
        json.dump(layout, f, ensure_ascii=False, indent=2)
        f.write("\n")


if __name__ == "__main__":
    main()
