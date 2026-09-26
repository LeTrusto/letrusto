"use client";

import { HomeHero, BuyerSellerSection, IntroSection, CategorySection, CityStory, LocalitySection, DifferenceSection, WhySection, ClosingSection } from "./PropertyHomeSections";
import { PropertyRail } from "./PropertyRail";

export function PropertyExperience() {
  return <main className="property-experience"><HomeHero /><PropertyRail title="Available properties" eyebrow="Live listings" /><BuyerSellerSection /><IntroSection /><CategorySection /><CityStory /><LocalitySection /><DifferenceSection /><WhySection /><ClosingSection /></main>;
}
