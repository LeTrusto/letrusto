/*
function MediaPanel({ property, selectedFile, localPreview, locked, onFile, onRegister, onDelete, saving }: { property: SellerProperty | null; selectedFile: File | null; localPreview: string; locked: boolean; onFile: (file: File) => void; onRegister: () => void; onDelete: (mediaId: string) => void; saving: boolean }) { return <aside className="seller-media-panel"><p className="seller-section-label">Property media</p><h2>Property photos</h2><p className="seller-muted">Upload clear images or a short property video. Files are checked before they become ready.</p>{property ? <><label className="seller-upload"><input type="file" accept="image/jpeg,image/png,image/webp,video/mp4,video/webm" disabled={locked || saving} onChange={(event) => { const file = event.target.files?.[0]; if (file) onFile(file); }} />{localPreview ? <Image src={localPreview} alt="Selected preview" fill unoptimized sizes="290px" /> : <><ImagePlus size={22} /><span>Upload photos or video</span><small>JPEG, PNG, WebP up to 10 MB. Video up to 100 MB.</small></>}</label>{selectedFile && <button type="button" className="seller-secondary-button seller-media-save" disabled={saving || locked} onClick={onRegister}>{saving ? <Loader2 className="spin" size={16} /> : <Video size={16} />} Upload media</button>}<div className="seller-media-list">{property.media.length === 0 ? <p className="seller-muted">No media added yet.</p> : property.media.map((media) => <div className="seller-media-item" key={media.id}>{media.public_url ? <Image src={media.public_url} alt={media.caption ?? "Property media"} fill unoptimized sizes="140px" /> : <span className="seller-media-placeholder"><ImagePlus size={18} /></span>}<span>{media.is_cover ? "Cover · Ready" : statusLabel(media.status)}</span><button type="button" aria-label={`Delete ${media.caption ?? "media"}`} disabled={saving || locked} onClick={() => onDelete(media.id)}><Trash2 size={15} /></button></div>)}</div></> : <div className="seller-media-locked"><ImagePlus size={22} /><p>Save the property draft first, then add media.</p></div>}</aside>; }
*/
"use client";

import {
  ArrowLeft,
  Check,
  ImagePlus,
  Loader2,
  Send,
  Save,
  Trash2,
  Video,
} from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

import SellerStatus, { statusLabel } from "@/components/seller/SellerStatus";
import { VerificationSummary } from "@/components/verification/VerificationSummary";
import { verificationFromStatus } from "@/utils/verification";
import { useAuth } from "@/hooks/useAuth";
import {
  createSellerMediaUploadTarget,
  createSellerProperty,
  deleteSellerMedia,
  getLocations,
  getSellerProperty,
  requestSellerPropertyChanges,
  submitSellerProperty,
  updateSellerProperty,
  uploadSellerMedia,
  type Location,
  type PropertyPayload,
  type SellerProperty,
} from "@/services/seller.service";

type FormState = Record<string, string | boolean>;
const propertyTypes = [
  { value: "APARTMENT", label: "Apartment" },
  { value: "INDEPENDENT_HOUSE", label: "Independent house" },
  { value: "VILLA", label: "Villa" },
  { value: "RESIDENTIAL_PLOT", label: "Residential plot" },
];
const amenities = [
  "Lift",
  "Parking",
  "Security",
  "Power backup",
  "Gym",
  "Swimming pool",
  "Garden",
  "Clubhouse",
];
const allowedMediaTypes = new Set([
  "image/jpeg",
  "image/png",
  "image/webp",
  "video/mp4",
  "video/webm",
]);
const imageMaxSize = 10 * 1024 * 1024;
const videoMaxSize = 100 * 1024 * 1024;
const initialForm: FormState = {
  location_id: "",
  title: "",
  description: "",
  property_type: "APARTMENT",
  price_amount: "",
  built_up_area_sqft: "",
  carpet_area_sqft: "",
  plot_area_sqft: "",
  bhk: "",
  floor_number: "",
  total_floors: "",
  property_age_years: "",
  facing: "",
  parking_details: "",
  maintenance_amount: "",
  possession_status: "",
  road_width_ft: "",
  plot_dimensions: "",
  corner_site: false,
  approval_information: "",
  address_line: "",
  address_visibility: "LOCALITY_ONLY",
};

