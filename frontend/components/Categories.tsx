import Link from "next/link";

const categories = [
  {
    name: "Phones",
    description: "Flagship cameras, Android picks, and iPhone essentials.",
    href: "/search?category=phone",
  },
  {
    name: "Laptops",
    description: "Portable performance for coding, office work, and study.",
    href: "/search?category=laptop",
  },
  {
    name: "Headphones",
    description: "Noise-cancelling audio for travel, focus, and music.",
    href: "/search?category=headphones",
  },
];

export default function Categories() {
  return (
    <section id="categories" className="py-20">
      <h2 className="text-4xl font-bold text-center mb-10">
        Popular Categories
      </h2>

      <div className="grid gap-6 md:grid-cols-3 max-w-5xl mx-auto px-6">
        {categories.map((item) => (
          <Link
            key={item.name}
            href={item.href}
            className="rounded-3xl border border-purple-100 bg-white p-8 text-left shadow-sm transition hover:-translate-y-1 hover:shadow-xl"
          >
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-purple-500">
              Discovery
            </p>
            <h3 className="mt-4 text-2xl font-bold text-gray-900">{item.name}</h3>
            <p className="mt-3 text-gray-500">{item.description}</p>
          </Link>
        ))}
      </div>
    </section>
  );
}