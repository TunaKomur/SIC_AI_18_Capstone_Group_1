# Bölüm 3: Teknoloji İncelemesi

**Proje:** Üretken yapay zeka kullanımında aşırı güven ve verimsiz kullanım döngülerinin tespiti
**Grup:** SIC AI 18 Capstone, Grup 1

---

## 1. Giriş

Projemizin hedefi, kullanıcının ChatGPT, Gemini, Claude veya Copilot gibi bir yapay zeka asistanıyla yaptığı sohbeti tarayıcıda izleyip verimsiz bir döngüye girdiği anı fark eden ve ona kısa, yargılamayan bir yönlendirme sunan bir Chrome eklentisi geliştirmek. Bu hedef, birbirine bağlı dört teknik soruyu beraberinde getiriyor:

1. **Veri:** Gerçek yapay zeka sohbetlerine nasıl erişir, büyük veri setlerini nasıl işleriz?
2. **Temsil ve modelleme:** Bir sohbetin "tıkandığını" makinenin anlayabileceği bir forma nasıl çeviririz ve hangi model bunu en iyi tahmin eder?
3. **Çalıştırma ortamı:** Model kullanıcının cihazında mı, tarayıcının kendi yapay zekasında mı, yoksa bir bulut sunucusunda mı çalışmalı?
4. **Ürün ve müdahale:** Uyarı kullanıcıya nasıl, ne zaman ve hangi dille ulaşmalı?

Bu bölümde her soru için değerlendirdiğimiz teknolojileri tanıtıyor, birbirleriyle karşılaştırıyor ve seçimlerimizi gerekçelendiriyoruz. Teknoloji seçimi bu projede yalnızca performans meselesi değildir: insanların en özel konuşmalarını işleyen bir araç tasarladığımız için **gizlilik**, kullanıcıya neden uyarıldığını söyleyebilmek için **açıklanabilirlik** ve Türkçe konuşan bir hedef grup için **dil desteği** en az doğruluk kadar belirleyicidir.

---



## 2. Teknolojilere Genel Bakış



### 2.1 Veri katmanı

**Hugging Face Datasets.** Açık veri setlerini indirmek, filtrelemek ve işlemek için kullanılan Python kütüphanesi. `streaming` modu sayesinde yüz binlerce sohbetten oluşan bir veri setini tamamen indirmeden, parça parça okuyup rastgele örneklem alabiliyoruz. Bölüm 2'deki analiz bu yöntemle WildChat 1M'den 50.000 sohbetlik bir örneklem çekti.

**pandas ve NumPy.** Tablo halindeki verinin temizlenmesi, gruplanması ve istatistiklerinin çıkarılması için standart araçlar.

### 2.2 Metni sayısal temsile çevirme

Bir sohbetin döngüye girip girmediğini anlamak için ardışık kullanıcı mesajlarının birbirine ne kadar benzediğini ölçmemiz gerekiyor. Bunun için iki yöntem değerlendirdik.

**TF-IDF (karakter n-gram).** Metni karakter dizilerinin sıklığına göre vektöre çeviren klasik bir yöntem. Hızlıdır, eğitim gerektirmez ve dilden bağımsız çalışır. Ancak yalnızca yüzeysel benzerliği yakalar: "bu kodu düzelt" ile "kodda hata var, tekrar yazar mısın" cümlelerinin aynı talep olduğunu anlayamaz.

**Sentence embeddings.** Cümleleri anlamlarına göre çok boyutlu bir uzaya yerleştiren sinir ağı modelleri (Reimers ve Gurevych, 2019). Biz `paraphrase-multilingual-MiniLM-L12-v2` modelini kullandık. Bu model 50'den fazla dili, Türkçe dahil, aynı uzayda temsil edecek şekilde eğitilmiştir (Reimers ve Gurevych, 2020). Farklı kelimelerle yazılmış aynı talebi ve farklı dillerde yazılmış benzer mesajları yakalayabilir. Model yaklaşık 118 milyon parametrelidir ve dizüstü bir bilgisayarda bile çalışabilir.

