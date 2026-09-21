import type { Metadata } from "next";
import Link from "next/link";

const SITE_NAME = "Bangalore Property Platform";
const SITE_DESCRIPTION = "Bangalore property discovery, marketing, and buyer lead generation.";

export const metadata: Metadata = {
  title: { absolute: SITE_NAME },
  description: SITE_DESCRIPTION,
  alternates: { canonical: "/" },
  openGraph: {
    title: SITE_NAME,
    description: SITE_DESCRIPTION,
    url: "/",
    siteName: SITE_NAME,
    type: "website",
  },
};

export default function Home() {
  return (
    <main className="flex flex-1 flex-col items-center justify-center gap-6 px-6 py-24 text-center">
      <h1 className="text-3xl font-black text-gray-900 md:text-4xl">{SITE_NAME}</h1>
      <p className="max-w-md text-gray-500">
        This is a temporary placeholder homepage. The Bangalore property experience is being designed from a clean foundation.
      </p>
      <Link
        href="/login"
        className="rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 px-6 py-3 text-sm font-bold text-white transition hover:scale-[1.02]"
      >
        Sign In
      </Link>
    </main>
  );
}

