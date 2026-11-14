import rules from "../data/personal-rules.json";
import { foldTurkish, normalizeText, withFolded } from "./text";

/**
 * Kişisel ve duygusal mesaj tespiti. İlke: bu sohbetlerde öneri gösterilmez.
 * Kurallar src/data/personal-rules.json dosyasında; Python tarafı (src/kafiai/personal.py)
 * aynı dosyayı okur ve tests/fixtures/personal_parity.json iki tarafı sınar.
 * Kurgu isteklerinde ("write a story") yalnızca kendine zarar ifadeleri sayılır.
 */

// Türkçe karaktersiz yazım da kişisel sayılır ("cok yalniz hissediyorum").
const PHRASES = withFolded(rules.phrases);
const FICTION_MARKERS = withFolded(rules.fiction_markers);
const FICTION_EXEMPT = withFolded(rules.fiction_exempt);

function variants(text: string): string[] {
  const raw = text ?? "";
  const tr = normalizeText(raw);
  const en = normalizeText(raw.replace(/I/g, "i"));
  return [...new Set([tr, en, foldTurkish(tr)])].map((v) => ` ${v} `);
}

function hit(padded: string[], phrases: string[]): boolean {
  return padded.some((v) => phrases.some((p) => v.includes(` ${p} `)));
}

export function isPersonal(text: string): boolean {
  const v = variants(text);
  if (hit(v, FICTION_MARKERS)) return hit(v, FICTION_EXEMPT);
  return hit(v, PHRASES);
}
