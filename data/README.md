# Veri

Bu klasörde ham veri tutulmaz. Kullandığımız ve kullanacağımız (sonradan kapsam büyüyecek) veri setleri büyük boyutludur ve lisans koşulları yeniden dağıtımı sınırlayabilir (özellikle LMSYS Chat 1M). Notebooklar veriyi doğrudan Hugging Face üzerinden okur.

İlk analiz ve girişgah için kullanılan, incelenen datasetleri şu şekildedir.


| Veri seti            | Kaynak                                                                                                       | Lisans                                  |
| -------------------- | ------------------------------------------------------------------------------------------------------------ | --------------------------------------- |
| WildChat 1M          | [https://huggingface.co/datasets/allenai/WildChat-1M](https://huggingface.co/datasets/allenai/WildChat-1M)   | ODC BY                                  |
| LMSYS Chat 1M        | [https://huggingface.co/datasets/lmsys/lmsys-chat-1m](https://huggingface.co/datasets/lmsys/lmsys-chat-1m)   | LMSYS Chat 1M Dataset License Agreement |
| OpenAssistant OASST1 | [https://huggingface.co/datasets/OpenAssistant/oasst1](https://huggingface.co/datasets/OpenAssistant/oasst1) | Apache 2.0                              |


Yerelde veri indirmeniz gerekirse `data/raw/` ve `data/processed/` klasörlerini kullanın. Bu klasörler `.gitignore` ile repo dışında tutulur.