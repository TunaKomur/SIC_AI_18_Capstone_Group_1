import type * as Ort from "onnxruntime-web";
import { SEMANTIC_MAX_TOKENS } from "../core/semantic";
import { UnigramTokenizer, type TokenizerJson } from "./tokenizer";

/**
 * Cümle modeli: metni 384 sayılık, uzunluğu 1 olan bir vektöre çevirir (ortalama havuzlama).
 * Tarayıcıda yalnızca eklentinin kendi gizli sayfasında (offscreen) çalışır; testlerde Node'da.
 * Python: kafiai.semantic.Embedder.
 */
export class Embedder {
  private readonly tokenizer: UnigramTokenizer;
  private readonly cache = new Map<string, Float32Array>();

  constructor(
    private readonly ort: typeof Ort,
    private readonly session: Ort.InferenceSession,
    tokenizer: TokenizerJson,
  ) {
    this.tokenizer = new UnigramTokenizer(tokenizer);
  }

  tokenIds(text: string): number[] {
    return this.tokenizer.encode(text, SEMANTIC_MAX_TOKENS);
  }

  async embed(text: string): Promise<Float32Array> {
    const hit = this.cache.get(text);
    if (hit) return hit;
    const ids = this.tokenIds(text);
    const tensor = (values: number[]) =>
      new this.ort.Tensor("int64", BigInt64Array.from(values.map((v) => BigInt(v))), [1, values.length]);
    const feeds: Record<string, Ort.Tensor> = {
      input_ids: tensor(ids),
      attention_mask: tensor(ids.map(() => 1)),
    };
    if (this.session.inputNames.includes("token_type_ids")) feeds["token_type_ids"] = tensor(ids.map(() => 0));
    const output = await this.session.run(feeds);
    const hidden = output[this.session.outputNames[0]!]!;
    const [, tokens, dim] = hidden.dims as [number, number, number];
    const data = hidden.data as Float32Array;
    const vec = new Float32Array(dim);
    for (let t = 0; t < tokens; t++) for (let d = 0; d < dim; d++) vec[d]! += data[t * dim + d]!;
    let norm = 0;
    for (let d = 0; d < dim; d++) {
      vec[d]! /= tokens;
      norm += vec[d]! * vec[d]!;
    }
    norm = Math.sqrt(norm) || 1;
    for (let d = 0; d < dim; d++) vec[d]! /= norm;
    if (this.cache.size > 200) this.cache.clear(); // yalnızca bellekte, küçük tutulur
    this.cache.set(text, vec);
    return vec;
  }
}
