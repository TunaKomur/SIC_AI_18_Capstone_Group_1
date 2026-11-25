import rules from "../data/repeat-rules.json";
import { foldTurkish } from "./text";

/**
 * Katman 1: sohbete göre yazım hatası toleransı. Yeni mesajın kelimeleri önceki mesajın kelimeleriyle
 * karşılaştırılır; yazım hatalı olanlar önceki mesajdaki karşılığıyla değiştirilir
 * ("anksrabın baskebti neresifir" → "ankaranın başkenti neresidir"). Sözlük ya da model yoktur:
 * sözlük, kullanıcının bir önceki mesajıdır. Düzeltilmiş metin yalnızca karşılaştırmada kullanılır,
 * mesaja dokunulmaz ve hiçbir yere yazılmaz. Kurallar: src/data/repeat-rules.json, "typo".
 * Python: kafiai.extension_similarity (osa_distance, typo_match, align_typos).
 */

const EDITS = [...rules.typo.edits].sort((a, b) => a[0]! - b[0]!);
const MIN_CHARS = rules.typo.min_chars;
const MAX_WORDS = rules.typo.max_words;
const PROTECTED = new Set<string>(rules.typo.protected);
const PROTECTED_STEMS = rules.typo.protected.filter((w) => Array.from(w).length >= 4);
const OPPOSITE = rules.typo.opposite_suffixes as [string, string][];

const hasDigit = (t: string) => /\p{N}/u.test(t);
const len = (t: string) => Array.from(t).length;

/** Bu uzunluktaki bir kelimede yazım hatası sayılan en çok düzenleme. */
function budget(length: number): number {
  let out = 0;
  for (const [minLen, edits] of EDITS) if (length >= minLen!) out = edits!;
  return out;
}

/**
 * Harf düzenleme uzaklığı: ekleme, silme, değiştirme ve yan yana iki harfin yer değiştirmesi
 * (Damerau-Levenshtein, optimal string alignment).
 */
export function osaDistance(a: string, b: string): number {
  const x = Array.from(a);
  const y = Array.from(b);
  const m = y.length;
  // Yalnızca son üç satır tutulur (yer değiştirme için iki satır geriye bakılır).
  let prev2 = new Array<number>(m + 1).fill(0);
  let prev = Array.from({ length: m + 1 }, (_, j) => j);
  let cur = new Array<number>(m + 1).fill(0);
  for (let i = 1; i <= x.length; i++) {
    cur[0] = i;
    for (let j = 1; j <= m; j++) {
      const cost = x[i - 1] === y[j - 1] ? 0 : 1;
      let v = Math.min(prev[j]! + 1, cur[j - 1]! + 1, prev[j - 1]! + cost);
      if (i > 1 && j > 1 && x[i - 1] === y[j - 2] && x[i - 2] === y[j - 1]) v = Math.min(v, prev2[j - 2]! + 1);
      cur[j] = v;
    }
    [prev2, prev, cur] = [prev, cur, prev2];
  }
  return prev[m]!;
}

/** Sayı ve sıra kelimeleri ("ikinci", "üçüncü", "first") düzeltilmez. */
function isProtected(folded: string): boolean {
  return PROTECTED.has(folded) || PROTECTED_STEMS.some((w) => folded.startsWith(w));
}

/** Aynı gövde, anlamı tersine çeviren ekler ("kaynakcali"/"kaynakcasiz"). */
function oppositeSuffix(a: string, b: string): boolean {
  for (const [x, y] of OPPOSITE) {
    for (const [p, q] of [
      [x, y],
      [y, x],
    ] as const) {
      if (a.endsWith(p) && b.endsWith(q) && a.slice(0, a.length - p.length) === b.slice(0, b.length - q.length)) return true;
    }
  }
  return false;
}

/** Kelime, önceki kelimelerden birinin yazım hatalı biçimi mi? Öyleyse o kelime, değilse null. */
export function typoMatch(token: string, previous: readonly string[]): string | null {
  if (hasDigit(token)) return null;
  const folded = foldTurkish(token);
  let best: { distance: number; word: string } | null = null;
  for (const prev of previous) {
    if (hasDigit(prev)) continue;
    const fp = foldTurkish(prev);
    let distance: number;
    if (fp === folded) {
      distance = 0;
    } else {
      const shorter = Math.min(len(fp), len(folded));
      const longer = Math.max(len(fp), len(folded));
      // Ek farkı ("düzelt"/"düzeltme", "grammatical"/"ungrammatical"); tek harf fazlası yazım hatası sayılır.
      const affix = fp.startsWith(folded) || folded.startsWith(fp) || fp.endsWith(folded) || folded.endsWith(fp);
      if (affix && longer - shorter >= 2) continue;
      if (shorter < MIN_CHARS || isProtected(folded) || isProtected(fp) || oppositeSuffix(folded, fp)) continue;
      const limit = budget(longer);
      if (limit === 0 || longer - shorter > limit) continue;
      distance = osaDistance(folded, fp);
      if (distance > limit) continue;
    }
    if (best === null || distance < best.distance) best = { distance, word: prev };
  }
  return best === null ? null : best.word;
}

/**
 * Yeni mesajın yazım hatalı kelimelerini önceki mesajdaki karşılıklarıyla değiştirir.
 * Girdiler sadeleştirilmiş metindir (normalizeText); çıktı da öyledir.
 */
export function alignTypos(newNormalized: string, previousNormalized: string): string {
  const newTokens = newNormalized.split(" ").filter((t) => t !== "");
  const prevTokens = previousNormalized.split(" ").filter((t) => t !== "");
  // Uzun metinlerde düzeltme yapılmaz (repeat-rules.json, typo.max_words): gönderimi yavaşlatmasın.
  if (newTokens.length > MAX_WORDS || prevTokens.length > MAX_WORDS) return newNormalized;
  const previous = [...new Set(prevTokens)];
  const known = new Set(previous);
  return newTokens.map((t) => (known.has(t) ? t : (typoMatch(t, previous) ?? t))).join(" ");
}
