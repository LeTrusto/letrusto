"use client";

import Link from "next/link";
import Image from "next/image";
import { ArrowDown, ArrowRight, Camera, Play, Sparkles } from "lucide-react";
import { motion } from "framer-motion";

import { categories, localities, properties } from "@/lib/propertyMockData";
import { PropertyCategoryCard } from "./PropertyCategoryCard";

export function HomeHero() {
  return (
    <section className="home-hero">
      <div className="hero-grain" aria-hidden="true" />
      <nav className="site-nav section-shell" aria-label="Main navigation">
        <Link href="/" className="temporary-mark" aria-label="Home"><span className="mark-dot" />BENGALURU / VOL. 01</Link>
        <div className="nav-links"><Link href="/properties">Discover</Link><a href="#story">Our point of view</a><Link href="/login">Sign in</Link></div>
        <Link href="/properties" className="nav-pill">Explore <ArrowRight size={15} /></Link>
      </nav>
      <div className="hero-inner section-shell">
        <div className="hero-copy">
          <p className="eyebrow hero-eyebrow"><span className="eyebrow-line" /> Bangalore / Vol. 01</p>
          <h1 className="hero-title">Find somewhere<br /><em>worth coming</em><br />home to.</h1>
          <p className="hero-subtitle">A more considered way to discover the homes, plots and spaces shaping Bangalore.</p>
          <div className="hero-actions"><Link href="/properties" className="button button-dark">Explore properties <ArrowRight size={17} /></Link><a href="#collection" className="hero-scroll"><span className="scroll-icon"><ArrowDown size={15} /></span> Scroll to wander</a></div>
        </div>
        <div className="hero-visual" aria-label="Featured Bangalore property">
          <div className="hero-stamp">The<br /><strong>good<br />address</strong><br />project</div>
          <div className="hero-image-main"><Image src={properties[0].image} alt="Sunlit courtyard home in Jayanagar" fill sizes="(max-width: 900px) 80vw, 55vw" priority /></div>
          <div className="hero-image-detail"><Image src={properties[0].secondaryImage ?? properties[0].image} alt="Interior detail from the featured home" fill sizes="(max-width: 900px) 36vw, 22vw" /></div>
          <div className="hero-caption"><span>01 / 08</span><strong>The Bougainvillea House</strong><span>Jayanagar, Bengaluru</span></div>
        </div>
      </div>
      <div className="hero-bottom section-shell"><span>Curated, not crowded</span><span className="hero-bottom-rule" /><span>Scroll to explore <ArrowDown size={14} /></span></div>
    </section>
  );
}

export function IntroSection() {
  return <section className="intro-section section-shell" id="story"><div className="intro-number">01</div><div className="intro-copy"><p className="eyebrow">A different kind of property platform</p><h2 className="display-title">Bangalore,<br /><em>seen differently.</em></h2></div><div className="intro-body"><p>Some places are more than an address. They are the way the morning light lands, the walk to coffee, the tree you can see from the kitchen.</p><p>We collect the ones with a little more feeling.</p><Link href="/properties" className="text-link">Enter the collection <ArrowRight size={16} /></Link></div></section>;
}

export function CategorySection() {
  return <section className="category-section section-shell"><div className="section-heading-split"><div><p className="eyebrow">Start with a feeling</p><h2 className="display-title display-title-small">What kind of<br /><em>living calls you?</em></h2></div><p className="section-aside">From high-rise horizons to a patch of red earth, begin wherever your imagination takes you.</p></div><div className="category-grid">{categories.map((category) => <PropertyCategoryCard key={category.label} category={category} />)}</div></section>;
}

export function CityStory() {
  return <section className="city-story"><div className="city-story-image"><Image src={properties[5].image} alt="Warm modern villa surrounded by Bangalore greenery" fill sizes="100vw" /></div><div className="city-story-content section-shell"><p className="eyebrow">A city in chapters</p><h2 className="display-title city-title">Every light.<br /><em>Every shade.</em><br />One city.</h2><div className="city-story-footer"><span>Explore Bangalore by mood</span><Link href="/properties" className="round-link" aria-label="Explore Bangalore"><ArrowRight size={19} /></Link></div></div><div className="city-word" aria-hidden="true">BANGALORE</div></section>;
}

