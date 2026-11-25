"""Yazım hatası toleransı (Katman 1): kurallar ve eklentiyle ortak örnekler."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from kafiai.extension_similarity import (
    align_typos, holds_send, is_repeat, normalize_text, osa_distance, typo_match, typo_similarity,
)  # noqa: E402


def test_user_example_is_exact_repeat():
    prev, new = "ankaranın başkenti neresidir?", "anksrabın baskebti neresifir"
    assert typo_similarity(new, prev) >= 0.99
    assert is_repeat(new, prev) and holds_send(new, prev)


def test_numbers_ordinals_and_opposites_are_not_typos():
    assert not is_repeat("birinci dünya savaşının sebeplerini yaz", "ikinci dünya savaşının sebeplerini yaz")
    assert typo_match("kaynakçasız", ["kaynakçalı"]) is None
    assert typo_match("düzeltme", ["düzelt"]) is None
    assert typo_match("ungrammaticality", ["grammaticality"]) is None
    assert not holds_send("bu ödevi kaynakçasız yaz", "bu ödevi kaynakçalı yaz")
    assert not is_repeat("2. soruyu çöz", "1. soruyu çöz")


def test_different_entity_is_not_a_typo():
    assert not is_repeat("amerikanın başkenti neresi", "türkiyenin başkenti neresi")


def test_matches_fixture():
    data = json.loads((ROOT / "tests" / "fixtures" / "typo_parity.json").read_text(encoding="utf-8"))
    for row in data["distances"]:
        assert osa_distance(row["a"], row["b"]) == row["distance"]
    for row in data["pairs"]:
        assert align_typos(normalize_text(row["new"]), normalize_text(row["previous"])) == row["aligned"], row["new"]
        assert abs(typo_similarity(row["new"], row["previous"]) - row["score"]) < 1e-5, row["new"]


def test_semantic_pairs_typo_recall_and_no_false_hold():
    """Test setinde yazım hatalı tekrarların en az %90'ı bekletilir; farklı isteklerin hiçbiri bekletilmez."""
    pairs = json.loads((ROOT / "tests" / "fixtures" / "semantic_pairs_tr.json").read_text(encoding="utf-8"))["pairs"]
    typos = [p for p in pairs if p["tur"] in ("yazim_hafif", "yazim_agir", "turkce_harfsiz")]
    held = sum(holds_send(p["yeni"], p["onceki"]) for p in typos)
    assert held / len(typos) >= 0.9
    assert not any(holds_send(p["yeni"], p["onceki"]) for p in pairs if not p["ayni"])
