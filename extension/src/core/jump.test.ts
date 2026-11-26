// @vitest-environment jsdom
import { afterEach, describe, expect, it, vi } from "vitest";
import type { UserMessage } from "../adapters/types";
import { findPreviousMessage, jumpTo } from "./jump";

function page(texts: string[]): UserMessage[] {
  document.body.replaceChildren();
  return texts.map((text) => {
    const element = document.createElement("div");
    element.textContent = text;
    document.body.append(element);
    return { element, text };
  });
}

describe("findPreviousMessage", () => {
  it("sadeleştirilmiş metni aynı olan en yeni mesajı bulur", () => {
    const messages = page(["Ankaranın başkenti neresidir?", "bugün hava nasıl", "ankaranın başkenti NERESİDİR"]);
    expect(findPreviousMessage(messages, "ankaranın başkenti neresidir")).toBe(messages[2]!.element);
  });

  it("küçük farklarla (satır sonu, fazladan boşluk) yine bulur", () => {
    const messages = page(["Bu metni\nkısalt ve maddeler halinde yaz lütfen", "başka bir soru"]);
    expect(findPreviousMessage(messages, "bu metni kısalt ve maddeler hâlinde yaz lütfen")).toBe(messages[0]!.element);
    // Sayfa metninin sonunda sitenin eklediği küçük bir fark ("Düzenlendi" gibi) olsa da bulur.
    const edited = page(["python ile bir csv dosyası nasıl okunur ve yazılır düzenlendi", "başka bir soru"]);
    expect(findPreviousMessage(edited, "python ile bir csv dosyası nasıl okunur ve yazılır")).toBe(edited[0]!.element);
  });

  it("dışarıda bırakılan metni (yeni mesajın kendisi) atlar", () => {
    const messages = page(["ankaranın başkenti neresidir?", "ankaranın başkenti hangi şehir"]);
    expect(findPreviousMessage(messages, "ankaranın başkenti neresidir?", "ankaranın başkenti hangi şehir")).toBe(messages[0]!.element);
    expect(findPreviousMessage(messages, "ankaranın başkenti hangi şehir", "ankaranın başkenti hangi şehir")).toBeNull();
  });

  it("sayfada yoksa ya da yalnızca benzeyen başka bir soru varsa null", () => {
    const messages = page(["python ile dosya nasıl okunur", "java ile dosya nasıl okunur"]);
    expect(findPreviousMessage(messages, "fransanın başkenti neresi")).toBeNull();
    expect(findPreviousMessage(messages, "c ile dosya nasıl okunur")).toBeNull();
    expect(findPreviousMessage([], "herhangi bir soru")).toBeNull();
    expect(findPreviousMessage(messages, "  ")).toBeNull();
  });
});

describe("jumpTo", () => {
  afterEach(() => {
    vi.useRealTimers();
  });

  it("öğeye kaydırır, vurgular ve öğenin stilini geri bırakır", () => {
    vi.useFakeTimers();
    const [message] = page(["ankaranın başkenti neresidir"]);
    const el = message!.element;
    el.style.scrollMarginTop = "4px";
    const scroll = vi.fn();
    const animate = vi.fn();
    Object.assign(el, { scrollIntoView: scroll, animate });
    expect(jumpTo(el)).toBe(true);
    expect(scroll).toHaveBeenCalledWith(expect.objectContaining({ block: "start" }));
    expect(el.style.scrollMarginTop).toBe("96px");
    expect(animate).toHaveBeenCalledTimes(1);
    vi.advanceTimersByTime(1000);
    expect(el.style.scrollMarginTop).toBe("4px");
    // jsdom'da öğenin konumu 0: ekranın üstünde sayılır, ikinci (anında) kaydırma gerekmez.
    expect(scroll).toHaveBeenCalledTimes(1);
  });

  it("yumuşak kaydırma ulaşmadıysa anında götürür", () => {
    vi.useFakeTimers();
    const [message] = page(["ankaranın başkenti neresidir"]);
    const el = message!.element;
    const scroll = vi.fn();
    Object.assign(el, { scrollIntoView: scroll, getBoundingClientRect: () => ({ top: -1500 }) as DOMRect });
    jumpTo(el);
    vi.advanceTimersByTime(1000);
    expect(scroll).toHaveBeenCalledTimes(2);
    expect(scroll).toHaveBeenLastCalledWith(expect.objectContaining({ behavior: "auto" }));
  });

  it("sayfadan kaldırılmış öğede hiçbir şey yapmaz", () => {
    const el = document.createElement("div");
    const scroll = vi.fn();
    Object.assign(el, { scrollIntoView: scroll });
    expect(jumpTo(el)).toBe(false);
    expect(scroll).not.toHaveBeenCalled();
  });
});
