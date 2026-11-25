"""Türkçe anlam test setinde (tests/fixtures/semantic_pairs_tr.json) tekrar kararlarını ölçer.

Her çiftte önceki mesaj hafızadadır, yeni mesaj gönderilir. Üç karar ölçülür:
    benzer  : şerit kuralı (benzerlik eşiği, yeni içerik yok, varyasyon değil); halka ve kart için sayılır
    bekletir: gönderim bekletilir (birebir tekrar ya da güçlü onarım ifadesi)
    yumusak : yumuşak tekrar (benzerlik 0,6 ve üstü); yalnızca çıkış kartı için sayılır
"Aynı istek" çiftlerinde bu oranların yüksek, "farklı istek" çiftlerinde düşük olması istenir.

Yöntemler:
    once   : yazım hatası toleransı kapalı (Katman 1 öncesi)
    katman1: sohbete göre yazım düzeltme açık

Çıktı: outputs/semantic_pairs_eval.json
Çalıştırma: python scripts/evaluate_semantic_pairs.py
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import kafiai.extension_similarity as es  # noqa: E402
from kafiai.config import EXT_SOFT_SIMILARITY_THRESHOLD  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "semantic_pairs_tr.json"
OUT = ROOT / "outputs" / "semantic_pairs_eval.json"


def decide(prev, new):
    score = es.typo_similarity(new, prev)
    variation = es.is_variation(new, score)
    return {
        "benzer": es.is_repeat(new, prev),
        "bekletir": es.holds_send(new, prev),
        "yumusak": score >= EXT_SOFT_SIMILARITY_THRESHOLD and not variation,
    }


def run(pairs, method):
    original = es.align_typos
    if method == "once":
        es.align_typos = lambda new, prev: new
    try:
        return [decide(p["onceki"], p["yeni"]) for p in pairs]
    finally:
        es.align_typos = original


def summarize(pairs, decisions):
    groups = defaultdict(list)
    for p, d in zip(pairs, decisions):
        groups[(p["split"], p["tur"])].append(d)
        groups[(p["split"], "TUM_AYNI" if p["ayni"] else "TUM_FARKLI")].append(d)
    out = {}
    for (split, kind), ds in sorted(groups.items()):
        out.setdefault(split, {})[kind] = {
            "n": len(ds),
            **{k: round(100 * sum(d[k] for d in ds) / len(ds), 1) for k in ("benzer", "bekletir", "yumusak")},
        }
    return out


def main():
    pairs = json.loads(FIXTURE.read_text(encoding="utf-8"))["pairs"]
    result = {m: summarize(pairs, run(pairs, m)) for m in ("once", "katman1")}
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for split in ("secim", "rapor"):
        print(f"\n== {split} (yüzde: benzer / bekletir / yumuşak)")
        kinds = result["once"][split]
        for kind in kinds:
            a, b = result["once"][split][kind], result["katman1"][split][kind]
            fmt = lambda r: f"{r['benzer']:5.1f} {r['bekletir']:5.1f} {r['yumusak']:5.1f}"
            print(f"{kind:22s} n={a['n']:3d} | önce {fmt(a)} | katman1 {fmt(b)}")


if __name__ == "__main__":
    main()
