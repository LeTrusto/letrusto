import Link from "next/link";

const CATEGORIES = [
  { name: "Smartphones", slug: "smartphones", icon: "📱", color: "from-blue-500 to-indigo-600", bg: "bg-blue-50", border: "border-blue-100" },
  { name: "Laptops", slug: "laptop", icon: "💻", color: "from-violet-500 to-purple-600", bg: "bg-violet-50", border: "border-violet-100" },
  { name: "Headphones", slug: "headphones", icon: "🎧", color: "from-pink-500 to-rose-600", bg: "bg-pink-50", border: "border-pink-100" },
  { name: "Smartwatches", slug: "smartwatch", icon: "⌚", color: "from-emerald-500 to-teal-600", bg: "bg-emerald-50", border: "border-emerald-100" },
  { name: "Cameras", slug: "camera", icon: "📷", color: "from-amber-500 to-orange-600", bg: "bg-amber-50", border: "border-amber-100" },
  { name: "Gaming", slug: "gaming", icon: "🎮", color: "from-red-500 to-rose-600", bg: "bg-red-50", border: "border-red-100" },
  { name: "Televisions", slug: "television", icon: "📺", color: "from-cyan-500 to-sky-600", bg: "bg-cyan-50", border: "border-cyan-100" },
  { name: "Web Hosting", slug: "web-hosting", icon: "🌐", color: "from-green-500 to-emerald-600", bg: "bg-green-50", border: "border-green-100" },
  { name: "Tablets", slug: "tablet", icon: "📲", color: "from-fuchsia-500 to-pink-600", bg: "bg-fuchsia-50", border: "border-fuchsia-100" },
  { name: "Refrigerators", slug: "refrigerator", icon: "🧊", color: "from-sky-500 to-blue-600", bg: "bg-sky-50", border: "border-sky-100" },
];

export default function Categories() {
  return (
    <section id="categories" className="bg-white py-16">
      <div className="mx-auto max-w-7xl px-6">
        <div className="mb-10 text-center">
          <h2 className="text-3xl font-black tracking-tight text-gray-900 md:text-4xl">
            Browse by Category
          </h2>
          <p className="mt-3 text-gray-500">
            Find the perfect product in your favourite category
          </p>
        </div>

        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
          {CATEGORIES.map((cat) => (
            <Link
              key={cat.slug}
              href={`/search?category=${cat.slug}`}
              className={`group flex flex-col items-center rounded-2xl border ${cat.border} ${cat.bg} p-5 text-center transition hover:-translate-y-1 hover:shadow-lg`}
            >
              <div className={`mb-3 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br ${cat.color} text-2xl shadow-sm`}>
                {cat.icon}
              </div>
              <span className="text-sm font-bold text-gray-800 group-hover:text-gray-900">
                {cat.name}
              </span>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}
