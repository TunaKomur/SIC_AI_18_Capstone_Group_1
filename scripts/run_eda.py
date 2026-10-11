"""WildChat 1M ve OpenAssistant OASST1 üzerinde keşifsel veri analizi.

Terminalden çalıştırma (repo kök klasöründe):
    python scripts/run_eda.py
    python scripts/run_eda.py --embeddings      # çok dilli embedding ile döngü analizi
    python scripts/run_eda.py --n-sample 20000  # daha hızlı deneme

Çıktılar:
    figures/*.png             grafikler
    outputs/eda_summary.json  özet istatistikler
"""
import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

ROOT = Path(__file__).resolve().parents[1]

parser = argparse.ArgumentParser(description="WildChat ve OASST1 keşifsel veri analizi")
parser.add_argument("--n-sample", type=int, default=50_000, help="WildChat örneklem büyüklüğü")
parser.add_argument("--n-similarity", type=int, default=10_000, help="Döngü analizi için sohbet sayısı")
parser.add_argument("--n-oasst", type=int, default=30_000, help="OASST1 mesaj sayısı")
parser.add_argument("--embeddings", action="store_true", help="TF-IDF yerine çok dilli sentence embedding kullan")
parser.add_argument("--mock", action="store_true", help="Sahte veriyle hızlı test")
parser.add_argument("--refresh", action="store_true", help="Önbelleği yok sayıp veriyi yeniden indir")
ARGS = parser.parse_args()

import os, re, json, random
from collections import Counter
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

MOCK_DATA = ARGS.mock
N_SAMPLE = ARGS.n_sample
N_SIMILARITY = ARGS.n_similarity
USE_EMBEDDINGS = ARGS.embeddings
N_OASST = ARGS.n_oasst
SEED = 42

FIG_DIR, OUT_DIR = str(ROOT / "figures"), str(ROOT / "outputs")
os.makedirs(FIG_DIR, exist_ok=True); os.makedirs(OUT_DIR, exist_ok=True)
random.seed(SEED); np.random.seed(SEED)

