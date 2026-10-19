# Bölüm 7: Veri Setleri, Kütüphaneler ve Hazır Kaynaklar

Bu belge projede kullandığımız ya da kullanmayı düşündüğümüz açık kaynakları tek yerde topluyor. Her kaynağın yanında projede ne işe yarayacağı ve dikkat edilmesi gereken noktalar yazılı.

---

## 1. Veri setleri

| Veri seti | İçerik | Projedeki rolü | Lisans ve erişim |
|---|---|---|---|
| [WildChat 1M](https://huggingface.co/datasets/allenai/WildChat-1M) | Yaklaşık 838 bin gerçek ChatGPT sohbeti, 68 dil, Nisan 2023 ile Nisan 2024 arası | Keşif analizi (Bölüm 2) ve ilk temel modeller | ODC BY, açık |
| [WildChat 4.8M](https://huggingface.co/datasets/allenai/WildChat-4.8M) | Yaklaşık 3,2 milyon toksik olmayan sohbet, Ağustos 2025'e kadar; GPT-4o, GPT-4.1 mini ve o1 modelleri dahil | Model eğitiminin ana verisi; daha güncel kullanım ve daha fazla Türkçe sohbet | ODC BY, açık (toksik içerikli tam sürüm başvuruyla) |
| [WildFeedback](https://huggingface.co/datasets/microsoft/WildFeedback) | WildChat üzerine kurulu; yaklaşık 1 milyon kullanıcı turu için GPT-4 ile üretilmiş memnuniyet ve memnuniyetsizlik etiketleri ve gerekçeleri | İngilizce sohbetler için hazır ikinci etiket katmanı; kendi kural etiketlerimizi doğrulamak | ODC BY, açık |
| [ShareChat](https://arxiv.org/abs/2512.17843) | 142 bin paylaşılmış sohbet; ChatGPT, Gemini, Claude, Grok, Perplexity | Farklı platformlarda genelleme testi | CC BY-NC 4.0, yalnızca araştırma |
| [LMSYS Chat 1M](https://huggingface.co/datasets/lmsys/lmsys-chat-1m) | 25 modelle 1 milyon sohbet | Gerekirse ek genelleme testi | Lisans sözleşmesi onayıyla |
| [OpenAssistant OASST1](https://huggingface.co/datasets/OpenAssistant/oasst1) | Yaklaşık 88 bin mesaj ve insan kalite puanları | "İyi giden" ve "kötü giden" cevaplar için referans | Apache 2.0 |
| [MultiTurn Feedback](https://huggingface.co/datasets/yuhan-nlp/multiturn-feedback) | WildChat ve LMSYS'ten 183 sohbette insan eliyle etiketlenmiş geri bildirim türleri (yeniden ifade etme, düzeltme, açıklama isteme) | Onarım düğmelerinin kategorilerini ve elle etiketleme kılavuzumuzu şekillendirmek | CC BY 4.0 |

**Dikkat edilecekler**

- WildChat'teki zaman damgası UTC'dir; Türkiye saatine çevrilmelidir (analiz kodumuz bunu yapıyor).
- Şifrelenmiş IP her zaman tek bir kişiyi temsil etmez; kullanıcı bazlı bölmede bu bir sınırlılık olarak yazılmalıdır.
- ShareChat paylaşılmış sohbetlerden oluşur; insanlar genelde başarılı sohbetlerini paylaştığı için döngüler bu veride az temsil edilir.
- WildFeedback etiketleri bir dil modeli tarafından üretilmiştir; insan etiketi gibi değil, ikinci bir görüş gibi kullanılmalıdır.

## 2. Bu projeye doğrudan dayanak olan çalışmalar

| Çalışma | Bize ne söylüyor |
|---|---|
| Laban vd. (2025), *LLMs get lost in multi-turn conversation* | Modeller çok turlu sohbette tek tura göre ortalama %39 daha kötü performans gösteriyor. "Taze başlat" önerisinin ve suçlamayan dilin bilimsel dayanağı. |
| Sarkar vd. (2025), *Conversational user-AI intervention: a study on prompt rewriting* | WildChat'teki memnuniyetsiz turlarda kullanıcının istemi yeniden yazıldığında cevaplar büyük oranda daha iyi bulunuyor; açıklık, belirginlik ve hedefin net yazılması en sık iyileştirme alanları. Onarım düğmelerinin ve "Taze başlat" taslağının dayanağı. |
| Shi vd. (2024), *WildFeedback* | Gerçek sohbetlerde memnuniyetsizliğin otomatik olarak etiketlenebildiğini gösteriyor; WildChat'te sohbetlerin yaklaşık %12'sinde memnuniyetsizlik var. |
| Liu vd. (2026), *Behavioral indicators of overreliance* | Aşırı güvenin davranış izleri (kopyala/yapıştır, görevi okumadan geçme) laboratuvarda görülüyor, ancak gerçek zamanlı bir dedektör için henüz yeterli değil. |

## 3. Kütüphaneler ve açık kaynak projeler

| Kaynak | Ne işe yarar | Not |
|---|---|---|
| [Hugging Face Datasets](https://huggingface.co/docs/datasets) | Büyük veri setlerini akış halinde okumak | WildChat 4.8M'yi tamamen indirmeden örneklem almak için |
| [sentence-transformers](https://www.sbert.net) ve [paraphrase-multilingual-MiniLM-L12-v2](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2) | Türkçe dahil çok dilli anlam benzerliği | Modelin ONNX sürümleri Hugging Face'te hazır; tarayıcıda Transformers.js ile çalışabilir |
| [Transformers.js](https://github.com/huggingface/transformers.js) | Hugging Face modellerini tarayıcıda çalıştırmak | Embedding benzerliği eklentiye eklenirse |
| [ONNX Runtime Web](https://onnxruntime.ai/docs/tutorials/web/) | Ağaç modellerini tarayıcıda çalıştırmak | XGBoost seçilirse; Logistic Regression için gerekmez, katsayılar JSON dosyası olarak yeterli |
| [chatgpt.js](https://github.com/KudoAI/chatgpt.js) | ChatGPT sayfasından mesajları okuyan hazır fonksiyonlar | MIT lisanslı; content script yazarken örnek alınabilir |
| [Clio](https://github.com/martymcenroe/Clio) | ChatGPT, Gemini ve Claude sohbetlerini yerelde okuyup dışa aktaran MV3 eklentisi | MIT lisanslı; üç platformun sayfa yapısını nasıl okuduğu ve testleri örnek alınabilir |
| [gemini-export](https://github.com/jujusharp/gemini-export) | Gemini sohbetlerini dışa aktarma | Gemini sayfa yapısı için ikinci bir örnek |

**Eklenti geliştirirken öğrenilmiş dersler**

- Sohbet arayüzleri cevabı parça parça yazar. Sayfa değişikliklerini izleyen kod cevabın yarısını yakalayabilir; cevabın bittiğini anlamak için kısa bir süre (yaklaşık yarım saniye) hiç değişiklik olmamasını beklemek gerekir.
- Sınıf adlarına dayanan seçiciler birkaç hafta içinde bozulabilir; sayfa yapısına dayanan seçiciler daha dayanıklıdır.

## 4. Hazır API'ler

| API | Ne için | Kullanım sınırı |
|---|---|---|
| Bir LLM API'si (ör. Gemini veya GPT) | Türkçe sohbetlerin ölçütlü etiketlenmesi | Yalnızca açık veri setindeki metinler gönderilir; pilot katılımcılarının verisi asla gönderilmez |
| Hugging Face Hub | Veri setlerini ve modelleri indirmek | Ürünün kendisi hiçbir API'ye bağlanmaz |

Ürünün kendisi hiçbir API kullanmaz. API'ler yalnızca geliştirme aşamasında, açık veri üzerinde kullanılır.
