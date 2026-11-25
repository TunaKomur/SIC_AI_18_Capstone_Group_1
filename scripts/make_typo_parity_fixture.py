"""Yazım hatası toleransı (Katman 1) için Python ile eklentinin ortak örneklerini yazar.

tests/fixtures/typo_parity.json: Türkçe anlam test setindeki her çift ve birkaç sınır durumu için
düzeltilmiş metin ve yazım hatası toleranslı benzerlik. Python (tests/test_typo.py) ve eklenti
(extension/src/core/typo.test.ts) aynı sonucu vermek zorunda. Kural değişirse yeniden üretilir.

Çalıştırma: python scripts/make_typo_parity_fixture.py
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from kafiai.extension_similarity import align_typos, normalize_text, osa_distance, typo_similarity  # noqa: E402

EXTRA = [
    ("ankaranın başkenti neresidir?", "anksrabın baskebti neresifir"),
    ("bu kodu düzelt", "bu kodu düzeltme"),
    ("ikinci dünya savaşının sebeplerini yaz", "birinci dünya savaşının sebeplerini yaz"),
    ("bu ödevi kaynakçalı yaz", "bu ödevi kaynakçasız yaz"),
    ("1. soruyu çöz", "2. soruyu çöz"),
    ("sunum için 10 slayt başlığı öner", "suum için 10 slayyt başlığı öenr"),
    ("What is the capital of France?", "Waht is the captial of France"),
    ("İstanbul'da hava nasıl?", "ISTANBUL'DA HAVA NASIL"),
]
DISTANCES = [("kitap", "kitpa"), ("ankaranin", "anksrabin"), ("", "abc"), ("aynı", "aynı"), ("başkenti", "baskebti")]


def main():
    pairs = json.loads((ROOT / "tests" / "fixtures" / "semantic_pairs_tr.json").read_text(encoding="utf-8"))["pairs"]
    rows = [(p["onceki"], p["yeni"]) for p in pairs] + EXTRA
    out = {
        "pairs": [
            {
                "previous": prev,
                "new": new,
                "aligned": align_typos(normalize_text(new), normalize_text(prev)),
                "score": round(typo_similarity(new, prev), 6),
            }
            for prev, new in rows
        ],
        "distances": [{"a": a, "b": b, "distance": osa_distance(a, b)} for a, b in DISTANCES],
    }
    path = ROOT / "tests" / "fixtures" / "typo_parity.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(out['pairs'])} çift yazıldı: {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