plt.rcParams.update({"figure.dpi": 120, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.alpha": 0.3, "font.size": 10})
COLOR, ACCENT = "#1F5F6B", "#C4562A"
SUMMARY = {}

def save(fig, name):
    path = os.path.join(FIG_DIR, name)
    fig.tight_layout(); fig.savefig(path, bbox_inches="tight"); plt.close(fig)
    print("kaydedildi:", path)

def extract(row):
    conv = row.get("conversation") or []
    users = [t.get("content") or "" for t in conv if t.get("role") == "user"]
    assistants = [t.get("content") or "" for t in conv if t.get("role") == "assistant"]
    return {
        "conversation_hash": row.get("conversation_hash"),
        "timestamp": row.get("timestamp"),
        "model": row.get("model"),
        "turn": row.get("turn"),
        "language": row.get("language"),
        "country": row.get("country"),
        "hashed_ip": row.get("hashed_ip"),
        "toxic": row.get("toxic"),
        "redacted": row.get("redacted"),
        "user_msgs": users,
        "n_user_msgs": len(users),
        "first_prompt": users[0] if users else "",
        "first_prompt_chars": len(users[0]) if users else 0,
        "assistant_chars": sum(len(a) for a in assistants),
    }

def mock_rows(n):
    rng = random.Random(SEED)
    langs = ["English"]*6 + ["Chinese"]*3 + ["Russian"]*2 + ["Turkish", "Spanish", "French"]
    countries = {"English": "United States", "Chinese": "China", "Russian": "Russia", "Turkish": "Türkiye",
                 "Spanish": "Spain", "French": "France"}
    prompts = ["Write an essay about climate change", "Explain how transformers work", "fix this python code",
               "Bana bir dilekçe yaz", "Neden gökyüzü mavi açıkla", "solve this equation 2x+3=7",
               "that's not what I asked, try again", "still wrong, write it again", "olmadı tekrar yaz"]
    ips = [f"ip{i}" for i in range(int(n*0.4))]
    for i in range(n):
        lang = rng.choice(langs); k = max(1, int(rng.expovariate(0.35)))
        base = rng.choice(prompts)
        users = [base] + [rng.choice(prompts if rng.random() < .5 else [base + " please"]) for _ in range(k-1)]
        yield {"conversation_hash": f"h{i}", "model": "gpt-3.5-turbo", "turn": k, "language": lang,
               "country": countries[lang], "hashed_ip": rng.choice(ips[: max(5, int(len(ips)*rng.random()))]),
               "toxic": rng.random() < .05, "redacted": rng.random() < .03,
               "timestamp": pd.Timestamp("2023-04-09") + pd.Timedelta(minutes=rng.randint(0, 60*24*365)),
               "conversation": [x for u in users for x in ({"role": "user", "content": u},
                                {"role": "assistant", "content": "answer " * rng.randint(5, 200)})]}

# İndirilen örneklem yerelde saklanır (data/processed, repo dışında). Sonraki çalıştırmalar
# veriyi tekrar indirmez; yeniden indirmek için --refresh kullanılır.
CACHE = ROOT / "data" / "processed" / f"wildchat_sample_{N_SAMPLE}.pkl"
if CACHE.exists() and not ARGS.refresh and not MOCK_DATA:
    df = pd.read_pickle(CACHE)
    print(f"Örneklem önbellekten okundu: {CACHE.name}")
else:
    if MOCK_DATA:
        source = mock_rows(N_SAMPLE)
    else:
        from datasets import load_dataset
        ds = load_dataset("allenai/WildChat-1M", split="train", streaming=True)
        source = ds.shuffle(seed=SEED, buffer_size=20_000).take(N_SAMPLE)
    records = []
    for i, row in enumerate(source):
        records.append(extract(row))
        if (i + 1) % 10_000 == 0:
            print(f"{i+1:,} sohbet okundu")
    df = pd.DataFrame(records)
    if not MOCK_DATA:
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        df.to_pickle(CACHE)

df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
print(df.shape)

# Şablon (template) tespiti: ilk mesajının ilk 80 karakteri örneklemde 20 veya daha fazla kez
# birebir tekrar eden sohbetler. Bunlar çoğunlukla API üzerinden otomatik gönderilen hazır
# promptlardır ve gerçek bireysel kullanımı temsil etmez.
prefix = df["first_prompt"].str.lower().str.replace(r"\s+", " ", regex=True).str.strip().str[:80]
df["templated"] = (prefix.map(prefix.value_counts()) >= 20) & (df["first_prompt_chars"] >= 30)
user_n = df.groupby("hashed_ip")["hashed_ip"].transform("size")
df["user_weight"] = 1 / user_n
SUMMARY["templates"] = {
    "templated_conversations_pct": round(float(df["templated"].mean() * 100), 2),
    "distinct_templates": int(prefix[df["templated"]].nunique()),
}
print(SUMMARY["templates"])

overview = {
    "n_conversations": int(len(df)),
    "n_unique_users_hashed_ip": int(df["hashed_ip"].nunique()),
    "date_min": str(df["timestamp"].min().date()) if df["timestamp"].notna().any() else None,
    "date_max": str(df["timestamp"].max().date()) if df["timestamp"].notna().any() else None,
    "n_languages": int(df["language"].nunique()),
    "n_countries": int(df["country"].nunique()),
    "models": df["model"].value_counts().head(5).to_dict(),
}
missing = (df.drop(columns=["user_msgs"]).isna().mean() * 100).round(2)
overview["missing_pct"] = missing[missing > 0].to_dict()
SUMMARY["overview"] = overview
print(json.dumps(overview, indent=2, ensure_ascii=False, default=str))

lang = df["language"].value_counts()
ctry = df["country"].value_counts()
is_tr = df["country"].isin(["Turkey", "Türkiye"])

fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
(lang.head(10)[::-1] / len(df) * 100).plot.barh(ax=axes[0], color=COLOR)
axes[0].set_title("En sık 10 dil (% sohbet)"); axes[0].set_xlabel("%")
top_c = (ctry.head(10)[::-1] / len(df) * 100)
top_c.plot.barh(ax=axes[1], color=[ACCENT if c in ("Turkey", "Türkiye") else COLOR for c in top_c.index])
axes[1].set_title("En sık 10 ülke (% sohbet)"); axes[1].set_xlabel("%")
save(fig, "01_language_country.png")

SUMMARY["language_country"] = {
    "top_languages_pct": (lang.head(10) / len(df) * 100).round(2).to_dict(),
    "top_countries_pct": (ctry.head(10) / len(df) * 100).round(2).to_dict(),
    "turkey_conversations": int(is_tr.sum()),
    "turkey_pct": round(float(is_tr.mean() * 100), 2),
    "turkish_language_conversations": int((df["language"] == "Turkish").sum()),
}
print(SUMMARY["language_country"])

turns = df["n_user_msgs"].clip(lower=1)
fig, ax = plt.subplots(figsize=(8, 4))
bins = np.arange(1, min(turns.max(), 40) + 2) - 0.5
ax.hist(turns.clip(upper=40), bins=bins, color=COLOR)
ax.set_yscale("log"); ax.set_xlabel("Sohbet başına kullanıcı mesajı (40+ birleştirildi)"); ax.set_ylabel("Sohbet sayısı (log)")
ax.set_title("Sohbet uzunluğu dağılımı")
save(fig, "02_turn_distribution.png")

SUMMARY["turns"] = {
    "mean": round(float(turns.mean()), 2), "median": float(turns.median()),
    "p90": float(turns.quantile(.9)), "p99": float(turns.quantile(.99)), "max": int(turns.max()),
    "single_turn_pct": round(float((turns == 1).mean() * 100), 2),
    "ge5_turn_pct": round(float((turns >= 5).mean() * 100), 2),
    "ge10_turn_pct": round(float((turns >= 10).mean() * 100), 2),
}
print(SUMMARY["turns"])

hours_utc = df["timestamp"].dt.hour
tr_local = (df.loc[is_tr, "timestamp"] + pd.Timedelta(hours=3)).dt.hour
# Birkaç yoğun kullanıcının dağılımı çarpıtmaması için her sohbet, o kullanıcının sohbet sayısının
# tersiyle ağırlıklandırılır; böylece her kullanıcı toplamda eşit ağırlık taşır.
tr_w = df.loc[is_tr, "user_weight"].groupby(tr_local.values).sum()
tr_w = (tr_w / tr_w.sum()).reindex(range(24), fill_value=0)

fig, axes = plt.subplots(1, 2, figsize=(12, 4))
hours_utc.value_counts(normalize=True).sort_index().mul(100).plot.bar(ax=axes[0], color=COLOR)
axes[0].set_title("Tüm sohbetler, saat (UTC)"); axes[0].set_ylabel("% sohbet"); axes[0].set_xlabel("")
if len(tr_local) > 0:
    tr_w.mul(100).plot.bar(ax=axes[1], color=ACCENT)
axes[1].set_title(f"Türkiye, yerel saat, kullanıcı ağırlıklı ({df.loc[is_tr, 'hashed_ip'].nunique()} kullanıcı)"); axes[1].set_xlabel("")
save(fig, "03_hour_of_day.png")

night = tr_local.between(0, 5)
SUMMARY["hours"] = {
    "peak_hour_utc": int(hours_utc.mode()[0]) if len(hours_utc) else None,
    "turkey_n": int(len(tr_local)),
    "turkey_night_00_05_pct": round(float(night.mean() * 100), 2) if len(tr_local) else None,
    "turkey_users": int(df.loc[is_tr, "hashed_ip"].nunique()),
    "turkey_night_00_05_user_weighted_pct": round(float(tr_w.loc[0:5].sum() * 100), 2),
    "turkey_peak_hour_local_user_weighted": int(tr_w.idxmax()),
    "turkey_peak_hour_local": int(tr_local.mode()[0]) if len(tr_local) else None,
}
print(SUMMARY["hours"])

per_user = df.groupby("hashed_ip").size().sort_values(ascending=False)
share = per_user.cumsum() / per_user.sum() * 100
users_pct = np.arange(1, len(per_user) + 1) / len(per_user) * 100

fig, axes = plt.subplots(1, 2, figsize=(12, 4))
axes[0].hist(per_user.clip(upper=50), bins=np.arange(1, 52) - 0.5, color=COLOR); axes[0].set_yscale("log")
axes[0].set_title("Kullanıcı başına sohbet (50+ birleştirildi)"); axes[0].set_xlabel("Sohbet"); axes[0].set_ylabel("Kullanıcı (log)")
axes[1].plot(users_pct, share.values, color=ACCENT); axes[1].plot([0, 100], [0, 100], "--", color="grey")
axes[1].set_title("Kullanımın yoğunlaşması"); axes[1].set_xlabel("En yoğun kullanıcılardan itibaren % kullanıcı"); axes[1].set_ylabel("% sohbet")
save(fig, "04_user_concentration.png")

def top_share(p):
    k = max(1, int(len(per_user) * p)); return round(float(per_user.head(k).sum() / per_user.sum() * 100), 2)
SUMMARY["users"] = {
    "conversations_per_user_mean": round(float(per_user.mean()), 2),
    "conversations_per_user_median": float(per_user.median()),
    "single_conversation_users_pct": round(float((per_user == 1).mean() * 100), 2),
    "top1pct_users_share_of_conversations": top_share(.01),
    "top10pct_users_share_of_conversations": top_share(.10),
}
print(SUMMARY["users"])

# Yoğun kullanıcılar ile diğerleri arasında şablon kullanımı karşılaştırması
top_ips = set(per_user.head(max(1, int(len(per_user) * .01))).index)
grp = np.where(df["hashed_ip"].isin(top_ips), "En yoğun %1 kullanıcı", "Diğer kullanıcılar")
tmpl_by_grp = df.groupby(grp)["templated"].mean().mul(100)
fig, ax = plt.subplots(figsize=(7, 4))
bars = ax.bar(tmpl_by_grp.index, tmpl_by_grp.values, color=[COLOR, ACCENT][:len(tmpl_by_grp)])
ax.bar_label(bars, fmt="%.1f%%"); ax.set_ylabel("Şablon sohbet oranı (%)"); ax.set_title("Şablon (otomatik) sohbetlerin kullanıcı gruplarına dağılımı")
save(fig, "09_templates_by_user_group.png")
SUMMARY["users"]["templated_pct_by_group"] = tmpl_by_grp.round(2).to_dict()

multi = df[df["n_user_msgs"] >= 3]
sub = multi.sample(min(N_SIMILARITY, len(multi)), random_state=SEED)
pairs = [(i, a[:1000], b[:1000]) for i, msgs in zip(sub.index, sub["user_msgs"]) for a, b in zip(msgs, msgs[1:])]
print(f"{len(sub):,} sohbet, {len(pairs):,} ardışık mesaj çifti")

if USE_EMBEDDINGS:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    A = model.encode([p[1] for p in pairs], batch_size=128, normalize_embeddings=True, show_progress_bar=False)
    B = model.encode([p[2] for p in pairs], batch_size=128, normalize_embeddings=True, show_progress_bar=False)
    sims = (A * B).sum(axis=1); THRESH = 0.85; method = "multilingual MiniLM embeddings"
else:
    from sklearn.feature_extraction.text import TfidfVectorizer
    vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=2).fit([p[1] for p in pairs] + [p[2] for p in pairs])
    A, B = vec.transform([p[1] for p in pairs]), vec.transform([p[2] for p in pairs])
    sims = np.asarray(A.multiply(B).sum(axis=1)).ravel(); THRESH = 0.7; method = "TF-IDF char n-gram"

pair_df = pd.DataFrame({"conv": [p[0] for p in pairs], "sim": sims})
pair_df["templated"] = pair_df["conv"].map(df["templated"])
conv_max = pair_df.groupby("conv")["sim"].max()
conv_rate = pair_df.assign(hi=pair_df["sim"] >= THRESH).groupby("conv")["hi"].mean()

fig, ax = plt.subplots(figsize=(8, 4))
ax.hist(pair_df["sim"], bins=50, color=COLOR); ax.axvline(THRESH, color=ACCENT, ls="--", label=f"eşik = {THRESH}")
ax.set_title("Ardışık kullanıcı mesajları arasındaki benzerlik"); ax.set_xlabel("Cosine similarity"); ax.set_ylabel("Mesaj çifti"); ax.legend()
save(fig, "05_consecutive_similarity.png")

SUMMARY["loops"] = {
    "method": method, "threshold": THRESH, "n_conversations": int(len(sub)), "n_pairs": int(len(pairs)),
    "pairs_above_threshold_pct": round(float((pair_df["sim"] >= THRESH).mean() * 100), 2),
    "conversations_with_any_near_repeat_pct": round(float((conv_max >= THRESH).mean() * 100), 2),
    "conversations_with_half_pairs_repeat_pct": round(float((conv_rate >= .5).mean() * 100), 2),
    "pairs_near_identical_ge_0_98_pct": round(float((pair_df["sim"] >= .98).mean() * 100), 2),
    "organic_conversations_with_any_near_repeat_pct": round(float((conv_max[~conv_max.index.map(df["templated"]).astype(bool)] >= THRESH).mean() * 100), 2),
}
# Sohbet uzadıkça tekrar eden mesaj görülme oranı (yalnızca şablon olmayan sohbetler)
organic_sub = sub[~sub["templated"]]
rep_len = pd.DataFrame({"n": organic_sub["n_user_msgs"], "rep": conv_max.reindex(organic_sub.index) >= THRESH})
rep_len["bucket"] = pd.cut(rep_len["n"], [2, 4, 9, 10_000], labels=["3-4", "5-9", "10+"])
rep_by_len = rep_len.groupby("bucket", observed=False)["rep"].mean().mul(100)
fig, ax = plt.subplots(figsize=(7, 4))
bars = ax.bar(rep_by_len.index.astype(str), rep_by_len.values, color=COLOR); ax.bar_label(bars, fmt="%.1f%%")
ax.set_xlabel("Kullanıcı mesajı sayısı"); ax.set_ylabel("% sohbet")
ax.set_title("En az bir kez neredeyse aynı mesajı tekrar eden sohbetler")
save(fig, "10_repeat_by_length.png")
SUMMARY.setdefault("loops_by_length_pct", rep_by_len.round(2).to_dict())
print(SUMMARY["loops"])

REPAIR = [r"\bnot what i (asked|wanted|meant)\b", r"\bthat'?s (not|wrong)\b", r"\b(still|is) (wrong|not working)\b",
          r"\btry again\b", r"\bdoesn'?t work\b", r"\bdidn'?t work\b", r"\byou didn'?t\b", r"\bi (said|asked)\b",
          r"\bwrong\b", r"\bincorrect\b",
          r"yanlış", r"olmadı", r"\btekrar\b", r"\bhala\b", r"hâlâ", r"çalışmıyor", r"anlamadın", r"öyle değil", r"ben ne dedim"]
rx = re.compile("|".join(REPAIR), re.IGNORECASE)

later = df[df["n_user_msgs"] >= 2]
has_repair = later["user_msgs"].apply(lambda m: any(rx.search(x or "") for x in m[1:]))
repair_by_len = later.assign(r=has_repair, bucket=pd.cut(later["n_user_msgs"], [1, 2, 4, 9, 10_000],
                             labels=["2", "3-4", "5-9", "10+"])).groupby("bucket", observed=False)["r"].mean() * 100

fig, ax = plt.subplots(figsize=(7, 4))
repair_by_len.plot.bar(ax=ax, color=COLOR); ax.set_ylabel("% sohbet"); ax.set_xlabel("Kullanıcı mesajı sayısı")
ax.set_title("Onarım/memnuniyetsizlik ifadesi içeren sohbetler")
save(fig, "06_repair_by_length.png")

SUMMARY["repair"] = {
    "n_multi_turn": int(len(later)),
    "with_repair_phrase_pct": round(float(has_repair.mean() * 100), 2),
    "by_length_pct": repair_by_len.round(2).to_dict(),
}
print(SUMMARY["repair"])

PRODUCE = re.compile(r"\b(write|generate|create|make|rewrite|paraphrase|translate|summari[sz]e|draft|compose|solve|"
                     r"fix|code|implement|complete|continue|list|give me|answer|correct|improve|"
                     r"yaz|çöz|oluştur|hazırla|çevir|özetle|düzelt|tamamla|devam et|listele|cevapla)\b", re.IGNORECASE)
UNDERSTAND = re.compile(r"\b(explain|why|how does|how do|how can|how to|what is|what are|what does|difference between|"
                        r"help me understand|teach|meaning of|açıkla|neden|niçin|nasıl|nedir|ne demek|farkı|anlat)\b", re.IGNORECASE)

def intent(row):
    p = (row["first_prompt"] or "")[:200]
    if row["templated"]: return "Şablon / otomatik"
    if PRODUCE.search(p): return "Doğrudan üretim"
    if UNDERSTAND.search(p) or p.strip().endswith("?"): return "Anlama / soru"
    return "Diğer"

ORDER = ["Doğrudan üretim", "Anlama / soru", "Diğer", "Şablon / otomatik"]
COLORS = {"Doğrudan üretim": ACCENT, "Anlama / soru": COLOR, "Diğer": "#9AA5A8", "Şablon / otomatik": "#D9CFC1"}
df["intent"] = df.apply(intent, axis=1)
dist = df["intent"].value_counts(normalize=True).mul(100).reindex(ORDER, fill_value=0)
by_tr = (df.assign(tr=np.where(is_tr, "Türkiye", "Diğer ülkeler")).groupby("tr")["intent"]
           .value_counts(normalize=True).mul(100).unstack().reindex(columns=ORDER, fill_value=0))

fig, ax = plt.subplots(figsize=(8, 4))
by_tr.plot.barh(ax=ax, stacked=True, color=[COLORS[c] for c in ORDER], width=0.6)
ax.set_xlabel("% sohbet"); ax.set_ylabel(""); ax.set_xlim(0, 100)
ax.legend(title="", ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.18), frameon=False)
ax.set_title("İlk talebin türü (kural tabanlı sınıflandırma)")
save(fig, "07_first_prompt_intent.png")

