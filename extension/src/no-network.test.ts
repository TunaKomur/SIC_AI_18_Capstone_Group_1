import { build } from "esbuild";
import { describe, expect, it } from "vitest";
import buildEntries from "../build-entries.json";
import platforms from "./data/platforms.json";
import manifest from "../public/manifest.json";

/**
 * Gizlilik sözünün denetimi: eklenti internete hiçbir istek göndermez.
 *
 * İki ayrı güvence var:
 *  1. İçerik betiği, arka plan çalışanı, araç çubuğu penceresi ve karşılama ekranı: derlenmiş kodda
 *     ağ isteği yapabilen hiçbir API geçmez (aşağıdaki FORBIDDEN listesi). İçerik betiği sohbet
 *     sitesinin sayfasında, o sayfanın kurallarıyla çalıştığı için onun güvencesi tarayıcıdan değil,
 *     bu testten gelir.
 *  2. Anlam modelinin gizli sayfası (offscreen, K52): model ve çalışma motoru eklentinin kendi
 *     dosyalarından okunduğu için bu sayfada fetch vardır. Güvence tarayıcı düzeyindedir: eklenti
 *     sayfalarının güvenlik kuralı connect-src 'self', yani yalnızca eklentinin kendi adresine
 *     (chrome-extension://…) izin verir; başka her adrese istek tarayıcı tarafından engellenir.
 *     Test bu kuralın tam olarak böyle kaldığını ve sayfanın kodunda uzak bir adres olmadığını denetler.
 */
const FORBIDDEN = ["fetch", "XMLHttpRequest", "WebSocket", "sendBeacon", "EventSource", "importScripts"];

const ENTRIES = buildEntries.entries as Record<string, string>;
/** Kendi dosyalarını okuyan tek giriş: anlam modelinin gizli sayfası. */
const OWN_FILE_READERS = new Set(["offscreen"]);
const STRICT = Object.entries(ENTRIES).filter(([name]) => !OWN_FILE_READERS.has(name));
/**
 * onnxruntime-web kodunda hata iletisi içinde geçen belge adresi; istek değil, metin.
 * (SharedArrayBuffer yoksa "çok iş parçacığı için şu sayfaya bakın" der.)
 */
const OFFSCREEN_TEXT_URLS = new Set(["https://web.dev/cross-origin-isolation-guide/"]);
// SVG ad alanı bir web adresine benzer ama ağ isteği değildir: logo DOM API ile çizilirken gerekir.
const SVG_NAMESPACE = "http://www.w3.org/2000/svg";
const ALLOWED_URLS = new Set([...Object.values(platforms.platforms).flatMap((p) => p.matches), SVG_NAMESPACE]);

/** ownOnly: yalnızca projenin kendi kodu (node_modules dışarıda bırakılır). */
async function bundle(entry: string, opts: { ownOnly?: boolean } = {}): Promise<string> {
  const result = await build({
    entryPoints: [entry],
    bundle: true,
    packages: opts.ownOnly ? "external" : undefined,
    format: "iife",
    target: "chrome120",
    write: false,
    minify: false,
    logLevel: "silent",
  });
  return result.outputFiles.map((f) => f.text).join("\n");
}

describe("ağ isteği yok", () => {
  it.each(STRICT)("%s derlemesinde ağ API'si geçmiyor", async (_name, entry) => {
    const code = await bundle(entry);
    for (const word of FORBIDDEN) {
      expect(new RegExp(`\\b${word}\\b`).test(code), `${entry}: ${word}`).toBe(false);
    }
  });

  it.each(STRICT)("%s derlemesinde izinli platform adresleri dışında web adresi yok", async (_name, entry) => {
    const code = await bundle(entry);
    const urls = code.match(/https?:\/\/[^\s"'`)]+/g) ?? [];
    for (const u of urls) expect(ALLOWED_URLS.has(u), `${entry}: ${u}`).toBe(true);
    expect(/\beval\s*\(|new Function\s*\(/.test(code), `${entry}: eval`).toBe(false);
  });

  it("giriş listesi boş değil ve üç temel giriş yerinde", () => {
    expect(Object.keys(ENTRIES)).toEqual(expect.arrayContaining(["content", "background", "popup"]));
  });

  it("eklenti sayfaları ve arka plan çalışanı yalnızca eklentinin kendi dosyalarına istek gönderebilir", () => {
    const csp = manifest.content_security_policy.extension_pages;
    const directives = Object.fromEntries(
      csp.split(";").map((d) => d.trim().split(/\s+/)).map(([name, ...values]) => [name, values]),
    ) as Record<string, string[]>;
    expect(directives["connect-src"]).toEqual(["'self'"]);
    // Uzaktan kod yok; yalnızca WebAssembly derlemesine izin (anlam modelinin motoru).
    expect(directives["script-src"]).toEqual(["'self'", "'wasm-unsafe-eval'"]);
    expect(csp).not.toMatch(/https?:|\*|data:|blob:/);
  });

  it("gizli sayfa kodunda uzak adres ve eval yok; fetch yalnızca eklentinin kendi adresiyle", async () => {
    const code = await bundle(ENTRIES["offscreen"]!);
    const urls = code.match(/https?:\/\/[^\s"'`)]+/g) ?? [];
    for (const u of urls) expect(OFFSCREEN_TEXT_URLS.has(u), `offscreen: ${u}`).toBe(true);
    expect(/\beval\s*\(|new Function\s*\(/.test(code), "offscreen: eval").toBe(false);
    const own = await bundle("src/offscreen/index.ts", { ownOnly: true });
    const fetches = own.match(/\bfetch\s*\([^)]*\)/g) ?? [];
    expect(fetches.length).toBeGreaterThan(0);
    for (const f of fetches) expect(f, "fetch yalnızca chrome.runtime.getURL ile").toMatch(/chrome\.runtime\.getURL/);
  });

  it("içerik betiği modeli çalıştırmaz (model motoru yalnızca gizli sayfada)", async () => {
    const code = await bundle(ENTRIES["content"]!);
    expect(code).not.toMatch(/InferenceSession|onnxruntime/);
  });

  it("manifest yalnızca depolama, pano ve gizli sayfa izni istiyor", () => {
    expect([...manifest.permissions].sort()).toEqual(["clipboardWrite", "offscreen", "storage"]);
  });
});
