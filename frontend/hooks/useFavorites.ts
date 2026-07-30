"use client";

import { useEffect, useState } from "react";

const STORAGE_KEY = "letrusto:favorites";
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
    return subscribe(setFavoriteIds);
  }, []);

  const toggleFavorite = (id: string) => {
    saveFavorites(
      favoriteIds.includes(id)
        ? favoriteIds.filter((item) => item !== id)
        : [...favoriteIds, id]
    );
  };

  const removeFavorite = (id: string) => {
    saveFavorites(favoriteIds.filter((item) => item !== id));
  };

  const clearFavorites = () => {
    saveFavorites([]);
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