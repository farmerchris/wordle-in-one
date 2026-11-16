"""Print the Wordle-in-One puzzles for any 5-letter clue word (need not be a real word).

usage: python3 clue.py WORD [WORD ...] [--min N] [--max N]
"""
import argparse
from pathlib import Path
from collections import defaultdict
from wio_core import score, load

EMOJI = {'G': '🟩', 'Y': '🟨', 'B': '⬜'}

ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
ap.add_argument('words', nargs='+')
ap.add_argument('--min', type=int, default=0, help='min colored boxes')
ap.add_argument('--max', type=int, default=5, help='max colored boxes')
args = ap.parse_args()

answers = load(Path(__file__).parent / 'data/answers.txt')
for clue in (w.lower() for w in args.words):
    if len(clue) != 5 or not clue.isalpha():
        print(f"{clue.upper()}: not a 5-letter word, skipped\n")
        continue
    buckets = defaultdict(list)
    for t in answers:
        buckets[score(clue, t)].append(t)
    hits = sorted((5 - pat.count('B'), pat, ts[0]) for pat, ts in buckets.items()
                  if len(ts) == 1 and pat != 'GGGGG' and args.min <= 5 - pat.count('B') <= args.max)
    print(f"{clue.upper()}: {len(hits)} puzzle(s)")
    for k, pat, t in hits:
        print(f"  {clue.upper()}  {''.join(EMOJI[c] for c in pat)}  →  {t.upper()}   ({k} colored)")
    print()
