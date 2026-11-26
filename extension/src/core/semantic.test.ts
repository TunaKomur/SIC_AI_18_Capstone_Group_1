import { describe, expect, it } from "vitest";
import fixture from "../../../tests/fixtures/semantic_parity.json";
import { isSwap, sameIntent, swappedContent } from "./semantic";

describe("Katman 2: 'aynı istek' kuralı ve bekçi", () => {
  it("içerik kelimesi yer değiştirince aynı istek sayılmaz", () => {
    expect(isSwap("metni daha kısa yaz", "metni daha uzun yaz")).toBe(true);
    expect(isSwap("python ile dosya nasıl okunur", "java ile dosya nasıl okunur")).toBe(true);
    expect(isSwap("1. soruyu çöz", "2. soruyu çöz")).toBe(true);
    expect(sameIntent(0.99, "metni daha kısa yaz", "metni daha uzun yaz")).toBe(false);
  });

  it("aynı sorunun başka söylenişi ve yazım hatalı hâli aynı istek sayılır", () => {
    expect(isSwap("ankaranın başkenti neresidir?", "ankaranın başkenti hangi şehir")).toBe(false);
    expect(isSwap("ankaranın başkenti neresidir?", "anksrabın baskebti neresifir")).toBe(false);
    expect(sameIntent(0.9, "ankaranın başkenti neresidir?", "ankaranın başkenti nedir")).toBe(true);
    expect(sameIntent(0.7, "ankaranın başkenti neresidir?", "ankaranın başkenti nedir")).toBe(false);
  });

  it("Python ile aynı karar (tests/fixtures/semantic_parity.json)", () => {
    for (const row of fixture.pairs) {
      expect([row.new, swappedContent(row.previous, row.new)]).toEqual([row.new, [row.only_old, row.only_new]]);
      expect([row.new, sameIntent(row.score, row.previous, row.new)]).toEqual([row.new, row.same]);
    }
  });
});
