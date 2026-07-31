"use client";

import { useEffect, useMemo, useState } from "react";

import { getAllProducts, getCatalogMetadata, type Product } from "@/services/product.service";

type UseProductsState = {
	products: Product[];
	isLoading: boolean;
	error: string | null;
	brands: string[];
};

type ProductsBootstrapPayload = {
	products: Product[];
	brands: string[];
};

let productsBootstrapPromise: Promise<ProductsBootstrapPayload> | null = null;
let productsBootstrapCache: ProductsBootstrapPayload | null = null;

async function loadProductsBootstrap() {
	if (productsBootstrapCache) {
		return productsBootstrapCache;
	}

	if (!productsBootstrapPromise) {
		productsBootstrapPromise = Promise.all([getAllProducts(), getCatalogMetadata()]).then(
			([catalog, metadata]) => {
				const payload = {
					products: catalog,
					brands: metadata.brands,
				};

				productsBootstrapCache = payload;
				return payload;
			}
		).catch((error) => {
			productsBootstrapPromise = null;
			throw error;
		});
	}

	return productsBootstrapPromise;
}

export function useProducts() {
	const [state, setState] = useState<UseProductsState>({
		products: [],
		isLoading: true,
		error: null,
		brands: [],
	});

	useEffect(() => {
		let mounted = true;

		async function load() {
			try {
				const payload = await loadProductsBootstrap();

				if (!mounted) {
					return;
				}

				setState({
					products: payload.products,
					brands: payload.brands,
					isLoading: false,
					error: null,
				});
			} catch (error) {
				if (!mounted) {
					return;
				}

				setState({
					products: [],
					brands: [],
					isLoading: false,
					error: error instanceof Error ? error.message : "Unable to load products.",
				});
			}
		}

		void load();

		return () => {
			mounted = false;
		};
	}, []);

	const productsById = useMemo(() => {
		return new Map(state.products.map((product) => [product.id, product]));
	}, [state.products]);

	const findById = (id: string) => productsById.get(id);

	return {
		...state,
		findById,
	};
}
