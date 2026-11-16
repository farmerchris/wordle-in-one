"""Wordle-in-One pairs using only common words (Wordle answer list) as clues."""

import json
from collections import defaultdict
from wio_core import score, load

answers = load("data/answers.txt")
idx = {w: i for i, w in enumerate(answers)}
pairs = []  # [clue_idx, target_idx, pattern]
for clue in answers:
    buckets = defaultdict(list)
    for t in answers:
        buckets[score(clue, t)].append(t)
    for pat, ts in buckets.items():
        if len(ts) == 1 and pat != "GGGGG":
            pairs.append((idx[clue], idx[ts[0]], pat))
print(len(pairs), "pairs")
json.dump(
    {"words": answers, "pairs": "".join(f"{c:04d}{t:04d}{p}" for c, t, p in pairs)},
    open("data/common_pairs.json", "w"),
    separators=(",", ":"),
)

import os

os.makedirs("docs", exist_ok=True)
codec = open("codec.js").read()
# Compact form for the page: words packed into one string, and for each clue (in word
# order) a count then its target indexes as gaps from the previous one. Each number is a
# base-64 varint: 5 data bits per char, chars >= 32 mean "more follows". Colors are
# recomputed in the page.
B64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"


def varint(n):
    out = ""
    while n >= 32:
        out += B64[32 + (n & 31)]
        n >>= 5
    return out + B64[n]


by_clue = defaultdict(list)
for c, t, _ in pairs:
    by_clue[c].append(t)
packed = ""
for c in range(len(answers)):
    ts, prev = sorted(by_clue[c]), 0
    packed += varint(len(ts))
    for t in ts:
        packed += varint(t - prev)
        prev = t
page_data = json.dumps(
    {"words": "".join(answers), "pairs": packed}, separators=(",", ":")
)
html = (
    open("template.html")
    .read()
    .replace("__CODEC__", codec)
    .replace("__DATA__", page_data)
)
open("docs/index.html", "w").write(html)
open("docs/puzzle.html", "w").write(
    open("puzzle_template.html").read().replace("__CODEC__", codec)
)

# Themes page: clue + Play link per puzzle, answers hidden behind the link token.
from html import escape
from codec import encode_pair
from themes import THEMES, theme_puzzles


def tiles(word, pat):
    return "".join(f'<div class="t {p}">{ch}</div>' for ch, p in zip(word, pat))


sections, jump, total = [], [], 0
for name in sorted(THEMES):
    hits = theme_puzzles(name, answers)
    if not hits:
        continue
    total += len(hits)
    anchor = escape(name.replace(" ", "-"))
    jump.append(f'<a href="#{anchor}">{escape(name)} ({len(hits)})</a>')
    cards = "".join(
        f'<a class="card" href="puzzle.html?p={encode_pair(clue, t)}">'
        f'<div class="row">{tiles(clue, pat)}</div><span class="play">Play ↗</span></a>'
        for k, clue, pat, t in hits
    )
    sections.append(
        f'  <h2 id="{anchor}">{escape(name)} <span class="n">{len(hits)}</span></h2>\n'
        f'  <div class="grid">{cards}</div>'
    )
page = (
    open("themes_template.html")
    .read()
    .replace("__CODEC__", codec)
    .replace("__SUMMARY__", f"{total} puzzles in {len(sections)} themes.")
    .replace("__JUMP__", "\n    ".join(jump))
    .replace("__SECTIONS__", "\n".join(sections))
)
open("docs/themes.html", "w").write(page)
print(f"themes page: {total} puzzles, {len(sections)} themes")
