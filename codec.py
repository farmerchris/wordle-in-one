"""Puzzle-link codec: hides a clue/target pair in a 12-character base-36 token
(10 chars of scrambled letters + 2-char checksum). Obfuscation, not security.

Keep in sync with codec.js.
"""
import re
import string

KEY = [3, 17, 8, 22, 11, 5, 19, 1, 14, 9]
B36 = string.digits + string.ascii_lowercase

def _check(v):
    h = 0
    for x in v:
        h = (h * 31 + x + 7) % 1296
    return h

def _b36(n, width):
    out = ''
    while n:
        n, r = divmod(n, 36)
        out = B36[r] + out
    return out.rjust(width, '0')

def encode_pair(clue, target):
    v = [ord(c) - 97 for c in (clue + target).lower()]
    if len(v) != 10 or any(not 0 <= x <= 25 for x in v):
        raise ValueError('need two 5-letter words')
    n = prev = 0
    for i, x in enumerate(v):
        prev = (x + KEY[i] + prev * 7) % 26
        n = n * 26 + prev
    return _b36(n, 10) + _b36(_check(v), 2)

def decode_pair(token):
    if not re.fullmatch(r'[0-9a-z]{12}', token or ''):
        return None
    n = int(token[:10], 36)
    if n >= 26 ** 10:
        return None
    enc = []
    for _ in range(10):
        n, r = divmod(n, 26)
        enc.insert(0, r)
    v, prev = [], 0
    for i, d in enumerate(enc):
        v.append((d - KEY[i] - prev * 7) % 26)
        prev = d
    if _check(v) != int(token[10:], 36):
        return None
    s = ''.join(chr(x + 97) for x in v)
    return s[:5], s[5:]
