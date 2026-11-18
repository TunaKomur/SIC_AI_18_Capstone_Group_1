import { FRESH_START_MAX_CHARS, MIN_NORMALIZED_CHARS, SIMILARITY_THRESHOLD } from "../config";
import { cosine, ngramVector } from "./similarity";
import { normalizeText } from "./text";

function clip(text: string, max: number): string {
  const oneLine = text.replace(/\s*\n\s*/g, " ").trim();
  const chars = Array.from(oneLine);
  return chars.length > max ? chars.slice(0, max).join("").trimEnd() + "…" : oneLine;
}

/**
 * "Taze başlat" taslağı: kullanıcının bir sohbette yazdığı istekleri numaralı tek bir metinde
 * toplar. Basit metin birleştirmedir, cihazda yapılır, hiçbir model veya ağ kullanılmaz.
 * Birbirine çok benzeyen istekler (yeniden denemeler) tek maddeye iner: en son hali kalır.
 */
/** Birbirine çok benzeyen metinleri tek maddeye indirir; en son hâli kalır. */
function dedupe(texts: string[]): string[] {
  const items: { text: string; vec: Map<number, number> | null }[] = [];
  for (const raw of texts) {
    const text = raw.trim();
    if (text === "") continue;
    const normalized = normalizeText(text);
    const vec = normalized.length >= MIN_NORMALIZED_CHARS ? ngramVector(normalized) : null;
    const similarIndex = vec
      ? items.findIndex((item) => item.vec !== null && cosine(vec, item.vec) >= SIMILARITY_THRESHOLD)
      : -1;
    if (similarIndex >= 0) items[similarIndex] = { text, vec };
    else items.push({ text, vec });
  }
  return items.map((item) => item.text);
}

/**
 * rules: kullanıcının sohbet içinde yeniden hatırlattığı kurallar (K48). Varsa taslağın en başına
 * girer; yeni sohbette baştan geçerli olsunlar diye. En fazla maxRules tane, en yenileri.
 */
export function buildFreshStartDraft(texts: string[], rules: string[] = [], maxRules = 3): string {
  const items = dedupe(texts);
  if (items.length === 0) return "";
  const lines = items.map((text, i) => `${i + 1}. ${clip(text, FRESH_START_MAX_CHARS)}`);
  const ruleLines = dedupe(rules)
    .slice(-maxRules)
    .map((text) => `- ${clip(text, FRESH_START_MAX_CHARS)}`);
  const ruleBlock =
    ruleLines.length > 0
      ? ["Bu sohbette baştan uymanı istediğim kurallar (önceki sohbette bunları yeniden hatırlatmam gerekti):", ...ruleLines, ""]
      : [];
  return [
    ...ruleBlock,
    "Önceki bir sohbetimde şunları istemiştim:",
    "",
    ...lines,
    "",
    // Yeni sohbet tek başına döngüyü çözmüyor (WildChat: yeniden başlayanlarda da %42 döngü); isteği
    // netleştirmek için kullanıcının dolduracağı iki satır.
    "Beklediğim sonuç: ",
    "Önceki denemelerde olmayan kısım: ",
    "",
    "Bunları birlikte düşünerek, tek seferde ele alır mısın?",
  ].join("\n");
}
