"use client";

import { HomeHero, BuyerSellerSection, IntroSection, CategorySection, CityStory, LocalitySection, DifferenceSection, WhySection, ClosingSection } from "./PropertyHomeSections";
import { PropertyRail } from "./PropertyRail";

export function PropertyExperience() {
  return <main className="property-experience"><HomeHero /><BuyerSellerSection /><IntroSection /><CategorySection /><CityStory /><PropertyRail title="Properties worth seeing" eyebrow="A considered selection" /><LocalitySection /><DifferenceSection /><WhySection /><ClosingSection /></main>;
}
