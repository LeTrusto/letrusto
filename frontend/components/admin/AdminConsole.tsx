"use client";

import {
  Check,
  CheckCheck,
  Copy,
  ChevronRight,
  CircleAlert,
  FileCheck2,
  MessageSquareWarning,
  Megaphone,
  RefreshCw,
  ArrowUpRight,
  Send,
  Users,
  X,
} from "lucide-react";
import Link from "next/link";
import Image from "next/image";
import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { verificationCheckLabels, verificationChecksForStatus, verificationLabelForStatus } from "@/utils/verification";
import {
  getAdminDashboard,
  getAdminProperty,
  listAdminEnquiries,
  listAdminProperties,
  listAdminSellers,
  publishAdminProperty,
  reviewAdminProperty,
  updateAdminVerification,
  createAdminCampaign,
  listAdminCampaigns,
  updateAdminCampaign,
  type AdminCampaign,
  type AdminDashboard,
  type AdminEnquiry,
  type AdminProperty,
  type AdminSeller,
  listAdminMonetizationPlans,
  type MonetizationPlan,
} from "@/services/admin.service";

const date = (value?: string | null) =>
  value
    ? new Date(value).toLocaleDateString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric",
      })
    : "-";
const money = (value: number | string | null) =>
  value == null ? "-" : `INR ${Number(value).toLocaleString("en-IN")}`;
function Status({ value }: { value: string }) {
  return (
    <span className={`admin-status status-${value.toLowerCase()}`}>
      {value.replaceAll("_", " ")}
    </span>
  );
}

