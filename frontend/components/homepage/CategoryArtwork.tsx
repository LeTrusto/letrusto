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

export default function CategoryArtwork({ id, className }: CategoryArtworkProps) {
  const imageSrc = ART_IMAGES[id] ?? ART_IMAGES.electronics;

  return (
    <div className={`group relative overflow-hidden rounded-[1.35rem] border border-slate-200 ${className ?? ""}`}>
      <div className="relative h-[124px] w-full">
        <Image
          src={imageSrc}
          alt=""
          fill
          sizes="(max-width: 768px) 220px, 240px"
          className="object-cover object-center transition duration-500 ease-out group-hover:scale-105"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-slate-950/42 via-slate-900/15 to-transparent" aria-hidden="true" />
      </div>
    </div>
  );
}