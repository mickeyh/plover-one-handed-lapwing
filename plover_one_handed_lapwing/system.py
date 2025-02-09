# Import everything from Lapwing, we'll override selectively.
from plover_lapwing.system import *


KEYS = ("#", "q", "a", "w") + KEYS[1:]  # q = -D, a = -Z, w = left only


KEYMAPS = {
    # Override the Keyboard keymap to (1) shift left and right one key (2) remove the left pinky `#`.
    "Keyboard": KEYMAPS["Keyboard"]
    | {
        "q": "q",
        "a": "a",
        "w": "w",
        "#": ("1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "="),
        "S-": "s",
        "T-": "e",
        "K-": "d",
        "P-": "r",
        "W-": "f",
        "H-": "t",
        "R-": "g",
        "A-": "v",
        "O-": "b",
        "*": ("y", "h"),
        "arpeggiate": "space",
        # Suppress adjacent keys to prevent miss-strokes.
        "no-op": ("z", "x", "c", ",", ".", "/", "]", "\\"),
    },
}