export function AdminOverview() {
  const { accessToken } = useAuth();
  const [data, setData] = useState<AdminDashboard | null>(null);
  const [plans, setPlans] = useState<MonetizationPlan[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const load = () => {
    if (!accessToken) return;
    setLoading(true);
    setError("");
    void Promise.all([getAdminDashboard(accessToken), listAdminMonetizationPlans(accessToken)]).then(([dashboard, planRows]) => { setData(dashboard); setPlans(planRows); }).catch((e) => setError(e.message)).finally(() => setLoading(false));
  };
  useEffect(() => {
    if (accessToken) void Promise.all([getAdminDashboard(accessToken), listAdminMonetizationPlans(accessToken)]).then(([dashboard, planRows]) => { setData(dashboard); setPlans(planRows); }).catch((e) => setError(e.message)).finally(() => setLoading(false));
  }, [accessToken]);
  if (loading && !data) return <div className="admin-loading-panel"><div className="admin-skeleton admin-skeleton-wide" /><div className="admin-skeleton-grid">{Array.from({ length: 6 }).map((_, index) => <div className="admin-skeleton" key={index} />)}</div></div>;
  if (error && !data) return <div className="admin-empty-panel"><h2>Operations data is unavailable.</h2><p>{error}</p><button className="admin-action-secondary" onClick={load}><RefreshCw size={15} /> Retry</button></div>;
  if (!data) return null;
  const propertyCards = [{ label: "Draft", key: "draft", href: "DRAFT" }, { label: "Submitted", key: "submitted", href: "SUBMITTED" }, { label: "Under review", key: "under_review", href: "UNDER_REVIEW" }, { label: "LIVE", key: "live", href: "LIVE" }, { label: "Changes requested", key: "changes_requested", href: "CHANGES_REQUESTED" }];
  const leadCards = [{ label: "New", key: "new", href: "NEW" }, { label: "Contacted", key: "contacted", href: "CONTACTED" }, { label: "Follow up", key: "follow_up", href: "FOLLOW_UP" }, { label: "Visited", key: "visited", href: "VISITED" }];
  return (
    <>
      <div className="admin-command-heading"><Heading title="Admin operations" eyebrow="Command center" /><button className="admin-action-secondary" onClick={load} disabled={loading}><RefreshCw size={15} className={loading ? "admin-spin" : ""} /> Refresh</button></div>
      <section className="admin-command-section"><div className="admin-section-head"><div><p className="admin-eyebrow">Property workflow</p><h2>Know what needs moving</h2></div><span className="admin-kicker">Live data</span></div><div className="admin-command-grid">{propertyCards.map((card) => <Link className="admin-command-card" href={`/admin/properties?status=${card.href}`} key={card.key}><span>{card.label}</span><strong>{data.properties[card.key] ?? 0}</strong><ArrowUpRight size={16} /></Link>)}</div></section>
      <section className="admin-command-section"><div className="admin-section-head"><div><p className="admin-eyebrow">Lead workflow</p><h2>Buyer enquiries</h2></div><Link href="/admin/enquiries">View all <ChevronRight size={15} /></Link></div><div className="admin-command-grid admin-command-grid-leads">{leadCards.map((card) => <Link className="admin-command-card" href={`/admin/enquiries?status=${card.href}`} key={card.key}><span>{card.label}</span><strong>{data.leads[card.key] ?? 0}</strong><ArrowUpRight size={16} /></Link>)}</div></section>
      <section className="admin-command-section"><div className="admin-command-grid admin-command-grid-secondary"><Link className="admin-command-card admin-command-card-accent" href="/admin/sellers"><Users size={18} /><span>Active sellers</span><strong>{data.sellers.active}</strong><ArrowUpRight size={16} /></Link><Link className="admin-command-card admin-command-card-accent" href="/admin/properties?status=LIVE"><Megaphone size={18} /><span>Active campaigns</span><strong>{data.campaigns.active}</strong><ArrowUpRight size={16} /></Link></div></section>
      <section className="admin-command-section"><div className="admin-section-head"><div><p className="admin-eyebrow">Monetization foundation</p><h2>Plan configuration</h2></div><span className="admin-kicker">Payments not enabled</span></div><div className="admin-command-grid admin-command-grid-plans">{plans.map((plan) => <article className="admin-command-card admin-plan-card" key={plan.code}><div className="admin-plan-card-top"><span>{plan.code}</span><Status value={plan.is_active ? "CONFIGURED" : "PLANNED"} /></div><h3>{plan.name}</h3><p>{plan.description}</p><strong>{plan.price_amount == null ? "Price to be configured" : `${plan.currency || ""} ${plan.price_amount}`}</strong><small>{plan.customer_purchase_enabled ? "Purchasing enabled" : "Not purchasable"} · {plan.features.length} feature concepts</small></article>)}</div></section>
      <section className="admin-attention-section"><div className="admin-section-head"><div><p className="admin-eyebrow">Priority queue</p><h2>Needs your attention</h2></div><CircleAlert size={21} /></div><div className="admin-attention-grid"><AttentionPanel title="Properties awaiting review" count={data.properties.submitted + data.properties.under_review} href="/admin/properties?status=SUBMITTED" rows={data.attention.review.map((item) => ({ id: item.id, title: item.title, detail: item.location || "Bengaluru", status: item.status }))} empty="No properties are currently waiting for review." /><AttentionPanel title="New buyer enquiries" count={data.leads.new} href="/admin/enquiries?status=NEW" rows={data.recent_enquiries.filter((item) => item.status === "NEW").slice(0, 4).map((item) => ({ id: item.id, title: item.property_title, detail: item.buyer_name, status: item.status }))} empty="No new buyer enquiries." /><AttentionPanel title="Waiting for seller changes" count={data.properties.changes_requested} href="/admin/properties?status=CHANGES_REQUESTED" rows={data.attention.changes_requested.map((item) => ({ id: item.id, title: item.title, detail: item.location || "Bengaluru", status: item.status }))} empty="No properties are waiting for seller changes." /><AttentionPanel title="Active marketing campaigns" count={data.campaigns.active} href="/admin/properties?status=LIVE" rows={data.attention.campaigns.map((item) => ({ id: item.property_id, title: item.title, detail: item.property_title || "LIVE property", status: "ACTIVE" }))} empty="No active campaigns." /></div></section>
      <section className="admin-section">
        <div className="admin-section-head">
          <h2>Recent enquiries</h2>
          <Link href="/admin/enquiries">
            View all <ChevronRight size={15} />
          </Link>
        </div>
        <EnquiryTable rows={data.recent_enquiries} />
      </section>
    </>
  );
}
function AttentionPanel({ title, count, href, rows, empty }: { title: string; count: number; href: string; rows: { id: string; title: string; detail: string; status: string }[]; empty: string }) {
  return <article className="admin-attention-panel"><div className="admin-attention-panel-head"><div><h3>{title}</h3><strong>{count}</strong></div><Link href={href} aria-label={`Open ${title}`}><ArrowUpRight size={17} /></Link></div>{rows.length ? <div className="admin-attention-list">{rows.map((row) => <Link href={`/admin/properties/${row.id}`} key={row.id}><span><strong>{row.title}</strong><small>{row.detail}</small></span><Status value={row.status} /></Link>)}</div> : <p className="admin-empty">{empty}</p>}</article>;
}
function Heading({ title, eyebrow }: { title: string; eyebrow: string }) {
  return (
    <div className="admin-heading">
      <p className="admin-eyebrow">{eyebrow}</p>
      <h1>{title}</h1>
    </div>
  );
}

export function AdminProperties() {
  const { accessToken } = useAuth();
  const searchParams = useSearchParams();
  const status = searchParams.get("status");
  const [rows, setRows] = useState<AdminProperty[]>([]);
  useEffect(() => {
    if (accessToken) void listAdminProperties(accessToken, status).then(setRows);
  }, [accessToken, status]);
  return (
    <>
      <Heading title={status ? `${status.replaceAll("_", " ")} properties` : "Review queue"} eyebrow="Properties" />
      <div className="admin-queue">
        {rows.length ? (
          rows.map((property) => (
            <Link
              className="admin-property-row"
              href={`/admin/properties/${property.id}`}
              key={property.id}
            >
              <div>
                <p className="admin-kicker">
                  {property.location.name} · submitted{" "}
                  {date(property.submitted_at)}
                </p>
                <h2>{property.title}</h2>
                <p>
                  {property.seller.display_name} ·{" "}
                  {money(property.price_amount)}
                </p>
              </div>
              <Status value={property.status} />
              <ChevronRight size={18} />
            </Link>
          ))
        ) : (
          <p className="admin-empty">No properties are waiting for review.</p>
        )}
      </div>
    </>
  );
}

export function AdminEnquiries() {
  const { accessToken } = useAuth();
  const searchParams = useSearchParams();
  const status = searchParams.get("status");
  const [rows, setRows] = useState<AdminEnquiry[]>([]);
  useEffect(() => {
    if (accessToken) void listAdminEnquiries(accessToken, status).then(setRows);
  }, [accessToken, status]);
  return (
    <>
      <Heading title={status ? `${status.replaceAll("_", " ")} enquiries` : "Buyer enquiries"} eyebrow="Leads" />
      <div className="admin-section">
        <EnquiryTable rows={rows} />
      </div>
    </>
  );
}
function EnquiryTable({ rows }: { rows: AdminEnquiry[] }) {
  return (
    <div className="admin-table-wrap">
      <table className="admin-table">
        <thead>
          <tr>
            <th>Buyer</th>
            <th>Property</th>
            <th>Contact</th>
            <th>Status</th>
            <th>Received</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.id}>
              <td>
                <strong>{row.buyer_name}</strong>
                <small>{row.buyer_email || "No email"}</small>
              </td>
              <td>
                {row.property_title}
                <small>{row.seller_name}</small>
              </td>
              <td>{row.buyer_phone}</td>
              <td>
                <Status value={row.status} />
              </td>
              <td>{date(row.created_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {!rows.length && <p className="admin-empty">No enquiries yet.</p>}
    </div>
  );
}

export function AdminSellers() {
  const { accessToken } = useAuth();
  const [rows, setRows] = useState<AdminSeller[]>([]);
  useEffect(() => {
    if (accessToken) void listAdminSellers(accessToken).then(setRows);
  }, [accessToken]);
  return (
    <>
      <Heading title="Seller directory" eyebrow="People" />
      <div className="admin-section">
        <div className="admin-table-wrap">
          <table className="admin-table">
            <thead>
              <tr>
                <th>Seller</th>
                <th>Type</th>
                <th>Contact</th>
                <th>Listings</th>
                <th>Verification</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.id}>
                  <td>
                    <strong>{row.display_name}</strong>
                    <small>{date(row.created_at)}</small>
                  </td>
                  <td>{row.seller_type.replaceAll("_", " ")}</td>
                  <td>
                    {row.phone}
                    <small>{row.email || "No email"}</small>
                  </td>
                  <td>{row.property_count ?? 0}</td>
                  <td>
                    <Status value={row.verification_status} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {!rows.length && (
            <p className="admin-empty">No seller profiles yet.</p>
          )}
        </div>
      </div>
    </>
  );
}

export function AdminPropertyDetail({ id }: { id: string }) {
  const { accessToken } = useAuth();
  const [property, setProperty] = useState<AdminProperty | null>(null);
  const [note, setNote] = useState("");
  const [verification, setVerification] = useState("NOT_REVIEWED");
  const [message, setMessage] = useState("");
  useEffect(() => {
    if (accessToken)
      void getAdminProperty(accessToken, id).then((value) => {
        setProperty(value);
        setVerification(
          value.verification?.verification_status || "NOT_REVIEWED",
        );
      });
  }, [accessToken, id]);
  if (!property) return <p className="admin-muted">Loading property...</p>;
  const act = async (
    decision: "APPROVED" | "CHANGES_REQUESTED" | "REJECTED",
  ) => {
    if (decision === "CHANGES_REQUESTED" && !note.trim()) {
      setMessage("A note is required when requesting changes.");
      return;
    }
    if (!accessToken) return;
    const result = await reviewAdminProperty(accessToken, id, decision, note);
    if (decision === "APPROVED" && result.status === "APPROVED") {
      const published = await publishAdminProperty(accessToken, id);
      setMessage("Property approved and published live.");
      setProperty({ ...property, status: published.status });
      return;
    }
    setMessage(`Property is now ${result.status}.`);
    setProperty({ ...property, status: result.status });
  };
  const publish = async () => {
    if (!accessToken) return;
    const result = await publishAdminProperty(accessToken, id);
    setMessage(`Property is now ${result.status}.`);
    setProperty({ ...property, status: result.status });
  };
  const verify = async () => {
    if (!accessToken) return;
    await updateAdminVerification(accessToken, id, verification, note);
    setMessage("Verification updated.");
    setProperty({
      ...property,
      verification: {
        ...(property.verification || {
          verification_method: null,
          notes: null,
          verified_by: null,
          verified_at: null,
          expires_at: null,
        }),
        verification_status: verification,
      },
    });
  };
  return (
    <>
      <div className="admin-detail-top">
        <div>
          <p className="admin-eyebrow">Property review</p>
          <h1>{property.title}</h1>
          <p>
            {property.location.name} · {money(property.price_amount)} ·{" "}
            {property.seller.display_name}
          </p>
        </div>
        <Status value={property.status} />
      </div>
      <div className="admin-detail-grid">
        <section className="admin-section">
          <h2>Listing information</h2>
          <dl className="admin-facts">
            <dt>Description</dt>
            <dd>{property.description}</dd>
            <dt>Address</dt>
            <dd>{property.address_line || "Locality only"}</dd>
            <dt>Evidence</dt>
            <dd>
              {property.approval_information ||
                "No approval information supplied."}
            </dd>
            <dt>Submitted</dt>
            <dd>{date(property.submitted_at)}</dd>
          </dl>
          <AdminVerificationState propertyStatus={property.status} verificationStatus={property.verification?.verification_status || "NOT_REVIEWED"} />
          <h2>Media inspection</h2>
          <div className="admin-media-review">
            {property.media.length ? (
              property.media.map((media) => (
                <div className="admin-media-review-item" key={media.id}>
                  <div className="admin-media-review-preview">
                    {media.public_url ? (
                      <Image
                        src={media.public_url}
                        alt={media.caption || "Property media"}
                        fill
                        unoptimized
                        sizes="160px"
                      />
                    ) : (
                      <span>No public preview</span>
                    )}
                  </div>
                  <strong>
                    {media.is_cover ? "Cover · " : ""}
                    {media.media_type}
                  </strong>
                  <small>
                    Order {media.sort_order + 1} · {media.status}
                  </small>
                </div>
              ))
            ) : (
              <p className="admin-muted">No media uploaded.</p>
            )}
          </div>
          <h2>Review history</h2>
          <div className="admin-timeline">
            {property.reviews.map((review) => (
              <div key={review.id}>
                <Status value={review.decision} />
                <span>{review.notes || "No note"}</span>
                <small>{date(review.created_at)}</small>
              </div>
            ))}
            {property.audit.map((entry) => (
              <div key={entry.id}>
                <FileCheck2 size={16} />
                <span>{entry.action.replaceAll("_", " ")}</span>
                <small>{date(entry.created_at)}</small>
              </div>
            ))}
          </div>
        </section>
        <aside className="admin-section admin-actions">
          <h2>Moderation</h2>
          <textarea
            value={note}
            onChange={(e) => setNote(e.target.value)}
            placeholder="Decision note"
            rows={4}
          />
          <div className="admin-action-grid">
            <button onClick={() => void act("APPROVED")}>
              <Check size={16} /> Approve & publish live
            </button>
            <button onClick={() => void act("CHANGES_REQUESTED")}>
              <MessageSquareWarning size={16} /> Request changes
            </button>
            <button className="danger" onClick={() => void act("REJECTED")}>
              <X size={16} /> Reject
            </button>
            {property.status === "APPROVED" && (
              <button className="publish" onClick={() => void publish()}>
                <Send size={16} /> Publish live
              </button>
            )}
          </div>
          <label>
            Verification status
            <select
              value={verification}
              onChange={(e) => setVerification(e.target.value)}
            >
              <option>NOT_REVIEWED</option>
              <option>CONTACT_VERIFIED</option>
              <option>RELATIONSHIP_REVIEWED</option>
              <option>DOCUMENT_EVIDENCE_REVIEWED</option>
              <option>FAILED</option>
              <option>EXPIRED</option>
            </select>
          </label>
          <button className="secondary" onClick={() => void verify()}>
            Update verification
          </button>
          {message && <p className="admin-message">{message}</p>}
        </aside>
      </div>
      {property.status === "LIVE" && <CampaignPanel property={property} token={accessToken} />}
    </>
  );
}

function AdminVerificationState({ propertyStatus, verificationStatus }: { propertyStatus: string; verificationStatus: string }) {
  const checks = verificationChecksForStatus(verificationStatus);
  return <section className="admin-verification-panel" aria-label="Verification state"><div className="admin-verification-head"><div><p className="admin-eyebrow">Separate workflow</p><h2>Property and verification</h2></div><Status value={verificationStatus} /></div><div className="admin-verification-states"><div><span>Property status</span><strong>{propertyStatus.replaceAll("_", " ")}</strong></div><div><span>Verification status</span><strong>{verificationLabelForStatus(verificationStatus)}</strong></div></div><ul className="admin-verification-checks">{verificationCheckLabels.map(([key, label]) => <li className={checks[key] ? "complete" : "incomplete"} key={key}><span aria-hidden="true">{checks[key] ? "✓" : "-"}</span>{label}{!checks[key] && <small>Not marked complete</small>}</li>)}</ul></section>;
}

function CampaignPanel({ property, token }: { property: AdminProperty; token: string | null }) {
  const [campaigns, setCampaigns] = useState<AdminCampaign[]>([]);
  const [title, setTitle] = useState(`${property.title} — Instagram Launch`);
  const [key, setKey] = useState(`${property.slug}-launch`);
  const [source, setSource] = useState("INSTAGRAM");
  const [medium, setMedium] = useState("social");
  const [content, setContent] = useState("property-post");
  const [message, setMessage] = useState("");
  const [saving, setSaving] = useState(false);
  const [copied, setCopied] = useState("");
  useEffect(() => { if (token) void listAdminCampaigns(token, property.id).then(setCampaigns).catch((error) => setMessage(error.message)); }, [token, property.id]);
  const create = async () => {
    if (!token) return;
    setSaving(true);
    try { const campaign = await createAdminCampaign(token, property.id, { campaign_title: title, campaign_key: key, source, medium, content, status: "ACTIVE" }); setCampaigns((current) => [campaign, ...current]); setMessage("Campaign saved."); } catch (error) { setMessage(error instanceof Error ? error.message : "Campaign could not be saved."); } finally { setSaving(false); }
  };
  const copy = async (label: string, value: string) => { await navigator.clipboard.writeText(value); setCopied(label); window.setTimeout(() => setCopied(""), 1600); };
  const baseUrl = typeof window === "undefined" ? "" : window.location.origin;
  return <section className="admin-section campaign-panel"><div className="admin-section-head"><div><p className="admin-eyebrow">Manual distribution</p><h2>Social campaign studio</h2></div><span className="admin-kicker">LIVE property</span></div><p className="admin-muted">Prepare a story-led content package, then publish it manually across your chosen channel.</p><div className="campaign-form"><label>Campaign name<input value={title} onChange={(event) => setTitle(event.target.value)} /></label><label>Campaign key<input value={key} onChange={(event) => setKey(event.target.value.toLowerCase().replace(/[^a-z0-9-]/g, "-"))} /></label><label>Channel<select value={source} onChange={(event) => setSource(event.target.value)}><option>INSTAGRAM</option><option>FACEBOOK</option><option>WHATSAPP</option></select></label><label>Medium<input value={medium} onChange={(event) => setMedium(event.target.value)} /></label><label>Content tag<input value={content} onChange={(event) => setContent(event.target.value)} /></label><button className="admin-action-primary" disabled={saving || !title || !key} onClick={() => void create()}>{saving ? "Saving..." : "Generate campaign"}</button></div>{message && <p className="admin-message">{message}</p>}<div className="campaign-list">{campaigns.map((campaign) => <CampaignCard key={campaign.id} campaign={campaign} token={token} copy={copy} />)}</div>{copied && <span className="campaign-copied"><CheckCheck size={14} /> Copied</span>}<p className="admin-kicker">Campaigns use only public property details. No seller or buyer information is included.</p><span className="campaign-base-url">{baseUrl}{property.slug ? `/properties/${property.slug}` : property.slug}</span></section>;
}

function CampaignCard({ campaign, token, copy }: { campaign: AdminCampaign; token: string | null; copy: (label: string, value: string) => Promise<void> }) {
  const [status, setStatus] = useState(campaign.status);
  const [posts, setPosts] = useState(campaign.social_posts);
  const url = `/properties/${campaign.property_slug}?utm_source=${campaign.source.toLowerCase()}&utm_medium=${campaign.medium}&utm_campaign=${campaign.campaign_key}&utm_content=${campaign.content || "property-post"}`;
  const save = async () => { if (!token) return; const updated = await updateAdminCampaign(token, campaign.id, { status, social_posts: posts.map((post) => ({ platform: post.platform, post_type: post.post_type, headline: post.headline, body: post.body, cta: post.cta, content: post.content })) }); setStatus(updated.status); setPosts(updated.social_posts); };
  return <article className="campaign-card"><div className="campaign-card-head"><div><p className="admin-kicker">{campaign.source} · {campaign.medium}</p><h3>{campaign.campaign_title}</h3></div><select value={status} onChange={(event) => setStatus(event.target.value)}><option>DRAFT</option><option>ACTIVE</option><option>PAUSED</option><option>COMPLETED</option></select></div><label className="campaign-url">Property URL<input readOnly value={url} onFocus={(event) => event.currentTarget.select()} /></label><button className="admin-copy-button" onClick={() => void copy("url", url)}><Copy size={14} /> Copy property URL</button><div className="campaign-post-grid">{posts.map((post, index) => <div className="campaign-post" key={`${post.platform}-${post.post_type}`}><div className="campaign-post-head"><strong>{post.platform} {post.post_type === "REEL" ? "Reel" : "Post"}</strong><button className="admin-copy-button" onClick={() => void copy(post.platform, post.body)}><Copy size={14} /> Copy</button></div><textarea value={post.body} onChange={(event) => setPosts((current) => current.map((item, itemIndex) => itemIndex === index ? { ...item, body: event.target.value } : item))} rows={7} /></div>)}</div><button className="admin-action-secondary" onClick={() => void save()}>Save campaign changes</button></article>;
}
