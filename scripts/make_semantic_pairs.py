"""Türkçe anlam test setini üretir: tests/fixtures/semantic_pairs_tr.json.

Her grup bir temel istekten, aynı isteğin başka söylenişlerinden ve "aynı kalıp, farklı istek"
örneklerinden oluşur. Yazım hatalı biçimler sabit tohumla, Türkçe Q klavye komşuluğuna göre
üretilir (komşu tuş, harf düşmesi, yer değiştirme, çift harf) ve Türkçe karaktersiz yazım ayrıca
eklenir. Tüm cümleler uydurmadır; gerçek bir kullanıcıdan gelmez.

Gruplar sırayla iki yarıya ayrılır: "secim" (kural ve eşik seçimi) ve "rapor" (yalnızca sonuç
bildirmek için). Bir grubun tüm çiftleri aynı yarıdadır.

Çalıştırma: python scripts/make_semantic_pairs.py
"""

import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "tests" / "fixtures" / "semantic_pairs_tr.json"

# (temel istek, [aynı istek, başka söyleniş], [(farklı istek, tür)])
# Türler: varlik (özel ad, dil, nesne değişti), seri (sayı ya da sıra değişti), zit (ters istek), konu (başka konu)
GROUPS = [
    ("ankaranın başkenti neresidir?", ["ankaranın başkenti nedir", "ankaranın başkenti hangi şehir"],
     [("ankaranın nüfusu kaç", "varlik"), ("python ile dosya nasıl okunur", "konu")]),
    ("türkiyenin başkenti neresi", ["türkiyenin başkenti hangi şehir", "türkiye'nin başkenti nedir"],
     [("amerikanın başkenti neresi", "varlik"), ("türkiyenin en kalabalık şehri neresi", "varlik")]),
    ("python ile dosya nasıl okunur", ["python'da bir dosyayı nasıl okurum", "pythonda dosya okuma nasıl yapılır"],
     [("python ile dosya nasıl yazılır", "zit"), ("java ile dosya nasıl okunur", "varlik")]),
    ("bu kodu düzelt çalışmıyor", ["kod hala çalışmıyor düzeltsene", "şu kodu onar, olmuyor"],
     [("bu koda yorum satırları ekle", "konu"), ("bu kodu javascripte çevir", "varlik")]),
    ("metni daha kısa yaz", ["bunu kısalt, çok uzun olmuş", "metni kısaltır mısın"],
     [("metni daha uzun yaz", "zit"), ("metni ingilizceye çevir", "konu")]),
    ("bana fotosentezi anlat", ["fotosentez nedir açıklar mısın", "fotosentez nasıl gerçekleşir anlatır mısın"],
     [("bana mitoz bölünmeyi anlat", "varlik"), ("fotosentez hakkında 5 soruluk test hazırla", "konu")]),
    ("bu hatanın sebebi ne", ["neden bu hatayı alıyorum", "bu hata neden çıkıyor"],
     [("bu hatayı nasıl düzeltirim", "konu"), ("bu uyarının sebebi ne", "varlik")]),
    ("excel'de iki sütunu nasıl birleştiririm", ["excelde iki kolonu birleştirmenin yolu ne", "excel iki sütunu tek sütunda birleştirme"],
     [("excel'de iki sütunu nasıl karşılaştırırım", "konu"), ("google sheets'te iki sütunu nasıl birleştiririm", "varlik")]),
    ("tabloyu markdown formatında ver", ["bunu markdown tablo olarak yaz", "tabloyu markdown olarak gösterir misin"],
     [("tabloyu csv formatında ver", "varlik"), ("tabloyu tarihe göre sırala", "konu")]),
    ("özgeçmişimi daha profesyonel yap", ["cv'mi daha profesyonel hale getir", "özgeçmişimi daha profesyonel bir dille yeniden yaz"],
     [("özgeçmişimi ingilizceye çevir", "konu"), ("ön yazımı daha profesyonel yap", "varlik")]),
    ("e-postayı daha resmi yaz", ["maili daha resmi bir dille yaz", "bu e-postayı resmi hale getir"],
     [("e-postayı daha samimi yaz", "zit"), ("e-postaya bir kapanış cümlesi ekle", "konu")]),
    ("bu cümleyi ingilizceye çevir", ["bu cümlenin ingilizcesi ne", "bunu ingilizce yazar mısın"],
     [("bu cümleyi almancaya çevir", "varlik"), ("bu cümledeki yazım hatalarını düzelt", "konu")]),
    ("listeyi alfabetik sırala", ["listeyi a'dan z'ye sırala", "bu listeyi alfabetik sıraya koy"],
     [("listeyi tersten sırala", "zit"), ("listedeki tekrar edenleri sil", "konu")]),
    ("istanbul için hava durumu", ["istanbulda hava nasıl", "istanbul hava durumu ne"],
     [("izmir için hava durumu", "varlik"), ("istanbul için gezilecek yerler", "konu")]),
    ("3x+5=20 denklemini çöz", ["3x+5=20 denkleminde x kaç", "3x+5=20 ise x nedir"],
     [("4x-2=10 denklemini çöz", "seri"), ("3x+5=20 denklemini grafikle göster", "konu")]),
    ("ilk paragrafı özetle", ["ilk paragrafın özetini çıkar", "birinci paragrafı kısaca özetle"],
     [("ikinci paragrafı özetle", "seri"), ("ilk paragrafı ingilizceye çevir", "konu")]),
    ("react'te state nasıl güncellenir", ["reactta state güncelleme nasıl yapılır", "react state'i nasıl değiştiririm"],
     [("vue'da state nasıl güncellenir", "varlik"), ("react'te nasıl api isteği atılır", "konu")]),
    ("sql sorgusunda join nasıl kullanılır", ["sql'de join kullanımını anlat", "join ifadesi sql'de nasıl yazılır"],
     [("sql sorgusunda group by nasıl kullanılır", "varlik"), ("mongodb'de join nasıl yapılır", "varlik")]),
    ("1. soruyu çöz", ["birinci soruyu çözer misin", "1. sorunun çözümünü yaz"],
     [("2. soruyu çöz", "seri"), ("1. soruyu açıkla ama çözme", "zit")]),
    ("bana bir şiir yaz", ["bir şiir yazar mısın", "benim için bir şiir yaz"],
     [("bana bir hikaye yaz", "varlik"), ("bu şiiri analiz et", "konu")]),
    ("fransanın nüfusu kaç", ["fransa'nın nüfusu ne kadar", "fransada kaç kişi yaşıyor"],
     [("almanyanın nüfusu kaç", "varlik"), ("fransanın yüzölçümü kaç", "varlik")]),
    ("bu fonksiyonu daha hızlı hale getir", ["bu fonksiyonu hızlandır", "bu fonksiyonun performansını iyileştir"],
     [("bu fonksiyona test yaz", "konu"), ("bu fonksiyonu daha okunur hale getir", "varlik")]),
    ("makaleyi 200 kelimeyle özetle", ["makalenin 200 kelimelik özetini yaz", "makaleyi 200 kelimede özetler misin"],
     [("makaleyi 500 kelimeyle özetle", "seri"), ("makaledeki kaynakları listele", "konu")]),
    ("ingilizce bir e-posta taslağı yaz", ["ingilizce mail taslağı hazırla", "ingilizce bir e-posta taslağı hazırlar mısın"],
     [("almanca bir e-posta taslağı yaz", "varlik"), ("ingilizce bir özgeçmiş taslağı yaz", "varlik")]),
    ("türev alma kurallarını anlat", ["türev kuralları nelerdir", "türev nasıl alınır kurallarıyla anlat"],
     [("integral alma kurallarını anlat", "varlik"), ("türev ile ilgili 10 soru hazırla", "konu")]),
    ("bu ödevi kaynakçalı yaz", ["bu ödevi kaynakça ekleyerek yaz", "ödevi kaynaklarıyla birlikte yaz"],
     [("bu ödevi kaynakçasız yaz", "zit"), ("bu ödevin sunumunu hazırla", "konu")]),
    ("docker container nasıl durdurulur", ["docker'da container durdurma komutu ne", "çalışan docker container'ı nasıl durdururum"],
     [("docker container nasıl başlatılır", "zit"), ("docker image nasıl silinir", "varlik")]),
    ("git'te son commit nasıl geri alınır", ["son commit'i nasıl geri alırım", "git son commit'i geri alma komutu"],
     [("git'te yeni branch nasıl açılır", "konu"), ("git'te son commit mesajı nasıl değiştirilir", "varlik")]),
    ("bu paragrafı daha akıcı yaz", ["paragrafı daha akıcı hale getir", "bu paragrafın akışını düzelt"],
     [("bu paragrafı daha resmi yaz", "varlik"), ("bu paragrafa bir başlık öner", "konu")]),
    ("haftalık çalışma planı hazırla", ["bana haftalık bir çalışma programı yap", "bir haftalık ders çalışma planı oluştur"],
     [("aylık çalışma planı hazırla", "seri"), ("haftalık yemek planı hazırla", "varlik")]),
    ("cevabı tablo halinde ver", ["cevabını tablo olarak yaz", "bunu tabloya dök"],
     [("cevabı madde madde ver", "varlik"), ("cevabı kısalt", "konu")]),
    ("bu kodun ne yaptığını açıkla", ["bu kod ne işe yarıyor", "bu kodu satır satır açıklar mısın"],
     [("bu kodun hatasını bul", "konu"), ("bu kodun karmaşıklığını hesapla", "konu")]),
    ("kahve mi çay mı daha sağlıklı", ["çay mı kahve mi daha sağlıklı", "sağlık açısından kahve mi çay mı"],
     [("kahve mi çay mı daha ucuz", "varlik"), ("kahve nasıl demlenir", "konu")]),
    ("ikinci dünya savaşının sebeplerini yaz", ["2. dünya savaşı neden çıktı", "ikinci dünya savaşının nedenleri neler"],
     [("birinci dünya savaşının sebeplerini yaz", "seri"), ("ikinci dünya savaşının sonuçlarını yaz", "zit")]),
    ("bu metindeki yazım hatalarını düzelt", ["metindeki yazım yanlışlarını düzelt", "bu yazıdaki imla hatalarını düzeltir misin"],
     [("bu metni özetle", "konu"), ("bu metindeki anlatım bozukluklarını bul", "varlik")]),
    ("javascriptte dizi nasıl sıralanır", ["js'de array sıralama nasıl yapılır", "javascript dizisini nasıl sıralarım"],
     [("javascriptte dizi nasıl ters çevrilir", "zit"), ("pythonda dizi nasıl sıralanır", "varlik")]),
    ("sunum için 10 slayt başlığı öner", ["sunumum için 10 tane slayt başlığı ver", "10 slaytlık sunuma başlık öner"],
     [("sunum için 5 slayt başlığı öner", "seri"), ("sunum için konuşma metni yaz", "konu")]),
    ("bu tarifi 4 kişilik yap", ["tarifi 4 kişiye göre ayarla", "bu tarifi dört kişilik hale getir"],
     [("bu tarifi 8 kişilik yap", "seri"), ("bu tarifi vegan yap", "varlik")]),
    ("mülakatta sorulabilecek soruları listele", ["iş görüşmesinde hangi sorular sorulur", "mülakat soruları neler olabilir"],
     [("mülakatta sorulacak sorulara cevap yaz", "konu"), ("mülakatta ne giymeliyim", "konu")]),
    ("bu cümlenin öznesini bul", ["bu cümlede özne hangisi", "cümlenin öznesi ne"],
     [("bu cümlenin yüklemini bul", "varlik"), ("bu cümleyi ögelerine ayır", "konu")]),
]

