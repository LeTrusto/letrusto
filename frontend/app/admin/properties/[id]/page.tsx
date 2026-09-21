import { AdminPropertyDetail } from "@/components/admin/AdminConsole";
export default async function AdminPropertyPage({ params }: { params: Promise<{ id: string }> }) { const { id } = await params; return <AdminPropertyDetail id={id} />; }
