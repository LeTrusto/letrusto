"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function AIShoppingAssistant() {
  const [query, setQuery] = useState("");
  const router = useRouter();
  const popularQuestions = [
    "Best phone under ₹30,000",
    "Best laptop for Python programming",
    "Compare iPhone vs Samsung",
    "Best camera for travel",
  ];

  const handleAskAI = () => {
    if (!query.trim()) return;
    router.push(`/ai?q=${encodeURIComponent(query)}`);
  };

  return (
    <section className="py-20 bg-gradient-to-b from-white to-gray-50">
      <div className="max-w-4xl mx-auto px-6">

        <div className="text-center mb-10">
          <span className="inline-block bg-purple-100 text-purple-700 px-4 py-2 rounded-full text-sm font-semibold">
            🤖 AI Shopping Assistant
          </span>

          <h2 className="text-4xl font-bold mt-4">
            Tell us what you need.
          </h2>

          <p className="text-gray-500 mt-3">
            Describe your requirement and LeTrusto AI will recommend the perfect product.
          </p>
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-6">

          <textarea
            rows={4}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Example: Best phone under ₹30,000 with a great camera"
            className="w-full border rounded-xl p-4 outline-none resize-none"
          />

          <button
            onClick={handleAskAI}
            className="mt-5 w-full bg-gradient-to-r from-pink-500 to-purple-600 text-white py-4 rounded-xl font-semibold text-lg hover:opacity-90"
          >
            Ask LeTrusto AI
          </button>

          <div className="mt-8">
            <h3 className="font-semibold mb-4">
              💡 Popular Questions
            </h3>

            <div className="grid md:grid-cols-2 gap-3">
              {popularQuestions.map((question) => (
                <button
                  key={question}
                  type="button"
                  onClick={() => {
                    setQuery(question);
                    router.push(`/ai?q=${encodeURIComponent(question)}`);
                  }}
                  className="w-full border rounded-xl p-3 text-left cursor-pointer transition hover:bg-gray-50"
                >
                  {question}
                </button>
              ))}
            </div>
          </div>

        </div>

      </div>
    </section>
  );
}