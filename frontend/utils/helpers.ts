export function getSearchParamValue(
	value: string | string[] | undefined,
	fallback = ""
) {
	if (Array.isArray(value)) {
		return value[0] ?? fallback;
	}

	return value ?? fallback;
}

