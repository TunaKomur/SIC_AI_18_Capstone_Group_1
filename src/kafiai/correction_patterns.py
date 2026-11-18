"""Aşama 3 ölçümü: ters yönlü düzeltmeler ve kuralın sohbet ortasında yeniden yazılması.

Yalnızca değerlendirmede kullanılır (scripts/evaluate_stage3.py); eklentide karşılığı yok. Bir kural
kabul edilirse sözlük signal-rules.json'a taşınır ve TypeScript ikizi yazılır.

Üç aile:
  A  Ters yönlü düzeltme: aynı eksende yön değiştiren istekler ("kısalt", sonra "uzat"). Tam salınım
     A, karşıtı, yine A. Ayrıca doğrudan geri dönüş isteği ("eski haline getir", "put it back").
  B1 Sözcüksel yeniden yazma: "söylemiştim", "kaç kere", "as I said", "you forgot".
  B2 Yapısal yeniden yazma: kısıt cümlesi ("tablo kullanma", "don't use bullet points") daha önceki
     bir kısıt cümlesine benziyor; kullanıcı aynı kuralı işaret kullanmadan yeniden yazıyor.

Eşleşme sadeleştirilmiş ve Türkçe karakterleri katlanmış metinde yapılır: "söylemiştim" ile
"soylemistim" aynıdır. Sonu "*" ile biten ifade önek sayılır; Türkçe ekler bu yolla yakalanır
("kısalt*": kısaltır mısın, kısaltabilir misin).
"""

import re

from .extension_similarity import fold_turkish, normalize_text, similarity


def fold(text):
    return fold_turkish(normalize_text(text))


def _compile(phrases):
    """İfade listesini tek bir düzenli ifadeye çevirir; kelime sınırına uyar."""
    parts = []
    for p in phrases:
        prefix = p.endswith("*")
        body = re.escape(fold(p.rstrip("*")))
        parts.append(body + (r"\w*" if prefix else ""))
    return re.compile(r"(?:^| )(?:" + "|".join(parts) + r")(?= |$)")


