// Puzzle-link codec: hides a clue/target pair in a 12-character base-36 token
// (10 chars of scrambled letters + 2-char checksum). Obfuscation, not security.
// Keep in sync with codec.py.
const CODEC_KEY = [3, 17, 8, 22, 11, 5, 19, 1, 14, 9];
const codecCheck = v => v.reduce((h, x) => (h * 31 + x + 7) % 1296, 0);
function encodePair(clue, target) {
  const v = [...(clue + target).toLowerCase()].map(ch => ch.charCodeAt(0) - 97);
  if (v.length !== 10 || v.some(x => x < 0 || x > 25)) throw new Error('need two 5-letter words');
  let prev = 0, n = 0;
  v.forEach((x, i) => { prev = (x + CODEC_KEY[i] + prev * 7) % 26; n = n * 26 + prev; });
  return n.toString(36).padStart(10, '0') + codecCheck(v).toString(36).padStart(2, '0');
}
function decodePair(token) {
  if (!/^[0-9a-z]{12}$/.test(token || '')) return null;
  let n = parseInt(token.slice(0, 10), 36);
  if (n >= 26 ** 10) return null;
  const enc = [];
  for (let i = 0; i < 10; i++) { enc.unshift(n % 26); n = Math.floor(n / 26); }
  let prev = 0;
  const v = enc.map((d, i) => { const x = ((d - CODEC_KEY[i] - prev * 7) % 26 + 26) % 26; prev = d; return x; });
  if (codecCheck(v) !== parseInt(token.slice(10), 36)) return null;
  const s = String.fromCharCode(...v.map(x => x + 97));
  return { clue: s.slice(0, 5), target: s.slice(5) };
}
// Wordle scoring: G = right spot, Y = elsewhere, B = absent (duplicates handled).
function scoreWord(guess, target) {
  const res = Array(5).fill('B'), left = {};
  for (let i = 0; i < 5; i++) {
    if (guess[i] === target[i]) res[i] = 'G'; else left[target[i]] = (left[target[i]] || 0) + 1;
  }
  for (let i = 0; i < 5; i++) {
    if (res[i] === 'B' && left[guess[i]] > 0) { res[i] = 'Y'; left[guess[i]]--; }
  }
  return res.join('');
}
// Solved puzzles, kept per browser as {token: true}. Storage can be missing or blocked.
const SOLVED_KEY = 'wio-solved';
function loadSolved() {
  try { return JSON.parse(localStorage.getItem(SOLVED_KEY)) || {}; } catch { return {}; }
}
function markSolved(token) {
  try { const s = loadSolved(); s[token] = true; localStorage.setItem(SOLVED_KEY, JSON.stringify(s)); } catch {}
}
