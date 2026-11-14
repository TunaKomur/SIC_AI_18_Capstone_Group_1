"""Türkçe gerçek kullanım senaryoları (tests/fixtures/scenarios_tr.json).

Her senaryo eklentinin karar zincirinin Python ikizinden (scripts/evaluate_replay.py, replay)
geçirilir ve beklenen davranış sınanır: şerit ne zaman çıkar, halka ne kadar yükselir, kart gelir
mi, konu değişimi ve kişisel sohbet tanınır mı. Aynı senaryolar elle doğrulamada sohbet sitelerinde
yazılır; bu test kuralların o senaryolardaki davranışını sabitler.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import evaluate_replay as er  # noqa: E402
from kafiai.personal import is_personal  # noqa: E402

SCENARIOS = json.loads((ROOT / "tests" / "fixtures" / "scenarios_tr.json").read_text(encoding="utf-8"))["scenarios"]


@pytest.fixture(scope="module")
def model():
    return er.load_model(), er.load_reasons()


@pytest.mark.parametrize("scenario", SCENARIOS, ids=[s["id"] for s in SCENARIOS])
def test_scenario(scenario, model):
    m, reasons = model
    user, answers, want = scenario["user"], scenario["answers"], scenario["beklenen"]
    preds = er.predictions_for(user, m, reasons)
    turns = er.replay(user, answers, m, reasons, "sonra", preds)
    ring = max(t["ring"] for t in turns)
    got = {
        "serit": sum(t["strip"] for t in turns),
        "kisa_serit": sum(bool(t["short_strip"]) for t in turns),
        "kart": any(t["card"] for t in turns),
        "kart_serit_turunda": any(t["card"] and (t["strip"] or t["short_strip"]) for t in turns),
        "cikis": any(t["exit"] for t in turns),
        "bolum": turns[-1]["segments"],
        "kisisel": is_personal(user[0]),
    }
    for key, value in want.items():
        if key == "halka_en_az":
            assert ring >= value, f"halka {ring} < {value}"
        elif key == "halka_en_cok":
            assert ring <= value, f"halka {ring} > {value}"
        else:
            assert got[key] == value, f"{key}: {got[key]} (beklenen {value})"
