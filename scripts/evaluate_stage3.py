"""Aşama 3 ölçümü: ters yönlü düzeltmeler ve kuralın sohbet ortasında yeniden yazılması.

Olay aileleri src/kafiai/correction_patterns.py içinde tanımlı (A: ters yön, salınım, geri dönüş;
B1: "söylemiştim" gibi işaretler; B2: kısıt cümlesinin benzer biçimde yeniden yazılması).

Her aile için:
  sıklık           sohbetlerin yüzde kaçında, 100 sohbette kaç kez
  memnuniyetsizlik olay turunda ya da bir sonrakinde (halka ve kart isabetiyle aynı tanım)
  ek değer         olayların kaçında mevcut bir sinyal (şerit, kısa şerit, halka 1+, kart) zaten var;
                   mevcut sinyalin olmadığı olaylarda memnuniyetsizlik ne
  aday kural       olay halkayı 1'e ya da 2'ye çıkarsa ya da kartı açsa (evaluate_replay.replay extra ile,
                   soğuma ve bir turda tek müdahale kuralı korunarak) halka ve kart sayıları nasıl değişir

Türkçe: WildFeedback ağırlıkla İngilizce. Türkçe biçimler WildChat Türkçe sohbetlerinde (etiket yok)
sayılır; vekil ölçüt bir sonraki kullanıcı mesajında güçlü onarım ifadesi olmasıdır.

Örneklemler (n_user_msgs >= 2 olan sohbetler):
  rapor  tohum 42 ile 20.000 sohbet (outputs/replay_eval.json ile aynı)
  secim  rapor örneklemi çıkarıldıktan sonra kalanlardan tohum 7 ile 20.000 sohbet

Kullanım:
    python scripts/evaluate_stage3.py                 # seçim örneklemi
    python scripts/evaluate_stage3.py --ornek 15      # her aileden 15 eşleşmeyi yalnızca ekrana yazar (elle kontrol)
    python scripts/evaluate_stage3.py --orneklem rapor   # doğrulama (kural seçildikten sonra)
Çıktı: outputs/stage3_<orneklem>.json (yalnızca sayılar ve sözlük öğesi adları; mesaj metni yazılmaz)
"""

import argparse
import json
import math
import pickle
import random
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from evaluate_replay import DATA, Tally, load_model, load_reasons, predictions_for, replay  # noqa: E402
from kafiai import config  # noqa: E402
from kafiai.correction_patterns import detect, matched_patterns  # noqa: E402
from kafiai.extension_similarity import similarity  # noqa: E402
from kafiai.text import has_strong_repair  # noqa: E402

TURKISH = ROOT / "data" / "processed" / "wildchat48_turkish.parquet"
SAMPLE_SIZE = 20000
SELECTION_SEED = 7
CANDIDATE_REASON = "asama3"

# Aday kural olarak denenen aileler (birleşimler aşağıda türetiliyor).
CANDIDATES = ["A_salinim", "A_geri", "A_hepsi", "B1_guclu", "B2_70", "B_hepsi", "A_ve_B"]
MODES = {"halka1": ("ring", 1), "halka2": ("ring", 2), "kart": ("card", CANDIDATE_REASON)}


def load_sample(name):
    df = pd.read_parquet(DATA)
    df = df[df.n_user_msgs >= 2]
    report = df.sample(SAMPLE_SIZE, random_state=config.SEED)
    if name == "rapor":
        return report
    return df.drop(report.index).sample(SAMPLE_SIZE, random_state=SELECTION_SEED)


def pct(a, b):
    return round(100 * a / b, 2) if b else None


def wilson(k, n, z=1.96):
    """%95 Wilson aralığı (yüzde); az olayda belirsizliği göstermek için."""
    if not n:
        return None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(100 * (c - h), 1), round(100 * (c + h), 1)]


def derive(ev, msgs):
    """Birleşik aileler ve 'benzer mesaj dışı' B2 (mesajın bütünü öncekilere benzemiyor; kural yeni bir mesaja gömülü)."""
    ev["A_hepsi"] = ev["A_donus"] | ev["A_geri"]
    ev["B2_70_benzer_disi"] = {t for t in ev["B2_70"]
                               if max((similarity(msgs[t], m) for m in msgs[max(0, t - config.EXT_RECENT_MESSAGES):t]),
                                      default=0) < config.EXT_SIMILARITY_THRESHOLD}
    ev["B_hepsi"] = ev["B1_guclu"] | ev["B2_70"]
    ev["A_ve_B"] = ev["A_hepsi"] | ev["B_hepsi"]
    return ev


def covered(d):
    return bool(d["strip"] or d.get("short_strip") or d.get("short_repeat_strip") or d["ring"] >= 1 or d["card"])


