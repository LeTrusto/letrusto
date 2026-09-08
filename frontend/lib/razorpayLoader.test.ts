import { beforeEach, describe, expect, it, vi } from "vitest";

type FakeScript = {
  src: string;
  async: boolean;
  addEventListener: (event: string, handler: () => void, options?: { once?: boolean }) => void;
  dispatchEvent: (event: Event) => void;
};

function createDocumentStub() {
  let script: FakeScript | null = null;
  const listeners = new Map<string, Array<() => void>>();
  script = {
    src: "",
    async: false,
    addEventListener: (event, handler) => {
      listeners.set(event, [...(listeners.get(event) ?? []), handler]);
    },
    dispatchEvent: (event) => {
      for (const handler of listeners.get(event.type) ?? []) handler();
    },
  };
  return {
    head: { appendChild: () => undefined },
    querySelector: () => script,
    createElement: () => script,
  };
}

describe("Razorpay loader", () => {
  let loadRazorpay: typeof import("@/lib/razorpayLoader").loadRazorpay;
  let isRazorpayReady: typeof import("@/lib/razorpayLoader").isRazorpayReady;
  let checkoutScript: typeof import("@/lib/razorpayLoader").RAZORPAY_CHECKOUT_SCRIPT_URL;

  beforeEach(() => {
    vi.resetModules();
    vi.stubGlobal("window", { Razorpay: undefined });
    vi.stubGlobal("document", createDocumentStub());
  });

  it("waits for the SDK load event before reporting readiness", async () => {
    ({ loadRazorpay, isRazorpayReady, RAZORPAY_CHECKOUT_SCRIPT_URL: checkoutScript } = await import("@/lib/razorpayLoader"));
    const loading = loadRazorpay();
    const script = document.querySelector(`script[src="${checkoutScript}"]`) as unknown as FakeScript;

    expect(script).not.toBeNull();
    expect(isRazorpayReady()).toBe(false);

    window.Razorpay = class {} as never;
    script?.dispatchEvent(new Event("load"));

    await expect(loading).resolves.toBeUndefined();
    expect(isRazorpayReady()).toBe(true);
  });

  it("shares one pending load and reports a distinct load failure", async () => {
    ({ loadRazorpay, RAZORPAY_CHECKOUT_SCRIPT_URL: checkoutScript } = await import("@/lib/razorpayLoader"));
    const first = loadRazorpay();
    const second = loadRazorpay();
    const script = document.querySelector(`script[src="${checkoutScript}"]`) as unknown as FakeScript;

    expect(first).toBe(second);
    script?.dispatchEvent(new Event("error"));

    await expect(first).rejects.toThrow("Razorpay Checkout could not be loaded.");
  });
});