import { redirect } from "next/navigation";

export default function ContactPage() {
  redirect("/support?tab=contact&category=contact");
}