class FamilyStats:
    def __init__(self):
        self.n = self.convs = self.dsat = self.dsat1 = 0
        self.cov = self.unc = self.unc_dsat1 = self.new_dsat = 0

    def add(self, turns_set, base, ds):
        if turns_set:
            self.convs += 1
        for t in turns_set:
            hit1 = (t in ds) or ((t + 1) in ds)
            self.n += 1
            self.dsat += t in ds
            self.dsat1 += hit1
            if covered(base[t]):
                self.cov += 1
            else:
                self.unc += 1
                self.unc_dsat1 += hit1
                self.new_dsat += t in ds

    def result(self, n_convs):
        return {"olay": self.n, "sohbet_yuzde": pct(self.convs, n_convs), "100_sohbette": round(100 * self.n / n_convs, 2),
                "o_turda_memnuniyetsizlik_yuzde": pct(self.dsat, self.n),
                "o_tur_ya_da_sonraki_memnuniyetsizlik_yuzde": pct(self.dsat1, self.n),
                "aralik_95": wilson(self.dsat1, self.n),
                "mevcut_sinyal_var_yuzde": pct(self.cov, self.n),
                "mevcut_sinyal_yokken": {"olay": self.unc, "memnuniyetsizlik_yuzde": pct(self.unc_dsat1, self.unc),
                                         "aralik_95": wilson(self.unc_dsat1, self.unc)},
                "yeni_yakalanan_memnuniyetsiz_tur": self.new_dsat}


class RingTally(Tally):
    """Tally'ye halka 1+ isabeti eklenir (aday halka 1 kuralını değerlendirmek için)."""

    def __init__(self):
        super().__init__()
        self.ring1_hits = 0

    def add(self, turns, ds, n_msgs):
        super().add(turns, ds, n_msgs)
        self.ring1_hits += sum(1 for t, d in enumerate(turns) if d["ring"] >= 1 and ((t in ds) or ((t + 1) in ds)))

    def summary(self):
        r = self.result()
        return {"halka1_ve_ustu_tur_yuzde": r["halka"]["seviye1_ve_ustu_tur_yuzde"],
                "halka1_ve_ustu_isabet_yuzde": pct(self.ring1_hits, self.ring1),
                "halka2_tur_yuzde": r["halka"]["seviye2_tur_yuzde"],
                "halka2_isabet_yuzde": r["halka"]["seviye2_isabet_yuzde"],
                "kart_100_sohbette": r["kart"]["100_sohbette"], "kart_isabet_yuzde": r["kart"]["isabet_yuzde"],
                "kart_yakalama_yuzde": r["kart"]["tekrarlayan_memnuniyetsizlikte_yakalama_yuzde"],
                "yeni_kart": r["kart"]["kaynaga_gore"].get(CANDIDATE_REASON)}


def cached_predictions(df, name, model, reasons):
    path = ROOT / "data" / "processed" / f"stage3_predictions_{name}.pkl"  # data/processed git dışında
    if path.exists():
        cache = pickle.loads(path.read_bytes())
        if set(cache) >= set(df.conv_id):
            return cache
    print("Tur modeli tahminleri hesaplanıyor (bir kez; sonra önbellekten)...", flush=True)
    cache = {}
    for i, (cid, msgs) in enumerate(zip(df.conv_id, df.user_msgs)):
        cache[cid] = predictions_for([str(m or "") for m in msgs], model, reasons)
        if (i + 1) % 5000 == 0:
            print(f"  {i + 1:,} sohbet", flush=True)
    path.write_bytes(pickle.dumps(cache))
    return cache


def evaluate_wildfeedback(df, preds, model, reasons, show):
    base_tally = RingTally()
    cand = {(f, m): RingTally() for f in CANDIDATES for m in MODES}
    fam = {}
    patterns = Counter()
    base_n = base_dsat1 = base_unc = base_unc_dsat1 = 0
    examples = {}
    for i, (cid, msgs, answers, dsat) in enumerate(zip(df.conv_id, df.user_msgs, df.assistant_msgs, df.dsat_turns)):
        msgs, answers = [str(m or "") for m in msgs], [str(a or "") for a in answers]
        ds = {int(x) for x in dsat}
        p = preds[cid]
        base = replay(msgs, answers, model, reasons, "sonra", p)
        base_tally.add(base, ds, len(msgs))
        for t in range(1, len(msgs)):
            hit1 = (t in ds) or ((t + 1) in ds)
            base_n += 1
            base_dsat1 += hit1
            if not covered(base[t]):
                base_unc += 1
                base_unc_dsat1 += hit1
        ev, _ = detect(msgs, [d["segment_start"] for d in base])
        ev = derive(ev, msgs)
        for name, turns_set in ev.items():
            fam.setdefault(name, FamilyStats()).add(turns_set, base, ds)
            if show:
                examples.setdefault(name, []).extend((msgs[t], t in ds or (t + 1) in ds) for t in turns_set)
        for t in ev["A_hepsi"] | ev["B1_guclu"] | ev["B1_genis"]:
            patterns.update(matched_patterns(msgs[t]))
        for f in CANDIDATES:
            for m, (kind, value) in MODES.items():
                if ev[f]:
                    turns = replay(msgs, answers, model, reasons, "sonra", p, extra={kind: {t: value for t in ev[f]}})
                else:
                    turns = base
                cand[(f, m)].add(turns, ds, len(msgs))
        if (i + 1) % 2000 == 0:
            print(f"  {i + 1:,} sohbet", flush=True)
    if show:
        print_examples(examples, show)
    n = len(df)
    return {
        "taban": {"tur": base_n, "o_tur_ya_da_sonraki_memnuniyetsizlik_yuzde": pct(base_dsat1, base_n),
                  "mevcut_sinyal_yokken_memnuniyetsizlik_yuzde": pct(base_unc_dsat1, base_unc)},
        "aileler": {k: v.result(n) for k, v in sorted(fam.items())},
        "mevcut_durum": base_tally.summary(),
        "aday_kurallar": {f: {m: cand[(f, m)].summary() for m in MODES} for f in CANDIDATES},
        "en_sik_sozluk_ogeleri": patterns.most_common(60),
    }


