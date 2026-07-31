"use client";

import { useEffect, useState } from "react";

import { API_BASE_URL, IS_API_CONFIGURED } from "@/services/api";

const STORAGE_KEY = "letrusto:favorites";
const USER_ID_STORAGE_KEY = "letrusto:user-id";
let favoriteStore: string[] = [];
let hasHydratedStore = false;

const listeners = new Set<(favoriteIds: string[]) => void>();

function readFavorites() {
  try {
    const saved = window.localStorage.getItem(STORAGE_KEY);
    const parsed = saved ? (JSON.parse(saved) as string[]) : [];

    return Array.isArray(parsed) ? parsed : [];
  }
  catch {
    return [];
  }
}

function getOrCreateUserId() {
  if (typeof window === "undefined") {
    return null;
  }

  const existing = window.localStorage.getItem(USER_ID_STORAGE_KEY);
  if (existing) {
    return existing;
  }

  const generated =
    typeof crypto !== "undefined" && typeof crypto.randomUUID === "function"
      ? crypto.randomUUID()
      : `${Date.now()}-${Math.random().toString(16).slice(2)}`;
  window.localStorage.setItem(USER_ID_STORAGE_KEY, generated);

  return generated;
}

async function fetchFavoritesFromApi() {
  const userId = getOrCreateUserId();
  if (!userId) {
    return [];
  }

  const response = await fetch(`${API_BASE_URL}/favorites?userId=${encodeURIComponent(userId)}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to load favorites (${response.status})`);
  }

  const payload = (await response.json()) as { items?: Array<{ id?: string }> };
  return (payload.items ?? []).map((item) => item.id).filter((value): value is string => Boolean(value));
}

async function syncFavoriteWithApi(productId: string, shouldFavorite: boolean) {
  const userId = getOrCreateUserId();
  if (!userId) {
    return;
  }

  const method = shouldFavorite ? "POST" : "DELETE";
  const response = await fetch(
    `${API_BASE_URL}/favorites/${encodeURIComponent(productId)}?userId=${encodeURIComponent(userId)}`,
    {
      method,
      headers: {
        "Content-Type": "application/json",
      },
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to update favorites (${response.status})`);
  }
}
function emitFavoritesChange(nextFavoriteIds: string[]) {
  favoriteStore = nextFavoriteIds;

  for (const listener of listeners) {
    listener(nextFavoriteIds);
  }
}

function saveFavorites(nextFavoriteIds: string[]) {
  favoriteStore = nextFavoriteIds;

  if (typeof window !== "undefined") {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(nextFavoriteIds));
  }

  emitFavoritesChange(nextFavoriteIds);
}

function ensureFavoritesHydrated() {
  if (typeof window === "undefined" || hasHydratedStore) {
    return favoriteStore;
  }

  favoriteStore = readFavorites();
  hasHydratedStore = true;

  return favoriteStore;
}

function arraysEqual(left: string[], right: string[]) {
  if (left.length !== right.length) {
    return false;
  }

  return left.every((value, index) => value === right[index]);
}

function subscribe(callback: (favoriteIds: string[]) => void) {
  listeners.add(callback);

  if (typeof window === "undefined") {
    return () => {
      listeners.delete(callback);
    };
  }

  const hydratedFavorites = ensureFavoritesHydrated();

  if (!arraysEqual(favoriteStore, hydratedFavorites)) {
    favoriteStore = hydratedFavorites;
  }

  queueMicrotask(() => {
    callback(favoriteStore);
  });

  const handleStorage = () => {
    const nextFavoriteIds = readFavorites();

    if (!arraysEqual(favoriteStore, nextFavoriteIds)) {
      favoriteStore = nextFavoriteIds;
      emitFavoritesChange(nextFavoriteIds);
    }
  };

  window.addEventListener("storage", handleStorage);

  return () => {
    listeners.delete(callback);
    window.removeEventListener("storage", handleStorage);
  };
}

export function useFavorites() {
  const [favoriteIds, setFavoriteIds] = useState<string[]>([]);

  useEffect(() => {
    const unsubscribe = subscribe(setFavoriteIds);

    if (IS_API_CONFIGURED) {
      void fetchFavoritesFromApi()
        .then((serverIds) => {
          saveFavorites(serverIds);
        })
        .catch(() => {
          // Keep local fallback state if backend fetch fails.
        });
    }

    return unsubscribe;
  }, []);

  const toggleFavorite = (id: string) => {
    const wasFavorite = favoriteIds.includes(id);
    const nextFavoriteIds = wasFavorite
      ? favoriteIds.filter((item) => item !== id)
      : [...favoriteIds, id];

    saveFavorites(nextFavoriteIds);

    if (IS_API_CONFIGURED) {
      const previousFavoriteIds = [...favoriteIds];
      void syncFavoriteWithApi(id, !wasFavorite).catch(() => {
        saveFavorites(previousFavoriteIds);
      });
    }
  };

  const removeFavorite = (id: string) => {
    const previousFavoriteIds = [...favoriteIds];
    const nextFavoriteIds = favoriteIds.filter((item) => item !== id);

    saveFavorites(nextFavoriteIds);

    if (IS_API_CONFIGURED) {
      void syncFavoriteWithApi(id, false).catch(() => {
        saveFavorites(previousFavoriteIds);
      });
    }
  };

  const clearFavorites = () => {
    const previousFavoriteIds = [...favoriteIds];
    saveFavorites([]);

    if (IS_API_CONFIGURED) {
      void Promise.all(previousFavoriteIds.map((id) => syncFavoriteWithApi(id, false))).catch(() => {
        saveFavorites(previousFavoriteIds);
      });
    }
  };

  const isFavorite = (id: string) => favoriteIds.includes(id);

  return {
    favoriteIds,
    toggleFavorite,
    removeFavorite,
    clearFavorites,
    isFavorite,
  };
}