SUMMARY["intent"] = {"overall_pct": dist.round(2).to_dict(), "by_region_pct": by_tr.round(2).to_dict()}
print(SUMMARY["intent"])

quality = {
    "toxic_flag_pct": round(float(df["toxic"].fillna(False).astype(bool).mean() * 100), 2),
    "redacted_flag_pct": round(float(df["redacted"].fillna(False).astype(bool).mean() * 100), 2),
    "empty_first_prompt_pct": round(float((df["first_prompt_chars"] == 0).mean() * 100), 2),
    "very_short_first_prompt_lt10_pct": round(float((df["first_prompt_chars"] < 10).mean() * 100), 2),
    "duplicate_hash_pct": round(float(df["conversation_hash"].duplicated().mean() * 100), 2),
    "top_language_share_pct": round(float(lang.iloc[0] / len(df) * 100), 2),
    "first_prompt_chars_median": float(df["first_prompt_chars"].median()),
}
SUMMARY["quality"] = quality
print(quality)

LABELS = ["quality", "helpfulness", "fails_task", "creativity", "humor", "toxicity"]
if MOCK_DATA:
    rng = np.random.default_rng(SEED)
    oa = pd.DataFrame({"role": rng.choice(["prompter", "assistant"], 2000), "lang": rng.choice(["en", "es", "tr", "de"], 2000),
                       "message_tree_id": rng.integers(0, 300, 2000)})
    for l in LABELS: oa[l] = np.where(rng.random(2000) < .7, rng.random(2000), np.nan)
