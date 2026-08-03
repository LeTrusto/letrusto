const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000";

export const API_BASE_URL =
	process.env.NEXT_PUBLIC_API_BASE_URL?.trim() ||
	process.env.API_BASE_URL?.trim() ||
	DEFAULT_API_BASE_URL;

export const IS_API_CONFIGURED =
	Boolean(process.env.NEXT_PUBLIC_API_BASE_URL?.trim()) ||
	Boolean(process.env.API_BASE_URL?.trim());

// Log data-source once at module init (client-side only)
if (typeof window !== "undefined") {
	if (IS_API_CONFIGURED) {
		console.info(`[LeTrusto] Data source: PostgreSQL`);
		console.info(`[LeTrusto] API_BASE_URL = "${API_BASE_URL}"`);
		console.info(`[LeTrusto] Sample URL: "${API_BASE_URL}/products/metadata"`);
		console.info(`[LeTrusto] Sample URL: "${API_BASE_URL}/products/collections/home"`);
		console.info(`[LeTrusto] Expected: these URLs must return HTTP 200`);
	} else {
		console.warn("[LeTrusto] Data source: Local mock data (set NEXT_PUBLIC_API_BASE_URL to connect to backend)");
	}
}

function normalizePath(path: string) {
	if (!path) {
		return "/";
	}

	return path.startsWith("/") ? path : `/${path}`;
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
	const response = await fetch(endpoint, {
		...init,
		headers: {
			"Content-Type": "application/json",
			...(init?.headers ?? {}),
		},
		next: { revalidate: 60 },
	});

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
	if (!IS_API_CONFIGURED) {
		return fallback();
	}

	try {
		return await request();
	} catch (error) {
		// API unreachable at build time or runtime — fall back to mock data gracefully
		if (typeof window === "undefined") {
			console.warn("[LeTrusto] API unreachable at build time, using fallback data");
		}
		return fallback();
	}
}
