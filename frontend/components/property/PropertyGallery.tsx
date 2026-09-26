"use client";

import Image from "next/image";
import { useState } from "react";

import type { PublicPropertyMedia } from "@/services/property.service";

export function PropertyGallery({ title, media }: { title: string; media: PublicPropertyMedia[] }) {
  const usableMedia = media.filter((item) => item.public_url && (item.media_type === "IMAGE" || item.media_type === "VIDEO")).sort((a, b) => a.sort_order - b.sort_order);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const selected = usableMedia[selectedIndex];

  if (!selected) {
    return <section className="detail-gallery" aria-label={`${title} media gallery`}><div className="detail-gallery-main"><div className="detail-media-empty">Media coming soon</div></div></section>;
  }

  return <section className="detail-gallery" aria-label={`${title} media gallery`}>
    <div className="detail-gallery-main">
      {selected.media_type === "VIDEO" ? <video src={selected.public_url ?? undefined} controls playsInline aria-label={`${title} property video`} /> : <Image src={selected.public_url!} alt={`${title} property image ${selectedIndex + 1}`} fill sizes="(max-width: 768px) 100vw, 68vw" priority={selectedIndex === 0} unoptimized />}
      <span className="detail-type-badge">{selected.media_type === "VIDEO" ? "Video" : "Property media"}</span>
    </div>
    {usableMedia.length > 1 && <div className="detail-media-rail" role="tablist" aria-label={`${title} media choices`}>
      {usableMedia.map((item, index) => <button type="button" role="tab" aria-selected={selectedIndex === index} className={`detail-media-thumb ${selectedIndex === index ? "is-selected" : ""}`} key={item.id} onClick={() => setSelectedIndex(index)}>
        <span className="sr-only">View media {index + 1}</span>
        {item.media_type === "VIDEO" ? <span className="video-thumb">Video</span> : <Image src={item.public_url!} alt={`${title} property image ${index + 1}`} fill sizes="150px" unoptimized />}
      </button>)}
    </div>}
  </section>;
}