### 2.3 Sınıflandırma modelleri

Projenin ilerleyen aşamasında iki sınıflandırma problemi çözeceğiz: bir sohbetin sonuçsuz kalma riskini tahmin etmek ve bir talebin "düşünmeyi devretme" niteliği taşıyıp taşımadığını belirlemek.

**Klasik makine öğrenmesi (Logistic Regression, XGBoost).** Tur sayısı, mesaj uzunluğundaki değişim, ardışık benzerlik, memnuniyetsizlik ifadeleri gibi elle tasarlanmış özelliklerle çalışır. XGBoost, karar ağaçlarını ardışık olarak eğiten ve tablo verisinde çok güçlü sonuç veren bir yöntemdir (Chen ve Guestrin, 2016). En önemli avantajı açıklanabilirliktir: SHAP değerleri ile her tahminin hangi özellikten kaynaklandığı gösterilebilir (Lundberg ve Lee, 2017).

**Transformer tabanlı dil modelleri (DistilBERT, XLM-RoBERTa).** Metni doğrudan okuyup sınıflandıran, önceden eğitilmiş modeller. DistilBERT, BERT'in yaklaşık %40 daha küçük ve %60 daha hızlı bir sürümüdür (Sanh vd., 2019). XLM-RoBERTa ise 100 dilde eğitilmiş çok dilli bir modeldir ve Türkçe metinlerde güçlüdür (Conneau vd., 2020). Bu modeller özellik tasarımına ihtiyaç duymadan bağlamı yakalar, ancak daha fazla etiketli veri ve hesaplama gücü ister.

**Büyük dil modelleri (LLM) ile etiketleme.** Sohbetlerin "verimsiz döngü" olup olmadığını gösteren hazır bir etiket yok. Bu boşluğu doldurmak için bir LLM'i belirli bir değerlendirme ölçütüyle etiketleyici olarak kullanmak mümkün. Lin vd. (2024) LLM'lerin bu tür ölçüt tabanlı değerlendirmede embedding tabanlı yöntemlerden daha doğru ve daha yorumlanabilir olduğunu gösterdi. Biz LLM'i yalnızca **eğitim aşamasında** etiket üretmek için kullanmayı, ürünün kendisinde ise daha küçük bir model çalıştırmayı planlıyoruz.

### 2.4 Tarayıcı ve ürün katmanı

**Chrome Extension, Manifest V3.** Chrome eklentilerinin güncel mimarisi. Chrome, eski Manifest V2 eklentilerini Temmuz 2025'te (Chrome 138) tamamen devre dışı bıraktı; bu nedenle yeni bir eklenti MV3 ile yazılmak zorunda (Google, 2026a). Projemizde üç bileşen kullanacağız:

- **Content script:** ChatGPT, Gemini, Copilot sayfalarında çalışıp kullanıcının mesajlarını okur.
- **Service worker:** Arka planda modeli çalıştırır ve kararları verir.
- **chrome.storage.local:** Yalnızca özet sayaçları kullanıcının cihazında saklar.

**Transformers.js ve ONNX Runtime Web.** Hugging Face'in geliştirdiği Transformers.js, Python'da eğitilen modellerin ONNX formatına çevrilerek doğrudan tarayıcıda, sunucuya ihtiyaç duymadan çalıştırılmasını sağlar. WebAssembly üzerinde CPU ile, WebGPU destekleyen cihazlarda ekran kartı ile çalışır (Hugging Face, 2026). Bu sayede kullanıcı mesajları hiçbir zaman cihazdan çıkmaz.

