import Link from "next/link";

export default function Footer() {
  return (
    <footer className="mt-auto border-t border-gray-100 bg-white/80 backdrop-blur-md">
      <div className="mx-auto max-w-7xl px-5 py-8 sm:px-6">
        <div className="flex flex-col items-center justify-between gap-4 sm:flex-row">
          <div className="text-sm font-medium text-gray-500">
            © {new Date().getFullYear()}{" "}
            <span className="font-black">
              <span className="text-pink-600">Le</span>Trusto
            </span>
            {" "}— Your AI Buying Advisor
          </div>
          <nav className="flex flex-wrap items-center gap-x-5 gap-y-2 text-sm text-gray-500">
            <Link href="/" className="hover:text-purple-700">Home</Link>
            <Link href="/deals" className="hover:text-purple-700">Deals</Link>
            <Link href="/compare" className="hover:text-purple-700">Compare</Link>
            <Link href="/ai" className="hover:text-purple-700">AI Advisor</Link>
            <Link href="/support" className="hover:text-purple-700">Support</Link>
            <Link href="/support?tab=contact" className="hover:text-purple-700">Contact</Link>
          </nav>
        </div>
      </div>
    </footer>
  );
}
