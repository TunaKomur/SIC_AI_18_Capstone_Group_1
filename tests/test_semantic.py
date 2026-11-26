"""Katman 2 (K52): "aynı istek" kuralı, kelime bölücü ve model; eklentiyle ortak örnekler."""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from kafiai import semantic  # noqa: E402

FIXTURE = json.loads((ROOT / "tests" / "fixtures" / "semantic_parity.json").read_text(encoding="utf-8"))
HAS_MODEL = (semantic.MODEL_DIR / "model.onnx").exists()


def test_guard_blocks_swapped_content_words():
    assert semantic.is_swap("metni daha kısa yaz", "metni daha uzun yaz")
    assert semantic.is_swap("python ile dosya nasıl okunur", "java ile dosya nasıl okunur")
    assert semantic.is_swap("1. soruyu çöz", "2. soruyu çöz")
    assert not semantic.is_swap("ankaranın başkenti neresidir?", "ankaranın başkenti hangi şehir")
    assert not semantic.is_swap("ankaranın başkenti neresidir?", "anksrabın baskebti neresifir")


def test_same_intent_needs_score_and_guard():
    assert semantic.same_intent(0.9, "ankaranın başkenti neresidir?", "ankaranın başkenti nedir")
    assert not semantic.same_intent(0.7, "ankaranın başkenti neresidir?", "ankaranın başkenti nedir")
    assert not semantic.same_intent(0.99, "metni daha kısa yaz", "metni daha uzun yaz")


def test_guard_matches_fixture():
    for row in FIXTURE["pairs"]:
        only_old, only_new = semantic.swapped_content(row["previous"], row["new"])
        assert [only_old, only_new] == [row["only_old"], row["only_new"]], row["new"]
        assert semantic.same_intent(row["score"], row["previous"], row["new"]) == row["same"], row["new"]


def test_tokenizer_matches_fixture():
    from tokenizers import Tokenizer
    tok = Tokenizer.from_file(str(semantic.MODEL_DIR / "tokenizer.json"))
    tok.enable_truncation(semantic.RULES["max_tokens"])
    for row in FIXTURE["tokens"]:
        assert tok.encode(row["text"]).ids == row["ids"], row["text"]


@pytest.mark.skipif(not HAS_MODEL, reason="model dosyası yok: python scripts/build_semantic_model.py")
def test_model_scores_match_fixture():
    emb = semantic.Embedder()
    for row in FIXTURE["pairs"]:
        assert abs(emb.similarity(row["previous"], row["new"]) - row["score"]) < 1e-4, row["new"]
