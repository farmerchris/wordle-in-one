"""Find Wordle-in-One puzzles: (clue, target) pairs where the clue's score
against the target is matched by no other possible answer."""
import sys
from collections import defaultdict

def score(guess, target):
    res = ['B'] * 5
    left = defaultdict(int)
    for i, (g, t) in enumerate(zip(guess, target)):
        if g == t:
            res[i] = 'G'
        else:
            left[t] += 1
    for i, g in enumerate(guess):
        if res[i] == 'B' and left[g] > 0:
            res[i] = 'Y'
            left[g] -= 1
    return ''.join(res)

def load(path):
    return [w.strip().lower() for w in open(path) if len(w.strip()) == 5]

