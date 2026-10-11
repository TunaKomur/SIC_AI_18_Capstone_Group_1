# Bölüm 1: Literatür Taraması

**Proje:** Üretken yapay zeka kullanımında aşırı güven ve verimsiz kullanım döngülerinin tespiti
**Grup:** SIC AI 18 Capstone, Grup 1
**Hedef grup:** Günlük, ders ve iş süreçlerinde üretken yapay zeka kullanan 18 ile 30 yaş arası yetişkinler (üniversite öğrencileri ve genç profesyoneller)

---

## 1. Giriş

### 1.1 Problem tanımı

Üretken yapay zeka araçları (ChatGPT, Gemini, Claude, Copilot gibi Large Language Model tabanlı sohbet asistanları) kısa sürede ders çalışmanın, ödev hazırlamanın ve iş yapmanın sıradan bir parçası haline geldi. Bu araçların verimliliği artırdığı pek çok çalışmada gösterildi. Ancak kullanım yaygınlaştıkça yeni bir davranış örüntüsü de görünür olmaya başladı: aynı talebi farklı kelimelerle tekrar tekrar sormak, daha iyi bir cevap gelir umuduyla yanıtı yeniden ürettirmek, düşünme ve karar verme işini giderek tamamen araca bırakmak.

Projemiz bu örüntüyü **problemli üretken yapay zeka kullanımı** olarak ele alıyor. Odak noktamız iki bileşenden oluşuyor:

1. **Aşırı güven ve bilişsel yük aktarımı (over-reliance, cognitive offloading):** Kullanıcının kendi düşünme çabasını azaltıp üretimi ve kararı yapay zekaya devretmesi.
2. **Verimsiz kullanım döngüleri:** Oturumun uzadığı ama somut bir sonuca ulaşmadığı, kompulsif tekrar içeren etkileşimler.

Hedef grubumuz, bu araçları en yoğun kullanan kesim olan 18 ile 30 yaş arası üniversite öğrencileri ve genç profesyonellerdir. Ürün ileride yapay zekayı günlük rutinleri için kullanan tüm yetişkinlere genişletilebilir; ancak bu çalışmada literatürün de en çok yoğunlaştığı bu gruba odaklanıyoruz.

### 1.2 Problemin önemi

Bu konu yalnızca bir verimlilik meselesi değildir. İncelediğimiz çalışmalar üretken yapay zekaya aşırı güvenin dört alanda iz bıraktığını gösteriyor:

1. **Eleştirel düşünme:** Yapay zekaya duyulan güven arttıkça kişinin kendi sorgulama çabası azalıyor (Gerlich, 2025; Lee vd., 2025).
2. **Öğrenme ve akademik performans:** Sınırsız erişim kısa vadede başarıyı artırırken araç ortadan kalktığında performansı düşürebiliyor (Bastani vd., 2025); yoğun kullanım erteleme ve hafıza kaybı bildirimleriyle ilişkili bulunuyor (Abbas vd., 2024).
3. **Duygusal iyi oluş:** Çok yoğun kullanım yalnızlık ve duygusal bağımlılık göstergeleriyle birlikte görülüyor (Fang vd., 2025; Phang vd., 2025).
4. **Karar verme özerkliği:** Öğrencilerin karar verme ve analitik akıl yürütme becerilerinin zayıfladığına dair bulgular birikiyor (Zhai vd., 2024).



### 1.3 Neden önce literatür taraması?

Çözüm tasarlamadan önce literatüre bakmamız üç nedenle gerekli:

1. **Kavram tartışmalı.** "Yapay zeka bağımlılığı" henüz WHO ICD-11'deki oyun oynama bozukluğu (gaming disorder) gibi tanımlanmış bir klinik tanı değildir. Bazı araştırmacılar bu kavramın erken ve aşırı genelleştirilmiş olduğunu savunuyor (Ciudad-Fernández vd., 2025). Projenin hangi dili kullanacağı bu tartışmaya göre belirlenmeli.
2. **Ölçüm yöntemleri farklı.** Ölçeklere, deneylere ve sohbet loglarına dayanan yaklaşımların güçlü ve zayıf yanlarını bilmek, kendi veri ve model tercihlerimizi gerekçelendirmemizi sağlar.
3. **Müdahale tasarımı kanıta dayanmalı.** Hangi tür müdahalenin işe yaradığı (yasaklama, süre sınırı, yönlendirme) daha önce test edilmiş; ürünümüzün bu birikimin üzerine kurulması gerekiyor.