**Chrome'un yerleşik yapay zekası (Prompt API, Gemini Nano).** Chrome, Gemini Nano modelini tarayıcının içine yerleştirip eklentilerin kullanımına açtı (eklentiler için Chrome 138'den itibaren). Ancak bugünkü haliyle önemli kısıtları var: en az 22 GB boş disk alanı, 4 GB'tan fazla ekran kartı belleği veya 16 GB RAM gerektiriyor ve yalnızca İngilizce, Japonca, İspanyolca, Almanca ve Fransızca dillerini destekliyor (Google, 2026b). **Türkçe desteklenmiyor.**

**Bulut LLM API'leri (OpenAI, Google Gemini, Anthropic).** En güçlü dil anlama yeteneğini sunar, ancak kullanıcının sohbet içeriğinin üçüncü bir tarafa gönderilmesini gerektirir ve her istek için maliyet oluşturur.

### 2.5 Yönergede önerilen kullanım takip API'leri

Ödev yönergesi Android UsageStatsManager ve Apple Screen Time gibi kullanım takip API'lerini de örnek veriyor. Bu araçları değerlendirdik ancak projemiz için uygun bulmadık: her ikisi de **hangi uygulamanın ne kadar süre açık kaldığını** ölçer, bir sohbetin **içeriğini ve akışını** göremez. Bölüm 1'de gösterdiğimiz gibi, problemli yapay zeka kullanımını belirleyen şey süreden çok kullanım biçimidir. Ayrıca hedef grubumuz yapay zeka araçlarını ağırlıklı olarak ders ve iş için bilgisayarda, tarayıcı üzerinden kullanıyor.

---



## 3. Projeyle İlgisi


| Projedeki zorluk                                            | Çözen teknoloji                         | Neden                                                             |
| ----------------------------------------------------------- | --------------------------------------- | ----------------------------------------------------------------- |
| Gerçek sohbet verisine erişim                               | Hugging Face Datasets                   | Açık lisanslı veri setlerine tek satırla, akış halinde erişim     |
| Aynı talebin farklı kelimelerle tekrar edilmesini yakalamak | Çok dilli sentence embeddings           | Anlam düzeyinde benzerlik, Türkçe desteği                         |
| Hazır etiket olmaması                                       | LLM ile etiketleme ve insan doğrulaması | Ölçüt tabanlı, ölçeklenebilir etiket üretimi                      |
| Kullanıcıya neden uyarıldığını söyleyebilmek                | XGBoost ve SHAP                         | Her kararın gerekçesini özellik düzeyinde gösterir                |
| Mesajların cihazdan çıkmaması                               | Transformers.js ve ONNX Runtime Web     | Model tarayıcıda yerel olarak çalışır                             |
| Kullanıcının zaten çalıştığı ortamda bulunmak               | Chrome Extension MV3                    | ChatGPT, Gemini ve Copilot'un web arayüzlerinde aynı anda çalışır |


---



## 4. Karşılaştırma ve Değerlendirme



### 4.1 Döngü tespiti için metin temsili


| Kriter                       | TF-IDF karakter n-gram | Çok dilli sentence embedding | LLM ile doğrudan değerlendirme |
| ---------------------------- | ---------------------- | ---------------------------- | ------------------------------ |
| Anlamsal benzerliği yakalama | Düşük                  | Yüksek                       | Çok yüksek                     |
| Türkçe desteği               | Dilden bağımsız        | Var                          | Modele bağlı                   |
| Hız                          | Çok hızlı              | Hızlı                        | Yavaş                          |
| Maliyet                      | Yok                    | Yok                          | API başına ücret               |
| Tarayıcıda çalışabilme       | Kolay                  | Mümkün (ONNX)                | Zor                            |
| **Değerlendirme**            | Hızlı ön analiz için   | **Ana yöntem**               | Yalnızca etiketleme için       |


Bölüm 2'deki analizde iki yöntemi de denedik. Embedding tabanlı yöntem, art arda gelen mesajlar arasında neredeyse birebir tekrarları ve anlamca aynı talepleri açıkça ayırt edebildi.

