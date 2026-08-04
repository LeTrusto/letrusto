"use client";

import { useEffect, useRef } from "react";
import Script from "next/script";
import { usePathname } from "next/navigation";

import { GA_MEASUREMENT_ID, isAnalyticsEnabled, trackPageView } from "@/lib/analytics";

export default function GoogleAnalytics() {
	const pathname = usePathname();
	const lastTrackedUrlRef = useRef<string | null>(null);

	useEffect(() => {
		if (!isAnalyticsEnabled()) {
			return;
		}

		const query = window.location.search;
		const currentUrl = query ? `${pathname}${query}` : pathname;

		if (!currentUrl || lastTrackedUrlRef.current === currentUrl) {
			return;
		}

		trackPageView(currentUrl);
		lastTrackedUrlRef.current = currentUrl;
	}, [pathname]);

	if (process.env.NODE_ENV !== "production") {
		return null;
	}

	return (
		<>
			<Script
				src={`https://www.googletagmanager.com/gtag/js?id=${GA_MEASUREMENT_ID}`}
				strategy="afterInteractive"
			/>
			<Script id="ga4-init" strategy="afterInteractive">
				{`
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
window.gtag = window.gtag || gtag;
gtag('js', new Date());
gtag('config', '${GA_MEASUREMENT_ID}', { send_page_view: false });
        `}
			</Script>
		</>
	);
}