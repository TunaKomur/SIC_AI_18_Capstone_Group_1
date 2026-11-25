"""Eklentinin benzerlik hesabının Python ikizi.

Chrome eklentisi (`extension/src/core/text.ts` ve `similarity.ts`) iki mesajın benzerliğini
şöyle hesaplıyor:

    1. Metni sadeleştir: Türkçeye uygun küçük harf, noktalamayı at, boşlukları teke indir.
    2. Başına ve sonuna birer boşluk ekleyip 3 karakterlik parçalara (3-gram) böl.
    3. Her parçayı FNV-1a ile 1024 kutudan birine at ve kutuları say.
    4. İki sayım vektörünün kosinüs benzerliğini al.

Bu dosya aynı hesabı Python'da birebir yapar. Böylece eklentinin eşiklerini gerçek
WildChat sohbetleri üzerinde deneyebiliyoruz: Python'da 0,62 çıkan bir benzerlik,
tarayıcıda da 0,62 çıkar. İki tarafın aynı sonucu verdiğini
`tests/fixtures/similarity_parity.json` dosyası üzerinden hem Python hem JavaScript
testleri kontrol eder.
"""

import json
import math
import re
import unicodedata
from pathlib import Path

from kafiai.config import EXT_HASH_DIM, EXT_MIN_NORMALIZED_CHARS, EXT_NGRAM_SIZE

_SPACES = re.compile(r"\s+")


def normalize_text(text):
    """`text.ts` içindeki normalizeText fonksiyonunun aynısı."""
    text = unicodedata.normalize("NFC", text or "")
    text = text.replace("İ", "i").replace("I", "ı").lower()
    # Harf ve rakam dışındaki her karakter (noktalama, emoji) boşluğa çevrilir.
    kept = []
    for ch in text:
        category = unicodedata.category(ch)
        if category[0] in ("L", "N") or ch.isspace():
            kept.append(ch)
        else:
            kept.append(" ")
    return _SPACES.sub(" ", "".join(kept)).strip()


_FOLD = str.maketrans("çğıöşüâîû", "cgiosuaiu")


def fold_turkish(normalized):
    """Türkçe karakterleri düz harfe indirir ("yanlış" -> "yanlis"); `text.ts` foldTurkish ile aynı.

    Birçok kullanıcı Türkçe klavye olmadan yazıyor. Kural listeleri bu yazımı da tanısın diye
    eşleştirmede ikinci biçim olarak kullanılır.
    """
    return normalized.translate(_FOLD)


def with_folded(items):
    """Kural listesine her ifadenin Türkçe karaktersiz hâlini de ekler (sıra korunur, tekrar yok)."""
    return list(dict.fromkeys(list(items) + [fold_turkish(i) for i in items]))


def _fnv1a(chunk):
    """32 bitlik FNV-1a; JavaScript'teki Math.imul ile aynı sonucu verir."""
    value = 0x811C9DC5
    for ch in chunk:
        value ^= ord(ch)
        value = (value * 0x01000193) & 0xFFFFFFFF
    return value


def ngram_vector(normalized, n=EXT_NGRAM_SIZE, dim=EXT_HASH_DIM):
    """Sadeleştirilmiş metni {kutu: sayı} sözlüğüne çevirir."""
    chars = f" {normalized} "
    vector = {}
    for i in range(len(chars) - n + 1):
        bucket = _fnv1a(chars[i:i + n]) % dim
        vector[bucket] = vector.get(bucket, 0) + 1
    return vector


def cosine(a, b):
    dot = sum(value * b.get(key, 0) for key, value in a.items())
    norm_a = sum(v * v for v in a.values())
    norm_b = sum(v * v for v in b.values())
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / math.sqrt(norm_a * norm_b)


def similarity(a, b):
    """İki mesajın benzerliği, 0 ile 1 arası. Mesajlar önce sadeleştirilir."""
    return cosine(ngram_vector(normalize_text(a)), ngram_vector(normalize_text(b)))


_SIGNAL_RULES = json.loads(
    (Path(__file__).resolve().parents[2] / "extension" / "src" / "data" / "signal-rules.json").read_text(encoding="utf-8")
)
_CONTINUE = _SIGNAL_RULES["continue"]


def is_bare_continue(text):
    """Yönsüz devam isteği ("devam", "devam et", "tamam devam", "continue", "go on"); intents.ts ile aynı.

    Yönlü devam ("devam et ama tablo olarak", "continue to day 2") sayılmaz.
    """
    words = set(with_folded(_CONTINUE["words"]))
    allowed = set(with_folded(_CONTINUE["allowed"] + _CONTINUE["words"]))
    normalized = fold_turkish(normalize_text(text))
    tokens = normalized.split()
    if not tokens or len(tokens) > _CONTINUE["max_words"] or not all(t in allowed for t in tokens):
        return False
    padded = f" {normalized} "
    return any(t in words for t in tokens) or any(f" {p} " in padded for p in with_folded(_CONTINUE["phrases"]))


