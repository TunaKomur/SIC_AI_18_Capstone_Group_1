import { dot, modelInputs, SEMANTIC_RECENT, sameIntent } from "./semantic";

/**
 * Katman 2'nin sohbet içi hafızası (K52): son kullanıcı mesajlarını yalnızca bellekte tutar ve yeni
 * mesajın bunlardan biriyle anlamca aynı istek olup olmadığına bakar. Vektörleri dışarıdaki model
 * hesaplar (embed); model yoksa ya da cevap vermezse sonuç null olur ve hiçbir şey değişmez.
 * Sohbet değişince reset() ile silinir.
 */

export type EmbedFn = (texts: string[]) => Promise<number[][] | null>;

export interface SemanticResult {
  same: boolean;
  /** En yüksek anlam benzerliği (aynı istek sayılan önceki mesajla, yoksa genel en yüksek). */
  score: number;
}

export class SemanticTracker {
  private recent: string[] = [];

  constructor(private readonly embed: EmbedFn) {}

  /**
   * Yeni mesajı son mesajlarla karşılaştırır. Hafızanın o anki hâli hemen alınır; böylece sonuç
   * gelmeden remember() çağrılsa da karşılaştırma yalnızca önceki mesajlarla yapılır.
   */
  async check(text: string): Promise<SemanticResult | null> {
    const previous = [...this.recent];
    if (previous.length === 0) return { same: false, score: 0 };
    const pairs = previous.map((p) => ({ prev: p, ...modelInputs(p, text) }));
    const texts = [...new Set(pairs.flatMap((p) => [p.previous, p.next]))].filter((t) => t !== "");
    const vectors = await this.embed(texts);
    if (!vectors || vectors.length !== texts.length) return null;
    const byText = new Map(texts.map((t, i) => [t, vectors[i]!]));
    let best: SemanticResult = { same: false, score: 0 };
    for (const p of pairs) {
      const a = byText.get(p.previous);
      const b = byText.get(p.next);
      if (!a || !b) continue;
      const score = dot(a, b);
      const same = sameIntent(score, p.prev, text);
      if ((same && !best.same) || (same === best.same && score > best.score)) best = { same, score };
    }
    return best;
  }

  /** Hafızada karşılaştırılacak en az bir mesaj var mı? */
  get hasHistory(): boolean {
    return this.recent.length > 0;
  }

  /** Mesaj gönderildi: hafızaya ekle (en çok son SEMANTIC_RECENT mesaj). */
  remember(text: string): void {
    this.recent.push(text);
    if (this.recent.length > SEMANTIC_RECENT) this.recent.shift();
  }

  reset(): void {
    this.recent = [];
  }
}
