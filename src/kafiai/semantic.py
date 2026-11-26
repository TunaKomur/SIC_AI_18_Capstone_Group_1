"""Katman 2: anlam modeli ve "aynı istek" kararı (K52). Eklentideki src/core/semantic.ts ile aynı kural.

Bir mesaj, son mesajlardan biriyle "aynı istek" sayılır, eğer:
    1. Cümle modelinin anlam benzerliği eşiği geçiyorsa (semantic-rules.json, threshold) ve
    2. iki mesaj arasında içerik kelimesi yer değiştirmemişse ve yeni mesaj en çok bir yeni içerik
       kelimesi getiriyorsa (bekçi).
Model karşılaştırmadan önce yeni mesajın yazım hataları önceki mesaja göre düzeltilir (Katman 1).

Bekçinin nedeni: cümle modelleri "metni daha kısa yaz" ile "metni daha uzun yaz"ı, "python ile dosya
nasıl okunur" ile "java ile dosya nasıl okunur"u da çok benzer buluyor. Bu cümlelerde bir içerik
kelimesi ötekinin yerine geçmiş; aynı sorunun başka söylenişinde ise genellikle yalnızca soru
kelimeleri ve hafif fiiller değişiyor ("neresidir" -> "hangi şehir", "yaz" -> "hale getir").

Model (Embedder) isteğe bağlıdır: onnxruntime ve tokenizers kurulu ve model dosyası üretilmişse
(scripts/build_semantic_model.py) çalışır. Bekçi modelsiz çalışır.
"""

import json
from pathlib import Path

from kafiai.extension_similarity import align_typos, fold_turkish, normalize_text, with_folded, _FILLER

ROOT = Path(__file__).resolve().parents[2]
RULES = json.loads((ROOT / "extension" / "src" / "data" / "semantic-rules.json").read_text(encoding="utf-8"))
MODEL_DIR = ROOT / "extension" / "public" / RULES["model"]["dir"]
THRESHOLD = RULES["threshold"]
_GENERIC = set(with_folded(RULES["generic"]))
_STEM = RULES["stem_chars"]
MAX_NEW_CONTENT = RULES["max_new_content"]


def _has_digit(token):
    return any(c.isdigit() for c in token)


def content_words(normalized):
    """Dolgu ve genel kelimeler (soru kelimeleri, hafif fiiller) dışındaki kelimeler."""
    return [t for t in normalized.split()
            if t not in _FILLER and t not in _GENERIC and (len(t) >= 2 or _has_digit(t))]


def _stem(token):
    return token if _has_digit(token) else fold_turkish(token)[:_STEM]


def swapped_content(previous_text, new_text):
    """(yalnızca öncekinde olan, yalnızca yenide olan) içerik kelimeleri; yeni mesaj yazım hatası düzeltilmiş hâliyle."""
    prev = normalize_text(previous_text)
    new = align_typos(normalize_text(new_text), prev)
    a, b = content_words(prev), content_words(new)
    sa, sb = {_stem(t) for t in a}, {_stem(t) for t in b}
    return [t for t in a if _stem(t) not in sb], [t for t in b if _stem(t) not in sa]


def is_swap(previous_text, new_text):
    """İki mesajda da ötekinde olmayan içerik kelimesi var mı (bir kelime ötekinin yerine geçmiş)?"""
    only_old, only_new = swapped_content(previous_text, new_text)
    return bool(only_old) and bool(only_new)


def same_intent(score, previous_text, new_text, threshold=THRESHOLD):
    """Anlam benzerliği (score) ve bekçiye göre "aynı istek" kararı.

    Bekçi: içerik kelimesi yer değiştirmemiş ve yeni mesaj en çok MAX_NEW_CONTENT yeni içerik kelimesi
    getiriyor (daha fazlası isteği geliştirmektir, döngü değil)."""
    if score < threshold:
        return False
    only_old, only_new = swapped_content(previous_text, new_text)
    return not (only_old and only_new) and len(only_new) <= MAX_NEW_CONTENT


def model_inputs(previous_text, new_text):
    """Modele verilen iki metin: önceki mesaj sadeleştirilmiş, yeni mesaj ayrıca yazım hatası düzeltilmiş."""
    prev = normalize_text(previous_text)
    return prev, align_typos(normalize_text(new_text), prev)


class Embedder:
    """Cümle modeli: metni 384 sayılık, uzunluğu 1 olan bir vektöre çevirir (ortalama havuzlama)."""

    def __init__(self, model_dir=MODEL_DIR):
        import numpy as np
        import onnxruntime as ort
        from tokenizers import Tokenizer

        self._np = np
        model = Path(model_dir) / "model.onnx"
        if not model.exists():
            raise FileNotFoundError(f"{model} yok. Önce: python scripts/build_semantic_model.py")
        self.tokenizer = Tokenizer.from_file(str(Path(model_dir) / "tokenizer.json"))
        self.tokenizer.enable_truncation(RULES["max_tokens"])
        self.session = ort.InferenceSession(str(model))
        self.inputs = [i.name for i in self.session.get_inputs()]
        self._cache = {}

    def token_ids(self, text):
        return self.tokenizer.encode(text).ids

    def embed(self, text):
        if text in self._cache:
            return self._cache[text]
        np = self._np
        ids = np.array([self.token_ids(text)], dtype=np.int64)
        mask = np.ones_like(ids)
        feed = {"input_ids": ids, "attention_mask": mask}
        if "token_type_ids" in self.inputs:
            feed["token_type_ids"] = np.zeros_like(ids)
        hidden = self.session.run(None, feed)[0][0]
        vec = hidden.mean(axis=0)
        vec = vec / max(float(np.linalg.norm(vec)), 1e-12)
        if len(self._cache) > 50000:
            self._cache.clear()
        self._cache[text] = vec
        return vec

    def similarity(self, previous_text, new_text):
        """Önceki ve yeni mesajın anlam benzerliği (kosinüs), yazım hataları düzeltilmiş hâliyle."""
        prev, new = model_inputs(previous_text, new_text)
        if not prev or not new:
            return 0.0
        return float(self.embed(prev) @ self.embed(new))