---



## 2. Düzen

Literatürü dört tema altında topladık. Bu düzen, problemi tanımlamaktan çözüme doğru ilerleyen bir mantık izliyor:


| Tema                                           | Soru                                                         | Çalışma sayısı |
| ---------------------------------------------- | ------------------------------------------------------------ | -------------- |
| Tema 1: Tanımlar, kuramsal çerçeve ve ölçekler | Problemli yapay zeka kullanımı nedir, nasıl ölçülür?         | 4              |
| Tema 2: Bilişsel ve psikososyal sonuçlar       | Aşırı güvenin bireye etkileri nelerdir?                      | 6              |
| Tema 3: Müdahale yaklaşımları                  | Hangi müdahaleler işe yarıyor?                               | 2              |
| Tema 4: Veriye dayalı tespit                   | Problemli kullanım davranış verisinden tespit edilebilir mi? | 2              |


---



## 3. Özet ve Sentez



### 3.1 Tema 1: Tanımlar, kuramsal çerçeve ve ölçekler

**Griffiths (2005): Bağımlılığın bileşenler modeli**

- **Amaç:** Davranışsal ve madde bağımlılıkları için ortak bir kuramsal çerçeve önermek.
- **Yöntem:** Kuramsal model.
- **Bulgular:** Bir davranışın bağımlılık sayılabilmesi için altı bileşen önerir: belirginlik (salience), duygu durum değişimi, tolerans, yoksunluk belirtileri, çatışma ve nüks.
- **Katkı:** Problemli ChatGPT kullanımı ölçeklerinin önemli bir kısmı bu modelden türetilmiştir. Projemizin "döngü" kavramı, modeldeki tolerans ve nüks bileşenlerinin sohbet içindeki karşılığı olarak okunabilir.

**Morales-García vd. (2024): Yapay Zekaya Bağımlılık Ölçeği (DIA)**

- **Amaç:** Üniversite öğrencilerinde yapay zekaya bağımlılığı ölçen kısa ve geçerli bir ölçek geliştirmek.
- **Örneklem:** Peru'da 528 üniversite öğrencisi (18 ile 37 yaş).
- **Yöntem:** Exploratory Factor Analysis (n = 226) ve Confirmatory Factor Analysis (n = 302), cinsiyete göre ölçme değişmezliği testi.
- **Bulgular:** 5 maddelik tek boyutlu yapı; güvenirlik α = 0.87, ω = 0.87; model uyumu yüksek (CFI = 0.99, RMSEA = 0.05).
- **Katkı:** Hedef grubumuzla birebir örtüşen bir öğrenci örneklemi. Ancak tek ülke, kolay ulaşılabilir örneklem ve kesitsel tasarım sınırlılıkları var.

**Maral vd. (2026): Problemli ChatGPT Kullanımı Ölçeği (Türkiye)**

- **Amaç:** Problemli ChatGPT kullanımını ölçen bir ölçek geliştirmek ve iyi oluşla ilişkisini incelemek.
- **Örneklem:** Türkiye'den iki çalışma; 391 katılımcı (ort. yaş 30.89) ve 473 katılımcı (ort. yaş 28.25).
- **Yöntem:** Doğrulayıcı faktör analizi, Item Response Theory, ölçme değişmezliği, aracılık analizi.
- **Bulgular:** 9 maddelik tek boyutlu yapı. Problemli ChatGPT kullanımı internet bağımlılığı ve oyun bozukluğuyla pozitif, sorumluluk bilinciyle negatif ilişkili. Problemli kullanım ile iyi oluş arasındaki ilişkide psikolojik sıkıntı ve öz denetim aracı rol oynuyor.
- **Katkı:** Türkiye örneklemi ve hedef grubumuzun yaş aralığına yakın katılımcılarla projemiz için en doğrudan referans. İleride kullanıcı çalışması yaparsak bu ölçek doğrulama aracı olabilir.