export default function PropertyEditor() {
  const { accessToken } = useAuth();
  const params = useParams<{ id?: string }>();
  const router = useRouter();
  const propertyId = params.id;
  const editing = Boolean(propertyId);
  const [form, setForm] = useState<FormState>(initialForm);
  const [property, setProperty] = useState<SellerProperty | null>(null);
  const [locations, setLocations] = useState<Location[]>([]);
  const [loading, setLoading] = useState(editing);
  const [saving, setSaving] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [requestingChanges, setRequestingChanges] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [localPreviews, setLocalPreviews] = useState<string[]>([]);
  const type = String(form.property_type);
  const isPlot = type === "RESIDENTIAL_PLOT";
  const isApartment = type === "APARTMENT";
  const showHomeFields = !isPlot;
  const localities = useMemo(
    () => locations.filter((location) => location.location_type === "LOCALITY"),
    [locations],
  );

  useEffect(() => {
    void getLocations()
      .then(setLocations)
      .catch(() =>
        setError("We couldn't load Bangalore localities. Please try again."),
      );
  }, []);
  useEffect(() => {
    if (!accessToken || !propertyId) return;
    void getSellerProperty(accessToken, propertyId)
      .then((loaded) => {
        setProperty(loaded);
        setForm(fromProperty(loaded));
      })
      .catch(() =>
        setError(
          "We couldn't find this property or you don't have permission to manage it.",
        ),
      )
      .finally(() => setLoading(false));
  }, [accessToken, propertyId]);
  function update(key: string, value: string | boolean) {
    setForm((current) => ({ ...current, [key]: value }));
    setNotice("");
  }
  function payload(): PropertyPayload {
    const result: Record<string, unknown> = {
      location_id: form.location_id,
      title: form.title,
      description: form.description,
      property_type: form.property_type,
      price_amount: numberValue(form.price_amount),
      currency: "INR",
      address_visibility: form.address_visibility,
    };
    [
      "built_up_area_sqft",
      "carpet_area_sqft",
      "plot_area_sqft",
      "bhk",
      "floor_number",
      "total_floors",
      "property_age_years",
      "maintenance_amount",
      "road_width_ft",
    ].forEach((key) => {
      if (String(form[key] ?? "").trim()) result[key] = numberValue(form[key]);
    });
    [
      "facing",
      "parking_details",
      "possession_status",
      "plot_dimensions",
      "approval_information",
      "address_line",
    ].forEach((key) => {
      if (String(form[key] ?? "").trim()) result[key] = form[key];
    });
    result.corner_site = form.corner_site;
    result.amenities = Object.fromEntries(
      amenities.map((name) => [name, Boolean(form[`amenity_${name}`])]),
    );
    return result as PropertyPayload;
  }
  async function saveDraft() {
    if (!accessToken) return;
    setSaving(true);
    setError("");
    setNotice("");
    try {
      const saved =
        editing && propertyId
          ? await updateSellerProperty(accessToken, propertyId, payload())
          : await createSellerProperty(accessToken, payload());
      setProperty(saved);
      setForm(fromProperty(saved));
      setNotice("Draft saved. You can return to it any time.");
      if (!editing && selectedFiles.length) await registerMedia(saved, selectedFiles);
      if (!editing) router.replace(`/seller/properties/${saved.id}`);
    } catch (err) {
      setError(friendlyError(err));
    } finally {
      setSaving(false);
    }
  }
  async function submit() {
    if (!accessToken) return;
    const missing = [
      !form.location_id && "locality",
      !String(form.title).trim() && "title",
      !String(form.description).trim() && "description",
      !String(form.price_amount).trim() && "price",
    ];
    if (missing.some(Boolean)) {
      setError(
        `Please add the required ${missing.filter(Boolean).join(", ")} before submitting.`,
      );
      return;
    }
    setSubmitting(true);
    setError("");
    try {
      let saved = property;
      if (!saved) {
        saved = await createSellerProperty(accessToken, payload());
        setProperty(saved);
      } else if (
        saved.status === "DRAFT" ||
        saved.status === "CHANGES_REQUESTED"
      ) {
        saved = await updateSellerProperty(accessToken, saved.id, payload());
        setProperty(saved);
      }
      await submitSellerProperty(accessToken, saved.id);
      setNotice(
        "Your property is now under review. We'll review the details before it becomes visible to buyers.",
      );
      setProperty((current) =>
        current ? { ...current, status: "SUBMITTED" } : current,
      );
    } catch (err) {
      setNotice("");
      setError(friendlyError(err));
    } finally {
      setSubmitting(false);
    }
  }
  async function requestChanges() {
    if (!accessToken || !property || property.status !== "LIVE") return;
    setRequestingChanges(true);
    setError("");
    setNotice("");
    try {
      const updated = await requestSellerPropertyChanges(accessToken, property.id);
      setProperty((current) => current ? { ...current, status: updated.status } : current);
      setNotice("Editing is enabled. Update the listing and submit it again for review.");
    } catch (err) {
      setError(friendlyError(err));
    } finally {
      setRequestingChanges(false);
    }
  }
  async function registerMedia(
    targetProperty = property,
    files = selectedFiles,
  ) {
    if (!accessToken || !targetProperty || !files.length) return;
    setSaving(true);
    setError("");
    try {
      for (const [index, file] of files.entries()) {
        setNotice(`Uploading media ${index + 1} of ${files.length}...`);
        const target = await createSellerMediaUploadTarget(
          accessToken,
          targetProperty.id,
          {
            media_type: file.type.startsWith("video/") ? "VIDEO" : "IMAGE",
            mime_type: file.type,
            file_size_bytes: file.size,
            is_cover: targetProperty.media.length === 0 && index === 0,
            caption: file.name,
          },
        );
        await uploadSellerMedia(accessToken, targetProperty.id, target.media_id, file, file.type);
      }
      setNotice(`Upload successful: ${files.length} media ${files.length === 1 ? "file" : "files"} ready for review.`);
      setSelectedFiles([]);
      setLocalPreviews([]);
      const refreshed = await getSellerProperty(accessToken, targetProperty.id);
      setProperty(refreshed);
    } catch (err) {
      setError(friendlyError(err));
    } finally {
      setSaving(false);
    }
  }
  async function removeMedia(mediaId: string) {
    if (!accessToken || !property || !window.confirm("Delete this media?"))
      return;
    setSaving(true);
    setError("");
    try {
      await deleteSellerMedia(accessToken, property.id, mediaId);
      setProperty((current) =>
        current
          ? {
              ...current,
              media: current.media.filter((media) => media.id !== mediaId),
            }
          : current,
      );
      setNotice("Media deleted.");
    } catch (err) {
      setError(friendlyError(err));
    } finally {
      setSaving(false);
    }
  }
  if (loading) return <p className="seller-empty">Loading property...</p>;
  if (error && editing && !property)
    return (
      <div className="seller-empty seller-empty-panel">
        <p className="eyebrow">Property unavailable</p>
        <h1>We couldn&apos;t open this property.</h1>
        <p>{error}</p>
        <Link href="/seller" className="seller-primary-button">
          Back to properties <ArrowLeft size={16} />
        </Link>
      </div>
    );
  const locked = Boolean(
    property && !["DRAFT", "CHANGES_REQUESTED"].includes(property.status),
  );
  return (
    <>
      <header className="seller-page-heading">
        <div>
          <Link href="/seller" className="seller-back-link">
            <ArrowLeft size={15} /> Your properties
          </Link>
          <p className="eyebrow">
            {editing ? "Manage property" : "New listing"}
          </p>
          <h1 className="seller-display-title">
            {editing ? property?.title || "Edit property" : "Add your property"}
          </h1>
          {property && <SellerStatus status={property.status} />}
        </div>
        <div className="seller-editor-actions">
          <button
            type="button"
            className="seller-secondary-button"
            disabled={saving || locked}
            onClick={() => void saveDraft()}
          >
            <Save size={16} /> Save draft
          </button>
          <button
            type="button"
            className="seller-primary-button"
            disabled={saving || submitting || locked}
            onClick={() => void submit()}
          >
            <Send size={16} />{" "}
            {submitting ? "Submitting..." : "Submit for review"}
          </button>
          {property?.status === "LIVE" && (
            <button
              type="button"
              className="seller-secondary-button"
              disabled={saving || submitting || requestingChanges}
              onClick={() => void requestChanges()}
            >
              {requestingChanges ? "Enabling edits..." : "Request changes to edit"}
            </button>
          )}
        </div>
      </header>
      {property?.status === "CHANGES_REQUESTED" && (
        <div className="seller-notice">
          <strong>Changes requested</strong>
          <span>
            Update the property details below and submit it again for review.
          </span>
        </div>
      )}
      {error && (
        <p className="seller-alert" role="alert">
          {error}
        </p>
      )}
      {notice && (
        <p className="seller-success" role="status">
          <Check size={16} /> {notice}
        </p>
      )}
      {property && <VerificationSummary verification={property.verification || verificationFromStatus(property.verification_label)} />}
      <div className={`seller-editor ${locked ? "seller-editor-locked" : ""}`}>
        <section className="seller-form-panel">
          <FormSection title="Property type">
            <div className="seller-type-grid">
              {propertyTypes.map((item) => (
                <label
                  key={item.value}
                  className={`seller-type-option ${type === item.value ? "selected" : ""}`}
                >
                  <input
                    type="radio"
                    name="property_type"
                    checked={type === item.value}
                    disabled={locked}
                    onChange={() => update("property_type", item.value)}
                  />
                  {item.label}
                </label>
              ))}
            </div>
          </FormSection>
          <FormSection title="Basic information">
            <div className="seller-form-grid">
              <label className="seller-span-2">
                Property title
                <input
                  required
                  disabled={locked}
                  value={String(form.title)}
                  onChange={(event) => update("title", event.target.value)}
                  placeholder="Spacious 3BHK Corner Apartment in Banashankari"
                />
              </label>
              <label className="seller-span-2">
                Description
                <textarea
                  required
                  disabled={locked}
                  value={String(form.description)}
                  onChange={(event) =>
                    update("description", event.target.value)
                  }
                  placeholder="Bright corner apartment with good ventilation, parking and easy access to daily conveniences."
                  rows={5}
                />
              </label>
              <label>
                Sale price (INR)
                <input
                  required
                  disabled={locked}
                  inputMode="numeric"
                  value={String(form.price_amount)}
                  onChange={(event) =>
                    update("price_amount", event.target.value)
                  }
                  placeholder="38500000"
                />
              </label>
              {showHomeFields && (
                <label>
                  BHK
                  <input
                    disabled={locked}
                    inputMode="numeric"
                    value={String(form.bhk)}
                    onChange={(event) => update("bhk", event.target.value)}
                    placeholder="3"
                  />
                </label>
              )}
              {showHomeFields && (
                <label>
                  Built-up area (sq ft)
                  <input
                    disabled={locked}
                    inputMode="numeric"
                    value={String(form.built_up_area_sqft)}
                    onChange={(event) =>
                      update("built_up_area_sqft", event.target.value)
                    }
                  />
                </label>
              )}
              {showHomeFields && (
                <label>
                  Carpet area (sq ft)
                  <input
                    disabled={locked}
                    inputMode="numeric"
                    value={String(form.carpet_area_sqft)}
                    onChange={(event) =>
                      update("carpet_area_sqft", event.target.value)
                    }
                  />
                </label>
              )}
              {isPlot && (
                <label>
                  Plot area (sq ft)
                  <input
                    disabled={locked}
                    inputMode="numeric"
                    value={String(form.plot_area_sqft)}
                    onChange={(event) =>
                      update("plot_area_sqft", event.target.value)
                    }
                  />
                </label>
              )}
              {showHomeFields && (
                <label>
                  Property age (years)
                  <input
                    disabled={locked}
                    inputMode="numeric"
                    value={String(form.property_age_years)}
                    onChange={(event) =>
                      update("property_age_years", event.target.value)
                    }
                  />
                </label>
              )}
              {isApartment && (
                <>
                  <label>
                    Floor
                    <input
                      disabled={locked}
                      inputMode="numeric"
                      value={String(form.floor_number)}
                      onChange={(event) =>
                        update("floor_number", event.target.value)
                      }
                    />
                  </label>
                  <label>
                    Total floors
                    <input
                      disabled={locked}
                      inputMode="numeric"
                      value={String(form.total_floors)}
                      onChange={(event) =>
                        update("total_floors", event.target.value)
                      }
                    />
                  </label>
                  <label>
                    Maintenance (INR)
                    <input
                      disabled={locked}
                      inputMode="numeric"
                      value={String(form.maintenance_amount)}
                      onChange={(event) =>
                        update("maintenance_amount", event.target.value)
                      }
                    />
                  </label>
                </>
              )}
              {showHomeFields && (
                <label>
                  Parking
                  <input
                    disabled={locked}
                    value={String(form.parking_details)}
                    onChange={(event) =>
                      update("parking_details", event.target.value)
                    }
                    placeholder="Covered parking"
                  />
                </label>
              )}
              <label>
                Facing
                <input
                  disabled={locked}
                  value={String(form.facing)}
                  onChange={(event) => update("facing", event.target.value)}
                  placeholder="East"
                />
              </label>
              <label>
                Possession
                <select
                  disabled={locked}
                  value={String(form.possession_status)}
                  onChange={(event) =>
                    update("possession_status", event.target.value)
                  }
                >
                  <option value="">Select status</option>
                  <option value="READY">Ready</option>
                  <option value="UNDER_CONSTRUCTION">Under construction</option>
                </select>
              </label>
            </div>
          </FormSection>
          <FormSection title="Location">
            <div className="seller-form-grid">
              <label>
                Locality
                <select
                  required
                  disabled={locked}
                  value={String(form.location_id)}
                  onChange={(event) =>
                    update("location_id", event.target.value)
                  }
                >
                  <option value="">Select a locality</option>
                  {localities.map((location) => (
                    <option key={location.id} value={location.id}>
                      {location.name}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Address visibility
                <select
                  disabled={locked}
                  value={String(form.address_visibility)}
                  onChange={(event) =>
                    update("address_visibility", event.target.value)
                  }
                >
                  <option value="LOCALITY_ONLY">Locality only</option>
                  <option value="APPROXIMATE">Approximate</option>
                  <option value="PRIVATE">Private</option>
                </select>
              </label>
              <label className="seller-span-2">
                Address or landmark
                <input
                  disabled={locked}
                  value={String(form.address_line)}
                  onChange={(event) =>
                    update("address_line", event.target.value)
                  }
                  placeholder="A nearby landmark, if useful"
                />
              </label>
            </div>
          </FormSection>
          <FormSection title="Features">
            <div className="seller-feature-grid">
              {amenities.map((name) => (
                <label key={name} className="seller-checkbox">
                  <input
                    type="checkbox"
                    disabled={locked}
                    checked={Boolean(form[`amenity_${name}`])}
                    onChange={(event) =>
                      update(`amenity_${name}`, event.target.checked)
                    }
                  />{" "}
                  {name}
                </label>
              ))}
            </div>
            {isPlot && (
              <div className="seller-form-grid seller-feature-extra">
                <label>
                  Road width (ft)
                  <input
                    disabled={locked}
                    value={String(form.road_width_ft)}
                    onChange={(event) =>
                      update("road_width_ft", event.target.value)
                    }
                  />
                </label>
                <label>
                  Plot dimensions
                  <input
                    disabled={locked}
                    value={String(form.plot_dimensions)}
                    onChange={(event) =>
                      update("plot_dimensions", event.target.value)
                    }
                    placeholder="40 ft x 60 ft"
                  />
                </label>
                <label className="seller-checkbox">
                  <input
                    type="checkbox"
                    disabled={locked}
                    checked={Boolean(form.corner_site)}
                    onChange={(event) =>
                      update("corner_site", event.target.checked)
                    }
                  />{" "}
                  Corner site
                </label>
                <label className="seller-span-2">
                  Approval information
                  <textarea
                    disabled={locked}
                    value={String(form.approval_information)}
                    onChange={(event) =>
                      update("approval_information", event.target.value)
                    }
                    rows={3}
                  />
                </label>
              </div>
            )}
          </FormSection>
        </section>
        <MediaPanel
          property={property}
          selectedFiles={selectedFiles}
          localPreviews={localPreviews}
          locked={locked}
          onFiles={(files) => {
            const invalidFiles = files.filter(
              (file) =>
                !allowedMediaTypes.has(file.type) ||
                file.size > (file.type.startsWith("video/") ? videoMaxSize : imageMaxSize),
            );
            const validFiles = files.filter((file) => !invalidFiles.includes(file));
            setSelectedFiles(validFiles);
            setError(
              invalidFiles.length
                ? `${invalidFiles.length} file${invalidFiles.length === 1 ? "" : "s"} could not be selected. Images must be under 10 MB; videos under 100 MB.`
                : "",
            );
            setLocalPreviews(
              validFiles.map((file) =>
                file.type.startsWith("image/")
                  ? URL.createObjectURL(file)
                  : "",
              ),
            );
          }}
          onRegister={() => void registerMedia()}
          onDelete={removeMedia}
          saving={saving}
        />
      </div>
    </>
  );
}

function FormSection({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="seller-form-section">
      <p className="seller-section-label">{title}</p>
      {children}
    </div>
  );
}
function MediaPanel({
  property,
  selectedFiles,
  localPreviews,
  locked,
  onFiles,
  onRegister,
  onDelete,
  saving,
}: {
  property: SellerProperty | null;
  selectedFiles: File[];
  localPreviews: string[];
  locked: boolean;
  onFiles: (files: File[]) => void;
  onRegister: () => void;
  onDelete: (mediaId: string) => void;
  saving: boolean;
}) {
  return (
    <aside className="seller-media-panel">
      <p className="seller-section-label">Property media</p>
      <h2>Property photos</h2>
      <p className="seller-muted">
        Upload clear images or a short property video. Files are checked before
        they become ready.
      </p>
      <>
        <label className="seller-upload">
          <input
            type="file"
            multiple
            accept="image/jpeg,image/png,image/webp,video/mp4,video/webm"
            disabled={locked || saving}
            onChange={(event) => {
              const files = Array.from(event.target.files ?? []);
              if (files.length) onFiles(files);
            }}
          />
          {localPreviews.length ? (
            <div className="seller-upload-preview-grid">
              {localPreviews.map((preview, index) =>
                preview ? (
                  <Image
                    key={preview}
                    src={preview}
                    alt={`Selected preview ${index + 1}`}
                    fill
                    unoptimized
                    sizes="145px"
                  />
                ) : (
                  <span className="seller-upload-file" key={`file-${index}`}>
                    <Video size={18} />
                    {selectedFiles[index]?.name}
                  </span>
                ),
              )}
            </div>
          ) : (
            <>
              <ImagePlus size={22} />
              <span>{property ? "Upload photos or video" : "Choose photos or video"}</span>
              <small>JPEG, PNG, WebP up to 10 MB. Video up to 100 MB.</small>
            </>
          )}
        </label>
        {selectedFiles.length && property ? (
            <button
              type="button"
              className="seller-secondary-button seller-media-save"
              disabled={saving || locked}
              onClick={onRegister}
            >
              {saving ? (
                <Loader2 className="spin" size={16} />
              ) : (
                <Video size={16} />
              )}{" "}
              Upload {selectedFiles.length} {selectedFiles.length === 1 ? "file" : "files"}
            </button>
          ) : selectedFiles.length ? (
            <p className="seller-media-note">Save the draft to enable upload for these selected files.</p>
          ) : null}
        {property ? (
          <div className="seller-media-list">
            {property.media.length === 0 ? (
              <p className="seller-muted">No media added yet.</p>
            ) : (
              property.media.map((media) => (
                <div className="seller-media-item" key={media.id}>
                  {media.public_url ? (
                    <Image
                      src={media.public_url}
                      alt={media.caption ?? "Property media"}
                      fill
                      unoptimized
                      sizes="140px"
                    />
                  ) : (
                    <span className="seller-media-placeholder">
                      <ImagePlus size={18} />
                    </span>
                  )}
                  <span>
                    {media.is_cover
                      ? "Cover - Ready"
                      : statusLabel(media.status)}
                  </span>
                  <button
                    type="button"
                    aria-label={`Delete ${media.caption ?? "media"}`}
                    disabled={saving || locked}
                    onClick={() => onDelete(media.id)}
                  >
                    <Trash2 size={15} />
                  </button>
                </div>
              ))
            )}
          </div>
        ) : (
          <p className="seller-media-note">You can choose media now. Save the property draft before uploading it.</p>
        )}
      </>
    </aside>
  );
}
function numberValue(value: string | boolean) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
}
function fromProperty(property: SellerProperty): FormState {
  const next: FormState = {
    ...initialForm,
    ...Object.fromEntries(
      Object.entries(property)
        .filter(([key]) => key in initialForm)
        .map(([key, value]) => [key, value ?? ""]),
    ),
    location_id: property.location.id,
  };
  next.corner_site = property.corner_site ?? false;
  Object.entries(property.amenities ?? {}).forEach(([name, enabled]) => {
    next[`amenity_${name}`] = Boolean(enabled);
  });
  return next;
}
function friendlyError(error: unknown) {
  const message =
    error instanceof Error
      ? error.message
      : "Something went wrong. Please try again.";
  if (message.includes("401")) return "Please sign in to continue.";
  if (message.includes("403"))
    return "You don't have permission to manage this property.";
  if (message.includes("422")) return "Please check the highlighted fields.";
  if (message.includes("404")) return "We couldn't find this property.";
  return message;
}
