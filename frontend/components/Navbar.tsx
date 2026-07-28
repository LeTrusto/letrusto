"use client";

import Image from "next/image";
import Link from "next/link";

export default function Navbar() {
  return (
    <header className="sticky top-0 z-50 bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">


        <Link href="/" className="flex items-center gap-3">
        <Image
            src="/images/logo/logo.png"
            alt="LeTrusto"
            width={70}
            height={70}
            priority
        />

        <div>
            <h1 className="text-2xl font-extrabold">
            <span className="text-pink-600">Le</span>
            <span className="text-slate-900">Trusto</span>
            </h1>

            <p className="text-xs text-gray-500">
            Know Before You Buy
            </p>
        </div>
        </Link>

        {/* Navigation */}
        <nav className="hidden md:flex items-center gap-8 font-medium text-gray-700">

          <Link href="/" className="hover:text-purple-600 transition">
            Home
          </Link>

          <Link href="#" className="hover:text-purple-600 transition">
            Categories
          </Link>

          <Link href="#" className="hover:text-purple-600 transition">
            Compare
          </Link>

          <Link href="#" className="hover:text-purple-600 transition">
            About
          </Link>

        </nav>

        {/* Buttons */}
        <div className="flex items-center gap-3">

          <button className="hidden md:block px-5 py-2 rounded-lg font-medium hover:bg-gray-100">
            Login
          </button>

          <button className="px-5 py-2 rounded-lg bg-gradient-to-r from-orange-500 via-pink-500 to-purple-600 text-white font-semibold hover:scale-105 transition">
            Get Started
          </button>

        </div>

      </div>
    </header>
  );
}