**Ciudad-Fernández vd. (2025): "İnsanlar AIholic olmuyor"**

- **Amaç:** "ChatGPT bağımlılığı" kavramının bilimsel temelini sorgulamak.
- **Yöntem:** Eleştirel yorum (commentary).
- **Bulgular:** Madde bağımlılığı kriterlerinin yeni bir teknolojiye doğrudan uygulanmasının sıradan davranışları gereğinden fazla patolojikleştirme riski taşıdığını savunur.
- **Katkı:** Literatürdeki en önemli karşı görüş. Projemizin dilini belirliyor: kullanıcıya "bağımlısın" demek yerine kullanım biçimindeki verimsiz örüntüleri görünür kılmak.



### 3.2 Tema 2: Bilişsel ve psikososyal sonuçlar

**Lee vd. (2025): Üretken yapay zeka ve eleştirel düşünme**

- **Amaç:** Bilgi çalışanlarının üretken yapay zeka kullanırken eleştirel düşünmeyi ne zaman ve nasıl uyguladığını anlamak.
- **Örneklem:** 319 bilgi çalışanı; 936 gerçek kullanım örneği.
- **Yöntem:** Anket, nicel ve nitel analiz (CHI 2025, Microsoft Research ve Carnegie Mellon University).
- **Bulgular:** Yapay zekaya güven arttıkça eleştirel düşünme çabası azalıyor; kişinin kendine güveni arttıkça eleştirel düşünme artıyor.
- **Katkı:** Hedef grubumuzun genç profesyoneller ayağını doğrudan temsil ediyor.

**Gerlich (2025): Bilişsel yük aktarımı ve eleştirel düşünme**

- **Amaç:** Yapay zeka araçlarının kullanımı ile eleştirel düşünme arasındaki ilişkiyi ve bilişsel yük aktarımının aracı rolünü incelemek.
- **Örneklem:** İngiltere'den 666 katılımcı; 50 katılımcıyla ek derinlemesine görüşme.
- **Yöntem:** Anket, ANOVA, korelasyon, regresyon, random forest ve tematik analiz.
- **Bulgular:** Yapay zeka kullanımı ile eleştirel düşünme arasında güçlü negatif ilişki (r = −0.68); bilişsel yük aktarımı ile eleştirel düşünme arasında r = −0.75. Etki en çok **17 ile 25 yaş** grubunda görülüyor; eğitim düzeyi koruyucu.
- **Katkı:** Hedef yaş grubumuzun en riskli grup olduğunu gösteriyor. Sınırlılık: öz bildirim, kesitsel tasarım, tek ülke.

**Abbas vd. (2024): Üniversite öğrencilerinde üretken yapay zeka kullanımının nedenleri ve sonuçları**

- **Amaç:** Öğrencileri ChatGPT kullanmaya iten etkenleri ve kullanımın akademik sonuçlarını incelemek.
- **Örneklem:** Pakistan'dan 494 üniversite öğrencisi.
- **Yöntem:** Ölçek geliştirme ve üç dalgalı, zaman gecikmeli anket.
- **Bulgular:** Akademik iş yükü ve zaman baskısı kullanımı artırıyor. Yoğun kullanım erteleme, hafıza kaybı bildirimi ve düşük not ortalamasıyla ilişkili.
- **Katkı:** Kullanımın bir baskı ile başa çıkma yolu olarak ortaya çıktığını gösteriyor; müdahalenin yasaklamak yerine doğru anda destek vermesi gerektiği fikrini destekliyor. Sınırlılık: yazarlar ilişkinin iki yönlü olabileceğini belirtiyor.

**Zhai vd. (2024): Yapay zeka sohbet sistemlerine aşırı güven (sistematik derleme)**

- **Amaç:** Öğrencilerin yapay zeka sohbet sistemlerine aşırı güveninin karar verme, eleştirel düşünme ve analitik akıl yürütmeye etkisini derlemek.
- **Yöntem:** PRISMA tabanlı sistematik derleme; 2017 ile 2023 arası 14 çalışma.
- **Bulgular:** Aşırı güven bağımsız karar verme ve eleştirel düşünmeyi zayıflatıyor; kullanıcılar hatalı veya yanlı çıktıları (hallucination) sorgulamadan kabul edebiliyor.
- **Katkı:** Tema 2'deki bireysel bulguları bir arada değerlendiriyor. Sınırlılık: az sayıda çalışma ve yalnızca İngilizce kaynaklar.

