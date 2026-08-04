import { trackEvent } from "@/lib/analytics";

export const AMAZON_ASSOCIATE_ID = process.env.NEXT_PUBLIC_AMAZON_ASSOCIATE_ID?.trim() || "letrusto-21";

export type AffiliateSource = {
	amazonAsin?: string | null;
	amazonAffiliateUrl?: string | null;
	flipkartAffiliateUrl?: string | null;
};

export type AffiliateClickProduct = {
	id: string;
	name: string;
	category: string;
};

export function getAmazonAffiliateUrl(product: AffiliateSource | null | undefined): string | null {
	const affiliateUrl = product?.amazonAffiliateUrl?.trim();
	if (affiliateUrl) {
		return affiliateUrl;
	}

	const asin = product?.amazonAsin?.trim();
	if (asin) {
		return `https://www.amazon.in/dp/${encodeURIComponent(asin)}?tag=${encodeURIComponent(AMAZON_ASSOCIATE_ID)}`;
	}

	return null;
}

export function getFlipkartAffiliateUrl(product: AffiliateSource | null | undefined): string | null {
	const affiliateUrl = product?.flipkartAffiliateUrl?.trim();
	return affiliateUrl || null;
}

export function trackAffiliateClick(
	product: AffiliateClickProduct,
	retailer: string,
	affiliate: string = retailer
) {
	trackEvent("affiliate_click", {
		retailer,
		product_name: product.name,
		product_id: product.id,
		category: product.category,
		affiliate,
	});
}