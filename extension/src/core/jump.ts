import type { UserMessage } from "../adapters/types";
import { cosine, ngramVector } from "./similarity";
import { foldTurkish, normalizeText } from "./text";

/**
 * "Önceki cevaba git" (K53): şeridin ya da anlam notunun işaret ettiği önceki soruyu sayfada bulur
 * ve oraya kaydırır. Yalnızca aynı sohbette, yalnızca sayfada o an bulunan mesajlarla çalışır;
 * hiçbir şey saklanmaz.
 */

/** Sayfa metni ile hafızadaki metin küçük farklarla gelebilir (satır sonları, görünmez karakterler). */
const NEAR_MATCH = 0.9;

/** Karşılaştırma biçimi: sadeleştirilmiş ve Türkçe karaktersiz ("hâlinde" ile "halinde" aynı). */
const key = (text: string) => foldTurkish(normalizeText(text));

/**
 * Hafızadaki önceki mesaja (target) karşılık gelen sayfa öğesi. Önce sadeleştirilmiş ve Türkçe
 * karaktersiz metni birebir aynı olan en yeni mesaj, yoksa 3-gram benzerliği NEAR_MATCH'i geçen en
 * benzer mesaj. exclude: aranmayacak metin (anlam notunda yeni mesajın kendisi). Bulunamazsa null.
 */
export function findPreviousMessage(messages: UserMessage[], target: string, exclude: string | null = null): HTMLElement | null {
  const wanted = key(target);
  if (wanted === "") return null;
  const skip = exclude === null ? null : key(exclude);
  const candidates = messages
    .map((m) => ({ element: m.element, normalized: key(m.text) }))
    .filter((m) => m.normalized !== "" && m.normalized !== skip);
  for (let i = candidates.length - 1; i >= 0; i--) {
    if (candidates[i]!.normalized === wanted) return candidates[i]!.element;
  }
  const vec = ngramVector(wanted);
  let best: HTMLElement | null = null;
  let bestScore = NEAR_MATCH;
  for (let i = candidates.length - 1; i >= 0; i--) {
    const score = cosine(ngramVector(candidates[i]!.normalized), vec);
    if (score > bestScore) {
      best = candidates[i]!.element;
      bestScore = score;
    }
  }
  return best;
}

/** Kaydırınca sorunun üstünde bırakılan pay (piksel). */
const TOP_MARGIN_PX = 96;

/** Yumuşak kaydırmanın sonucuna bakılan süre (milisaniye). */
const SMOOTH_CHECK_MS = 900;

/** Öğenin üstü ekranın üst yarısında mı (kaydırma vardı)? */
function nearTop(element: HTMLElement): boolean {
  const top = element.getBoundingClientRect().top;
  return top >= -8 && top <= window.innerHeight / 2;
}

/** Vurgu rengi: Kâfi AI temasının vurgu rengi (açık kahve); animasyonla, iz bırakmadan. */
const HIGHLIGHT = "rgba(201, 168, 117, 0.95)";

/**
 * Öğeye yumuşakça kaydırır ve birkaç saniye çerçeveyle işaretler. Öğenin stili kalıcı olarak değişmez
 * (Web Animations: animasyon bitince iz kalmaz; kaydırma payı kısa süre sonra geri alınır). Öğe artık
 * sayfada değilse false.
 */
export function jumpTo(element: HTMLElement): boolean {
  if (!element.isConnected) return false;
  const reduce = typeof matchMedia === "function" && matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (typeof element.scrollIntoView === "function") {
    // Sitelerin üstteki sabit başlığı sorunun ilk satırını örtmesin: kısa bir süre üst pay verilir,
    // sonra öğenin kendi değeri geri konur.
    const margin = element.style.scrollMarginTop;
    element.style.scrollMarginTop = `${TOP_MARGIN_PX}px`;
    element.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
    setTimeout(() => {
      // Yumuşak kaydırma bazen hiç başlamıyor ya da yarıda kesiliyor (Chromium'da, başsız tarayıcıyla
      // ölçüldü). Soru hâlâ ekranın üst yarısında değilse doğrudan götürülür.
      if (!nearTop(element)) element.scrollIntoView({ behavior: "auto", block: "start" });
      element.style.scrollMarginTop = margin;
    }, SMOOTH_CHECK_MS);
  }
  if (typeof element.animate === "function") {
    element.animate(
      [
        { outline: `3px solid ${HIGHLIGHT}`, outlineOffset: "4px" },
        { outline: `3px solid ${HIGHLIGHT}`, outlineOffset: "4px", offset: 0.75 },
        { outline: "3px solid rgba(201, 168, 117, 0)", outlineOffset: "4px" },
      ],
      { duration: 2600, easing: "ease-out" },
    );
  }
  return true;
}