def evaluate_turkish():
    df = pd.read_parquet(TURKISH)
    df = df[df.n_user_msgs >= 2]
    fam = {}
    patterns = Counter()
    base_n = base_rep = 0
    for msgs in df.user_msgs:
        msgs = [str(m or "") for m in msgs]
        nxt = [has_strong_repair(msgs[t + 1]) if t + 1 < len(msgs) else None for t in range(len(msgs))]
        for t in range(1, len(msgs) - 1):
            base_n += 1
            base_rep += nxt[t]
        ev, _ = detect(msgs)
        ev = derive(ev, msgs)
        for name, turns_set in ev.items():
            s = fam.setdefault(name, {"olay": 0, "sohbet": 0, "sonraki_n": 0, "sonraki_onarim": 0})
            s["olay"] += len(turns_set)
            s["sohbet"] += bool(turns_set)
            for t in turns_set:
                if nxt[t] is not None:
                    s["sonraki_n"] += 1
                    s["sonraki_onarim"] += nxt[t]
        for t in ev["A_hepsi"] | ev["B1_guclu"] | ev["B1_genis"]:
            patterns.update(matched_patterns(msgs[t]))
    n = len(df)
    return {"kaynak": "WildChat 4.8M Türkçe sohbetler (etiket yok)", "sohbet": n,
            "vekil": "bir sonraki kullanıcı mesajında güçlü onarım ifadesi",
            "taban_sonraki_onarim_yuzde": pct(base_rep, base_n),
            "aileler": {k: {"olay": v["olay"], "sohbet_yuzde": pct(v["sohbet"], n),
                            "sonraki_onarim_yuzde": pct(v["sonraki_onarim"], v["sonraki_n"]),
                            "aralik_95": wilson(v["sonraki_onarim"], v["sonraki_n"])}
                        for k, v in sorted(fam.items())},
            "en_sik_sozluk_ogeleri": patterns.most_common(40)}


def print_examples(examples, k):
    """Elle kontrol için: yalnızca ekrana yazılır, hiçbir dosyaya kaydedilmez."""
    rng = random.Random(0)
    for name in ["A_donus", "A_salinim", "A_geri", "B1_guclu", "B1_genis", "B2_70_benzer_disi"]:
        items = examples.get(name, [])
        print(f"\n=== {name} ({len(items)} olay) ===")
        for text, hit in rng.sample(items, min(k, len(items))):
            print(f"[{'M' if hit else '-'}] {' '.join(text.split())[:220]}")


def main():
    ap = argparse.ArgumentParser(description="Aşama 3: ters yönlü düzeltme ve kural yeniden yazma ölçümü")
    ap.add_argument("--orneklem", choices=["secim", "rapor"], default="secim")
    ap.add_argument("--ornek", type=int, default=0, help="her aileden kaç eşleşme ekrana yazılsın (dosyaya yazılmaz)")
    ap.add_argument("--max", type=int, default=0, help="hızlı deneme için sohbet sayısı sınırı")
    args = ap.parse_args()
    df = load_sample(args.orneklem)
    if args.max:
        df = df.head(args.max)
    model, reasons = load_model(), load_reasons()
    preds = cached_predictions(df, args.orneklem, model, reasons)
    print(f"{len(df):,} sohbet ölçülüyor ({args.orneklem})...", flush=True)
    result = {"kaynak": "WildFeedback (sat_dsat_annotation)", "orneklem": args.orneklem, "sohbet": len(df),
              "not": "isabet ve memnuniyetsizlik: olay turunda ya da bir sonrakinde DSAT; aday kart öncelikte 'tekrar'dan sonra"}
    result.update(evaluate_wildfeedback(df, preds, model, reasons, args.ornek))
    result["turkce"] = evaluate_turkish()
    if args.max:
        print(json.dumps(result, ensure_ascii=False, indent=1)[:3000])
        return
    out = ROOT / "outputs" / f"stage3_{args.orneklem}.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Yazıldı: {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
