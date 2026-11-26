import { build, context } from "esbuild";
import { cpSync, existsSync, mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";

const watch = process.argv.includes("--watch");

rmSync("dist", { recursive: true, force: true });
mkdirSync("dist", { recursive: true });
cpSync("public", "dist", { recursive: true });
// Montserrat (SIL OFL 1.1) yalnızca eklenti sayfaları için; ağdan değil pakete gömülü olarak gelir.
const FONT_DIR = "node_modules/@fontsource/montserrat/files";
mkdirSync("dist/fonts", { recursive: true });
for (const subset of ["latin", "latin-ext"]) {
  for (const weight of [400, 500, 600]) {
    const name = `montserrat-${subset}-${weight}-normal.woff2`;
    cpSync(`${FONT_DIR}/${name}`, `dist/fonts/${name}`);
  }
}
cpSync("node_modules/@fontsource/montserrat/LICENSE", "dist/fonts/OFL.txt");
// Anlam modelinin çalışma motoru (onnxruntime-web, MIT): WebAssembly dosyası ve onu yükleyen modül,
// pakete gömülü; gizli sayfa ikisini de eklentinin kendi adresinden okur (K52).
mkdirSync("dist/ort", { recursive: true });
for (const name of ["ort-wasm-simd-threaded.wasm", "ort-wasm-simd-threaded.mjs"]) {
  cpSync(`node_modules/onnxruntime-web/dist/${name}`, `dist/ort/${name}`);
}
writeFileSync("dist/ort/LICENSE.txt", "onnxruntime-web, Microsoft Corporation. MIT lisansı (package.json: license).\n");
// Model dosyası betikle üretilir (python scripts/build_semantic_model.py); yoksa Katman 2 sessizce kapalı kalır.
if (!existsSync("dist/models/minilm-tr/model.onnx")) {
  console.warn("UYARI: anlam modeli yok (extension/public/models/minilm-tr/model.onnx). Katman 2 çalışmaz; üretmek için: python scripts/build_semantic_model.py");
}

const options = {
  // Giriş listesi build-entries.json içinde; ağ testi de aynı listeyi okur.
  entryPoints: JSON.parse(readFileSync("build-entries.json", "utf8")).entries,
  outdir: "dist",
  bundle: true,
  format: "iife",
  target: "chrome120",
  sourcemap: true,
  logLevel: "info",
};

if (watch) {
  const ctx = await context(options);
  await ctx.watch();
  console.log("İzleniyor... (Ctrl+C ile çık)");
} else {
  await build(options);
}
