import { products, categoryLabels, categoryPluralLabels, productSpotlightBadges } from "@/lib/products";
import { filterProducts } from "@/lib/filterProducts";
import { sortProducts } from "@/lib/sortProducts";
import {
	buildCompareHref,
	discoverProducts,
	getRelatedProducts,
	recommendProducts,
	resolveCompareProducts,
} from "@/lib/recommendations";
import type {
	PaginatedProductsResponse,
	Product,
	ProductAiScoreFilter,
	ProductFilterState,
	ProductPriceFilter,
	ProductQueryOptions,
	ProductRatingFilter,
	ProductSortOption,
} from "@/types/products";

import { apiRequest, buildQueryString, withApiFallback } from "@/services/api";

const DEFAULT_PAGE_SIZE = 12;

function toNumber(value: unknown): number {
	if (typeof value === "number" && Number.isFinite(value)) {
		return value;
	}

	if (typeof value === "string") {
		const parsed = Number(value);
		if (Number.isFinite(parsed)) {
			return parsed;
		}
	}

	return 0;
}

function normalizeProduct(product: Product): Product {
	return {
		...product,
		priceValue: toNumber(product.priceValue),
		rating: toNumber(product.rating),
		aiScore: toNumber(product.aiScore),
		priceHistory: product.priceHistory.map((point) => ({
			...point,
			price: toNumber(point.price),
		})),
		reviews: product.reviews.map((review) => ({
			...review,
			rating: toNumber(review.rating),
		})),
	};
}

function clampPage(value: number) {
	if (!Number.isFinite(value) || value < 1) {
		return 1;
	}

	return Math.floor(value);
}

function normalizeFilters(options: ProductQueryOptions): ProductFilterState {
	return {
		category: options.category ?? "all",
		price: options.price ?? "all",
		rating: options.rating ?? "all",
		aiScore: options.aiScore ?? "all",
	};
}

function applyAdvancedFilters(productsToFilter: Product[], options: ProductQueryOptions) {
	const normalizedBrand = options.brand?.toLowerCase().trim();

	return productsToFilter.filter((product) => {
		if (normalizedBrand && product.brand.toLowerCase() !== normalizedBrand) {
			return false;
		}

		if (options.minPrice !== undefined && product.priceValue < options.minPrice) {
			return false;
		}

		if (options.maxPrice !== undefined && product.priceValue > options.maxPrice) {
			return false;
		}

		if (options.minRating !== undefined && product.rating < options.minRating) {
			return false;
		}

		if (options.minAiScore !== undefined && product.aiScore < options.minAiScore) {
			return false;
		}

		return true;
	});
}

function buildLocalSearchResponse(options: ProductQueryOptions): PaginatedProductsResponse {
	const query = (options.q ?? "").trim();
	const filters = normalizeFilters(options);
	const sortBy = options.sortBy ?? "relevance";

	const discovered = discoverProducts(query);
	const filtered = filterProducts(discovered, filters);
	const advancedFiltered = applyAdvancedFilters(filtered, options);
	const sorted = sortProducts(advancedFiltered, sortBy, query);

	const page = clampPage(options.page ?? 1);
	const pageSize = Math.max(1, Math.floor(options.pageSize ?? DEFAULT_PAGE_SIZE));
	const totalItems = sorted.length;
	const totalPages = Math.max(1, Math.ceil(totalItems / pageSize));
	const safePage = Math.min(page, totalPages);
	const start = (safePage - 1) * pageSize;
	const end = start + pageSize;

	return {
		items: sorted.slice(start, end),
		pagination: {
			page: safePage,
			pageSize,
			totalItems,
			totalPages,
			hasNextPage: safePage < totalPages,
			hasPreviousPage: safePage > 1,
		},
	};
}

export async function getAllProducts() {
	return withApiFallback(
		() => apiRequest<Product[]>("/products").then((catalog) => catalog.map(normalizeProduct)),
		() => products
	);
}

export async function getProductById(productId: string) {
	return withApiFallback(
		() => apiRequest<Product>(`/products/${productId}`).then((product) => normalizeProduct(product)),
		() => products.find((product) => product.id === productId) ?? null
	);
}

export async function getProductsByIds(productIds: string[]) {
	const idSet = new Set(productIds);

	return withApiFallback(
		() =>
			apiRequest<Product[]>(`/products${buildQueryString({ ids: productIds.join(",") })}`).then((catalog) =>
				catalog.map(normalizeProduct)
			),
		() => products.filter((product) => idSet.has(product.id))
	);
}

