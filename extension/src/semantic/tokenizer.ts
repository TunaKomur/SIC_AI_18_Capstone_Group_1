/**
 * Cümle modelinin kelime bölücüsü (SentencePiece Unigram). Hugging Face'in tokenizers kütüphanesindeki
 * hesabın sade bir karşılığı; Python ile aynı parçaları verdiği tests/fixtures/semantic_parity.json
 * ile denetlenir. Girdi zaten sadeleştirilmiş metindir (normalizeText): harf, rakam ve boşluk.
 *
 * Adımlar: NFKC ve kontrol karakterlerinin atılması → boşluklardan bölme → her kelimenin başına "▁"
 * → kelime içinde en yüksek puanlı parça dizisi (Viterbi) → başa <s>, sona </s>.
 */

export interface TokenizerJson {
  model: { vocab: [string, number][]; unk_id: number };
}

const CONTROL = /[\p{Cc}]/gu;

export class UnigramTokenizer {
  private readonly pieces = new Map<string, { id: number; score: number }>();
  private readonly maxLen: number;
  private readonly unkId: number;
  private readonly unkScore: number;
  private readonly bos: number;
  private readonly eos: number;

  constructor(json: TokenizerJson) {
    let maxLen = 1;
    let minScore = 0;
    json.model.vocab.forEach(([piece, score], id) => {
      if (!this.pieces.has(piece)) this.pieces.set(piece, { id, score });
      maxLen = Math.max(maxLen, Array.from(piece).length);
      minScore = Math.min(minScore, score);
    });
    this.maxLen = maxLen;
    this.unkId = json.model.unk_id;
    this.unkScore = minScore - 10;
    this.bos = this.pieces.get("<s>")!.id;
    this.eos = this.pieces.get("</s>")!.id;
  }

  private word(word: string): number[] {
    const chars = Array.from(word);
    const n = chars.length;
    const score = new Array<number>(n + 1).fill(-Infinity);
    const from = new Array<number>(n + 1).fill(-1);
    const piece = new Array<number>(n + 1).fill(-1);
    score[0] = 0;
    for (let i = 0; i < n; i++) {
      if (score[i] === -Infinity) continue;
      let single = false;
      let text = "";
      for (let j = i + 1; j <= Math.min(n, i + this.maxLen); j++) {
        text += chars[j - 1];
        const hit = this.pieces.get(text);
        if (!hit) continue;
        if (j === i + 1) single = true;
        const v = score[i]! + hit.score;
        if (v > score[j]!) {
          score[j] = v;
          from[j] = i;
          piece[j] = hit.id;
        }
      }
      if (!single) {
        const v = score[i]! + this.unkScore;
        if (v > score[i + 1]!) {
          score[i + 1] = v;
          from[i + 1] = i;
          piece[i + 1] = this.unkId;
        }
      }
    }
    const out: number[] = [];
    for (let j = n; j > 0; j = from[j]!) out.push(piece[j]!);
    out.reverse();
    // Ardışık bilinmeyen parçalar tek <unk> olur.
    return out.filter((id, k) => !(id === this.unkId && out[k - 1] === this.unkId));
  }

  /** Parça kimlikleri: <s> … </s>, en çok maxTokens tane. */
  encode(text: string, maxTokens = 128): number[] {
    const normalized = text.normalize("NFKC").replace(CONTROL, "");
    const ids: number[] = [];
    for (const w of normalized.split(/\s+/)) {
      if (w === "") continue;
      ids.push(...this.word("▁" + w));
      if (ids.length >= maxTokens - 2) break;
    }
    return [this.bos, ...ids.slice(0, maxTokens - 2), this.eos];
  }
}