**Fang vd. (2025): Uzun süreli sohbet botu kullanımının psikososyal etkileri**

- **Amaç:** Sohbet botu kullanım biçiminin yalnızlık, sosyalleşme, duygusal bağımlılık ve problemli kullanıma etkisini incelemek.
- **Örneklem:** 981 katılımcı; 300.000'den fazla mesaj.
- **Yöntem:** 4 haftalık randomize kontrollü deney (MIT Media Lab ve OpenAI).
- **Bulgular:** Deney koşulları tek başına anlamlı fark yaratmadı; ancak gönüllü olarak daha çok kullananlarda yalnızlık, duygusal bağımlılık ve problemli kullanım göstergeleri daha yüksekti. Yapay zekaya güven ve sosyal çekim duygusal bağımlılıkla ilişkiliydi.
- **Katkı:** Riskin kullanım süresinden çok kullanım biçimi ve yoğunluğuyla ilgili olduğunu gösteriyor.

**Kosmyna vd. (2025): ChatGPT kullanımı ve "bilişsel borç"**

- **Amaç:** Makale yazarken LLM kullanımının beyin aktivitesine ve öğrenmeye etkisini incelemek.
- **Örneklem:** 54 katılımcı.
- **Yöntem:** EEG ile ölçüm; LLM, arama motoru ve hiçbir araç kullanmayan üç grup.
- **Bulgular:** LLM grubunda en düşük beyin bağlantısallığı ve yazdığı metni hatırlamada zorluk gözlendi.
- **Katkı:** Biyolojik düzeyde bir gösterge sunuyor. **Not:** Hakem değerlendirmesinden geçmemiş bir ön baskıdır ve örneklemi küçüktür; bu nedenle destekleyici kanıt olarak temkinli kullanılmıştır.



### 3.3 Tema 3: Müdahale yaklaşımları

**Bastani vd. (2025): Koruyucu kurallar olmadan üretken yapay zeka öğrenmeye zarar verebilir**

- **Amaç:** Üretken yapay zeka erişiminin ve araç tasarımının öğrenmeye etkisini ölçmek.
- **Örneklem:** Türkiye'de yaklaşık 1.000 lise öğrencisi (matematik dersi).
- **Yöntem:** Saha deneyi; kontrol grubu, standart ChatGPT arayüzü ("GPT Base") ve öğrenmeyi koruyan yönergelerle tasarlanmış "GPT Tutor".
- **Bulgular:** Erişim varken pratik başarısı GPT Base ile %48, GPT Tutor ile %127 arttı. Erişim kaldırıldığında GPT Base grubu, hiç erişimi olmayan gruba göre %17 daha düşük not aldı. GPT Tutor bu olumsuz etkiyi büyük ölçüde önledi. Öğrenciler kuralsız araçları bir "koltuk değneği" gibi kullandı.
- **Katkı:** Projemizin temel tasarım ilkesinin en güçlü dayanağı: sorun yapay zekanın kendisi değil, nasıl kullanıldığı; çözüm de yasaklamak değil, kullanımı doğru anda yönlendirmek. Sınırlılık: hedef grup lise öğrencileri ve tek ders.

**Okeke vd. (2018): Dijital dürtme (digital nudge) ile kullanımın azaltılması**

- **Amaç:** Basit bir dijital dürtmenin sosyal medya kullanımını azaltıp azaltmadığını test etmek.
- **Örneklem:** 50 katılımcı.
- **Yöntem:** 3 haftalık saha çalışması; kullanım limiti aşıldığında titreşim ile uyarı.
- **Bulgular:** Müdahale haftasında Facebook kullanımı %20'den fazla azaldı; ancak uyarılar kaldırıldığında kullanım eski düzeyine döndü.
- **Katkı:** Dürtmelerin işe yaradığını ama dışarıdan konan kısıtların kalıcı alışkanlık oluşturmadığını gösteriyor. Projemizde uyarıların nedenini açıklayan, farkındalık oluşturan bir yapı tercih etmemizin gerekçesi.