export function LocalitySection() {
  return <section className="locality-section section-shell"><div className="section-heading-split"><div><p className="eyebrow">The neighbourhood edit</p><h2 className="display-title display-title-small">Explore<br /><em>Bangalore.</em></h2></div><div className="section-aside">Discover properties across every part of Bengaluru.<br /><br />From established neighbourhoods to emerging corridors — explore properties across Bengaluru.</div></div><div className="locality-grid">{localities.map((locality, index) => <Link href={`/properties?locality=${locality.name}`} className={`locality-card locality-card-${index + 1}`} key={locality.name}><Image src={locality.image} alt="" fill sizes="(max-width: 560px) 50vw, 30vw" /><div className="locality-card-overlay" /><div className="locality-card-copy"><span>Discovery examples</span><h3>{locality.name}</h3><p>{locality.examples}</p></div></Link>)}</div></section>;
}

export function DifferenceSection() {
  const steps = [{ number: "01", title: "Discover", copy: "Property discovery with a point of view." }, { number: "02", title: "See", copy: "Rich photography and the details that matter." }, { number: "03", title: "Enquire", copy: "A direct line to the person behind the place." }, { number: "04", title: "Follow", copy: "Know what happens after you reach out." }];
  return <section className="difference-section" id="collection"><div className="section-shell"><div className="difference-top"><div><p className="eyebrow">The difference</p><h2 className="display-title display-title-small">Less noise.<br /><em>More place.</em></h2></div><p className="section-aside">A home deserves more than a thumbnail and a filter. We are building a slower, more human way to find one.</p></div><div className="difference-grid">{steps.map((step, index) => <motion.div key={step.number} className={`difference-step difference-step-${index + 1}`} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, amount: 0.4 }} transition={{ delay: index * 0.08 }}><span>{step.number}</span><div className="difference-icon">{index === 0 ? <Sparkles size={19} /> : index === 1 ? <Play size={17} /> : index === 2 ? <ArrowRight size={19} /> : <span className="follow-dot" />}</div><h3>{step.title}</h3><p>{step.copy}</p></motion.div>)}</div></div></section>;
}

export function SocialSection() {
  return <section className="social-section section-shell"><div className="social-copy"><p className="eyebrow"><Camera size={14} /> The social edit</p><h2 className="display-title display-title-small">Seen somewhere<br /><em>beautiful?</em></h2><p>Every property can become a story worth sharing. Follow the trail from a saved post to a place you can actually visit.</p><Link href="/properties" className="button button-outline">Discover the stories <ArrowRight size={17} /></Link></div><div className="social-collage"><div className="social-card social-card-main"><Image src={properties[2].image} alt="Garden villa discovery" fill sizes="(max-width: 560px) 77vw, 35vw" /><span className="social-handle">@bengaluru / 04:32 PM</span><strong>Somewhere between<br />inside and outside.</strong></div><div className="social-card social-card-note"><Camera size={18} /><span>Saved by<br /><strong>2,418 curious people</strong></span></div><div className="social-card social-card-small"><Image src={properties[7].image} alt="Indigo Court interior" fill sizes="200px" /><span>Swipe to see the inside <ArrowRight size={14} /></span></div></div></section>;
}

export function ClosingSection() {
  return <section className="closing-section"><div className="section-shell closing-grid"><div><p className="eyebrow">The next chapter</p><h2 className="display-title">Your next address<br /><em>might feel like this.</em></h2></div><div className="closing-actions"><Link href="/properties" className="button button-light">Explore Bangalore <ArrowRight size={17} /></Link><Link href="/login" className="button button-quiet">Have a property worth showing? <ArrowRight size={16} /></Link></div></div><footer className="site-footer section-shell"><span className="temporary-mark"><span className="mark-dot" />BENGALURU / VOL. 01</span><span>Property, with a point of view.</span><div><Link href="/properties">Discover</Link><Link href="/login">For sellers</Link><Link href="/login">Sign in</Link></div></footer></section>;
}
