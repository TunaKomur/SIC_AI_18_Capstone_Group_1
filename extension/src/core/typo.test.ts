import { describe, expect, it } from "vitest";
import fixture from "../../../tests/fixtures/typo_parity.json";
import { RepeatDetector } from "./repeat-detector";
import { normalizeText } from "./text";
import { alignTypos, osaDistance, typoMatch } from "./typo";
import { cosine, ngramVector } from "./similarity";

describe("yazım hatası toleransı (Katman 1)", () => {
  it("kullanıcının örneği: ağır yazım hatası birebir tekrar sayılır ve gönderim bekletilir", () => {
    const d = new RepeatDetector();
    d.remember("ankaranın başkenti neresidir?");
    const r = d.check("anksrabın baskebti neresifir");
    expect(r.similar).toBe(true);
    expect(r.hold).toBe(true);
    expect(r.score).toBeGreaterThanOrEqual(0.99);
  });

  it("Türkçe karaktersiz yazım birebir tekrar sayılır", () => {
    const d = new RepeatDetector();
    d.remember("Bu cümleyi İngilizceye çevir");
    expect(d.check("bu cumleyi ingilizceye cevir").hold).toBe(true);
  });

  it("sayı ve sıra kelimeleri düzeltilmez: farklı istekler tekrar sayılmaz", () => {
    const d = new RepeatDetector();
    d.remember("ikinci dünya savaşının sebeplerini yaz");
    const r = d.check("birinci dünya savaşının sebeplerini yaz");
    expect(r.similar).toBe(false);
    expect(r.hold).toBe(false);
  });

  it("anlamı tersine çeviren ekler ve olumsuzluk eki yazım hatası sayılmaz", () => {
    expect(typoMatch("kaynakçasız", ["kaynakçalı"])).toBeNull();
    expect(typoMatch("düzeltme", ["düzelt"])).toBeNull();
    expect(typoMatch("ungrammaticality", ["grammaticality"])).toBeNull();
    const d = new RepeatDetector();
    d.remember("bu ödevi kaynakçalı yaz");
    expect(d.check("bu ödevi kaynakçasız yaz").hold).toBe(false);
  });

  it("farklı özel ad yazım hatası sayılmaz", () => {
    const d = new RepeatDetector();
    d.remember("türkiyenin başkenti neresi");
    expect(d.check("amerikanın başkenti neresi").similar).toBe(false);
  });

  it("tek harf fazlası ya da eksiği yazım hatası sayılır", () => {
    expect(typoMatch("özetlee", ["özetle"])).toBe("özetle");
    expect(typoMatch("ban", ["bana"])).toBe("bana");
  });

  it("düzeltilmiş metin yalnızca karşılaştırmada kullanılır; hiçbir şey saklanmaz", () => {
    const d = new RepeatDetector();
    d.remember("python ile dosya nasıl okunur");
    d.check("pyhton ile dosya nasıl okunr");
    // remember çağrılmadıkça yeni mesaj hafızaya girmez
    d.reset();
    expect(d.check("pyhton ile dosya nasıl okunr").similar).toBe(false);
  });
});

describe("Python ile aynı sonuç (tests/fixtures/typo_parity.json)", () => {
  it("düzenleme uzaklığı", () => {
    for (const row of fixture.distances) expect([row.a, row.b, osaDistance(row.a, row.b)]).toEqual([row.a, row.b, row.distance]);
  });

  it("düzeltilmiş metin ve benzerlik", () => {
    for (const row of fixture.pairs) {
      const prev = normalizeText(row.previous);
      const neu = normalizeText(row.new);
      const aligned = alignTypos(neu, prev);
      expect([row.new, aligned]).toEqual([row.new, row.aligned]);
      const score = Math.max(cosine(ngramVector(neu), ngramVector(prev)), cosine(ngramVector(aligned), ngramVector(prev)));
      expect(Math.abs(score - row.score)).toBeLessThan(1e-5);
    }
  });
});