TR_KEYBOARD_ROWS = ["qwertyuıopğü", "asdfghjklşi", "zxcvbnmöç"]


def neighbours():
    out = {}
    for r, row in enumerate(TR_KEYBOARD_ROWS):
        for c, ch in enumerate(row):
            near = set()
            for dr in (-1, 0, 1):
                rr = r + dr
                if 0 <= rr < len(TR_KEYBOARD_ROWS):
                    for dc in (-1, 0, 1):
                        cc = c + dc
                        if (dr, dc) != (0, 0) and 0 <= cc < len(TR_KEYBOARD_ROWS[rr]):
                            near.add(TR_KEYBOARD_ROWS[rr][cc])
            out[ch] = sorted(near)
    return out


NEAR = neighbours()
FOLD = str.maketrans("çğıöşü", "cgiosu")


def typo_word(word, rng):
    letters = [i for i, ch in enumerate(word) if ch.isalpha()]
    if len(letters) < 4:
        return word
    i = rng.choice(letters[1:])  # ilk harf çoğu zaman doğru yazılır
    kind = rng.choice(["komsu", "dusme", "yer", "cift"])
    if kind == "komsu" and word[i] in NEAR:
        return word[:i] + rng.choice(NEAR[word[i]]) + word[i + 1:]
    if kind == "dusme":
        return word[:i] + word[i + 1:]
    if kind == "yer" and i + 1 < len(word) and word[i + 1].isalpha():
        return word[:i] + word[i + 1] + word[i] + word[i + 2:]
    return word[:i] + word[i] + word[i:]


