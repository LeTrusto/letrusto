import fs from "node:fs/promises";
import path from "node:path";

const repoRoot = process.cwd();
const productsFile = path.join(repoRoot, "lib", "products.ts");
const imagesDir = path.join(repoRoot, "public", "images", "products");
const manifestFile = path.join(repoRoot, "lib", "productImageManifest.ts");

const USER_AGENT = "LeTrustoImageSync/1.0 (educational project)";

async function parseProducts() {
  const src = await fs.readFile(productsFile, "utf8");
  const sectionStart = src.indexOf("const productSeeds: ProductSeed[] = [");
  if (sectionStart === -1) {
    throw new Error("Unable to locate productSeeds in lib/products.ts");
  }

  const section = src.slice(sectionStart);
  const regex = /id:\s*"([^"]+)"[\s\S]*?name:\s*"([^"]+)"[\s\S]*?brand:\s*"([^"]+)"[\s\S]*?category:\s*"([^"]+)"/g;

  const products = [];
  let match;
  while ((match = regex.exec(section)) !== null) {
    const [, id, name, brand, category] = match;
    products.push({ id, name, brand, category });
  }

  return products;
}

async function fetchJson(url) {
  const response = await fetch(url, {
    headers: { "User-Agent": USER_AGENT },
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status} for ${url}`);
  }

  return response.json();
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function buildSearchQueries(product) {
  const normalizedModel = product.name
    .replace(/\bgen\s*\d+\b/gi, "")
    .replace(/\bmark\s*ii\b/gi, "mark 2")
    .replace(/\bmk\s*ii\b/gi, "mark 2")
    .trim();

  return [
    `${product.brand} ${product.name}`,
    `${product.name} ${product.brand}`,
    normalizedModel,
    `${product.brand} ${normalizedModel} front`,
    `${product.brand} ${normalizedModel} back`,
    `${product.brand} ${normalizedModel} product photo`,
    `${product.brand} ${product.category}`,
    `${product.category} ${product.brand}`,
    `${product.brand} ${normalizedModel} product`,
    `${product.category} ${normalizedModel}`,
  ];
}

async function searchWikipediaTitle(query) {
  const url = new URL("https://en.wikipedia.org/w/api.php");
  url.searchParams.set("action", "query");
  url.searchParams.set("list", "search");
  url.searchParams.set("srsearch", query);
  url.searchParams.set("srlimit", "5");
  url.searchParams.set("format", "json");
  url.searchParams.set("origin", "*");

  const data = await fetchJson(url.toString());
  const results = data?.query?.search ?? [];
  if (results.length === 0) {
    return null;
  }

  return results[0].title;
}

async function searchWikidataEntities(query) {
  const url = new URL("https://www.wikidata.org/w/api.php");
  url.searchParams.set("action", "wbsearchentities");
  url.searchParams.set("search", query);
  url.searchParams.set("language", "en");
  url.searchParams.set("format", "json");
  url.searchParams.set("origin", "*");
  url.searchParams.set("limit", "5");

  const data = await fetchJson(url.toString());
  return data?.search ?? [];
}

async function getWikidataP18ImageFile(entityId) {
  const url = `https://www.wikidata.org/wiki/Special:EntityData/${encodeURIComponent(entityId)}.json`;
  const data = await fetchJson(url);
  const entity = data?.entities?.[entityId];
  const p18 = entity?.claims?.P18?.[0]?.mainsnak?.datavalue?.value;
  return p18 ?? null;
}

function buildCommonsFilePathUrl(fileName) {
  return `https://commons.wikimedia.org/wiki/Special:FilePath/${encodeURIComponent(fileName)}`;
}

function scoreWikidataEntity(product, entity) {
  const haystack = `${entity?.label ?? ""} ${entity?.description ?? ""}`.toLowerCase();
  const tokens = tokenize(`${product.brand} ${product.name}`);

  let score = 0;
  for (const token of tokens) {
    if (haystack.includes(token.toLowerCase())) {
      score += 2;
    }
  }

  if (haystack.includes(product.category.toLowerCase())) {
    score += 1;
  }

  return score;
}

async function findBestWikidataImage(product, usedUrls) {
  const queries = buildSearchQueries(product);
  const candidates = [];

  for (const query of queries) {
    try {
      const entities = await searchWikidataEntities(query);
      for (const entity of entities) {
        candidates.push(entity);
      }
    } catch {
      // continue
    }
    await sleep(120);
  }

  if (candidates.length === 0) {
    return null;
  }

  const uniqueEntities = [];
  const seen = new Set();
  for (const entity of candidates) {
    if (!entity?.id || seen.has(entity.id)) {
      continue;
    }
    seen.add(entity.id);
    uniqueEntities.push(entity);
  }

  const ranked = uniqueEntities
    .map((entity) => ({ entity, score: scoreWikidataEntity(product, entity) }))
    .sort((a, b) => b.score - a.score)
    .slice(0, 10);

  for (const candidate of ranked) {
    try {
      const fileName = await getWikidataP18ImageFile(candidate.entity.id);
      await sleep(120);

      if (!fileName) {
        continue;
      }

      const url = buildCommonsFilePathUrl(fileName);
      if (usedUrls.has(url)) {
        continue;
      }

      return {
        title: `${candidate.entity.label ?? candidate.entity.id} (${candidate.entity.id})`,
        url,
      };
    } catch {
      // try next
    }
  }

  return null;
}

async function getPageImageUrl(title) {
  const url = new URL("https://en.wikipedia.org/w/api.php");
  url.searchParams.set("action", "query");
  url.searchParams.set("prop", "pageimages");
  url.searchParams.set("piprop", "thumbnail");
  url.searchParams.set("pithumbsize", "1200");
  url.searchParams.set("titles", title);
  url.searchParams.set("format", "json");
  url.searchParams.set("origin", "*");

  const data = await fetchJson(url.toString());
  const pages = data?.query?.pages ?? {};
  const firstPage = Object.values(pages)[0];
  return firstPage?.thumbnail?.source ?? null;
}

async function searchCommonsFileCandidates(query) {
  const url = new URL("https://commons.wikimedia.org/w/api.php");
  url.searchParams.set("action", "query");
  url.searchParams.set("generator", "search");
  url.searchParams.set("gsrsearch", query);
  url.searchParams.set("gsrnamespace", "6");
  url.searchParams.set("gsrlimit", "12");
  url.searchParams.set("prop", "imageinfo");
  url.searchParams.set("iiprop", "url");
  url.searchParams.set("format", "json");
  url.searchParams.set("origin", "*");

  const data = await fetchJson(url.toString());
  const pages = data?.query?.pages ? Object.values(data.query.pages) : [];

  return pages
    .map((page) => ({
      title: page?.title ?? "",
      url: page?.imageinfo?.[0]?.url ?? null,
    }))
    .filter((entry) => Boolean(entry.url));
}

function tokenize(text) {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, " ")
    .split(/\s+/)
    .filter((token) => token.length > 1);
}

function scoreCommonsCandidate(product, candidate) {
  const productTokens = new Set(tokenize(`${product.brand} ${product.name}`));
  const titleTokens = tokenize(candidate.title.replace(/^File:/i, ""));

  let score = 0;
  for (const token of titleTokens) {
    if (productTokens.has(token)) {
      score += 3;
    }
  }

  const lowerTitle = candidate.title.toLowerCase();
  if (lowerTitle.includes("logo") || lowerTitle.includes("wordmark") || lowerTitle.includes("icon")) {
    score -= 15;
  }
  if (lowerTitle.includes("poster") || lowerTitle.includes("wallpaper") || lowerTitle.includes("box art")) {
    score -= 10;
  }
  if (lowerTitle.includes("render") || lowerTitle.includes("mockup")) {
    score -= 4;
  }
  if (lowerTitle.includes("front") || lowerTitle.includes("back") || lowerTitle.includes("side")) {
    score += 2;
  }
  if (lowerTitle.includes(product.category.toLowerCase())) {
    score += 2;
  }
  if (lowerTitle.includes("jpg") || lowerTitle.includes("jpeg") || lowerTitle.includes("png") || lowerTitle.includes("webp")) {
    score += 1;
  }

  return score;
}

async function findBestCommonsImage(product, usedUrls) {
  const queries = buildSearchQueries(product);
  const seen = new Set();
  const candidates = [];

  for (const query of queries) {
    try {
      const entries = await searchCommonsFileCandidates(query);
      for (const entry of entries) {
        if (seen.has(entry.url)) {
          continue;
        }
        seen.add(entry.url);
        candidates.push(entry);
      }
    } catch {
      // continue
    }
  }

  if (candidates.length === 0) {
    return null;
  }

  const ranked = candidates
    .map((candidate) => ({
      ...candidate,
      score: scoreCommonsCandidate(product, candidate),
    }))
    .sort((a, b) => b.score - a.score);

  const uniqueBest = ranked.find((candidate) => !usedUrls.has(candidate.url));
  const best = uniqueBest ?? ranked[0];

  return best?.score >= 0 ? best : null;
}

function extensionFromContentType(contentType) {
  if (!contentType) return ".jpg";
  if (contentType.includes("image/webp")) return ".webp";
  if (contentType.includes("image/png")) return ".png";
  if (contentType.includes("image/jpeg")) return ".jpg";
  if (contentType.includes("image/svg")) return ".svg";
  return ".jpg";
}

async function downloadImage(url, outputPathWithoutExt) {
  const response = await fetch(url, {
    headers: { "User-Agent": USER_AGENT },
    redirect: "follow",
  });

  if (!response.ok) {
    throw new Error(`Failed image download ${response.status} from ${url}`);
  }

  const contentType = response.headers.get("content-type") || "";
  if (!contentType.startsWith("image/")) {
    throw new Error(`Non-image content-type: ${contentType}`);
  }

  const ext = extensionFromContentType(contentType);
  const outputPath = `${outputPathWithoutExt}${ext}`;
  const bytes = Buffer.from(await response.arrayBuffer());
  await fs.writeFile(outputPath, bytes);

  return outputPath;
}

async function cleanupExistingProductAssets(productId) {
  const files = await fs.readdir(imagesDir);
  const targets = files.filter((file) => file.startsWith(`${productId}-`) || file === `${productId}.jpg` || file === `${productId}.png` || file === `${productId}.webp`);

  await Promise.all(
    targets.map((file) => fs.rm(path.join(imagesDir, file), { force: true }))
  );
}

async function main() {
  await fs.mkdir(imagesDir, { recursive: true });
  const products = await parseProducts();

  const mapping = {};
  const missing = [];
  const resolved = [];
  const usedUrls = new Set();

  for (const product of products) {
    let imageUrl = null;
    let resolvedTitle = null;

    const wikidataMatch = await findBestWikidataImage(product, usedUrls);
    if (wikidataMatch) {
      imageUrl = wikidataMatch.url;
      resolvedTitle = wikidataMatch.title;
    }

    if (!imageUrl) {
      const commonsMatch = await findBestCommonsImage(product, usedUrls);
      if (commonsMatch) {
        imageUrl = commonsMatch.url;
        resolvedTitle = commonsMatch.title;
      }
    }

    if (!imageUrl) {
      const queries = buildSearchQueries(product);
      for (const query of queries) {
        try {
          const title = await searchWikipediaTitle(query);
          if (!title) continue;

          const candidateImage = await getPageImageUrl(title);
          if (candidateImage) {
            if (usedUrls.has(candidateImage)) {
              continue;
            }
            imageUrl = candidateImage;
            resolvedTitle = title;
            break;
          }
        } catch {
          // try next query
        }
      }
    }

    if (!imageUrl) {
      missing.push(product.id);
      continue;
    }

    try {
      await cleanupExistingProductAssets(product.id);
      const outputWithoutExt = path.join(imagesDir, `${product.id}-1`);
      const savedPath = await downloadImage(imageUrl, outputWithoutExt);
      const relativePath = "/images/products/" + path.basename(savedPath).replace(/\\/g, "/");
      mapping[product.id] = [relativePath];
      usedUrls.add(imageUrl);
      resolved.push({ id: product.id, title: resolvedTitle, imageUrl: relativePath });
    } catch {
      missing.push(product.id);
    }
  }

  const sortedIds = products.map((p) => p.id);
  const mappingEntries = sortedIds
    .filter((id) => mapping[id])
    .map((id) => `  ${JSON.stringify(id)}: [${mapping[id].map((src) => JSON.stringify(src)).join(", ")}],`)
    .join("\n");

  const missingEntries = sortedIds
    .filter((id) => !mapping[id])
    .map((id) => `  ${JSON.stringify(id)},`)
    .join("\n");

  const fileContent = `export const productImagesById: Partial<Record<string, string[]>> = {\n${mappingEntries}\n};\n\nexport const productsMissingImages: string[] = [\n${missingEntries}\n];\n`;

  await fs.writeFile(manifestFile, fileContent, "utf8");

  const report = {
    totalProducts: products.length,
    resolvedProducts: resolved.length,
    missingProducts: missing.length,
    missingIds: missing,
  };

  await fs.writeFile(path.join(repoRoot, "image-sync-report.json"), JSON.stringify(report, null, 2), "utf8");

  console.log(JSON.stringify(report, null, 2));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
