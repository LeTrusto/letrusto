import { NextRequest, NextResponse } from "next/server";

const backendBase = (
  process.env.API_BASE_URL?.trim() ||
  process.env.NEXT_PUBLIC_API_BASE_URL?.trim() ||
  "https://letrusto-production.up.railway.app"
).replace(/\/api\/v1\/?$/i, "").replace(/\/$/, "");

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ widgetId: string }> },
) {
  const { widgetId } = await params;
  const response = await fetch(`${backendBase}/api/v1/public/embed/${encodeURIComponent(widgetId)}`, {
    headers: {
      Accept: "application/json",
      ...(request.headers.get("origin") ? { Origin: request.headers.get("origin") as string } : {}),
    },
    next: { revalidate: 60 },
  });
  const body = await response.text();
  const headers = new Headers({
    "Cache-Control": "public, max-age=60, s-maxage=60",
    "Content-Type": response.headers.get("content-type") || "application/json",
  });
  const origin = request.headers.get("origin");
  if (origin) {
    headers.set("Access-Control-Allow-Origin", origin);
    headers.set("Vary", "Origin");
  }
  return new NextResponse(body, { status: response.status, headers });
}