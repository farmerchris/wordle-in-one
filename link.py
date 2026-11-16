"""Print a puzzle link for a clue/target pair (any letters, real words or not).

usage: python3 link.py CLUE TARGET [--base URL]
"""

import argparse
from pathlib import Path
from codec import encode_pair
from wio_core import score, load

ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
ap.add_argument("clue")
ap.add_argument("target")
ap.add_argument(
    "--base",
    default="puzzle.html",
    help="puzzle page URL, e.g. https://you.github.io/repo/puzzle.html",
)
args = ap.parse_args()
clue, target = args.clue.lower(), args.target.lower()

pat = score(clue, target)
rivals = [
    w
    for w in load(Path(__file__).parent / "data/answers.txt")
    if w != target and score(clue, w) == pat
]
print("".join({"G": "🟩", "Y": "🟨", "B": "⬜"}[c] for c in pat), clue.upper())
print(
    f"warning: not unique, also fits {', '.join(w.upper() for w in rivals[:5])}"
    if rivals
    else "unique ✓"
)
print(f"{args.base}?p={encode_pair(clue, target)}")
