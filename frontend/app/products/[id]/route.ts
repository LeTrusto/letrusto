import { NextResponse } from "next/server";
import { buildApiUrl } from "@/services/api";

type Context = { params: Promise<{ id: string }> };

export const dynamic = "force-dynamic";

export async function GET(request: Request, { params }: Context) {
  const { id } = await params;
  const response = await fetch(buildApiUrl(`/products/${encodeURIComponent(id)}`), { cache: "no-store" });
  if (!response.ok) return new NextResponse(null, { status: response.status === 404 ? 404 : 503 });

  const product = await response.json() as { id: string };
  return NextResponse.redirect(new URL(`/product/${product.id}`, request.url), 307);
}