export async function getProductSearch(options: ProductQueryOptions): Promise<PaginatedProductsResponse> {
	return withApiFallback(
		() =>
			apiRequest<PaginatedProductsResponse>(
				`/products/search${buildQueryString({
					q: options.q,
					sort: options.sortBy,
					category: options.category,
					price: options.price,
					rating: options.rating,
					aiScore: options.aiScore,
					brand: options.brand,
					minPrice: options.minPrice,
					maxPrice: options.maxPrice,
					minRating: options.minRating,
					minAiScore: options.minAiScore,
					page: options.page,
					pageSize: options.pageSize,
				})}`
			).then((response) => ({
				...response,
				items: response.items.map(normalizeProduct),
			})),
		() => buildLocalSearchResponse(options)
	);
}

export async function getAiRecommendations(query: string, limit = 4) {
	const safeLimit = Math.max(1, limit);
	const normalizedQuery = query.trim();

	if (!normalizedQuery) {
		return recommendProducts("", safeLimit);
	}

	return withApiFallback(
		() =>
			apiRequest<Product[]>(
				`/products/recommendations${buildQueryString({ q: normalizedQuery, limit: safeLimit })}`
			).then((recommendations) => recommendations.map(normalizeProduct)),
		() => recommendProducts(query, safeLimit)
	);
}

export async function getRelatedProductsByProductId(productId: string, limit = 4) {
	const safeLimit = Math.max(1, limit);

	return withApiFallback(
		() =>
			apiRequest<Product[]>(
				`/products/${productId}/similar${buildQueryString({ limit: safeLimit })}`
			).then((relatedProducts) => relatedProducts.map(normalizeProduct)),
		() => {
			const source = products.find((product) => product.id === productId);

			if (!source) {
				return [];
			}

			const byIds = source.similarProductIds
				.slice(0, safeLimit)
				.map((id) => products.find((product) => product.id === id))
				.filter((product): product is Product => Boolean(product));

			return byIds.length > 0 ? byIds : getRelatedProducts(productId, safeLimit);
		}
	);
}

export async function getCompareProducts(firstId?: string, secondId?: string) {
	return withApiFallback(
		() =>
			apiRequest<{ firstProduct: Product; secondProduct: Product }>(
				`/products/compare${buildQueryString({ first: firstId, second: secondId })}`
			).then((response) => ({
				firstProduct: normalizeProduct(response.firstProduct),
				secondProduct: normalizeProduct(response.secondProduct),
			})),
		() => resolveCompareProducts(firstId, secondId)
	);
}

export async function getSearchSuggestions(limit = 24) {
	const safeLimit = Math.max(1, limit);

	return withApiFallback(
		() => apiRequest<string[]>(`/products/suggestions${buildQueryString({ limit: safeLimit })}`),
		() => products.slice(0, safeLimit).map((product) => product.name)
	);
}

export async function getHomeCollections() {
	return withApiFallback(
		() =>
			apiRequest<{
				featured: Product[];
				newArrivals: Product[];
				topAiPicks: Product[];
				trending: Product[];
			}>("/products/collections/home").then((collections) => ({
				featured: collections.featured.map(normalizeProduct),
				newArrivals: collections.newArrivals.map(normalizeProduct),
				topAiPicks: collections.topAiPicks.map(normalizeProduct),
				trending: collections.trending.map(normalizeProduct),
			})),
		() => {
			const featured = products.slice(0, 4);
			const newArrivals = [...products].sort((left, right) => right.aiScore - left.aiScore).slice(4, 8);
			const topAiPicks = [...products].sort((left, right) => right.aiScore - left.aiScore).slice(0, 4);
			const trending = products.slice(0, 8);

			return {
				featured,
				newArrivals,
				topAiPicks,
				trending,
			};
		}
	);
}

export async function getCatalogMetadata() {
	return withApiFallback(
		() =>
			apiRequest<{
				categoryLabels: Record<string, string>;
				categoryPluralLabels: Record<string, string>;
				productSpotlightBadges: Record<string, string>;
				brands: string[];
			}>("/products/metadata"),
		() => ({
			categoryLabels,
			categoryPluralLabels,
			productSpotlightBadges,
			brands: Array.from(new Set(products.map((product) => product.brand))).sort((left, right) =>
				left.localeCompare(right)
			),
		})
	);
}

export function getCompareHref(productId: string, compareWithId?: string) {
	return buildCompareHref(productId, compareWithId);
}

export type {
	Product,
	ProductAiScoreFilter,
	ProductFilterState,
	ProductPriceFilter,
	ProductQueryOptions,
	ProductRatingFilter,
	ProductSortOption,
};
