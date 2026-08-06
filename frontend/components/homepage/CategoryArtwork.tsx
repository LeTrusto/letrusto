import Image from "next/image";

type CategoryArtworkProps = {
  id: string;
  className?: string;
};

const ART_IMAGES: Record<string, string> = {
  electronics: "/images/categories/Electronics.png",
  hosting: "/images/categories/Hosting.png",
  saas: "/images/categories/SaaS.png",
  beauty: "/images/categories/Beauty.png",
  "pet-care": "/images/categories/Pet.png",
  home: "/images/categories/Home Appliances.png",
  kitchen: "/images/categories/Kitchen.png",
  fitness: "/images/categories/Fitness.png",
  travel: "/images/categories/Travel.png",
  finance: "/images/categories/Finance.png",
  insurance: "/images/categories/Insurance.png",
};

const ART_LAYOUTS: Record<
  string,
  {
    fit: "object-cover" | "object-contain";
    position: string;
    frameInset: string;
    panelBackground: string;
  }
> = {
  electronics: {
    fit: "object-cover",
    position: "object-center",
    frameInset: "inset-y-2 inset-x-2",
    panelBackground: "bg-[radial-gradient(circle_at_top,_rgba(255,255,255,0.95),_rgba(241,245,249,0.92))]",
  },
  hosting: {
    fit: "object-contain",
    position: "object-center",
    frameInset: "inset-y-2 inset-x-2",
    panelBackground: "bg-[radial-gradient(circle_at_top,_rgba(248,250,252,0.96),_rgba(239,246,255,0.94))]",
  },
  saas: {
    fit: "object-contain",
    position: "object-center",
    frameInset: "inset-y-2 inset-x-4",
    panelBackground: "bg-[radial-gradient(circle_at_top,_rgba(245,243,255,0.96),_rgba(238,242,255,0.94))]",
  },
  beauty: {
    fit: "object-contain",
    position: "object-center",
    frameInset: "inset-y-2 inset-x-2",
    panelBackground: "bg-[radial-gradient(circle_at_top,_rgba(255,241,242,0.95),_rgba(255,247,237,0.92))]",
  },
  "pet-care": {
    fit: "object-contain",
    position: "object-center",
    frameInset: "inset-y-2 inset-x-2",
    panelBackground: "bg-[radial-gradient(circle_at_top,_rgba(255,251,235,0.96),_rgba(254,249,195,0.92))]",
  },
  home: {
    fit: "object-contain",
    position: "object-center",
    frameInset: "inset-y-2 inset-x-2",
    panelBackground: "bg-[radial-gradient(circle_at_top,_rgba(250,250,249,0.97),_rgba(254,249,240,0.93))]",
  },
  kitchen: {
    fit: "object-contain",
    position: "object-center",
    frameInset: "inset-y-2 inset-x-2",
    panelBackground: "bg-[radial-gradient(circle_at_top,_rgba(255,247,237,0.96),_rgba(254,249,195,0.9))]",
  },
  fitness: {
    fit: "object-contain",
    position: "object-center",
    frameInset: "inset-y-2 inset-x-2",
    panelBackground: "bg-[radial-gradient(circle_at_top,_rgba(240,253,244,0.96),_rgba(236,253,245,0.92))]",
  },
  travel: {
    fit: "object-contain",
    position: "object-center",
    frameInset: "inset-y-2 inset-x-2",
    panelBackground: "bg-[radial-gradient(circle_at_top,_rgba(239,246,255,0.97),_rgba(248,250,252,0.93))]",
  },
  finance: {
    fit: "object-contain",
    position: "object-center",
    frameInset: "inset-y-2 inset-x-2",
    panelBackground: "bg-[radial-gradient(circle_at_top,_rgba(236,253,245,0.96),_rgba(240,253,250,0.92))]",
  },
  insurance: {
    fit: "object-contain",
    position: "object-center",
    frameInset: "inset-y-2 inset-x-2",
    panelBackground: "bg-[radial-gradient(circle_at_top,_rgba(245,243,255,0.96),_rgba(239,246,255,0.92))]",
  },
};

export default function CategoryArtwork({ id, className }: CategoryArtworkProps) {
  const imageSrc = ART_IMAGES[id] ?? ART_IMAGES.electronics;
  const layout = ART_LAYOUTS[id] ?? ART_LAYOUTS.electronics;

  return (
    <div className={`group relative overflow-hidden rounded-[1.35rem] border border-slate-200 ${className ?? ""}`}>
      <div className={`relative h-[152px] w-full overflow-hidden ${layout.panelBackground}`}>
        <div className={`absolute ${layout.frameInset}`}>
          <Image
            src={imageSrc}
            alt=""
            fill
            sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, (max-width: 1280px) 33vw, 25vw"
            className={`${layout.fit} ${layout.position} transition duration-500 ease-out group-hover:scale-[1.03]`}
          />
        </div>
        <div className="absolute inset-0 bg-gradient-to-t from-slate-950/18 via-transparent to-white/8" aria-hidden="true" />
      </div>
    </div>
  );
}