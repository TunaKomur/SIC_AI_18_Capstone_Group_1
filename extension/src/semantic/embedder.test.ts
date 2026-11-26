// @ts-expect-error: test Node üzerinde çalışır; Node tip tanımları eklenti derlemesine bilerek dahil değil
import { existsSync, readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import fixture from "../../../tests/fixtures/semantic_parity.json";
import { dot, modelInputs, SEMANTIC_THRESHOLD } from "../core/semantic";

/**
 * Tarayıcıdaki motor (onnxruntime-web) ile Python'daki (onnxruntime) nicemlenmiş modelde sayıları
 * birebir aynı yuvarlamıyor: 140 çiftte fark ortanca 0,000001, en çok 0,0096. Karar ancak skor
 * eşiğe bu kadar yakınsa farklı çıkabilir.
 */
const TOLERANCE = 0.015;
import { Embedder } from "./embedder";
import type { TokenizerJson } from "./tokenizer";

const MODEL = new URL("../../public/models/minilm-tr/model.onnx", import.meta.url);
const TOKENIZER = new URL("../../public/models/minilm-tr/tokenizer.json", import.meta.url);
const hasModel = existsSync(MODEL);

// Model dosyası depoda değil (python scripts/build_semantic_model.py ile üretilir); yoksa atlanır.
describe.skipIf(!hasModel)("cümle modeli (onnxruntime-web, Node)", () => {
  it("Python ile aynı anlam benzerliğini verir", async () => {
    const ort = await import("onnxruntime-web/wasm");
    ort.env.wasm.numThreads = 1;
    const session = await ort.InferenceSession.create(readFileSync(MODEL));
    const embedder = new Embedder(ort, session, JSON.parse(readFileSync(TOKENIZER, "utf8")) as TokenizerJson);
    for (const row of fixture.pairs) {
      const { previous, next } = modelInputs(row.previous, row.new);
      const score = dot(await embedder.embed(previous), await embedder.embed(next));
      expect(Math.abs(score - row.score), row.new).toBeLessThan(TOLERANCE);
      if (Math.abs(row.score - SEMANTIC_THRESHOLD) > TOLERANCE) {
        expect([row.new, score >= SEMANTIC_THRESHOLD]).toEqual([row.new, row.score >= SEMANTIC_THRESHOLD]);
      }
    }
  }, 120_000);
});
