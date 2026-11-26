"""Katman 2 (K52) için Python ile eklentinin ortak örneklerini yazar: tests/fixtures/semantic_parity.json.

    tokens: modele giren metinler ve kelime bölücünün verdiği parça kimlikleri (Hugging Face tokenizers)
    pairs : mesaj çiftleri; bekçinin yer değiştiren kelimeleri, modelin anlam benzerliği ve "aynı istek" kararı

Eklenti testleri (extension/src/semantic/*.test.ts, src/core/semantic.test.ts) aynı sonucu vermek zorunda.
Model dosyası gerekir: python scripts/build_semantic_model.py
Çalıştırma: python scripts/make_semantic_parity_fixture.py
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from kafiai import semantic  # noqa: E402

EXTRA = [
    ("ankaranın başkenti neresidir?", "ankaranın başkenti hangi şehir"),
    ("ankaranın başkenti neresidir?", "anksrabın baskebti neresifir"),
    ("metni daha kısa yaz", "metni daha uzun yaz"),
    ("python ile dosya nasıl okunur", "java ile dosya nasıl okunur"),
    ("What is the capital of France?", "Which city is the capital of France?"),
    ("Écrire un poème", "ﬁle naïve café"),
]


def main():
    emb = semantic.Embedder()
    pairs = json.loads((ROOT / "tests" / "fixtures" / "semantic_pairs_tr.json").read_text(encoding="utf-8"))["pairs"]
    rows = [(p["onceki"], p["yeni"]) for p in pairs[::3]] + EXTRA
    texts, out_pairs = [], []
    for prev, new in rows:
        a, b = semantic.model_inputs(prev, new)
        texts += [a, b]
        score = emb.similarity(prev, new)
        only_old, only_new = semantic.swapped_content(prev, new)
        out_pairs.append({
            "previous": prev, "new": new, "only_old": only_old, "only_new": only_new,
            "score": round(score, 5), "same": semantic.same_intent(score, prev, new),
        })
    texts += [t for pair in EXTRA for t in pair]  # ham metinler de (büyük harf, noktalama, NFKC)
    tokens = [{"text": t, "ids": emb.token_ids(t)} for t in dict.fromkeys(texts)]
    path = ROOT / "tests" / "fixtures" / "semantic_parity.json"
    path.write_text(json.dumps({"tokens": tokens, "pairs": out_pairs}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(tokens)} metin, {len(out_pairs)} çift yazıldı: {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
