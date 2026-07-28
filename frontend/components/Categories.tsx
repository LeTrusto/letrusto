const categories = [
  "📱 Mobiles",
  "💻 Laptops",
  "🎧 Headphones",
  "⌚ Smart Watches",
  "🏠 Home Appliances",
  "🖥️ Monitors",
];

export default function Categories() {
  return (
    <section className="py-20">
      <h2 className="text-4xl font-bold text-center mb-10">
        Popular Categories
      </h2>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
        {categories.map((item) => (
          <div
            key={item}
            className="rounded-2xl border p-8 text-center text-lg font-semibold hover:shadow-xl hover:-translate-y-1 transition cursor-pointer"
          >
            {item}
          </div>
        ))}
      </div>
    </section>
  );
}