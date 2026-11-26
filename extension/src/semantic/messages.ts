/**
 * Anlam modeli mesajları (K52). İçerik betiği, gönderilen mesajın sadeleştirilmiş metnini eklentinin
 * kendi gizli sayfasına (offscreen) yollar ve karşılığında yalnızca sayılar (vektörler) alır.
 * Mesajlar tarayıcının içinde, eklentinin kendi parçaları arasında gider; ağ değildir. Metin hiçbir
 * yere yazılmaz ve günlüğe girmez. Gizli sayfa yalnızca bellekte, küçük bir önbellek tutar.
 */

/** İçerik betiği → arka plan çalışanı: bu metinlerin vektörlerini istiyorum. */
export const MSG_SEMANTIC_EMBED = "kafiai.semantic.embed";
/** Arka plan çalışanı → gizli sayfa: aynı istek, gizli sayfaya yönlendirilmiş. */
export const MSG_SEMANTIC_OFFSCREEN = "kafiai.semantic.offscreen";

export interface SemanticEmbedRequest {
  type: typeof MSG_SEMANTIC_EMBED | typeof MSG_SEMANTIC_OFFSCREEN;
  texts: string[];
}

export type SemanticEmbedResponse = { ok: true; vectors: number[][] } | { ok: false; error: string };

export function isEmbedRequest(message: unknown, type: SemanticEmbedRequest["type"]): message is SemanticEmbedRequest {
  if (typeof message !== "object" || message === null) return false;
  const m = message as { type?: unknown; texts?: unknown };
  return m.type === type && Array.isArray(m.texts) && m.texts.every((t) => typeof t === "string") && m.texts.length <= 12;
}