### 4.2 Sınıflandırma modeli


| Kriter                | Logistic Regression | XGBoost                      | DistilBERT / XLM-RoBERTa        |
| --------------------- | ------------------- | ---------------------------- | ------------------------------- |
| Doğruluk potansiyeli  | Orta                | Yüksek                       | En yüksek                       |
| Gereken etiketli veri | Az                  | Az ile orta                  | Fazla                           |
| Açıklanabilirlik      | Yüksek              | Yüksek (SHAP ile)            | Düşük                           |
| Eğitim maliyeti       | Çok düşük           | Düşük                        | Ekran kartı gerektirir          |
| Tarayıcıda çalışma    | Kolay               | Mümkün                       | Mümkün ama ağır                 |
| **Değerlendirme**     | Başlangıç modeli    | **Ana karşılaştırma modeli** | Yeterli etiket olursa son model |


Planımız, önce XGBoost ile güçlü ve açıklanabilir bir temel model kurmak, ardından yeterli etiketli veri oluştuğunda çok dilli bir Transformer modelini karşılaştırmak. Karşılaştırma yalnızca doğruluğa göre değil, açıklanabilirlik ve tarayıcıdaki hız da hesaba katılarak yapılacak.

### 4.3 Çalıştırma ortamı


| Kriter                                   | Cihaz içi (Transformers.js)          | Chrome yerleşik yapay zeka (Gemini Nano) | Bulut LLM API                         |
| ---------------------------------------- | ------------------------------------ | ---------------------------------------- | ------------------------------------- |
| Gizlilik                                 | **Çok yüksek**, veri cihazdan çıkmaz | Yüksek                                   | Düşük, içerik üçüncü tarafa gider     |
| Türkçe desteği                           | Seçtiğimiz modele bağlı              | **Yok**                                  | Var                                   |
| Kullanıcı için maliyet                   | Yok                                  | Yok                                      | Var                                   |
| Donanım gereksinimi                      | Düşük                                | Yüksek (22 GB disk, 16 GB RAM)           | Yok                                   |
| Erişilebilirlik (öğrenci bilgisayarları) | Yüksek                               | Düşük                                    | Yüksek                                |
| Kontrol ve özelleştirme                  | Tam                                  | Sınırlı                                  | Sınırlı                               |
| **Değerlendirme**                        | **Seçilen yöntem**                   | Türkçe gelirse ileride                   | Yalnızca eğitim aşamasında etiketleme |


Bu tablo, cihaz içi çalıştırmanın projemiz için tek uygun seçenek olduğunu gösteriyor. Hedef grubumuzun bilgisayarlarının önemli bir kısmı Gemini Nano'nun donanım şartlarını karşılamayacaktır, Türkçe desteğinin olmaması ise belirleyicidir. Bulut API'si ise kullanıcı mesajlarının dışarı gönderilmesini gerektirdiği için ürünün kendisinde kabul edilemez.

---



## 5. Kullanım Örnekleri

**Android Digital Wellbeing ve Apple Screen Time (2018).** Akıllı telefonlarda uygulama başına kullanım süresini gösteren, süre sınırı ve uyku modu sunan yerleşik araçlar. Dijital iyi oluş araçlarını milyarlarca kullanıcıya ulaştırdılar, ancak süre odaklıdırlar ve kullanımın içeriğine bakmazlar.

**one sec.** Kullanıcı seçtiği bir uygulamayı açmak istediğinde birkaç saniyelik bir duraklama ve nefes egzersizi gösteren bir "kendi kendine dürtme" uygulaması. 280 kişiyle 6 hafta süren saha çalışmasında kullanıcılar açma girişimlerinin ortalama %36'sında uygulamayı açmaktan vazgeçti; altı haftanın sonunda uygulama açma sayısı %57 azaldı (Grüning vd., 2023). Kısa ve doğru zamanlanmış bir duraklamanın yasaklamadan daha etkili olabileceğini gösteren en güçlü örneklerden biri. Bizim müdahale tasarımımıza en yakın örnek.

