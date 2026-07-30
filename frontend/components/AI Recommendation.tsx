"use client";

import { Sparkles } from "lucide-react";

export default function AIRecommendation() {
  return (
    <section className="py-24 bg-gradient-to-r from-purple-50 to-pink-50">
      <div className="max-w-6xl mx-auto px-6">

        <div className="text-center">

          <div className="inline-flex items-center gap-2 bg-white px-5 py-2 rounded-full shadow">
            <Sparkles className="text-purple-600" size={20} />
            <span className="font-semibold">AI Shopping Assistant</span>
          </div>

          <h2 className="text-5xl font-bold mt-6">
            Tell us what you need.
          </h2>

          <p className="text-gray-600 mt-4 text-lg">
            Describe your requirement and LeTrusto AI will recommend the
            perfect product.
          </p>

        </div>

        {/* Search */}

        <div className="mt-12 bg-white rounded-3xl shadow-xl p-8">

          <input
            type="text"
            placeholder="Example: Best phone under ₹30,000 with good camera"
            className="w-full border rounded-2xl p-5 text-lg outline-none"
          />

          <button className="mt-6 w-full bg-gradient-to-r from-pink-500 to-purple-600 text-white rounded-2xl py-4 text-lg font-bold hover:scale-[1.02] transition">
            Ask AI
          </button>

        </div>

        {/* Recommendation */}

        <div className="mt-12 bg-white rounded-3xl shadow-xl p-8">

          <span className="bg-green-100 text-green-700 px-4 py-2 rounded-full text-sm">
            🏆 AI Recommendation
          </span>

          <h3 className="text-4xl font-bold mt-6">
            Samsung Galaxy S25
          </h3>

          <p className="text-2xl text-yellow-500 mt-2">
            ⭐⭐⭐⭐⭐
          </p>

          <div className="mt-8 grid md:grid-cols-2 gap-8">

            <div>

              <h4 className="font-bold text-xl">
                AI Score
              </h4>

              <p className="text-6xl font-extrabold text-purple-600 mt-2">
                96
              </p>

              <p className="text-gray-500">
                out of 100
              </p>

            </div>

            <div className="space-y-3 text-lg">

              <p>✅ Excellent Camera</p>

              <p>✅ Powerful Processor</p>

              <p>✅ Long Battery Life</p>

              <p>✅ Best Value for Money</p>

            </div>

          </div>

          <div className="flex gap-4 mt-10">

            <button className="bg-purple-600 text-white px-8 py-3 rounded-xl">
              Compare
            </button>

            <button className="border px-8 py-3 rounded-xl">
              View Details
            </button>

          </div>

        </div>

      </div>
    </section>
  );
}