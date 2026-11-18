/** Doğrulama aralığı ve en uzun bekleme (K38; ChatGPT'de elle doğrulamada seçildi). */
export const CONFIRM_TICK_MS = 100;
export const CONFIRM_TIMEOUT_MS = 4000;

/** Sayfanın mesajı gerçekten gönderdiğini gösteren kanıtlar; her site kendi seçicileriyle verir. */
export interface SendEvidence<C extends HTMLElement> {
  /** Mesaj kutusundaki metin (kırpılmış). */
  composerText(composer: C): string;
  /** Sayfada çizili kullanıcı mesajı sayısı. */
  userCount(): number;
  /** Yapay zeka cevap üretiyor mu? */
  generating(): boolean;
}

/**
 * Gönderim doğrulaması (K38). Bir gönderme girişimi ancak sayfada gönderildiği görülünce sayılır:
 * kutu boşaldı, yeni kullanıcı mesajı belirdi ya da üretim başladı. Görülmezse sayılmaz.
 *
 * Neden: ChatGPT'de yeni sekmede Enter işlenmediği hâlde mesaj sayılıyor, kullanıcı yeniden
 * gönderince yanlış bir "benzer mesaj" şeridi çıkıyordu. Aynı risk her sitede var.
 *
 * Çift olay: bazı siteler Enter'dan sonra kendi Gönder düğmesine de tıklıyor. Doğrulanmayı bekleyen
 * aynı metnin ikinci olayı yeni bir girişim değildir (isSameSubmission); dokunulmaz.
 */
export class SendConfirmer<C extends HTMLElement> {
  private pending: { text: string; composer: C; users: number; startedAt: number } | null = null;
  private timer: number | undefined;

  constructor(
    private readonly evidence: SendEvidence<C>,
    private readonly onConfirmed: (text: string, now: number) => void,
    private readonly onNotSeen: () => void,
  ) {}

  /** Yeni bir gönderme girişimi. Önceki girişim hâlâ bekliyorsa önce o sonuçlanır. */
  begin(composer: C, text: string): void {
    if (this.pending) this.settle(this.pending.startedAt + CONFIRM_TIMEOUT_MS);
    this.pending = { text, composer, users: this.evidence.userCount(), startedAt: Date.now() };
    this.stopTimer();
    this.timer = window.setInterval(() => this.settle(Date.now()), CONFIRM_TICK_MS);
  }

  /** Doğrulanmayı bekleyen aynı gönderimin ikinci olayı mı? */
  isSameSubmission(composer: C, text: string): boolean {
    const p = this.pending;
    return p !== null && p.composer === composer && p.text === text && Date.now() - p.startedAt < CONFIRM_TIMEOUT_MS;
  }

  cancel(): void {
    this.stopTimer();
    this.pending = null;
  }

  private sent(p: NonNullable<SendConfirmer<C>["pending"]>): boolean {
    return (
      !p.composer.isConnected ||
      this.evidence.composerText(p.composer) === "" ||
      this.evidence.userCount() > p.users ||
      this.evidence.generating()
    );
  }

  private settle(now: number): void {
    const p = this.pending;
    if (!p) return;
    if (this.sent(p)) {
      this.cancel();
      this.onConfirmed(p.text, now);
    } else if (now - p.startedAt >= CONFIRM_TIMEOUT_MS) {
      this.cancel();
      this.onNotSeen();
    }
  }

  private stopTimer(): void {
    if (this.timer !== undefined) window.clearInterval(this.timer);
    this.timer = undefined;
  }
}
