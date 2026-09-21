"use client";

import { HomeHero, IntroSection, CategorySection, CityStory, LocalitySection, DifferenceSection, SocialSection, ClosingSection } from "./PropertyHomeSections";
import { PropertyRail } from "./PropertyRail";

export function PropertyExperience() {
  return <main className="property-experience"><HomeHero /><IntroSection /><CategorySection /><CityStory /><PropertyRail /><LocalitySection /><DifferenceSection /><SocialSection /><ClosingSection /></main>;
}