### 3.4 Tema 4: Veriye dayalı tespit

**Phang vd. (2025): ChatGPT'de duygusal kullanım ve iyi oluş**

- **Amaç:** ChatGPT ile etkileşimlerin kullanıcıların duygusal iyi oluşuna etkisini platform verisi üzerinden incelemek.
- **Örneklem:** 3 milyondan fazla sohbet, 4.000'den fazla kullanıcıyla anket ve yaklaşık 1.000 kişilik randomize deney.
- **Yöntem:** Gizliliği koruyan otomatik sınıflandırıcılarla sohbet analizi.
- **Bulgular:** Duygusal yüklü kullanım az sayıda yoğun kullanıcıda toplanıyor; çok yüksek kullanım duygusal bağımlılık göstergeleriyle ilişkili.
- **Katkı:** Problemli kullanım sinyallerinin sohbet metninden otomatik olarak çıkarılabildiğini gösteren en büyük ölçekli çalışma. Ancak veri kamuya açık değil.

**Lin vd. (2024): Sohbet sistemlerinde kullanıcı memnuniyetinin tahmini (SPUR)**

- **Amaç:** Sohbet metninden kullanıcı memnuniyetini yorumlanabilir şekilde tahmin etmek.
- **Yöntem:** LLM tabanlı, etiketli örneklerle yönlendirilen değerlendirme ölçütleri (ACL 2024, Microsoft).
- **Bulgular:** LLM tabanlı yaklaşım, embedding tabanlı ve klasik özellik tabanlı modellerden daha doğru ve daha yorumlanabilir sonuç veriyor.
- **Katkı:** Bir sohbetin "kötü gittiğini" metinden tespit etmenin teknik olarak mümkün olduğunu gösteriyor; projemizdeki döngü tespiti modelinin metodolojik dayanağı.



### 3.5 Karşılaştırma

**Hemfikir olunan noktalar**

1. Üretken yapay zekaya yoğun ve eleştirisiz güven, eleştirel düşünme ve öğrenme üzerinde olumsuz izler bırakıyor (Gerlich, 2025; Lee vd., 2025; Zhai vd., 2024; Bastani vd., 2025).
2. Risk kullanım süresinden çok **kullanım biçimiyle** ilgili: aynı aracı "koltuk değneği" olarak kullanmak ile düşünmeyi destekleyen bir araç olarak kullanmak farklı sonuçlar doğuruyor (Bastani vd., 2025; Fang vd., 2025).
3. Olumsuz etkiler genç kullanıcılarda daha belirgin (Gerlich, 2025).

**Ayrışan noktalar**

1. **Kavramın kendisi:** Ölçek çalışmaları problemli kullanımı bağımlılık modeliyle tanımlarken (Morales-García vd., 2024; Maral vd., 2026), Ciudad-Fernández vd. (2025) bu yaklaşımın sıradan davranışları patolojikleştirdiğini savunuyor.
2. **Nedensellik:** Deneysel çalışmalar (Bastani vd., 2025) nedensel etki gösterirken anket çalışmaları yalnızca ilişki ortaya koyuyor ve ilişkinin yönü belirsiz kalıyor (Abbas vd., 2024).
3. **Müdahalenin kalıcılığı:** Kısıtlama tabanlı dürtmeler kısa vadede işe yarıyor ama kalıcı değil (Okeke vd., 2018); tasarımla gelen yönlendirme ise daha kalıcı görünüyor (Bastani vd., 2025).

**Ortak sınırlılıklar**


| Sınırlılık                                             | Görüldüğü çalışmalar                                                                      |
| ------------------------------------------------------ | ----------------------------------------------------------------------------------------- |
| Öz bildirime dayalı ölçüm                              | Morales-García vd., Maral vd., Gerlich, Abbas vd., Lee vd.                                |
| Kesitsel tasarım, nedensellik kurulamıyor              | Morales-García vd., Gerlich, Lee vd.                                                      |
| Tek ülke örneklemi                                     | Morales-García vd. (Peru), Gerlich (İngiltere), Abbas vd. (Pakistan), Maral vd. (Türkiye) |
| Küçük örneklem veya hakem değerlendirmesinden geçmemiş | Kosmyna vd., Okeke vd.                                                                    |
| Kamuya açık olmayan veri                               | Phang vd., Fang vd.                                                                       |


