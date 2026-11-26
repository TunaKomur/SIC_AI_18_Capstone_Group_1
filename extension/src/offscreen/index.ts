import * as ort from "onnxruntime-web/wasm";
import { SEMANTIC_MODEL_DIR } from "../core/semantic";
import { Embedder } from "../semantic/embedder";
import { isEmbedRequest, MSG_SEMANTIC_OFFSCREEN, type SemanticEmbedResponse } from "../semantic/messages";
import type { TokenizerJson } from "../semantic/tokenizer";

/**
 * Anlam modelinin çalıştığı gizli eklenti sayfası (K52). Model ve kelime bölücü eklentinin kendi
 * dosyalarından okunur (chrome-extension:// adresi); eklenti sayfalarının güvenlik kuralı
 * (connect-src 'self') eklenti dışındaki her adrese isteği tarayıcı düzeyinde engeller.
 * Mesaj metni yalnızca bellekte işlenir, hiçbir yere yazılmaz ve günlüğe girmez.
 */

let loading: Promise<Embedder> | null = null;

async function own(path: string): Promise<Response> {
  const response = await fetch(chrome.runtime.getURL(path));
  if (!response.ok) throw new Error(`${path} okunamadı`);
  return response;
}

function embedder(): Promise<Embedder> {
  loading ??= (async () => {
    ort.env.wasm.numThreads = 1; // gizli sayfa cross-origin isolated değil; tek iş parçacığı
    ort.env.wasm.proxy = false;
    ort.env.wasm.wasmPaths = chrome.runtime.getURL("ort/");
    const [model, tokenizer] = await Promise.all([
      own(`${SEMANTIC_MODEL_DIR}/model.onnx`).then((r) => r.arrayBuffer()),
      own(`${SEMANTIC_MODEL_DIR}/tokenizer.json`).then((r) => r.json() as Promise<TokenizerJson>),
    ]);
    const session = await ort.InferenceSession.create(new Uint8Array(model), { executionProviders: ["wasm"] });
    console.log("[KafiAI] anlam modeli yüklendi");
    return new Embedder(ort, session, tokenizer);
  })();
  loading.catch(() => {
    loading = null; // bir sonraki istekte yeniden denenir
  });
  return loading;
}

chrome.runtime.onMessage.addListener((message: unknown, _sender, respond: (r: SemanticEmbedResponse) => void) => {
  if (!isEmbedRequest(message, MSG_SEMANTIC_OFFSCREEN)) return false;
  void (async () => {
    try {
      const e = await embedder();
      const vectors: number[][] = [];
      for (const text of message.texts) vectors.push(Array.from(await e.embed(text)));
      respond({ ok: true, vectors });
    } catch (error) {
      respond({ ok: false, error: error instanceof Error ? error.message : "bilinmeyen hata" });
    }
  })();
  return true; // cevap eşzamansız
});