**ChatGPT'nin mola hatırlatıcıları ve öğrenme modu (2025).** OpenAI, Ağustos 2025'te uzun oturumlarda kullanıcıya mola vermesini hatırlatan mesajlar eklediğini ve kişisel kararlarda doğrudan cevap vermek yerine kullanıcının düşünmesine yardım edecek bir yaklaşıma geçtiğini duyurdu. Şirket ayrıca hedefinin kullanıcının dikkatini tutmak değil, onu iyi kullanmasına yardımcı olmak olduğunu açıkça ifade etti (OpenAI, 2025a). Temmuz 2025'te ise öğrencilere cevabı doğrudan vermek yerine problemi adım adım çözdüren "study mode" özelliğini tanıttı (OpenAI, 2025b). Bu gelişmeler, sektörün kendisinin de bu problemi kabul ettiğini gösteriyor.

**GPT Tutor (Bastani vd., 2025).** Türkiye'de yaklaşık 1.000 lise öğrencisiyle yapılan deneyde, öğrenmeyi koruyan yönergelerle tasarlanan yapay zeka asistanı, sınırsız ChatGPT erişiminin öğrenmeye verdiği zararı büyük ölçüde önledi. Teknolojinin kendisi aynı, fark tasarımda.

**Yeşilay Danışmanlık Merkezi (YEDAM).** Yeşilay, teknoloji bağımlılığı dahil bağımlılık türlerinde 12 yaş ve üzeri bireylere ücretsiz psikososyal destek sunuyor; randevu ve danışma için 115 numaralı hat kullanılıyor (YEDAM, 2026). Ürünümüz yüksek risk sinyali gördüğünde kullanıcıyı bu profesyonel desteğe yönlendirecek.

---



## 6. Boşluklar ve Araştırma Fırsatları



### 6.1 Mevcut araçlardaki boşluklar

1. **Süre odaklılık.** Digital Wellbeing, Screen Time ve one sec süreyi ya da açılış sayısını ölçer. Bir yapay zeka sohbetinin verimli mi yoksa kısır döngüde mi ilerlediğini ayırt edemezler.
2. **Platforma bağımlılık.** ChatGPT'nin mola hatırlatıcıları yalnızca ChatGPT içinde çalışır ve kurallarını tek bir şirket belirler. Bir kullanıcı gün içinde birden fazla yapay zeka aracı kullandığında bütüncül bir resim oluşmaz.
3. **Dil desteği.** Tarayıcıya yerleşik yapay zeka modelleri henüz Türkçeyi desteklemiyor; Türkçe konuşan kullanıcılar için uyarlanmış bir araç bulunmuyor.
4. **Açıklanabilirlik eksikliği.** Mevcut hatırlatıcılar genellikle neden gösterildiğini söylemez. Kullanıcının uyarıyı anlamlı bulması için gerekçesini görmesi gerekir.



### 6.2 Projemize özgü özelleştirmeler

- Çok dilli embedding modelinin Türkçe yapay zeka sohbetleri üzerinde ayrıca test edilmesi.
- Modelin ONNX formatına çevrilip küçültülmesi (quantization) ve tarayıcıda gecikmesinin ölçülmesi.
- Kural tabanlı ilk sınıflandırmanın yerine etiketli veriyle eğitilmiş bir modelin geçirilmesi.
- ChatGPT, Gemini ve Copilot'un sayfa yapıları değiştikçe content script'in güncellenmesi.



### 6.3 Kendi çözümümüzün riskleri ve önlemler