# Eksenler: her eksenin iki kutbu var. "Çok uzun" kısa kutbuna, "lafı uzatma" da kısa kutbuna gider:
# kutup kullanıcının istediği yöndür, şikayet ettiği durum değil.
AXES = {
    "uzunluk": {
        "kisa": ["shorter", "shorten*", "more concise", "be concise", "make it concise", "too long", "too lengthy",
                 "too wordy", "less wordy", "condense*", "cut it down", "trim it", "fewer words", "less detail",
                 "less detailed", "keep it short", "keep it brief", "make it brief", "briefer", "more brief",
                 "reduce the length", "reduce the word count",
                 "kısalt*", "daha kısa", "çok uzun", "fazla uzun", "uzun olmuş", "uzun oldu", "kısa tut", "kısa yaz",
                 "kısaca yaz", "kısaca anlat", "özet geç", "daha az detay", "daha az ayrıntı", "daha öz", "öz yaz",
                 "uzatma", "uzatmadan", "uzatmayın", "uzatmasın", "lafı uzatma", "kelime sayısını azalt*"],
        "uzun": ["longer", "lengthen*", "expand*", "elaborate*", "more detail", "more details", "more detailed",
                 "in more detail", "too short", "too brief", "extend it", "add more", "write more", "make it long",
                 "flesh out", "flesh it out", "increase the length", "increase the word count",
                 "uzat*", "daha uzun", "çok kısa", "fazla kısa", "kısa olmuş", "kısa oldu", "detaylandır*",
                 "detaylı yaz", "daha detaylı", "daha ayrıntılı", "ayrıntılandır*", "genişlet*", "daha fazla detay",
                 "daha fazla ayrıntı", "daha çok yaz", "biraz daha yaz", "uzun yaz", "kelime sayısını artır*"],
    },
    "uslup": {
        "resmi": ["more formal", "too casual", "too informal", "more professional", "less casual", "formal tone",
                  "professional tone",
                  "daha resmi", "resmi yaz", "resmi dil", "resmi bir dil", "çok samimi", "fazla samimi",
                  "daha profesyonel", "profesyonel yaz", "profesyonel bir dil", "daha ciddi", "ciddi bir dil",
                  "resmileştir*"],
        "samimi": ["less formal", "too formal", "more casual", "casual tone", "more friendly", "friendlier",
                   "more conversational", "too professional", "less professional",
                   "daha samimi", "samimi yaz", "samimi bir dil", "çok resmi", "fazla resmi", "daha az resmi",
                   "daha rahat", "günlük dil", "konuşma dili", "daha sıcak"],
    },
    "duzey": {
        "basit": ["simpler", "simplify*", "more simple", "easier to understand", "plain language", "plain english",
                  "layman", "eli5", "for a beginner", "for beginners", "too complex", "too complicated",
                  "too technical", "less technical", "dumb it down",
                  "basitleştir*", "daha basit", "basit anlat", "basit yaz", "basitçe", "sadeleştir*", "daha sade",
                  "daha anlaşılır", "anlaşılır yaz", "çok karmaşık", "fazla karmaşık", "çok teknik", "fazla teknik",
                  "daha az teknik", "teknik olmasın", "yeni başlayan", "çocuğa anlatır gibi"],
        "ileri": ["more technical", "more advanced", "more complex", "more sophisticated", "more in depth", "in depth",
                  "too simple", "too basic", "too simplistic", "go deeper", "more academic", "more rigorous",
                  "daha teknik", "teknik yaz", "daha ileri", "ileri seviye", "daha karmaşık", "daha derin",
                  "derinlemesine", "çok basit", "fazla basit", "çok yüzeysel", "yüzeysel olmuş", "daha akademik",
                  "akademik yaz", "akademik bir dil"],
    },
    "bicim": {
        "liste": ["bullet points", "bullet point", "in bullets", "as a list", "in a list", "use bullets",
                  "numbered list", "as a table", "in a table", "table format", "in table form",
                  "madde madde", "maddeler halinde", "maddele*", "liste halinde", "liste olarak", "tablo olarak",
                  "tablo halinde", "tabloya dök*", "tablo yap", "tablo şeklinde"],
        "duz": ["in paragraph", "in paragraphs", "as a paragraph", "paragraph form", "in prose", "no bullet",
                "no bullets", "without bullet", "without bullets", "no list", "not a list", "without a table",
                "no table", "no tables",
                "paragraf olarak", "paragraf halinde", "paragraf şeklinde", "düz yazı", "düzyazı", "madde kullanma",
                "maddesiz", "madde olmadan", "liste olmadan", "tablo olmadan", "tablo kullanma", "tablo yapma"],
    },
}

# Önekle yakalanıp yanlış kutba düşen biçimler. "kısaltma" hem "kısaltma (abbreviation)" adı hem
# "kısaltma (yapma)" olumsuz emri; anlamı belirsiz olduğu için sayılmaz. "uzatma" ailesi kısa kutbunda.
EXCLUDE = {"kisa": _compile(["kısaltma", "kısaltmalar*", "kısaltmayı"]),
           "uzun": _compile(["uzatma", "uzatmadan", "uzatmayın", "uzatmasın", "expanded", "expanding", "extended"])}

# Doğrudan geri dönüş isteği: kullanıcı modelin önceki hâlini geri istiyor (salınımın en açık izi).
REVERT = ["put it back", "add it back", "bring it back", "bring back", "change it back", "go back to the",
          "revert*", "undo", "previous version", "the original version", "the first version", "the way it was",
          "as it was before", "old version", "previous one was better", "first one was better",
          "old one was better", "original was better",
          "geri al", "geri ekle", "geri koy", "eski haline", "eski hali", "önceki haline", "önceki hali",
          "ilk haline", "ilk hali", "ilk versiyon*", "önceki versiyon*", "önceki sürüm*", "eski versiyon*",
          "eskisi gibi", "önceki gibi", "ilk yazdığın", "eskisi daha iyi", "öncekisi daha iyi",
          "önceki daha iyiydi", "ilki daha iyi"]

