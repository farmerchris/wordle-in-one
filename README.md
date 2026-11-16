# Wordle-in-One

A Wordle-in-One puzzle shows you one **clue** word with its Wordle colors. Exactly one
possible answer gives those colors, and you have to find it.

```
RAVEN  🟩⬜⬜⬜🟩   →  ROBIN
```

This project finds every such puzzle, lets you browse them, and makes shareable puzzle
links, including custom ones that use made-up words.

## Word lists

- `data/answers.txt`: the 2,315 original Wordle answers. These are the **common words**,
  and the only words that count as possible answers.
- `data/allowed.txt`: the other 10,657 valid Wordle guesses (obscure words). These are
  only used as clues, and only when you ask for them (`--all-clues`, `wio.py`).

A clue makes a puzzle when no other answer word gives the same colors. The answer list
leaves out plurals, so a clue like `DORTS ⬜⬜⬜🟨🟩 → FETUS` works here even though
228 valid guesses (BATES, BITES…) give the same colors.

## Web pages (`docs/`, ready for GitHub Pages)

- `docs/index.html`: browse all 50,294 common-word puzzles. Filter by clue, target, and
  min/max colored boxes. Each row has a **Play** link. In the Clue box, a prefix
  (`cr`) or pattern (`_r_n_`) filters the list. Typing all 5 letters, a real word or
  not, lists every puzzle that clue makes. Every row has Play and Copy link buttons.
- `docs/themes.html`: 269 themed puzzles in 82 themes (generated from `themes.py`). Each
  card shows only the clue's colors and a Play link, never the answer.
- `docs/puzzle.html?p=TOKEN`: the game. The token hides the clue and target, so the URL
  doesn't give the answer away. The page needs no word list, so any letters work.
  Wrong guesses get no colors, since colors would give away extra clues. They're just
  listed as "Not it" so you can try again or give up.
- **Solved tracking:** winning a puzzle (not giving up) saves its token in the browser's
  `localStorage` (`wio-solved`). The browser and themes pages mark those puzzles
  "✓ Solved". The puzzle page always starts blank, so you can replay.

To publish, push the repo to GitHub, then go to Settings → Pages and choose to deploy
from the `main` branch, `/docs` folder.

To try it locally: `cd docs && python3 -m http.server`, then open http://localhost:8000.

### Tokens

`codec.js` and `codec.py` hold the same encoder. A token is 12 base-36 characters: the
10 letters scrambled with a chained key, plus a 2-character checksum, so most typos or
made-up tokens are rejected. This hides the answer from a glance but isn't security:
anyone who reads the page source can decode it.

## Command-line tools

| Command | What it does |
|---|---|
| `python3 clue.py WORD… [--min N] [--max N]` | All puzzles a clue creates. The clue can be any letters. |
| `python3 target.py WORD… [--min N] [--max N] [--all-clues]` | All clues that solve a target. Targets not on the list are added as one extra possible answer. |
| `python3 themes.py [THEME…] [--min N] [--max N] [--list]` | Puzzles where clue and target share a theme. Edit `THEMES` in the file to add your own. |
| `python3 link.py CLUE TARGET [--base URL]` | Prints the colors, a uniqueness check, and a puzzle link. Pass `--base https://you.github.io/repo/puzzle.html` for a full URL. |
| `python3 build_common.py` | Recomputes the common-word puzzles and rebuilds all three pages in `docs/` (about 8 seconds). |
| `python3 wio.py` | Full run with every valid guess as a clue. Writes `wordle_in_one.txt` and `.csv` (262,463 puzzles, about 50 seconds). |

`--min` and `--max` filter by the number of colored (yellow or green) boxes. The fewer
colored boxes, the harder the puzzle.

## Files

```
data/answers.txt, data/allowed.txt   word lists
data/common_pairs.json               generated puzzle data embedded in docs/index.html
wio_core.py                          Wordle scoring + list loading
codec.js / codec.py                  puzzle-link token encoder (keep in sync)
template.html                        source for docs/index.html
puzzle_template.html                 source for docs/puzzle.html
themes_template.html                 source for docs/themes.html
docs/                                generated site; edit the templates, then run build_common.py
```

## How it works

For each clue, the script scores it against every answer and groups the answers by
colors. A group holding exactly one word is a puzzle. That's clues × answers scorings,
which is O(n²), rather than checking every (clue, target) pair against every other
answer, which would be O(n³).
