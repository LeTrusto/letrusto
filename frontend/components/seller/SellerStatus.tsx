const labels: Record<string, string> = {
  DRAFT: "Draft",
  SUBMITTED: "Submitted",
  UNDER_REVIEW: "Under Review",
  CHANGES_REQUESTED: "Changes Requested",
  APPROVED: "Approved",
  LIVE: "Live",
  SUSPENDED: "Suspended",
  SOLD: "Sold",
  WITHDRAWN: "Withdrawn",
  EXPIRED: "Expired",
  REJECTED: "Rejected",
};

export function statusLabel(status: string) {
  return labels[status] ?? status.replaceAll("_", " ").toLowerCase().replace(/(^|\s)\S/g, (letter) => letter.toUpperCase());
}

export default function SellerStatus({ status }: { status: string }) {
  return <span className={`seller-status seller-status-${status.toLowerCase()}`}>{statusLabel(status)}</span>;
}
