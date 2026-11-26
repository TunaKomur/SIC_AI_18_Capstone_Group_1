"""Anlam modelini (Katman 2, K52) indirir ve Türkçe ile İngilizceye kırpar.

Ne yapar:
    1. Hugging Face'ten sabit sürümle iki dosya indirir: nicemlenmiş ONNX model (yaklaşık 118 MB)
       ve kelime bölücü (tokenizer.json). SHA-256 özetleri extension/src/data/semantic-rules.json
       ile karşılaştırılır; tutmazsa durur.
    2. Kelime tablosunu scripts/data/semantic_keep_ids.json listesindeki parçalara indirir
       (250.002 parçadan 44.612'ye). Liste scripts/make_semantic_vocab.py ile üretildi: Türkçe
       (quora-tr) ve Latin harfli İngilizce (WildFeedback) metinlerde en az iki kez geçen parçalar,
       tek harfli Latin ve Türkçe parçalar ve özel parçalar.
    3. extension/public/models/minilm-tr/ altına model.onnx (yaklaşık 39 MB) ve tokenizer.json yazar.
       tokenizer.json depoda da var; betik aynı dosyayı üretmezse uyarır.

Model dosyası depoya girmez (.gitignore). Eklentiyi derlemeden önce bir kez çalıştırılır:
    pip install onnx
    python scripts/build_semantic_model.py

İnternet gerekir (yalnızca bu betik; eklentinin kendisi hiçbir zaman ağa çıkmaz).
"""

import hashlib
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULES = json.loads((ROOT / "extension" / "src" / "data" / "semantic-rules.json").read_text(encoding="utf-8"))
KEEP = ROOT / "scripts" / "data" / "semantic_keep_ids.json"
OUT_DIR = ROOT / "extension" / "public" / RULES["model"]["dir"]
CACHE = ROOT / "data" / "raw" / "semantic_model"
TOKENIZER_SHA256 = "b60b6b43406a48bf3638526314f3d232d97058bc93472ff2de930d43686fa441"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download(file, expected):
    m = RULES["model"]
    target = CACHE / Path(file).name
    if not target.exists() or sha256(target) != expected:
        target.parent.mkdir(parents=True, exist_ok=True)
        url = f"https://huggingface.co/{m['source_repo']}/resolve/{m['source_revision']}/{file}"
        print(f"İndiriliyor: {url}")
        urllib.request.urlretrieve(url, target)
    got = sha256(target)
    if got != expected:
        sys.exit(f"{file}: SHA-256 tutmuyor ({got}); indirme bozuk ya da dosya değişmiş.")
    return target


def trim_tokenizer(source, keep):
    """Kelime tablosunu keep listesine indirir; <mask> en sona taşınır. Sonuç deterministiktir."""
    t = json.loads(Path(source).read_text(encoding="utf-8"))
    vocab = t["model"]["vocab"]
    old2new = {old: new for new, old in enumerate(keep)}
    mask_id = len(keep)
    t["model"]["vocab"] = [vocab[old] for old in keep] + [["<mask>", 0.0]]
    t["model"]["unk_id"] = old2new[t["model"]["unk_id"]]
    t["added_tokens"] = [dict(a, id=old2new.get(a["id"], mask_id)) for a in t["added_tokens"]]
    return json.dumps(t, ensure_ascii=False)


def trim_model(source, keep, mask_old_id):
    import numpy as np
    import onnx
    from onnx import numpy_helper

    model = onnx.load(str(source))
    name = RULES["model"]["embedding_initializer"]
    for init in model.graph.initializer:
        if init.name == name:
            weights = numpy_helper.to_array(init)
            rows = np.concatenate([weights[keep], weights[mask_old_id:mask_old_id + 1]])
            init.CopyFrom(numpy_helper.from_array(rows, name))
            print(f"Kelime tablosu: {weights.shape[0]:,} satır -> {rows.shape[0]:,} satır")
            return model
    sys.exit(f"Modelde {name} bulunamadı.")


def main():
    keep = json.loads(KEEP.read_text(encoding="utf-8"))
    model_src = download(RULES["model"]["source_file"], RULES["model"]["source_sha256"])
    tok_src = download("tokenizer.json", TOKENIZER_SHA256)
    src_tok = json.loads(tok_src.read_text(encoding="utf-8"))
    mask_old = next(a["id"] for a in src_tok["added_tokens"] if a["content"] == "<mask>")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tokenizer = trim_tokenizer(tok_src, keep)
    tok_out = OUT_DIR / "tokenizer.json"
    if tok_out.exists() and tok_out.read_text(encoding="utf-8") != tokenizer:
        print("UYARI: depodaki tokenizer.json bu betiğin ürettiğinden farklı; yeniden yazılıyor.")
    tok_out.write_text(tokenizer, encoding="utf-8")

    import onnx
    model = trim_model(model_src, keep, mask_old)
    model_out = OUT_DIR / "model.onnx"
    onnx.save(model, str(model_out))
    print(f"Yazıldı: {model_out.relative_to(ROOT)} ({model_out.stat().st_size / 1e6:.1f} MB)")
    print(f"Yazıldı: {tok_out.relative_to(ROOT)} ({tok_out.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
