// @vitest-environment jsdom
import { afterEach, describe, expect, it, vi } from "vitest";
import type { UserMessage } from "../adapters/types";
import { findPreviousMessage, jumpTo, scrollContainerOf, seekMessage } from "./jump";

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

/**
 * ChatGPT gibi sanal liste: 20 mesaj, her biri 500 piksel; yalnızca görünen alanın 1000 piksel
 * yakınındaki mesajlar "çizilir" (find yalnızca onları görür).
 */
function virtualList(scrollTop: number) {
  const container = document.createElement("div");
  let top = scrollTop;
  Object.defineProperty(container, "clientHeight", { value: 800 });
  Object.defineProperty(container, "scrollHeight", { value: 20 * 500 });
  Object.defineProperty(container, "scrollTop", {
    get: () => top,
    set: (v: number) => (top = Math.max(0, Math.min(v, 20 * 500 - 800))),
  });
  const items = Array.from({ length: 20 }, (_, i) => {
    const element = document.createElement("div");
    element.textContent = `soru ${i}`;
    return element;
  });
  const rendered = () => items.filter((_, i) => i * 500 > top - 1000 && i * 500 < top + 800 + 1000);
  return { container, items, rendered, top: () => top };
}

describe("seekMessage (sayfadan kaldırılmış eski mesaj)", () => {
  const noWait = async () => undefined;

  it("sayfadaysa kaydırmadan döner", async () => {
    const v = virtualList(9200);
    const el = await seekMessage(() => v.rendered().find((e) => e.textContent === "soru 19") ?? null, v.container, noWait);
    expect(el).toBe(v.items[19]);
    expect(v.top()).toBe(9200);
  });

  it("yukarıdaki eski mesajı kaydırarak bulur", async () => {
    const v = virtualList(9200);
    const el = await seekMessage(() => v.rendered().find((e) => e.textContent === "soru 0") ?? null, v.container, noWait);
    expect(el).toBe(v.items[0]);
  });

  it("aşağıdaki mesajı da bulur (kullanıcı yukarıdayken)", async () => {
    const v = virtualList(0);
    const el = await seekMessage(() => v.rendered().find((e) => e.textContent === "soru 18") ?? null, v.container, noWait);
    expect(el).toBe(v.items[18]);
  });

  it("bulunamazsa sohbet başladığı yere döner", async () => {
    const v = virtualList(4000);
    expect(await seekMessage(() => null, v.container, noWait)).toBeNull();
    expect(v.top()).toBe(4000);
  });
});

describe("scrollContainerOf", () => {
  it("kaydırılabilir ataya ulaşır, yoksa sayfanın kendisi", () => {
    const outer = document.createElement("div");
    outer.style.overflowY = "auto";
    Object.defineProperty(outer, "scrollHeight", { value: 2000 });
    Object.defineProperty(outer, "clientHeight", { value: 500 });
    const inner = document.createElement("div");
    outer.append(inner);
    document.body.append(outer);
    expect(scrollContainerOf(inner)).toBe(outer);
    expect(scrollContainerOf(null)).toBe(document.scrollingElement ?? document.documentElement);
    outer.remove();
  });
});

