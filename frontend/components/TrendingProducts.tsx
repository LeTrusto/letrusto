import Image from "next/image";

const products = [
  {
    name: "iPhone 16 Pro",
    image: "/images/products/iphone16pro.png",
    price: "₹1,19,900",
    rating: "⭐ 4.8",
    badge: "Trending",
  },
  {
    name: "Samsung Galaxy S25",
    image: "/images/products/galaxy-s25.png",
    price: "₹84,999",
    rating: "⭐ 4.7",
    badge: "Best Seller",
  },
  {
    name: "MacBook Air M4",
    image: "/images/products/macbook-air-m4.png",
    price: "₹99,900",
    rating: "⭐ 4.9",
    badge: "AI Pick",
  },
  {
    name: "Sony WH-1000XM6",
    image: "/images/products/sony-wh1000xm6.png",
    price: "₹29,990",
    rating: "⭐ 4.8",
    badge: "Top Rated",
  },
];

export default function TrendingProducts() {
  return (
    <section className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-6">

        <h2 className="text-4xl font-bold text-center mb-3">
          🔥 Trending Products
        </h2>

        <p className="text-center text-gray-500 mb-12">
          Most searched products today
        </p>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {products.map((product) => (
            <div
              key={product.name}
              className="rounded-3xl bg-white shadow-md hover:shadow-2xl transition duration-300 p-6"
            >
              <div className="h-44 rounded-2xl bg-gradient-to-r from-pink-100 to-purple-100 flex items-center justify-center">
                <Image
                  src={product.image}
                  alt={product.name}
                  width={220}
                  height={220}
                  className="object-contain hover:scale-105 transition duration-300"
                />
              </div>

              <div className="mt-5">

                <span className="inline-block bg-pink-100 text-pink-700 text-xs px-3 py-1 rounded-full">
                  {product.badge}
                </span>

                <h3 className="font-bold text-xl mt-4">
                  {product.name}
                </h3>

                <p className="text-gray-500 mt-2">
                  {product.rating}
                </p>

                <p className="text-2xl font-bold mt-3">
                  {product.price}
                </p>

                <div className="flex gap-3 mt-6">
                  <button className="flex-1 bg-purple-600 text-white rounded-xl py-3 hover:bg-purple-700">
                    Compare
                  </button>

                  <button className="flex-1 border rounded-xl py-3 hover:bg-gray-100">
                    Details
                  </button>
                </div>

              </div>
            </div>
          ))}
        </div>

      </div>
    </section>
  );
}