---



## 4. Araştırma Boşluğu ve Sonuç



### 4.1 Temel çıkarımlar

1. Üretken yapay zekaya aşırı güven, özellikle hedef grubumuz olan genç yetişkinlerde, eleştirel düşünme, öğrenme ve duygusal iyi oluş üzerinde ölçülebilir izler bırakıyor.
2. Sorun aracın kendisinde değil, kullanım biçiminde. Aynı araç doğru tasarımla öğrenmeyi destekleyebiliyor.
3. "Bağımlılık" etiketi tartışmalı; bu nedenle kişiyi etiketlemek yerine davranışa odaklanan bir yaklaşım daha savunulabilir.
4. Kısıtlamaya dayalı müdahalelerin etkisi kalıcı değil; farkındalık ve yönlendirme odaklı tasarım daha umut verici.



### 4.2 Araştırma boşluğu

İncelediğimiz çalışmaların büyük çoğunluğu **anket ve öz bildirime** dayanıyor. Gerçek kullanım verisini analiz eden çalışmalar ise ya kamuya açık olmayan platform verisi kullanıyor (Phang vd., 2025) ya da kullanıcı memnuniyeti gibi genel bir hedefe odaklanıyor (Lin vd., 2024). Literatürde şu üç noktayı birlikte ele alan bir çalışmaya rastlamadık:

1. Problemli kullanımı **gerçek sohbet davranışından** (tekrar eden talepler, sonuçsuz uzayan oturumlar, düşünmenin tamamen devredilmesi) ölçmek,
2. Bunu kişiyi etiketlemeden, **kullanımın akışı sırasında** fark etmek,
3. Ölçümü kısıtlama yerine **yönlendirici bir müdahaleye** dönüştürmek.



### 4.3 Projenin katkısı

Projemiz bu boşluğu, açık kaynak sohbet veri setleri (WildChat, LMSYS Chat 1M, OpenAssistant) üzerinde eğitilen bir model ve bu modeli kullanıcının tarayıcısında çalıştıran bir Chrome eklentisi ile doldurmayı hedefliyor. Bilimsel katkısı, problemli yapay zeka kullanımını öz bildirim yerine davranış verisiyle tanımlayan bir yaklaşım önermesi; uygulamadaki katkısı ise Bastani vd. (2025) çalışmasındaki "koruyucu kural" fikrini herhangi bir yapay zeka aracında kullanılabilecek, gizliliği koruyan bir ürüne dönüştürmesidir.

---



## 5. Kaynakça (APA 7)

