"""Aşama 3 sözlüğü: Türkçe ve İngilizce biçimler, Türkçe karaktersiz yazım ve sınır durumları.

WildFeedback ağırlıkla İngilizce olduğu için Türkçe biçimlerin doğruluğu en çok bu testlerle güvenceye alınır.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from kafiai.correction_patterns import constraint_clauses, detect, is_revert, poles, restate_marker  # noqa: E402


@pytest.mark.parametrize("text,axis,pole", [
    ("biraz kısaltır mısın", "uzunluk", "kisa"),
    ("kisaltabilir misin", "uzunluk", "kisa"),
    ("çok uzun olmuş", "uzunluk", "kisa"),
    ("lafı uzatma, direkt söyle", "uzunluk", "kisa"),
    ("biraz daha uzat", "uzunluk", "uzun"),
    ("detaylandırır mısın", "uzunluk", "uzun"),
    ("cok kisa olmus", "uzunluk", "uzun"),
    ("make it shorter", "uzunluk", "kisa"),
    ("too short, expand it", "uzunluk", "uzun"),
    ("daha resmi bir dille yaz", "uslup", "resmi"),
    ("fazla resmi oldu", "uslup", "samimi"),
    ("daha basit anlat", "duzey", "basit"),
    ("cok yuzeysel kaldi, derinlemesine anlat", "duzey", "ileri"),
    ("madde madde yaz", "bicim", "liste"),
    ("madde kullanma, paragraf olarak yaz", "bicim", "duz"),
])
def test_poles(text, axis, pole):
    assert poles(text).get(axis) == pole


@pytest.mark.parametrize("text", [
    "bu kısaltma ne anlama geliyor",   # ad olarak "kısaltma"
    "kısa değil uzun olsun",           # iki kutup birden: belirsiz
    "the story expanded over years",   # anlatı içinde geçmiş zaman
])
def test_no_length_pole(text):
    assert "uzunluk" not in poles(text)


@pytest.mark.parametrize("text", ["eski haline getir", "onceki hali daha iyiydi", "ilk versiyonu geri ver",
                                  "put it back the way it was", "the first one was better"])
def test_revert(text):
    assert is_revert(text)


@pytest.mark.parametrize("text,marker", [
    ("sana söylemiştim tablo kullanma diye", "guclu"),
    ("soylemistim tablo kullanma", "guclu"),
    ("kaç kere söyleyeceğim", "guclu"),
    ("dediğim gibi sadece kod ver", "guclu"),
    ("I told you not to use lists", "guclu"),
    ("as I said, keep it short", "guclu"),
    ("unutma sadece türkçe", "genis"),
    ("bir hikaye yaz", None),
])
def test_restate_marker(text, marker):
    assert restate_marker(text) == marker


def test_constraint_clauses_turkish_negative_suffix():
    clauses = constraint_clauses("Bir e-posta yaz. Cevapta emoji olmasın lütfen. Selam.")
    assert clauses == ["cevapta emoji olmasin lutfen"]


def test_detect_oscillation_and_restatement():
    msgs = [
        "Bana bir ürün tanıtım metni yaz. Cevapta hiç emoji kullanma lütfen.",
        "kısalt",
        "şimdi biraz uzat",
        "yine kısalt",
        "Lütfen hiç emoji kullanma cevapta, bunu tekrar yazıyorum.",
    ]
    ev, _ = detect(msgs)
    assert ev["A_donus"] == {2, 3}
    assert ev["A_salinim"] == {3}
    assert 4 in ev["B1_guclu"]  # "tekrar yazıyorum"
    assert 4 in ev["B2_60"]     # emoji kuralı ilk mesajdakine benziyor


def test_reversal_needs_same_segment():
    msgs = ["metin yaz", "kısalt", "yeni konu", "uzat"]
    ev, _ = detect(msgs, segment_starts=[0, 0, 2, 2])
    assert ev["A_donus"] == set()