| Risk                                                                  | Önlem                                                                                                                                                                                        |
| --------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Ürünün kendisinin yeni bir kompulsif kullanım kaynağına dönüşmesi** | Seri (streak), puan, rozet gibi oyunlaştırma öğeleri yok. Panel yalnızca haftalık özet gösterir, sürekli bildirim gönderilmez.                                                               |
| **Gizlilik ihlali**                                                   | Mesajlar cihaz içinde işlenir, saklanmaz ve hiçbir sunucuya gönderilmez. Yalnızca özet sayaçlar (örneğin "bu hafta 4 döngü") yerel olarak tutulur. Kullanıcı tüm veriyi tek tuşla silebilir. |
| **Gözetim aracı olarak kötüye kullanım**                              | Ebeveyn veya işveren modu bulunmaz; eklenti yalnızca kullanıcının kendisine geri bildirim verir.                                                                                             |
| **Yanlış alarm**                                                      | Her uyarı gerekçesini gösterir ("son 5 mesajda aynı talep"). Kullanıcı uyarıyı "yanlış" olarak işaretleyebilir; eşik kişiye göre ayarlanır.                                                  |
| **Etiketleme ve damgalama**                                           | Ürün "bağımlısın" demez, teşhis koymaz. Yalnızca kullanım biçimindeki örüntüyü görünür kılar (Ciudad-Fernández vd., 2025).                                                                   |
| **Profesyonel desteğin yerini alma**                                  | Ürün terapi veya danışmanlık sunmaz. Uzun süreli ve yoğun risk sinyallerinde kullanıcıyı YEDAM'a ve 115 hattına yönlendirir.                                                                 |


---



## 7. Sonuç

Teknoloji incelemesinden çıkan seçimlerimiz şöyle:


| Katman        | Seçim                                                                                                |
| ------------- | ---------------------------------------------------------------------------------------------------- |
| Veri          | Hugging Face Datasets ile WildChat 1M, LMSYS Chat 1M ve OASST1                                       |
| Analiz        | Python, pandas, scikit-learn                                                                         |
| Metin temsili | `paraphrase-multilingual-MiniLM-L12-v2` sentence embeddings                                          |
| Etiketleme    | LLM ile ölçüt tabanlı etiketleme ve ekip tarafından insan doğrulaması                                |
| Model         | XGBoost ve SHAP ile açıklanabilir temel model; yeterli veriyle çok dilli Transformer karşılaştırması |
| Çalıştırma    | ONNX formatı, Transformers.js ile tarayıcı içinde                                                    |
| Ürün          | Chrome Extension (Manifest V3), yerel depolama, YEDAM yönlendirmesi                                  |


Bu seçimlerin ortak noktası, kullanıcının verisini cihazında tutmak, her kararı açıklayabilmek ve Türkçe konuşan bir hedef gruba hizmet edebilmek. Literatür, sorunun kullanım biçiminde olduğunu ve en etkili müdahalenin doğru anda yapılan küçük bir yönlendirme olduğunu gösteriyordu; seçtiğimiz teknolojiler bu yönlendirmeyi gizliliği koruyarak ve platformdan bağımsız biçimde sunmamızı sağlıyor.

---



## 8. Kaynakça (APA 7)

