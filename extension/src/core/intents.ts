import rules from "../data/signal-rules.json";
import { foldTurkish, normalizeText, withFolded } from "./text";

/**
 * Kısa mesaj niyetleri. Şimdilik bir sınıf: yönsüz devam ("devam", "devam et", "tamam devam",
 * "continue", "go on"). Bu mesajlar bir istek değil, akışı sürdürme; kısa tekrar serisi metne değil
 * bu niyete göre sayılır ve tekrar dedektörü onları karşılaştırmaz. Yönlü devam ("devam et ama tablo
 * olarak") bu sınıfa girmez. Kurallar signal-rules.json içinde "continue"; Python ikizi
 * src/kafiai/extension_similarity.py is_bare_continue.
 */

const WORDS = new Set<string>(withFolded(rules.continue.words));
const PHRASES = withFolded(rules.continue.phrases);
const ALLOWED = new Set<string>(withFolded([...rules.continue.allowed, ...rules.continue.words]));

export function isBareContinue(text: string): boolean {
  const normalized = foldTurkish(normalizeText(text ?? ""));
  const tokens = normalized.split(" ").filter((t) => t !== "");
  if (tokens.length === 0 || tokens.length > rules.continue.max_words) return false;
  if (!tokens.every((t) => ALLOWED.has(t))) return false;
  const padded = ` ${normalized} `;
  return tokens.some((t) => WORDS.has(t)) || PHRASES.some((p) => padded.includes(` ${p} `));
}
