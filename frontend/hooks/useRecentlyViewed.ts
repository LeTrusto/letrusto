"use client";

import { useEffect, useState } from "react";

const RECENTLY_VIEWED_STORAGE_KEY = "letrusto:recently-viewed";
const MAX_RECENTLY_VIEWED = 6;
const EMPTY_RECENTLY_VIEWED_IDS: string[] = [];

let recentlyViewedStore: string[] = EMPTY_RECENTLY_VIEWED_IDS;
let hasHydratedStore = false;

const listeners = new Set<(recentlyViewedIds: string[]) => void>();

function readRecentlyViewedIds() {
  try {
    const rawValue = window.localStorage.getItem(RECENTLY_VIEWED_STORAGE_KEY);
    const parsedValue = rawValue ? (JSON.parse(rawValue) as string[]) : EMPTY_RECENTLY_VIEWED_IDS;

    return Array.isArray(parsedValue) ? parsedValue : EMPTY_RECENTLY_VIEWED_IDS;
  } catch {
    return EMPTY_RECENTLY_VIEWED_IDS;
  }
}

function arraysEqual(left: string[], right: string[]) {
  if (left.length !== right.length) {
    return false;
  }

  return left.every((value, index) => value === right[index]);
}

function emitRecentlyViewedChange(nextRecentlyViewedIds: string[]) {
  recentlyViewedStore = nextRecentlyViewedIds;

  for (const listener of listeners) {
    listener(nextRecentlyViewedIds);
  }
}

function ensureRecentlyViewedHydrated() {
  if (typeof window === "undefined" || hasHydratedStore) {
    return recentlyViewedStore;
  }

  recentlyViewedStore = readRecentlyViewedIds();
  hasHydratedStore = true;

  return recentlyViewedStore;
}

function saveRecentlyViewed(nextRecentlyViewedIds: string[]) {
  recentlyViewedStore = nextRecentlyViewedIds;

  if (typeof window !== "undefined") {
    window.localStorage.setItem(
      RECENTLY_VIEWED_STORAGE_KEY,
      JSON.stringify(nextRecentlyViewedIds)
    );
  }

  emitRecentlyViewedChange(nextRecentlyViewedIds);
}

function subscribe(callback: (recentlyViewedIds: string[]) => void) {
  listeners.add(callback);

  if (typeof window === "undefined") {
    return () => {
      listeners.delete(callback);
    };
  }

  const hydratedIds = ensureRecentlyViewedHydrated();

  if (!arraysEqual(recentlyViewedStore, hydratedIds)) {
    recentlyViewedStore = hydratedIds;
  }

  queueMicrotask(() => {
    callback(recentlyViewedStore);
  });

  const handleStorage = () => {
    const nextIds = readRecentlyViewedIds();

    if (!arraysEqual(recentlyViewedStore, nextIds)) {
      recentlyViewedStore = nextIds;
      emitRecentlyViewedChange(nextIds);
    }
  };

  window.addEventListener("storage", handleStorage);

  return () => {
    listeners.delete(callback);
    window.removeEventListener("storage", handleStorage);
  };
}

export function useRecentlyViewed(currentProductId?: string) {
  const [recentlyViewedIds, setRecentlyViewedIds] = useState<string[]>(
    EMPTY_RECENTLY_VIEWED_IDS
  );

  useEffect(() => subscribe(setRecentlyViewedIds), []);

  useEffect(() => {
    if (!currentProductId) {
      return;
    }

    const currentIds = ensureRecentlyViewedHydrated();

    if (currentIds[0] === currentProductId) {
      return;
    }

    const nextIds = [
      currentProductId,
      ...currentIds.filter((id) => id !== currentProductId),
    ].slice(0, MAX_RECENTLY_VIEWED);

    saveRecentlyViewed(nextIds);
  }, [currentProductId]);

  return {
    recentlyViewedIds,
  };
}
