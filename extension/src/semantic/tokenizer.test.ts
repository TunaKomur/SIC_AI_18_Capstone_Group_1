// @ts-expect-error: test Node üzerinde çalışır; Node tip tanımları eklenti derlemesine bilerek dahil değil
import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import fixture from "../../../tests/fixtures/semantic_parity.json";
import { UnigramTokenizer, type TokenizerJson } from "./tokenizer";

const json = JSON.parse(readFileSync(new URL("../../public/models/minilm-tr/tokenizer.json", import.meta.url), "utf8")) as TokenizerJson;
const tokenizer = new UnigramTokenizer(json);

describe("kelime bölücü (Unigram)", () => {
  it("Python (Hugging Face tokenizers) ile aynı parçaları verir", () => {
    for (const row of fixture.tokens) expect([row.text, tokenizer.encode(row.text)]).toEqual([row.text, row.ids]);
  });

  it("en çok 128 parça; baştaki ve sondaki özel parçalar korunur", () => {
    const ids = tokenizer.encode(Array.from({ length: 300 }, () => "kelime").join(" "));
    expect(ids).toHaveLength(128);
    expect(ids[0]).toBe(0);
    expect(ids[127]).toBe(2);
  });

  it("sözlükte olmayan harfler tek bir bilinmeyen parçaya iner", () => {
    const ids = tokenizer.encode("☃☃☃");
    expect(ids.filter((id) => id === json.model.unk_id)).toHaveLength(1);
  });
});
