# Bölüm 5: Mimari Kararlar

Bu belge projede verdiğimiz teknik kararları ve nedenlerini kayıt altına alıyor. Her karar aynı düzende yazıldı: bağlam, karar, neden, bedeli. Yeni bir karar alındığında listenin sonuna eklenir; eski bir karar değişirse silinmez, "değiştirildi" notu düşülür.

| # | Karar | Durum |
|---|---|---|
| K01 | Problem, ilk turlardan erken uyarı olarak tanımlanır | Kabul |
| K02 | Etiket önce kurallarla, sonra hazır ve LLM etiketleri ile insan doğrulamasıyla üretilir | Kabul |
| K03 | Benzerlik için eğitimsiz karakter n-gram vektörü kullanılır | Kabul |
| K04 | Veri kullanıcı bazlı bölünür | Kabul |
| K05 | İlk model küçük ve açıklanabilirdir, tarayıcıda çalışır | Kabul |
| K06 | Tüm eşikler tek bir ayar dosyasında tutulur | Kabul |
| K07 | Tahmin ile tespit ayrılır; öneriler kesin sinyallerle tetiklenir | Kabul |
| K08 | Eğitim verisi WildChat 4.8M, hazır etiket kaynağı WildFeedback olur | Kabul |

---

## K01. Problem, ilk turlardan erken uyarı olarak tanımlanır

**Bağlam.** Bir sohbetin döngüye girdiğini sohbet bittikten sonra söylemek kolay ama işe yaramaz; kullanıcı zamanı zaten kaybetmiş olur.

**Karar.** İlk sürümde model kullanıcının yalnızca ilk iki mesajını görür ve sohbetin geri kalanında döngü olup olmayacağını tahmin eder (`config.K_TURNS = 2`). Etiket, modelin görmediği kısımdan üretilir.

**Neden.** Eklenti uyarıyı döngü başlamadan önce verebilir. Ayrıca girdi ve etiket farklı turlardan geldiği için etiket bilgisinin modele sızması yapısal olarak engellenir.

**Bedeli.** İlk iki tur az bilgi taşır, bu yüzden başarı tavanı düşüktür. Sonraki aşamada aynı modeli 3. ve 4. turlarda da çalıştırıp uyarıyı güncellemeyi deneyeceğiz.

## K02. Etiket önce kurallarla, sonra hazır ve LLM etiketleri ile insan doğrulamasıyla üretilir

**Bağlam.** Hiçbir açık veri setinde "verimsiz döngü" etiketi yok.

**Karar.** İlk sürümde etiket açık kurallarla üretilir (`labels.py`): ikinci turdan sonra en az 2 tekrar veya en az 2 onarım ifadesi. Sonra İngilizce sohbetler için WildFeedback'teki hazır memnuniyetsizlik etiketleri, Türkçe sohbetler için aynı ölçütle bir dil modeli kullanılır; 300 sohbet (en az 100'ü Türkçe) elle doğrulanır. "Devam et" gibi kısa ve meşru tekrarlar etiketten ayıklanır.

**Neden.** Kurallar hızlı ve denetlenebilir; veri hattını hemen kurmamızı sağlar. LLM, kuralların kaçırdığı anlam düzeyindeki tekrarları yakalar. İnsan doğrulaması iki yöntemin ne kadar güvenilir olduğunu sayıyla gösterir.

**Bedeli.** Kural tabanlı etiketle eğitilen model, kuralları yeniden öğrenmeye eğilimlidir. Bu yüzden nihai değerlendirme yalnızca elle doğrulanmış set üzerinde yapılacak.

## K03. Benzerlik için eğitimsiz karakter n-gram vektörü kullanılır

**Bağlam.** Bölüm 2'de hem TF-IDF hem çok dilli embedding denedik. Embedding anlam benzerliğini daha iyi yakalıyor ama tarayıcıda ek bir model gerektiriyor.

**Karar.** Öznitelik ve kural etiketinde `HashingVectorizer` (karakter 3 ile 5 gram) kullanılır. Çok dilli embedding, LLM etiketleme ve ileri model karşılaştırması için ayrı tutulur.

**Neden.** HashingVectorizer eğitim gerektirmez; aynı hesap JavaScript ile birebir yapılabilir. Python'da eğitilen model ile tarayıcıda çalışan model aynı sayıları görür.

**Bedeli.** "Bu kodu düzelt" ile "kodda hata var, tekrar yazar mısın" gibi anlamca aynı ama kelimece farklı mesajları kaçırır. Bu açığı onarım ifadesi özniteliği kısmen kapatıyor.

## K04. Veri kullanıcı bazlı bölünür

