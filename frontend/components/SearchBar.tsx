export default function SearchBar() {
  return (
    <div className="flex justify-center -mt-8">
      <div className="flex w-full max-w-3xl rounded-2xl border bg-white shadow-lg p-2">
        <input
          type="text"
          placeholder="What do you want to buy today?"
          className="flex-1 px-5 py-4 outline-none text-lg"
        />

        <button className="rounded-xl bg-gradient-to-r from-pink-500 to-purple-600 px-8 py-4 text-white font-semibold">
          Search
        </button>
      </div>
    </div>
  );
}