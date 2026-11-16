"""Print the Wordle-in-One puzzles for any 5-letter target word (need not be on the list).

usage: python3 target.py WORD [WORD ...] [--min N] [--max N] [--all-clues]
"""
import argparse
from pathlib import Path
from wio_core import score, load

EMOJI = {'G': '🟩', 'Y': '🟨', 'B': '⬜'}
DATA = Path(__file__).parent / 'data'

ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
ap.add_argument('words', nargs='+')
ap.add_argument('--min', type=int, default=0, help='min colored boxes')
ap.add_argument('--max', type=int, default=5, help='max colored boxes')
ap.add_argument('--all-clues', action='store_true', help='also use obscure valid guesses as clues')
args = ap.parse_args()

answers = load(DATA / 'answers.txt')
clues = sorted(set(answers) | set(load(DATA / 'allowed.txt'))) if args.all_clues else answers
for target in (w.lower() for w in args.words):
    if len(target) != 5 or not target.isalpha():
        print(f"{target.upper()}: not a 5-letter word, skipped\n")
        continue
    others = [a for a in answers if a != target]
    note = '' if target in answers else ' (not on the answer list; treated as one extra possible answer)'
    hits = []
    for clue in clues:
        if clue == target:
            continue
        pat = score(clue, target)
        k = 5 - pat.count('B')
        if args.min <= k <= args.max and all(score(clue, o) != pat for o in others):
            hits.append((k, clue, pat))
    hits.sort()
    print(f"{target.upper()}: {len(hits)} puzzle(s){note}")
    for k, clue, pat in hits:
        print(f"  {clue.upper()}  {''.join(EMOJI[c] for c in pat)}  →  {target.upper()}   ({k} colored)")
    print()