def is_comparable(text):
    """Eklenti 12 karakterden kısa mesajları ("devam et", "evet") ve yönsüz devam isteklerini karşılaştırmaz."""
    return len(normalize_text(text)) >= EXT_MIN_NORMALIZED_CHARS and not is_bare_continue(text)


_REPEAT_RULES = json.loads(
    (Path(__file__).resolve().parents[2] / "extension" / "src" / "data" / "repeat-rules.json").read_text(encoding="utf-8")
)
_FILLER = set(with_folded(_REPEAT_RULES["filler"]))


_CHOICE = set(_REPEAT_RULES["choice_letters"])
_VARIATION = _REPEAT_RULES["variation"]
_VARIATION_WORDS = set(with_folded(_VARIATION["words"]))
_VARIATION_PREFIXES = with_folded(_VARIATION["prefixes"])
_VARIATION_PHRASES = with_folded(_VARIATION["phrases"])


def has_variation_cue(text):
    """Varyasyon işareti: yeni bir örnek isteği ("başka", "sonraki", "bir tane daha", "more", "next")."""
    normalized = fold_turkish(normalize_text(text))  # "baska fikir" de sayılır
    tokens = normalized.split()
    if any(t in _VARIATION_WORDS for t in tokens):
        return True
    if any(t.startswith(p) for t in tokens for p in _VARIATION_PREFIXES):
        return True
    padded = f" {normalized} "
    return any(f" {p} " in padded for p in _VARIATION_PHRASES)


def is_variation(text, score=0.0):
    """Varyasyon isteği: işaret var, güçlü onarım ifadesi yok (repeat-detector.ts, isVariation).

    Orta uzunlukta (16-40 kelime) bir mesajın birebir yeniden gönderimi varyasyon sayılmaz; score önceki mesajlarla en yüksek benzerliktir.
    """
    from kafiai.text import has_strong_repair
    if not has_variation_cue(text) or has_strong_repair(text):
        return False
    words = len(normalize_text(text).split())
    # Çok uzun birebir tekrarlar yeniden kullanılan istem şablonlarıdır; onlar yine varyasyon sayılır.
    return not (score >= _VARIATION["exact_similarity"]
                and _VARIATION["max_exact_words"] < words <= _VARIATION["template_words"])


_TYPO_EDITS = sorted(_REPEAT_RULES["typo"]["edits"])
_TYPO_MIN_CHARS = _REPEAT_RULES["typo"]["min_chars"]
_TYPO_MAX_WORDS = _REPEAT_RULES["typo"]["max_words"]
_PROTECTED = set(_REPEAT_RULES["typo"]["protected"])
_PROTECTED_STEMS = [w for w in _REPEAT_RULES["typo"]["protected"] if len(w) >= 4]
_OPPOSITE = [tuple(pair) for pair in _REPEAT_RULES["typo"]["opposite_suffixes"]]


def _has_digit(token):
    return any(c.isdigit() for c in token)


def _typo_budget(length):
    """Bu uzunluktaki bir kelimede yazım hatası sayılan en çok düzenleme (repeat-rules.json, typo.edits)."""
    budget = 0
    for min_len, edits in _TYPO_EDITS:
        if length >= min_len:
            budget = edits
    return budget


def osa_distance(a, b):
    """Harf düzenleme uzaklığı: ekleme, silme, değiştirme ve yan yana iki harfin yer değiştirmesi
    (Damerau-Levenshtein, optimal string alignment). typo.ts osaDistance ile aynı."""
    n, m = len(a), len(b)
    d = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        d[i][0] = i
    for j in range(m + 1):
        d[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + cost)
            if i > 1 and j > 1 and a[i - 1] == b[j - 2] and a[i - 2] == b[j - 1]:
                d[i][j] = min(d[i][j], d[i - 2][j - 2] + 1)
    return d[n][m]


def _opposite_suffix(a, b):
    """İki kelime aynı gövdeye anlamı tersine çeviren eklerle mi bitiyor? ("kaynakcali"/"kaynakcasiz")"""
    for x, y in _OPPOSITE:
        for p, q in ((x, y), (y, x)):
            if a.endswith(p) and b.endswith(q) and a[: len(a) - len(p)] == b[: len(b) - len(q)]:
                return True
    return False


def _protected(folded):
    """Sayı ve sıra kelimeleri ("ikinci", "üçüncü", "first") yazım hatası diye düzeltilmez."""
    return folded in _PROTECTED or any(folded.startswith(w) for w in _PROTECTED_STEMS)


