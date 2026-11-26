"""Anlam modelinin kırpma listesini üretir: scripts/data/semantic_keep_ids.json (K52).

Temel modelin kelime bölücüsü 250.002 parçalı; çoğu Türkçe ve İngilizcede hiç geçmeyen dillerin
parçaları. Hangi parçaların kalacağını gerçek metinlerde sayarak seçiyoruz:
    - Türkçe: quora-tr soru metinleri (trmteb/quora-tr, corpus bölümü, 522.931 soru)
    - İngilizce: WildFeedback kullanıcı mesajları, yalnızca Latin harfli olanlar (ilk 1.000 karakter)
Kalan parçalar: iki kaynaktan birinde en az MIN_COUNT kez geçenler, tek harfli Latin ve Türkçe
parçalar (her kelime harf harf bölünebilsin), "▁" ve dört özel parça (<s>, <pad>, </s>, <unk>).
Ölçüm: en az iki kez geçen parçalar Türkçe metinlerdeki parçaların %99,997'sini, İngilizce
metinlerdekilerin %99,990'ını kapsıyor.

Metinlerin kendisi hiçbir yere yazılmaz; yalnızca parça kimlikleri yazılır.

Gerekenler: data/processed/wildfeedback_conversations.parquet (scripts/fetch_wildfeedback.py),
internet (quora-tr indirilir, yaklaşık 28 MB), pip install tokenizers.
Çalıştırma: python scripts/make_semantic_vocab.py
"""

import json
import re
import urllib.request
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "scripts" / "data" / "semantic_keep_ids.json"
CACHE = ROOT / "data" / "raw" / "semantic_model"
WILDFEEDBACK = ROOT / "data" / "processed" / "wildfeedback_conversations.parquet"
QUORA_TR = "https://huggingface.co/datasets/trmteb/quora-tr/resolve/main/corpus/corpus-00000-of-00001.parquet"
MIN_COUNT = 2
SPECIAL = [0, 1, 2, 3]

_NON_LATIN = re.compile(r"[^A-Za-z0-9\s\.,;:!\?'\"\(\)\-çğıöşüÇĞİÖŞÜâîûÂÎÛ/&%\+=\*#@_<>\[\]{}|~`^$€₺]")
_SINGLE = re.compile(r"^[A-Za-z0-9çğıöşüÇĞİÖŞÜâîûÂÎÛ\.,;:!\?'\"\(\)\-/&%\+=\*#@_<>\[\]{}|~`\^\$€₺]$")


def mostly_latin(text):
    return len(_NON_LATIN.findall(text)) <= 0.02 * max(1, len(text))


def count(tokenizer, texts):
    counts = Counter()
    for i in range(0, len(texts), 4000):
        for enc in tokenizer.encode_batch(texts[i:i + 4000]):
            counts.update(enc.ids)
    return counts


def main():
    from tokenizers import Tokenizer

    import build_semantic_model as bsm

    source = bsm.download("tokenizer.json", bsm.TOKENIZER_SHA256)
    tokenizer = Tokenizer.from_file(str(source))
    vocab = json.loads(source.read_text(encoding="utf-8"))["model"]["vocab"]

    quora = CACHE / "quora_tr_corpus.parquet"
    if not quora.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(QUORA_TR, quora)
    turkish = pd.read_parquet(quora)["text"].astype(str).tolist()
    english = [m[:1000] for msgs in pd.read_parquet(WILDFEEDBACK, columns=["user_msgs"]).user_msgs
               for m in msgs if mostly_latin(m[:1000])]
    counts = count(tokenizer, turkish) + count(tokenizer, english)
    # Not: iki kaynağın sayıları toplanır; en az MIN_COUNT kez geçen parça kalır.

    keep = set(SPECIAL)
    for i, (piece, _score) in enumerate(vocab):
        core = piece[1:] if piece.startswith("▁") else piece
        if counts.get(i, 0) >= MIN_COUNT or piece == "▁" or (len(core) == 1 and _SINGLE.match(core)):
            keep.add(i)
    keep = sorted(keep)
    OUT.write_text(json.dumps(keep) + "\n", encoding="utf-8")
    print(f"{len(keep):,} parça yazıldı: {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    main()
