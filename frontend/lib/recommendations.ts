import type { Product } from "@/types/products";

import { getFirstAvailableProduct, getProductById, products } from "@/lib/products";

const categoryKeywords = {
  phone: ["phone", "mobile", "android", "iphone", "camera", "smartphone"],
  laptop: ["laptop", "notebook", "coding", "python", "developer", "office", "work"],
  headphones: ["headphone", "headphones", "music", "noise", "noise cancellation", "audio"],
  smartwatch: ["watch", "smartwatch", "wearable", "fitness", "health"],
  television: ["tv", "television", "oled", "qled", "streaming", "movie"],
  refrigerator: ["fridge", "refrigerator", "kitchen", "cooling"],
  "washing-machine": ["washing machine", "washing", "laundry", "washer"],
  gaming: ["gaming", "console", "playstation", "xbox", "handheld", "pc gaming"],
  tablet: ["tablet", "ipad", "note taking", "student", "sketch"],
  camera: ["camera", "mirrorless", "photography", "video", "vlog"],
} as const;

const priorityRecommendations: Record<string, string[]> = {
  phone: ["nothing-phone-2a", "oneplus-nord-4", "motorola-edge-50-pro", "galaxy-s25"],
  laptop: ["macbook-air-m4", "asus-zenbook-14-oled", "lenovo-thinkpad-x1-carbon", "dell-xps-13"],
  headphones: ["sony-wh-1000xm6", "bose-qc-ultra", "airpods-max", "sennheiser-momentum-4"],
};

type BudgetRange = {
  min?: number;
  max?: number;
};

export function normalizeQuery(query: string) {
  return query.toLowerCase().trim();
}

function parseBudgetToken(value: string) {
  const normalizedValue = value.replace(/,/g, "").trim().toLowerCase();

  if (normalizedValue.endsWith("k")) {
    return Number(normalizedValue.slice(0, -1)) * 1000;
  }

  return Number(normalizedValue);
}

export function extractBudgetFromQuery(query: string): BudgetRange {
  const normalizedQuery = normalizeQuery(query);
  const underMatch = normalizedQuery.match(/(?:under|below|less than)\s*(₹?\s*[\d,]+k?)/i);
  const aboveMatch = normalizedQuery.match(/(?:above|over|more than)\s*(₹?\s*[\d,]+k?)/i);
  const betweenMatch = normalizedQuery.match(/(?:between)\s*(₹?\s*[\d,]+k?)\s*(?:and|to)\s*(₹?\s*[\d,]+k?)/i);

  if (betweenMatch) {
    return {
      min: parseBudgetToken(betweenMatch[1].replace(/₹/g, "")),
      max: parseBudgetToken(betweenMatch[2].replace(/₹/g, "")),
    };
  }

  if (underMatch) {
    return {
      max: parseBudgetToken(underMatch[1].replace(/₹/g, "")),
    };
  }

  if (aboveMatch) {
    return {
      min: parseBudgetToken(aboveMatch[1].replace(/₹/g, "")),
    };
  }

  return {};
}

export function detectCategoryFromQuery(query: string) {
  const normalizedQuery = normalizeQuery(query);

  return Object.entries(categoryKeywords).find(([, keywords]) =>
    keywords.some((keyword) => normalizedQuery.includes(keyword))
  )?.[0] as Product["category"] | undefined;
}

function isWithinBudget(product: Product, budget: BudgetRange) {
  if (budget.min !== undefined && product.priceValue < budget.min) {
    return false;
  }

  if (budget.max !== undefined && product.priceValue > budget.max) {
    return false;
  }

  return true;
}

export function scoreProductForQuery(product: Product, query: string) {
  const normalizedQuery = normalizeQuery(query);
  const detectedCategory = detectCategoryFromQuery(normalizedQuery);
  const budget = extractBudgetFromQuery(normalizedQuery);

  if (!normalizedQuery) {
    return 0;
  }

  const tokens = normalizedQuery.split(/\s+/).filter(Boolean);
  const searchableContent = [
    product.name.toLowerCase(),
    product.description.toLowerCase(),
    product.category.toLowerCase(),
    ...product.features.map((feature) => feature.toLowerCase()),
    ...product.tags.map((tag) => tag.toLowerCase()),
  ];

  let score = 0;

  if (product.name.toLowerCase().includes(normalizedQuery)) {
    score += 60;
  }

  if (product.category.toLowerCase().includes(normalizedQuery)) {
    score += 20;
  }

  if (detectedCategory && product.category === detectedCategory) {
    score += 36;
  }

  for (const token of tokens) {
    if (product.name.toLowerCase().includes(token)) {
      score += 18;
    }

    if (product.tags.some((tag) => tag.includes(token))) {
      score += 16;
    }

    if (searchableContent.some((entry) => entry.includes(token))) {
      score += 8;
    }
  }

  if (budget.min !== undefined || budget.max !== undefined) {
    if (isWithinBudget(product, budget)) {
      score += 28;
    } else {
      score -= 18;
    }
  }

  if (product.brand.toLowerCase() && normalizedQuery.includes(product.brand.toLowerCase())) {
    score += 22;
  }

  if (priorityRecommendations[product.category]?.includes(product.id)) {
    score += 10;
  }

  return score;
}

