/**
 * Onarım düğmeleri: kullanıcının "neyin eksik olduğunu" söylemesinin hazır yolları.
 * Seçilen cümle mesaj kutusuna eklenir; kullanıcı tamamlayıp kendisi gönderir.
 * Cümleler iki türlüdür: iki nokta ile bitenler kullanıcının devam etmesini bekler.
 */
export interface Repair {
  id: "format" | "info" | "shorter" | "longer" | "error" | "expected" | "wrong_part" | "continue_what" | "continue_how" | "summary";
  label: string;
  sentence: string;
}

export const REPAIRS: readonly Repair[] = [
  {
    id: "format",
    label: "Biçim yanlış",
    sentence: "Cevabın içeriği doğru ama biçimi istediğim gibi değil. Şu biçimde yaz: ",
  },
  {
    id: "info",
    label: "Bilgi yanlış",
    sentence: "Önceki cevabın yanlış olan kısmını düzelt, gerisine dokunma. Yanlış olan kısım: ",
  },
  { id: "shorter", label: "Fazla uzun", sentence: "Aynı cevabı daha kısa yaz." },
  { id: "longer", label: "Fazla kısa", sentence: "Aynı cevabı daha ayrıntılı yaz." },
];

/**
 * Kısa onarım şeridi ("olmadı", "yanlış"): mesajın kendisi zaten memnuniyetsizliği söylüyor,
 * eksik olan neyin olmadığı. Kod isteklerinde hata mesajı, diğerlerinde yanlış olan kısım istenir.
 */
export function shortRepairs(task: string | null): readonly Repair[] {
  const first: Repair =
    task === "kod"
      ? { id: "error", label: "Hata mesajını ekle", sentence: "Aldığım hata mesajı: " }
      : { id: "wrong_part", label: "Neyin yanlış olduğunu yaz", sentence: "Yanlış olan kısım: " };
  return [first, { id: "expected", label: "Beklediğimi yaz", sentence: "Beklediğim sonuç: " }];
}

/**
 * Aynı kısa mesaj ("devam") üçüncü kez gönderilmek üzereyken: model neyle ve nasıl devam edeceğini
 * tahmin ediyor; yönü kullanıcı bir cümleyle belirler.
 */
export const CONTINUE_REPAIRS: readonly Repair[] = [
  { id: "continue_what", label: "Neyle devam etsin, yaz", sentence: "Şununla devam et: " },
  { id: "continue_how", label: "Nasıl devam etsin, yaz", sentence: "Bundan sonra şu şekilde devam et: " },
];

/** Kısa onay zincirinden sonra: modelden şu ana kadar anladığını özetlemesini isteyen hazır cümle. */
export const SUMMARY_REPAIR: Repair = {
  id: "summary",
  label: "Özetlet",
  sentence:
    "Devam etmeden önce şu ana kadar ne istediğimi nasıl anladığını üç maddede özetle ve bir sonraki adım için bana seçenekler sun.",
};
