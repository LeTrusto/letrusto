import { redirect } from "next/navigation";

export default function ReportIssuePage() {
  redirect("/support?tab=contact&category=report_broken");
}
