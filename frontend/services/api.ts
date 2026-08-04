// Default only used locally when NEXT_PUBLIC_API_BASE_URL is not set
const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000";

// Strip any trailing /api/v1 from the env var — the prefix is added automatically below
const _rawBase = (
	process.env.NEXT_PUBLIC_API_BASE_URL?.trim() ||
	process.env.API_BASE_URL?.trim() ||
	DEFAULT_API_BASE_URL
).replace(/\/api\/v1\/?$/, "");

export const API_BASE_URL = _rawBase;
const API_PREFIX = "/api/v1";

// During static generation, never block page export on backend availability.
export const IS_STATIC_GENERATION_BUILD =
	typeof window === "undefined" &&
	(process.env.NEXT_PHASE === "phase-production-build" ||
		process.env.npm_lifecycle_event === "build");

export const IS_API_CONFIGURED =
	Boolean(process.env.NEXT_PUBLIC_API_BASE_URL?.trim()) ||
	Boolean(process.env.API_BASE_URL?.trim());

// Log data-source once at module init (client-side only)
if (typeof window !== "undefined" && IS_API_CONFIGURED) {
	console.info(`[LeTrusto] Connected to API: ${API_BASE_URL}`);
}

function normalizePath(path: string): string {
	const p = path.startsWith("/") ? path : `/${path}`;
	// Always prepend /api/v1 — works whether NEXT_PUBLIC_API_BASE_URL has it or not
	return p.startsWith(API_PREFIX) ? p : `${API_PREFIX}${p}`;
}

export function buildQueryString(
	params: Record<string, string | number | boolean | undefined | null>
) {
	const searchParams = new URLSearchParams();

	for (const [key, value] of Object.entries(params)) {
		if (value === undefined || value === null || value === "") {
			continue;
		}

		searchParams.set(key, String(value));
	}

	const queryString = searchParams.toString();
	return queryString ? `?${queryString}` : "";
}

export async function apiRequest<T>(
	path: string,
	init?: RequestInit
): Promise<T> {
	const endpoint = `${API_BASE_URL}${normalizePath(path)}`;

	// Abort after 4s so SSG/ISR never hangs the build
	const controller = new AbortController();
	const timeoutId = setTimeout(() => controller.abort(), 4000);

	let response: Response;
	try {
		response = await fetch(endpoint, {
			...init,
			signal: controller.signal,
			headers: {
				"Content-Type": "application/json",
				...(init?.headers ?? {}),
			},
			next: { revalidate: 60 },
		});
	} finally {
		clearTimeout(timeoutId);
	}

	if (!response.ok) {
		console.error(`[LeTrusto] ${response.status} ${response.statusText} → ${endpoint}`);
		throw new Error(`API request failed (${response.status}) for ${endpoint}`);
	}

	return (await response.json()) as T;
}

export async function withApiFallback<T>(
	request: () => Promise<T>,
	fallback: () => T | Promise<T>
): Promise<T> {
	if (IS_STATIC_GENERATION_BUILD) {
		return fallback();
	}

	if (!IS_API_CONFIGURED) {
		return fallback();
	}

	try {
		return await request();
	} catch {
		// API unreachable at build time or runtime — fall back to mock data gracefully
		if (typeof window === "undefined") {
			console.warn("[LeTrusto] API unreachable at build time, using fallback data");
		}
		return fallback();
	}
}