Abbas, M., Jam, F. A., & Khan, T. I. (2024). Is it harmful or helpful? Examining the causes and consequences of generative AI usage among university students. *International Journal of Educational Technology in Higher Education, 21*, Article 10. [https://doi.org/10.1186/s41239-024-00444-7](https://doi.org/10.1186/s41239-024-00444-7)

Bastani, H., Bastani, O., Sungu, A., Ge, H., Kabakcı, Ö., & Mariman, R. (2025). Generative AI without guardrails can harm learning: Evidence from high school mathematics. *Proceedings of the National Academy of Sciences, 122*, e2422633122. [https://doi.org/10.1073/pnas.2422633122](https://doi.org/10.1073/pnas.2422633122)

Ciudad-Fernández, V., von Hammerstein, C., & Billieux, J. (2025). People are not becoming "AIholic": Questioning the "ChatGPT addiction" construct. *Addictive Behaviors, 166*, Article 108325. [https://doi.org/10.1016/j.addbeh.2025.108325](https://doi.org/10.1016/j.addbeh.2025.108325)

Fang, C. M., Liu, A. R., Danry, V., Lee, E., Chan, S. W. T., Pataranutaporn, P., Maes, P., Phang, J., Lampe, M., Ahmad, L., & Agarwal, S. (2025). *How AI and human behaviors shape psychosocial effects of extended chatbot use: A longitudinal randomized controlled study* (arXiv:2503.17473). arXiv. [https://doi.org/10.48550/arXiv.2503.17473](https://doi.org/10.48550/arXiv.2503.17473)

Gerlich, M. (2025). AI tools in society: Impacts on cognitive offloading and the future of critical thinking. *Societies, 15*(1), Article 6. [https://doi.org/10.3390/soc15010006](https://doi.org/10.3390/soc15010006)

Griffiths, M. (2005). A "components" model of addiction within a biopsychosocial framework. *Journal of Substance Use, 10*(4), 191–197. [https://doi.org/10.1080/14659890500114359](https://doi.org/10.1080/14659890500114359)

Kosmyna, N., Hauptmann, E., Yuan, Y. T., Situ, J., Liao, X.H., Beresnitzky, A. V., Braunstein, I., & Maes, P. (2025). *Your brain on ChatGPT: Accumulation of cognitive debt when using an AI assistant for essay writing task* (arXiv:2506.08872). arXiv. [https://doi.org/10.48550/arXiv.2506.08872](https://doi.org/10.48550/arXiv.2506.08872)

Lee, H. P., Sarkar, A., Tankelevitch, L., Drosos, I., Rintel, S., Banks, R., & Wilson, N. (2025). The impact of generative AI on critical thinking: Self-reported reductions in cognitive effort and confidence effects from a survey of knowledge workers. In *Proceedings of the 2025 CHI Conference on Human Factors in Computing Systems*. Association for Computing Machinery. [https://doi.org/10.1145/3706598.3713778](https://doi.org/10.1145/3706598.3713778)

Lin, Y. C., Neville, J., Stokes, J. W., Yang, L., Safavi, T., Wan, M., Counts, S., Suri, S., Andersen, R., Xu, X., Gupta, D., Jauhar, S. K., Song, X., Buscher, G., Tiwary, S., Hecht, B., & Teevan, J. (2024). Interpretable user satisfaction estimation for conversational systems with large language models. In *Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)* (pp. 11100–11115). Association for Computational Linguistics. [https://aclanthology.org/2024.acl-long.598/](https://aclanthology.org/2024.acl-long.598/)

Maral, S., Naycı, N., Bilmez, H., Erdemir, E. İ., & Satıcı, S. A. (2026). Problematic ChatGPT Use Scale: AI-human collaboration or unraveling the dark side of ChatGPT. *International Journal of Mental Health and Addiction, 24*(3), 2369–2395. [https://doi.org/10.1007/s11469-025-01509-y](https://doi.org/10.1007/s11469-025-01509-y)

Morales-García, W. C., Sairitupa-Sanchez, L. Z., Morales-García, S. B., & Morales-García, M. (2024). Development and validation of a scale for dependence on artificial intelligence in university students. *Frontiers in Education, 9*, Article 1323898. [https://doi.org/10.3389/feduc.2024.1323898](https://doi.org/10.3389/feduc.2024.1323898)

Okeke, F., Sobolev, M., Dell, N., & Estrin, D. (2018). Good vibrations: Can a digital nudge reduce digital overload? In *Proceedings of the 20th International Conference on Human-Computer Interaction with Mobile Devices and Services (MobileHCI '18)*. Association for Computing Machinery. [https://doi.org/10.1145/3229434.3229463](https://doi.org/10.1145/3229434.3229463)

Phang, J., Lampe, M., Ahmad, L., Agarwal, S., Fang, C. M., Liu, A. R., Danry, V., Lee, E., Chan, S. W. T., Pataranutaporn, P., & Maes, P. (2025). *Investigating affective use and emotional well-being on ChatGPT* (arXiv:2504.03888). arXiv. [https://doi.org/10.48550/arXiv.2504.03888](https://doi.org/10.48550/arXiv.2504.03888)

World Health Organization. (2019). *International classification of diseases for mortality and morbidity statistics* (11th rev.). [https://icd.who.int/](https://icd.who.int/)

Zhai, C., Wibowo, S., & Li, L. D. (2024). The effects of over-reliance on AI dialogue systems on students' cognitive abilities: A systematic review. *Smart Learning Environments, 11*, Article 28. [https://doi.org/10.1186/s40561-024-00316-7](https://doi.org/10.1186/s40561-024-00316-7)