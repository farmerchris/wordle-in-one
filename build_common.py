"""Wordle-in-One pairs using only common words (Wordle answer list) as clues."""
import json
from collections import defaultdict
from wio_core import score, load

answers = load('data/answers.txt')
idx = {w: i for i, w in enumerate(answers)}
pairs = []  # [clue_idx, target_idx, pattern]
for clue in answers:
    buckets = defaultdict(list)
    for t in answers:
        buckets[score(clue, t)].append(t)
    for pat, ts in buckets.items():
        if len(ts) == 1 and pat != 'GGGGG':
            pairs.append((idx[clue], idx[ts[0]], pat))
print(len(pairs), 'pairs')
json.dump({'words': answers, 'pairs': ''.join(f"{c:04d}{t:04d}{p}" for c, t, p in pairs)},
          open('data/common_pairs.json', 'w'), separators=(',', ':'))

import os
os.makedirs('docs', exist_ok=True)
codec = open('codec.js').read()
html = open('template.html').read().replace('__CODEC__', codec).replace('__DATA__', open('data/common_pairs.json').read())
open('docs/index.html', 'w').write(html)
open('docs/puzzle.html', 'w').write(open('puzzle_template.html').read().replace('__CODEC__', codec))

# Themes page: clue + Play link per puzzle, answers hidden behind the link token.
from html import escape
from codec import encode_pair
from themes import THEMES, theme_puzzles

def tiles(word, pat):
    return ''.join(f'<div class="t {p}">{ch}</div>' for ch, p in zip(word, pat))

sections, jump, total = [], [], 0
for name in sorted(THEMES):
    hits = theme_puzzles(name, answers)
    if not hits:
        continue
    total += len(hits)
    anchor = escape(name.replace(' ', '-'))
    jump.append(f'<a href="#{anchor}">{escape(name)} ({len(hits)})</a>')
    cards = ''.join(
        f'<a class="card" href="puzzle.html?p={encode_pair(clue, t)}">'
        f'<div class="row">{tiles(clue, pat)}</div><span class="play">Play ↗</span></a>'
        for k, clue, pat, t in hits)
    sections.append(f'  <h2 id="{anchor}">{escape(name)} <span class="n">{len(hits)}</span></h2>\n'
                    f'  <div class="grid">{cards}</div>')
page = (open('themes_template.html').read().replace('__CODEC__', codec)
        .replace('__SUMMARY__', f'{total} puzzles in {len(sections)} themes.')
        .replace('__JUMP__', '\n    '.join(jump))
        .replace('__SECTIONS__', '\n'.join(sections)))
open('docs/themes.html', 'w').write(page)
print(f'themes page: {total} puzzles, {len(sections)} themes')