# B1: kuralı yeniden hatırlatan işaretler. Güçlü işaretler kendi başına yeniden yazmadır; geniş işaretler
# anlatı içinde de geçebilir ("ona dedim ki", "I said hello"), ayrı sayılır.
RESTATE_STRONG = ["i told you", "i already told you", "told you to", "i ve told you", "i have told you",
                  "as i said", "like i said", "i already said", "i ve said", "as i mentioned", "i already mentioned",
                  "i ve mentioned", "as i asked", "i already asked", "i ve asked", "you forgot", "did you forget",
                  "you ignored", "you are ignoring", "you keep ignoring", "you didn t follow", "you did not follow",
                  "you are not following", "follow my instruction*", "follow the instruction*",
                  "read my instruction*", "read the instruction*", "i repeat", "how many times",
                  "söylemiştim", "söyledim ya", "dedim ya", "demiştim", "sana söyledim", "daha önce söyledim",
                  "daha önce de söyledim", "zaten söyledim", "zaten dedim", "kaç kere", "kaç kez", "kaçıncı kez",
                  "kaç defa", "tekrar ediyorum", "tekrarlıyorum", "tekrar yazıyorum", "bir daha yazıyorum", "yine söylüyorum", "bir daha söylüyorum",
                  "tekrar söylüyorum", "unuttun", "dediğim gibi", "söylediğim gibi", "belirttiğim gibi",
                  "bahsettiğim gibi", "yazdığım gibi", "talimatlarıma uy*", "talimata uy*", "kurala uy*",
                  "kurallara uy*", "dememiş miydim", "söylememiş miydim", "istememiş miydim", "istemiştim",
                  "belirtmiştim", "yazmıştım", "hatırlatırım", "hatırlatayım", "hatırlatıyorum", "görmezden",
                  "dikkate almadın", "dinlemiyorsun", "uymadın", "uymuyorsun"]
RESTATE_BROAD = ["i said", "i asked you to", "i asked for", "i specifically", "remember", "once again",
                 "as instructed", "i mentioned",
                 "dedim", "söyledim", "unutma", "hatırla", "istediğim gibi", "dediğimi yap", "sadece dediğimi"]

# B2: kısıt cümlesi işaretleri. Türkçe olumsuz emir ekleri (-masın, -mayın, -mamalı, -madan) ayrıca
# yakalanır; tek tek fiil yazmak yerine ek bakılır.
CONSTRAINT_CUES = ["don t", "dont", "do not", "never", "always", "only", "must", "mustn t", "should not",
                   "shouldn t", "without", "avoid", "make sure", "no more than", "at most", "at least", "exactly",
                   "asla", "hiçbir zaman", "her zaman", "sadece", "yalnızca", "mutlaka", "kesinlikle", "olmasın",
                   "olmadan", "en fazla", "en az", "kullanma", "yazma", "ekleme", "koyma", "yapma", "verme",
                   "değiştirme", "çevirme"]
_NEG_SUFFIX = re.compile(r"(?:^| )\w{3,}(?:masin|mesin|mayin|meyin|mamali|memeli|madan|meden)(?= |$)")

_AXES_RX = {axis: {pole: _compile(ph) for pole, ph in poles.items()} for axis, poles in AXES.items()}
_REVERT_RX = _compile(REVERT)
_STRONG_RX = _compile(RESTATE_STRONG)
_BROAD_RX = _compile(RESTATE_BROAD)
_CUE_RX = _compile(CONSTRAINT_CUES)
_CLAUSE_SPLIT = re.compile(r"[.!?;\n]+")

# Uzun mesajlarda (yapıştırılmış metin) eşleşme yalnızca başta ve sonda aranır; talimat orada durur.
WHOLE_MAX = 300
EDGE = 150
MAX_CHARS = 4000


def _instruction_text(text):
    folded = fold(text)
    if len(folded) <= WHOLE_MAX:
        return folded
    return folded[:EDGE] + " | " + folded[-EDGE:]


