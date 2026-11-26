import repeatRules from "../data/repeat-rules.json";
import rules from "../data/semantic-rules.json";
import { foldTurkish, normalizeText, withFolded } from "./text";
import { alignTypos } from "./typo";

/**
 * Katman 2: "aynı istek" kararı (K52). Model sonucu (anlam benzerliği) dışarıdan gelir; bu dosya
 * yalnızca kuralı uygular ve modelsiz test edilebilir. Python: kafiai.semantic.
 *
 * Bir mesaj öncekiyle aynı istek sayılır, eğer anlam benzerliği eşiği geçiyorsa, iki mesaj arasında
 * içerik kelimesi yer değiştirmemişse ve yeni mesaj en çok bir yeni içerik kelimesi getiriyorsa
 * (bekçi): modeller "metni daha kısa yaz" ile "metni daha uzun yaz"ı da çok benzer buluyor.
 */

export const SEMANTIC_THRESHOLD = rules.threshold;
export const SEMANTIC_RECENT = rules.recent_messages;
export const SEMANTIC_MAX_TOKENS = rules.max_tokens;
export const SEMANTIC_MODEL_DIR = rules.model.dir;

const FILLER = new Set<string>(withFolded(repeatRules.filler));
const GENERIC = new Set<string>(withFolded(rules.generic));
const STEM = rules.stem_chars;
const MAX_NEW_CONTENT = rules.max_new_content;
const hasDigit = (t: string) => /\p{N}/u.test(t);

/** Dolgu ve genel kelimeler (soru kelimeleri, hafif fiiller) dışındaki kelimeler. */
export function contentWords(normalized: string): string[] {
  return normalized
    .split(" ")
    .filter((t) => t !== "")
    .filter((t) => !FILLER.has(t) && !GENERIC.has(t) && (Array.from(t).length >= 2 || hasDigit(t)));
}

const stem = (t: string) => (hasDigit(t) ? t : Array.from(foldTurkish(t)).slice(0, STEM).join(""));

/** Modele verilen iki metin: önceki sadeleştirilmiş, yeni ayrıca yazım hatası düzeltilmiş (Katman 1). */
export function modelInputs(previousText: string, newText: string): { previous: string; next: string } {
  const previous = normalizeText(previousText);
  return { previous, next: alignTypos(normalizeText(newText), previous) };
}

/** [yalnızca öncekinde olan, yalnızca yenide olan] içerik kelimeleri. */
export function swappedContent(previousText: string, newText: string): [string[], string[]] {
  const { previous, next } = modelInputs(previousText, newText);
  const a = contentWords(previous);
  const b = contentWords(next);
  const sa = new Set(a.map(stem));
  const sb = new Set(b.map(stem));
  return [a.filter((t) => !sb.has(stem(t))), b.filter((t) => !sa.has(stem(t)))];
}

/** İki mesajda da ötekinde olmayan içerik kelimesi var mı (bir kelime ötekinin yerine geçmiş)? */
export function isSwap(previousText: string, newText: string): boolean {
  const [onlyOld, onlyNew] = swappedContent(previousText, newText);
  return onlyOld.length > 0 && onlyNew.length > 0;
}

/**
 * Anlam benzerliği (score) ve bekçiye göre "aynı istek" kararı. Bekçi: içerik kelimesi yer
 * değiştirmemiş ve yeni mesaj en çok MAX_NEW_CONTENT yeni içerik kelimesi getiriyor (daha fazlası
 * isteği geliştirmektir: "ST dili neden kullanılır" → "… PLC sistemlerinde"; döngü değil).
 */
export function sameIntent(score: number, previousText: string, newText: string, threshold = SEMANTIC_THRESHOLD): boolean {
  if (score < threshold) return false;
  const [onlyOld, onlyNew] = swappedContent(previousText, newText);
  return !(onlyOld.length > 0 && onlyNew.length > 0) && onlyNew.length <= MAX_NEW_CONTENT;
}

/** İki birim vektörün iç çarpımı (kosinüs benzerliği). */
export function dot(a: ArrayLike<number>, b: ArrayLike<number>): number {
  let s = 0;
  for (let i = 0; i < a.length; i++) s += a[i]! * b[i]!;
  return s;
}