def typo_match(token, previous_tokens):
    """Kelime, önceki mesajdaki bir kelimenin yazım hatalı biçimi mi? Öyleyse o kelimeyi döner, değilse None.

    Türkçe karaktersiz biçimde karşılaştırılır; en az düzenleme isteyen, eşitlikte ilk geçen kelime seçilir.
    Rakam içeren kelimeler ve yalnızca ek farkı olan kelimeler ("düzelt"/"düzeltme") düzeltilmez.
    """
    if _has_digit(token):
        return None
    folded = fold_turkish(token)
    best = None
    for prev in previous_tokens:
        if _has_digit(prev):
            continue
        fp = fold_turkish(prev)
        if fp == folded:
            distance = 0
        else:
            shorter, longer = sorted((len(fp), len(folded)))
            affix = fp.startswith(folded) or folded.startswith(fp) or fp.endswith(folded) or folded.endswith(fp)
            if affix and longer - shorter >= 2:
                continue  # ek farkı ("düzelt"/"düzeltme", "grammatical"/"ungrammatical"); tek harf fazlası yazım hatası sayılır
            if shorter < _TYPO_MIN_CHARS or _protected(folded) or _protected(fp) or _opposite_suffix(folded, fp):
                continue
            budget = _typo_budget(longer)
            if budget == 0 or longer - shorter > budget:
                continue
            distance = osa_distance(folded, fp)
            if distance > budget:
                continue
        if best is None or distance < best[0]:
            best = (distance, prev)
    return None if best is None else best[1]


def align_typos(new_normalized, previous_normalized):
    """Yeni mesajın yazım hatalı kelimelerini önceki mesajdaki karşılıklarıyla değiştirir (yalnızca karşılaştırma için).

    "anksrabın baskebti neresifir" ile "ankaranın başkenti neresidir" -> "ankaranın başkenti neresidir".
    Girdiler sadeleştirilmiş metindir (normalize_text). typo.ts alignTypos ile aynı.
    """
    new_tokens = new_normalized.split()
    prev_tokens = previous_normalized.split()
    if len(new_tokens) > _TYPO_MAX_WORDS or len(prev_tokens) > _TYPO_MAX_WORDS:
        return new_normalized  # uzun metinlerde düzeltme yapılmaz (repeat-rules.json, typo.max_words)
    prev = list(dict.fromkeys(prev_tokens))
    prev_set = set(prev)
    out = []
    for token in new_tokens:
        if token in prev_set:
            out.append(token)
            continue
        match = typo_match(token, prev)
        out.append(match if match is not None else token)
    return " ".join(out)


def typo_similarity(new_text, previous_text):
    """Yazım hataları düzeltildikten sonraki benzerlik; ham benzerlikten küçük çıkarsa ham benzerlik."""
    new_n, prev_n = normalize_text(new_text), normalize_text(previous_text)
    raw = cosine(ngram_vector(new_n), ngram_vector(prev_n))
    aligned = align_typos(new_n, prev_n)
    return max(raw, cosine(ngram_vector(aligned), ngram_vector(prev_n)))


def new_content(new_text, previous_text):
    """Yeni mesajın öncekinde karşılığı olmayan içerik kelimeleri (repeat-detector.ts ile aynı kural).

    Yazım hatalı kelimeler önce öncekindeki karşılığına çevrilir; yazım hatası yeni içerik sayılmaz.
    """
    stem = _REPEAT_RULES["stem_chars"]
    prev = normalize_text(previous_text).split()
    prev_set = set(prev)
    prev_stems = {t[:stem] for t in prev if len(t) >= stem and not any(c.isdigit() for c in t)}
    words = align_typos(normalize_text(new_text), " ".join(prev)).split()
    short = len(words) <= _REPEAT_RULES["choice_max_words"]
    out = []
    for t in words:
        if short and t in _CHOICE:
            # Kısa mesajda tek başına şık harfi içeriktir: "cevabım B" ile "cevabım C" farklı.
            if t not in prev_set:
                out.append(t)
            continue
        if t in _FILLER or not (len(t) >= _REPEAT_RULES["min_token_chars"] or any(c.isdigit() for c in t)):
            continue
        if t in prev_set:
            continue
        if not any(c.isdigit() for c in t) and len(t) >= stem and t[:stem] in prev_stems:
            continue
        out.append(t)
    return out


def is_repeat(new_text, previous_text, threshold=None):
    """Şerit kuralı: benzerlik eşiği geçiyor, yeni mesaj yeni bir içerik getirmiyor ve bir varyasyon isteği değil."""
    from kafiai.config import EXT_SIMILARITY_THRESHOLD
    limit = EXT_SIMILARITY_THRESHOLD if threshold is None else threshold
    score = typo_similarity(new_text, previous_text)
    return score >= limit and not new_content(new_text, previous_text) and not is_variation(new_text, score)


def holds_send(new_text, previous_text):
    """Gönderimi bekleten şerit: tekrar kuralı geçer ve ya birebir tekrardır ya da güçlü onarım ifadesi taşır.

    Birebir olmayan yeniden yazımlar halka ve çıkış kartı için benzer sayılır ama gönderim bekletilmez
    (repeat-rules.json, hold_note; eklentide RepeatDetector.check().hold).
    """
    from kafiai.text import has_strong_repair
    if not is_repeat(new_text, previous_text):
        return False
    exact = typo_similarity(new_text, previous_text) >= _REPEAT_RULES["hold_exact_similarity"]
    return exact or has_strong_repair(new_text)
