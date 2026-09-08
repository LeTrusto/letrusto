const checkoutScript = "https://checkout.razorpay.com/v1/checkout.js";

let loadPromise: Promise<void> | null = null;

export function loadRazorpay(): Promise<void> {
  if (isRazorpayReady()) return Promise.resolve();
  if (loadPromise) return loadPromise;

  loadPromise = new Promise<void>((resolve, reject) => {
    if (typeof document === "undefined") {
      reject(new Error("Razorpay Checkout could not be loaded."));
      return;
    }

    const existingScript = document.querySelector<HTMLScriptElement>(`script[src="${checkoutScript}"]`);
    const script = existingScript ?? document.createElement("script");
    if (!existingScript) {
      script.src = checkoutScript;
      script.async = true;
      document.head.appendChild(script);
    }

    const complete = () => {
      if (isRazorpayReady()) resolve();
      else reject(new Error("Razorpay Checkout could not be loaded."));
    };
    script.addEventListener("load", complete, { once: true });
    script.addEventListener("error", () => reject(new Error("Razorpay Checkout could not be loaded.")), { once: true });
  }).catch((error) => {
    loadPromise = null;
    throw error;
  });

  return loadPromise;
}

export function isRazorpayReady(): boolean {
  return typeof window !== "undefined" && Boolean((window as Window & { Razorpay?: unknown }).Razorpay);
}

export const RAZORPAY_CHECKOUT_SCRIPT_URL = checkoutScript;