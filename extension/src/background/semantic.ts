import { isEmbedRequest, MSG_SEMANTIC_EMBED, MSG_SEMANTIC_OFFSCREEN, type SemanticEmbedResponse } from "../semantic/messages";

/**
 * Arka plan çalışanı, içerik betiğinden gelen anlam isteğini gizli sayfaya (offscreen) iletir.
 * Gizli sayfa ilk istekte açılır ve açık kalır (model her seferinde yeniden yüklenmesin diye).
 */

const OFFSCREEN_URL = "offscreen.html";
let creating: Promise<void> | null = null;

async function ensureOffscreen(): Promise<void> {
  const contexts = await chrome.runtime.getContexts({
    contextTypes: [chrome.runtime.ContextType.OFFSCREEN_DOCUMENT],
    documentUrls: [chrome.runtime.getURL(OFFSCREEN_URL)],
  });
  if (contexts.length > 0) return;
  creating ??= chrome.offscreen
    .createDocument({
      url: OFFSCREEN_URL,
      reasons: [chrome.offscreen.Reason.WORKERS],
      justification: "Türkçe anlam modelini (Kâfi AI, Katman 2) bilgisayarda çalıştırmak için",
    })
    .finally(() => {
      creating = null;
    });
  await creating;
}

export function listenSemantic(): void {
  chrome.runtime.onMessage.addListener((message: unknown, _sender, respond: (r: SemanticEmbedResponse) => void) => {
    if (!isEmbedRequest(message, MSG_SEMANTIC_EMBED)) return false;
    void (async () => {
      try {
        await ensureOffscreen();
        const result = (await chrome.runtime.sendMessage({ type: MSG_SEMANTIC_OFFSCREEN, texts: message.texts })) as SemanticEmbedResponse;
        respond(result ?? { ok: false, error: "gizli sayfa cevap vermedi" });
      } catch (error) {
        respond({ ok: false, error: error instanceof Error ? error.message : "bilinmeyen hata" });
      }
    })();
    return true;
  });
}