def poles(text):
    """Mesajın istediği yönler: {eksen: kutup}. Bir eksende iki kutup birden geçiyorsa o eksen sayılmaz
    ("kısa değil uzun olsun" gibi cümleler belirsiz)."""
    t = _instruction_text(text)
    found = {}
    for axis, rx in _AXES_RX.items():
        hits = set()
        for pole, prx in rx.items():
            # Önekin yanlış yakaladığı biçimler o kutupta silinir ("uzatma" uzun kutbuna, "kısaltma" kısa kutbuna girmez).
            source = EXCLUDE[pole].sub(" ", t) if pole in EXCLUDE else t
            if prx.search(source):
                hits.add(pole)
        if len(hits) == 1:
            found[axis] = hits.pop()
    return found


def is_revert(text):
    return bool(_REVERT_RX.search(_instruction_text(text)))


def restate_marker(text):
    """'guclu', 'genis' ya da None."""
    t = _instruction_text(text)
    if _STRONG_RX.search(t):
        return "guclu"
    if _BROAD_RX.search(t):
        return "genis"
    return None


def constraint_clauses(text, max_clauses=30):
    """Kısıt taşıyan cümleler (4 ile 40 kelime arası)."""
    out = []
    for clause in _CLAUSE_SPLIT.split((text or "")[:MAX_CHARS]):
        f = fold(clause)
        n = len(f.split())
        if 4 <= n <= 40 and (_CUE_RX.search(f) or _NEG_SUFFIX.search(f)):
            out.append(f)
            if len(out) >= max_clauses:
                break
    return out


def best_clause_similarity(clauses, earlier):
    best = 0.0
    for c in clauses:
        for e in earlier:
            best = max(best, similarity(c, e))
    return best


def detect(msgs, segment_starts=None, thresholds=(0.6, 0.7, 0.8)):
    """Bir sohbetin kullanıcı mesajlarında Aşama 3 olaylarını bulur.

    Dönüş: {aile: set(tur)} ve her turun B2 benzerliği. İlk mesaj (t=0) istektir, düzeltme sayılmaz;
    ama kısıtları B2 için hafızaya girer. segment_starts verilirse ters yön yalnızca aynı konu bölümünde aranır.
    """
    ev = {k: set() for k in ("A_donus", "A_salinim", "A_geri", "B1_guclu", "B1_genis")}
    for th in thresholds:
        ev[f"B2_{int(th * 100)}"] = set()
    history = {}  # eksen -> [(tur, kutup)]
    earlier_clauses = []
    b2_sim = {}
    for t, text in enumerate(msgs):
        text = text or ""
        clauses = constraint_clauses(text)
        if t > 0:
            seg = segment_starts[t] if segment_starts else 0
            for axis, pole in poles(text).items():
                past = [p for (tt, p) in history.get(axis, []) if tt >= seg]
                if past and past[-1] != pole:
                    ev["A_donus"].add(t)
                    if len(past) >= 2 and past[-2] == pole:
                        ev["A_salinim"].add(t)
                history.setdefault(axis, []).append((t, pole))
            if is_revert(text):
                ev["A_geri"].add(t)
            marker = restate_marker(text)
            if marker == "guclu":
                ev["B1_guclu"].add(t)
            elif marker == "genis":
                ev["B1_genis"].add(t)
            if clauses and earlier_clauses:
                s = best_clause_similarity(clauses, earlier_clauses)
                b2_sim[t] = s
                for th in thresholds:
                    if s >= th:
                        ev[f"B2_{int(th * 100)}"].add(t)
        earlier_clauses.extend(clauses)
    return ev, b2_sim


_PATTERN_RX = [(f"{group}:{p}", _compile([p])) for group, phrases in
               [("geri", REVERT), ("b1_guclu", RESTATE_STRONG), ("b1_genis", RESTATE_BROAD)]
               + [(f"{a}_{pole}", ph) for a, poles_ in AXES.items() for pole, ph in poles_.items()]
               for p in phrases]


def matched_patterns(text):
    """Bir mesajda eşleşen sözlük öğelerinin adları (yalnızca sayım için; metin saklanmaz)."""
    t = _instruction_text(text)
    return [name for name, rx in _PATTERN_RX if rx.search(t)]