**Bağlam.** WildChat'te en yoğun %1 kullanıcı sohbetlerin %28'ini oluşturuyor.

**Karar.** Eğitim ve test ayrımı şifrelenmiş IP'ye göre yapılır (`split.user_split`). Aynı kişinin sohbetleri iki tarafta birden bulunmaz.

**Neden.** Rastgele bölmede model yoğun kullanıcıların yazım tarzını ezberler ve test skoru gerçekte olduğundan iyi görünür.

**Bedeli.** Test seti küçülür ve skorlar daha dalgalı olur. Bunu ileride kullanıcı bazlı çapraz doğrulama (GroupKFold) ile dengeleyeceğiz.

## K05. İlk model küçük ve açıklanabilirdir, tarayıcıda çalışır

**Bağlam.** Ürün kullanıcının bilgisayarında çalışacak; mesajlar dışarı gönderilmeyecek. Chrome'un yerleşik modeli Türkçeyi desteklemiyor.

**Karar.** Karşılaştırma sırası: kural, Logistic Regression, XGBoost. Logistic Regression seçilirse katsayılar küçük bir JSON dosyası olarak eklentiye konur; ek bir kütüphane gerekmez. XGBoost seçilirse ONNX formatına çevrilip ONNX Runtime Web ile çalıştırılır. Transformer modeller yalnızca belirgin fark yaratırsa ve 150 ms sınırına sığarsa kullanılır.

**Neden.** Küçük, hızlı ve SHAP ile açıklanabilir. Her uyarının gerekçesini göstermek ürünün temel ilkelerinden biri.

**Bedeli.** Metnin anlamını doğrudan okuyan büyük modellerin doğruluğuna ulaşamayabilir.

## K06. Tüm eşikler tek bir ayar dosyasında tutulur

**Bağlam.** Benzerlik eşiği, etiket kuralı ve şablon tespiti gibi değerler deneyler boyunca değişecek.

**Karar.** Hepsi `src/kafiai/config.py` içinde, yanında gerekçesiyle durur.

**Neden.** Bir değeri değiştirmek için kodun içinde arama yapmak gerekmez; rapordaki sayılar ile koddaki değerler aynı yerden okunur.

**Bedeli.** Yok denecek kadar az.

## K07. Tahmin ile tespit ayrılır; öneriler kesin sinyallerle tetiklenir

**Bağlam.** Döngüler sohbetlerin yaklaşık %10'unda görülüyor. Bu oranda, döngülerin yarısını yakalayıp normal sohbetlerin %90'ını rahat bırakan iyi bir model bile verdiği her üç uyarıdan yaklaşık ikisinde yanılır. Ayrıca döngü, henüz yazılmamış yapay zeka cevaplarına bağlı olduğu için erken tahminin bir tavanı var.

**Karar.** Model yalnızca mesaj kutusunun kenarındaki halkanın tonunu etkiler. Kullanıcının önüne çıkan öneriler kesin sinyallerle tetiklenir: gerçekleşmiş bir tekrar uyarı şeridini, görev normunu aşan tur sayısı çıkış kartını açar. Haftalık özet yalnızca kesin sayımlardan oluşur.

**Neden.** Yanılma ihtimali olan sinyal kullanıcıyı rahatsız etmez; kullanıcıyı yönlendiren öneriler ise olmuş bir şeye dayanır. Ürünün değeri modelin isabetine bağlı kalmaz.

**Bedeli.** Model kullanıcıyı tek başına yönlendiremediği için bazı döngüler ancak başladıktan sonra yakalanır.

## K08. Eğitim verisi WildChat 4.8M, hazır etiket kaynağı WildFeedback olur

**Bağlam.** Keşif analizini WildChat 1M ile yaptık. Bu sürüm 2023 ile 2024 arasını ve eski modelleri kapsıyor; Türkçe sohbet sayısı da az.

**Karar.** Model eğitiminde Ağustos 2025'e kadar uzanan, yaklaşık 3,2 milyon sohbetlik WildChat 4.8M kullanılır. İngilizce sohbetlerde ikinci etiket katmanı olarak Microsoft'un WildFeedback veri setindeki tur bazlı memnuniyetsizlik etiketleri kullanılır.

**Neden.** Daha güncel modeller ve kullanım biçimleri, daha fazla Türkçe sohbet. WildFeedback etiketleri, aynı yöntemi kendimiz uygulamanın maliyetini ve süresini ortadan kaldırıyor.

**Bedeli.** WildFeedback etiketleri bir dil modeli tarafından üretildi; insan etiketi gibi değil, ikinci bir görüş gibi kullanılmalı. Veri seti büyük olduğu için tamamı değil, akış halinde örneklem alınarak kullanılacak.