else:
    from datasets import load_dataset
    raw = load_dataset("OpenAssistant/oasst1", split="train")
    raw = raw.select(range(min(N_OASST, len(raw))))
    rows = []
    for r in raw:
        lab = r.get("labels") or {}
        vals = dict(zip(lab.get("name") or [], lab.get("value") or []))
        rows.append({"role": r["role"], "lang": r["lang"], "message_tree_id": r["message_tree_id"],
                     **{l: vals.get(l, np.nan) for l in LABELS}})
    oa = pd.DataFrame(rows)

asst = oa[oa["role"] == "assistant"]
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
axes[0].hist(asst["quality"].dropna(), bins=20, color=COLOR); axes[0].set_title("Asistan cevaplarının kalite puanı")
axes[0].set_xlabel("quality (0 ile 1)"); axes[0].set_ylabel("Mesaj")
asst[LABELS].mean().sort_values().plot.barh(ax=axes[1], color=ACCENT); axes[1].set_title("Etiket ortalamaları (asistan)")
save(fig, "08_oasst_labels.png")

SUMMARY["oasst1"] = {
    "n_messages_read": int(len(oa)), "n_trees": int(oa["message_tree_id"].nunique()),
    "assistant_messages": int(len(asst)), "languages_top": oa["lang"].value_counts().head(8).to_dict(),
    "turkish_messages": int((oa["lang"] == "tr").sum()),
    "label_coverage_pct": (asst[LABELS].notna().mean() * 100).round(2).to_dict(),
    "label_means": asst[LABELS].mean().round(3).to_dict(),
    "low_quality_lt_0_3_pct": round(float((asst["quality"].dropna() < .3).mean() * 100), 2),
}
print(json.dumps(SUMMARY["oasst1"], indent=2, ensure_ascii=False))

with open(os.path.join(OUT_DIR, "eda_summary.json"), "w", encoding="utf-8") as f:
    json.dump(SUMMARY, f, indent=2, ensure_ascii=False, default=str)

print("Özet yazıldı:", os.path.join(OUT_DIR, "eda_summary.json"))

