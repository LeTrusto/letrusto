import Hero from "@/components/Hero";
import Categories from "@/components/Categories";
import TrendingProducts from "@/components/TrendingProducts";
import AIShoppingAssistant from "@/components/AIShoppingAssistant";
import HomeCollections from "@/components/HomeCollections";
import LatestArticles from "@/components/LatestArticles";

export default function Home() {
  return (
    <>
      <Hero />
      <div className="mx-auto w-full max-w-7xl px-6">
        <HomeCollections />
        <LatestArticles />
      </div>
      <Categories />
      <TrendingProducts />
      <AIShoppingAssistant />
    </>
  );
}
