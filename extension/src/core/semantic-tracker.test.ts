import { describe, expect, it, vi } from "vitest";
import { SemanticTracker } from "./semantic-tracker";

/** Sahte model: her metne sabit bir vektör; "başkent" geçen metinler aynı yöne bakar. */
const fakeEmbed = vi.fn(async (texts: string[]) =>
  texts.map((t) => (t.includes("başkent") || t.includes("baskent") ? [1, 0] : t.includes("uzun") ? [0.9, 0.436] : [0, 1])),
);

describe("SemanticTracker", () => {
  it("ilk mesajda modele hiç gitmez", async () => {
    const t = new SemanticTracker(fakeEmbed);
    fakeEmbed.mockClear();
    expect(await t.check("ankaranın başkenti neresidir")).toEqual({ same: false, score: 0 });
    expect(fakeEmbed).not.toHaveBeenCalled();
  });

  it("başka söyleniş aynı istek sayılır", async () => {
    const t = new SemanticTracker(fakeEmbed);
    t.remember("ankaranın başkenti neresidir?");
    const r = await t.check("ankaranın başkenti hangi şehir");
    expect(r?.same).toBe(true);
    expect(r?.score).toBeCloseTo(1);
  });

  it("model yüksek benzerlik verse de içerik kelimesi yer değiştirdiyse aynı istek sayılmaz", async () => {
    const t = new SemanticTracker(async (texts) => texts.map(() => [1, 0]));
    t.remember("metni daha kısa yaz");
    expect((await t.check("metni daha uzun yaz"))?.same).toBe(false);
  });

  it("model yoksa sonuç null; hafıza yalnızca son beş mesajı tutar", async () => {
    const t = new SemanticTracker(async () => null);
    for (let i = 0; i < 7; i++) t.remember(`mesaj ${i} hakkında bir soru`);
    expect(await t.check("başka bir soru")).toBeNull();
    const seen: string[][] = [];
    const t2 = new SemanticTracker(async (texts) => {
      seen.push(texts);
      return texts.map(() => [0, 1]);
    });
    for (let i = 0; i < 7; i++) t2.remember(`soru numara ${i} burada`);
    await t2.check("yeni bir istek");
    expect(seen[0]!.filter((x) => x.startsWith("soru numara"))).toHaveLength(5);
  });

  it("sonuç beklenirken eklenen mesaj karşılaştırmaya girmez; reset hafızayı siler", async () => {
    let release: (v: number[][]) => void = () => undefined;
    const t = new SemanticTracker((texts) => new Promise((r) => (release = () => r(texts.map(() => [1, 0])))));
    t.remember("ankaranın başkenti neresidir");
    const pending = t.check("ankaranın başkenti hangi şehir");
    t.remember("ankaranın başkenti hangi şehir");
    release([]);
    expect((await pending)?.same).toBe(true);
    t.reset();
    expect(await t.check("ankaranın başkenti nedir")).toEqual({ same: false, score: 0 });
  });
});
