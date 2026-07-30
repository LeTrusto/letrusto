import Hero from "@/components/Hero";
import SearchBar from "@/components/SearchBar";
import Categories from "@/components/Categories";
import TrendingProducts from "@/components/TrendingProducts";
import CompareSection from "@/components/CompareSection";
import AIShoppingAssistant from "@/components/AIShoppingAssistant";
import HomeCollections from "@/components/HomeCollections";
import HomePersonalized from "@/components/HomePersonalized";

 

export default function Home() {
  return (
    <>
      <Hero />
      <SearchBar />
      <div className="mx-auto w-full max-w-7xl px-6">
        <HomeCollections />
      </div>
      <Categories />
      <TrendingProducts />
      <div className="mx-auto w-full max-w-7xl px-6 pb-12">
        <HomePersonalized />
      </div>
      <AIShoppingAssistant />
      <CompareSection />
    </>
  );
}