export function recommendProducts(query: string, limit = 4) {
  const normalizedQuery = normalizeQuery(query);
  const detectedCategory = detectCategoryFromQuery(normalizedQuery);
  const budget = extractBudgetFromQuery(normalizedQuery);

  if (!normalizedQuery) {
    return [];
  }

  const categoryCandidates = detectedCategory
    ? products.filter((product) => product.category === detectedCategory)
    : products;

  const budgetFiltered =
    budget.min !== undefined || budget.max !== undefined
      ? categoryCandidates.filter((product) => isWithinBudget(product, budget))
      : categoryCandidates;

  const candidatePool = budgetFiltered.length > 0 ? budgetFiltered : categoryCandidates;

  const recommended = candidatePool
    .map((product) => ({
      product,
      score: scoreProductForQuery(product, normalizedQuery) + product.aiScore / 10,
    }))
    .filter((entry) => entry.score > 0)
    .sort((left, right) => right.score - left.score)
    .map((entry) => entry.product);

  if (recommended.length > 0) {
    return recommended.slice(0, limit);
  }

  const priorityIds = detectedCategory ? priorityRecommendations[detectedCategory] : undefined;

  if (!priorityIds) {
    return [];
  }

  return priorityIds
    .map((productId) => getProductById(productId))
    .filter((product): product is Product => Boolean(product))
    .filter((product) => isWithinBudget(product, budget))
    .slice(0, limit);
}

export function discoverProducts(query: string) {
  const normalizedQuery = normalizeQuery(query);

  if (!normalizedQuery) {
    return products;
  }

  const budget = extractBudgetFromQuery(normalizedQuery);
  const detectedCategory = detectCategoryFromQuery(normalizedQuery);

  const scopedProducts = products.filter((product) => {
    if (detectedCategory && product.category !== detectedCategory) {
      return false;
    }

    if ((budget.min !== undefined || budget.max !== undefined) && !isWithinBudget(product, budget)) {
      return false;
    }

    return true;
  });

  const discovered = scopedProducts
    .map((product) => ({
      product,
      score: scoreProductForQuery(product, normalizedQuery),
    }))
    .filter((entry) => entry.score > 0)
    .sort((left, right) => right.score - left.score)
    .map((entry) => entry.product);

  if (discovered.length > 0) {
    return discovered;
  }

  return recommendProducts(normalizedQuery, 8);
}

export function getRelatedProducts(productId: string, limit = 4) {
  const currentProduct = getProductById(productId);

  if (!currentProduct) {
    return [];
  }

  return products
    .filter((product) => product.id !== productId)
    .map((product) => {
      const sharedTags = product.tags.filter((tag) => currentProduct.tags.includes(tag)).length;
      const sameCategoryBonus = product.category === currentProduct.category ? 3 : 0;
      const aiScoreDistance = Math.abs(product.aiScore - currentProduct.aiScore);

      return {
        product,
        score:
          sharedTags * 10 +
          sameCategoryBonus * 12 -
          aiScoreDistance +
          (product.brand === currentProduct.brand ? 8 : 0),
      };
    })
    .sort((left, right) => right.score - left.score)
    .slice(0, limit)
    .map((entry) => entry.product);
}

export function resolveCompareProducts(firstId?: string, secondId?: string) {
  const firstProduct = getProductById(firstId ?? "") ?? products[0];
  const fallbackSecond = getFirstAvailableProduct(firstProduct.id);
  const secondProduct =
    getProductById(secondId ?? "")?.id !== firstProduct.id
      ? getProductById(secondId ?? "")
      : undefined;

  return {
    firstProduct,
    secondProduct: secondProduct ?? fallbackSecond,
  };
}

export function buildCompareHref(productId: string, compareWithId?: string) {
  const compareTarget =
    (compareWithId && compareWithId !== productId
      ? getProductById(compareWithId)
      : getRelatedProducts(productId, 1)[0]) ?? getFirstAvailableProduct(productId);

  return `/compare?first=${productId}&second=${compareTarget.id}`;
}