def typo_sentence(text, rng, rate):
    words = text.split(" ")
    out = [typo_word(w, rng) if rng.random() < rate else w for w in words]
    if out == words:  # en az bir hata olsun
        j = max(range(len(words)), key=lambda k: len(words[k]))
        out[j] = typo_word(words[j], rng)
    return " ".join(out)


def main():
    rng = random.Random(20261125)
    pairs = []
    for g, (base, paras, negs) in enumerate(GROUPS):
        split = "secim" if g % 2 == 0 else "rapor"
        def add(new, kind, same):
            pairs.append({"grup": g, "split": split, "tur": kind, "ayni": same, "onceki": base, "yeni": new})
        add(typo_sentence(base, rng, 0.35), "yazim_hafif", True)
        add(typo_sentence(base, rng, 0.8), "yazim_agir", True)
        add(base.translate(FOLD), "turkce_harfsiz", True)
        for p in paras:
            add(p, "baska_soylenis", True)
        add(typo_sentence(paras[0], rng, 0.35), "baska_soylenis_yazim", True)
        for text, kind in negs:
            add(text, kind, False)
            add(typo_sentence(text, rng, 0.35), f"{kind}_yazim", False)
    # Kullanıcının kendi örneği (mentor görüşmesi): ağır yazım hatası.
    pairs.append({"grup": 0, "split": "secim", "tur": "yazim_agir", "ayni": True,
                  "onceki": "ankaranın başkenti neresidir?", "yeni": "anksrabın baskebti neresifir"})
    note = (__doc__ or "").strip().splitlines()[0]
    OUT.write_text(json.dumps({"note": note, "pairs": pairs}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    from collections import Counter
    print(len(pairs), "çift", Counter(p["tur"] for p in pairs))


if __name__ == "__main__":
    main()
