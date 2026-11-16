"""Find Wordle-in-One puzzles: (clue, target) pairs where the clue's score
against the target is matched by no other possible answer."""

import sys
from collections import defaultdict


def score(guess, target):
    res = ["B"] * 5
    left = defaultdict(int)
    for i, (g, t) in enumerate(zip(guess, target)):
        if g == t:
            res[i] = "G"
        else:
            left[t] += 1
    for i, g in enumerate(guess):
        if res[i] == "B" and left[g] > 0:
            res[i] = "Y"
            left[g] -= 1
    return "".join(res)


def load(path):
    return [w.strip().lower() for w in open(path) if len(w.strip()) == 5]


answers = load("data/answers.txt")
clues = sorted(set(answers) | set(load("data/allowed.txt")))

by_target = defaultdict(list)
for clue in clues:
    buckets = defaultdict(list)
    for t in answers:
        buckets[score(clue, t)].append(t)
    for pat, ts in buckets.items():
        if len(ts) == 1 and pat != "GGGGG":
            by_target[ts[0]].append((clue, pat))

EMOJI = {"G": "🟩", "Y": "🟨", "B": "⬜"}
with open("wordle_in_one.txt", "w") as f:
    for t in answers:
        f.write(f"{t.upper()}  ({len(by_target[t])} clues)\n")
        for clue, pat in by_target[t]:
            f.write(f"  {clue.upper()}  {''.join(EMOJI[c] for c in pat)}  {pat}\n")
with open("wordle_in_one.csv", "w") as f:
    f.write("target,clue,pattern\n")
    for t in answers:
        for clue, pat in by_target[t]:
            f.write(f"{t},{clue},{pat}\n")
n = sum(len(v) for v in by_target.values())
print(
    f"{n} puzzles; {sum(1 for t in answers if by_target[t])}/{len(answers)} targets have >=1 clue"
)