Bastani, H., Bastani, O., Sungu, A., Ge, H., Kabakcı, Ö., & Mariman, R. (2025). Generative AI without guardrails can harm learning: Evidence from high school mathematics. *Proceedings of the National Academy of Sciences, 122*, e2422633122. [https://doi.org/10.1073/pnas.2422633122](https://doi.org/10.1073/pnas.2422633122)

Chen, T., & Guestrin, C. (2016). XGBoost: A scalable tree boosting system. In *Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining* (pp. 785–794). Association for Computing Machinery. [https://doi.org/10.1145/2939672.2939785](https://doi.org/10.1145/2939672.2939785)

Ciudad-Fernández, V., von Hammerstein, C., & Billieux, J. (2025). People are not becoming "AIholic": Questioning the "ChatGPT addiction" construct. *Addictive Behaviors, 166*, Article 108325. [https://doi.org/10.1016/j.addbeh.2025.108325](https://doi.org/10.1016/j.addbeh.2025.108325)

Conneau, A., Khandelwal, K., Goyal, N., Chaudhary, V., Wenzek, G., Guzmán, F., Grave, E., Ott, M., Zettlemoyer, L., & Stoyanov, V. (2020). Unsupervised cross-lingual representation learning at scale. In *Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics* (pp. 8440–8451). Association for Computational Linguistics. [https://doi.org/10.18653/v1/2020.acl-main.747](https://doi.org/10.18653/v1/2020.acl-main.747)

Google. (2026a). *Manifest V2 support timeline*. Chrome for Developers. [https://developer.chrome.com/docs/extensions/develop/migrate/mv2-deprecation-timeline](https://developer.chrome.com/docs/extensions/develop/migrate/mv2-deprecation-timeline)

Google. (2026b). *The Prompt API*. Chrome for Developers. [https://developer.chrome.com/docs/ai/prompt-api](https://developer.chrome.com/docs/ai/prompt-api)

Grüning, D. J., Riedel, F., & Lorenz-Spreen, P. (2023). Directing smartphone use through the self-nudge app one sec. *Proceedings of the National Academy of Sciences, 120*, e2213114120. [https://doi.org/10.1073/pnas.2213114120](https://doi.org/10.1073/pnas.2213114120)

Hugging Face. (2026). *Transformers.js* [Computer software]. GitHub. [https://github.com/huggingface/transformers.js](https://github.com/huggingface/transformers.js)

Lin, Y. C., Neville, J., Stokes, J. W., Yang, L., Safavi, T., Wan, M., Counts, S., Suri, S., Andersen, R., Xu, X., Gupta, D., Jauhar, S. K., Song, X., Buscher, G., Tiwary, S., Hecht, B., & Teevan, J. (2024). Interpretable user satisfaction estimation for conversational systems with large language models. In *Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)* (pp. 11100–11115). Association for Computational Linguistics. [https://aclanthology.org/2024.acl-long.598/](https://aclanthology.org/2024.acl-long.598/)

Lundberg, S. M., & Lee, S. I. (2017). A unified approach to interpreting model predictions. In *Advances in Neural Information Processing Systems 30* (pp. 4765–4774). Curran Associates.

OpenAI. (2025a, August 4). *What we're optimizing ChatGPT for*. [https://openai.com/index/optimizing-chatgpt/](https://openai.com/index/optimizing-chatgpt/)

OpenAI. (2025b, July 29). *Introducing study mode in ChatGPT*. [https://openai.com/index/chatgpt-study-mode/](https://openai.com/index/chatgpt-study-mode/)

Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence embeddings using Siamese BERT-networks. In *Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing* (pp. 3982–3992). Association for Computational Linguistics. [https://doi.org/10.18653/v1/D19-1410](https://doi.org/10.18653/v1/D19-1410)

Reimers, N., & Gurevych, I. (2020). Making monolingual sentence embeddings multilingual using knowledge distillation. In *Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing* (pp. 4512–4525). Association for Computational Linguistics. [https://doi.org/10.18653/v1/2020.emnlp-main.365](https://doi.org/10.18653/v1/2020.emnlp-main.365)

Sanh, V., Debut, L., Chaumond, J., & Wolf, T. (2019). *DistilBERT, a distilled version of BERT: Smaller, faster, cheaper and lighter* (arXiv:1910.01108). arXiv. [https://doi.org/10.48550/arXiv.1910.01108](https://doi.org/10.48550/arXiv.1910.01108)

Yeşilay Danışmanlık Merkezi. (2026). *Teknoloji bağımlılığı*. [https://www.yedam.org.tr/bagimlilik-turleri/teknoloji-bagimliligi](https://www.yedam.org.tr/bagimlilik-turleri/teknoloji-bagimliligi)