"use client";

import Link from "next/link";
import Image from "next/image";
import { ArrowDown, ArrowRight, Check, Eye, Menu, Send, Sparkles, X } from "lucide-react";
import { motion } from "framer-motion";
import { useState } from "react";

import { categories, localities, properties } from "@/lib/propertyMockData";
import { PropertyCategoryCard } from "./PropertyCategoryCard";

export function HomeHero() {
  const [menuOpen, setMenuOpen] = useState(false);
  return (
    <section className="home-hero">
      <div className="hero-grain" aria-hidden="true" />
      <nav className="site-nav section-shell" aria-label="Main navigation">
        <Link href="/" className="temporary-mark" aria-label="Home"><span className="mark-dot" />BENGALURU PROPERTY</Link>
        <div id="homepage-navigation" className={`nav-links ${menuOpen ? "is-open" : ""}`}><Link href="/properties" onClick={() => setMenuOpen(false)}>Discover</Link><Link href="/properties" onClick={() => setMenuOpen(false)}>Buy</Link><Link href="/sell" onClick={() => setMenuOpen(false)}>Sell</Link><a href="#how-it-works" onClick={() => setMenuOpen(false)}>How it works</a></div>
        <div className="nav-actions"><Link href="/login" className="nav-sign-in">Sign in</Link><Link href="/sell" className="nav-pill">List your property <ArrowRight size={15} /></Link></div>
        <button type="button" className="mobile-menu-button" aria-expanded={menuOpen} aria-controls="homepage-navigation" aria-label={menuOpen ? "Close navigation" : "Open navigation"} onClick={() => setMenuOpen((open) => !open)}>{menuOpen ? <X size={20} /> : <Menu size={20} />}</button>
      </nav>
      <div className="hero-inner section-shell">
        <div className="hero-copy">
          <p className="eyebrow hero-eyebrow"><span className="eyebrow-line" /> Bangalore / Property journal</p>
          <h1 className="hero-title">Find somewhere<br /><em>worth coming</em><br />home to.</h1>
          <p className="hero-subtitle">A more considered way to discover homes, plots and spaces across Bengaluru.</p>
          <div className="hero-actions"><Link href="/properties" className="button button-dark">Explore properties <ArrowRight size={17} /></Link><Link href="/sell" className="button button-outline hero-seller-button">Sell your property <ArrowRight size={17} /></Link></div>
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

export function BuyerSellerSection() {
  return <section className="buyer-seller-section section-shell" aria-label="Choose your journey"><article className="journey-panel journey-buyers" style={{ backgroundImage: `linear-gradient(90deg, rgba(22, 27, 21, .84), rgba(22, 27, 21, .18)), url(${properties[1].image})` }}><p className="eyebrow">For buyers</p><h2>Find a place worth<br /><em>coming home to.</em></h2><p>Discover apartments, houses, villas and plots across Bengaluru.</p><Link href="/properties" className="button button-light">Explore properties <ArrowRight size={17} /></Link></article><article className="journey-panel journey-sellers" style={{ backgroundImage: `linear-gradient(90deg, rgba(44, 38, 30, .87), rgba(44, 38, 30, .17)), url(${properties[4].image})` }}><p className="eyebrow">For sellers</p><h2>Have a property<br /><em>to sell?</em></h2><p>Let us present your property beautifully and connect it with interested buyers.</p><Link href="/sell" className="button button-light">List your property <ArrowRight size={17} /></Link></article></section>;
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
  const steps = [{ number: "01", title: "Discover", copy: "Explore carefully presented properties across Bengaluru.", icon: <Sparkles size={19} /> }, { number: "02", title: "See the story", copy: "View photos, details and property information.", icon: <Eye size={18} /> }, { number: "03", title: "Get details", copy: "Send a free enquiry for the property you're interested in.", icon: <Send size={18} /> }, { number: "04", title: "Connect", copy: "The property contact can follow up with you.", icon: <Check size={18} /> }];
  return <section className="difference-section" id="how-it-works"><div className="section-shell"><div className="difference-top"><div><p className="eyebrow">How it works</p><h2 className="display-title display-title-small">A simpler way<br /><em>to begin.</em></h2></div><p className="section-aside">Discover a property, understand the story, and enquire when something feels right.</p></div><div className="difference-grid">{steps.map((step, index) => <motion.div key={step.number} className={`difference-step difference-step-${index + 1}`} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, amount: 0.4 }} transition={{ delay: index * 0.08 }}><span>{step.number}</span><div className="difference-icon">{step.icon}</div><h3>{step.title}</h3><p>{step.copy}</p></motion.div>)}</div><div className="seller-flow"><p className="eyebrow">For sellers</p><strong>Submit</strong><ArrowRight size={15} /><strong>Review</strong><ArrowRight size={15} /><strong>Publish</strong><ArrowRight size={15} /><strong>Reach buyers</strong></div></div></section>;
}

export function WhySection() {
  const differences = [{ title: "Visual first", copy: "Beautiful property presentation instead of endless text-heavy listings." }, { title: "Bangalore focused", copy: "Built around properties across Bengaluru." }, { title: "Free buyer enquiries", copy: "Interested buyers can enquire without creating a paid account." }, { title: "Seller-first marketing", copy: "We give each property a proper presentation rather than treating it as just another database entry." }];
  return <section className="why-section section-shell"><div className="why-heading"><p className="eyebrow">Why this platform</p><h2 className="display-title display-title-small">A more considered way<br /><em>to discover property.</em></h2></div><div className="why-grid">{differences.map((item, index) => <article key={item.title}><span>0{index + 1}</span><h3>{item.title}</h3><p>{item.copy}</p></article>)}</div></section>;
}

export function ClosingSection() {
  return <><section className="closing-section"><div className="section-shell closing-grid"><div><p className="eyebrow">For property owners</p><h2 className="display-title">Have a property<br /><em>in Bengaluru?</em></h2><p className="closing-copy">Give it more than a listing. Give it a story worth discovering.</p></div><div className="closing-actions"><Link href="/sell" className="button button-light">List your property <ArrowRight size={17} /></Link><span>No complicated process. Submit your property and we&apos;ll review it before it goes live.</span></div></div></section><section className="contact-section section-shell" id="contact"><div><p className="eyebrow">Reach us</p><h2 className="display-title display-title-small">Let&apos;s talk<br /><em>property.</em></h2></div><div className="contact-copy"><p>Have a question about a property, want to list your property, or simply want to know more about Bengaluru Property? Reach us.</p><dl><div><dt>Email</dt><dd>hello@YOURDOMAIN.com <small>development placeholder</small></dd></div><div><dt>Phone</dt><dd>[BUSINESS PHONE] <small>development placeholder</small></dd></div><div><dt>Location</dt><dd>Bengaluru, Karnataka</dd></div></dl><div className="contact-actions"><Link href="/sell" className="text-link">List your property <ArrowRight size={16} /></Link><Link href="/properties" className="text-link">Explore properties <ArrowRight size={16} /></Link></div></div></section><footer className="site-footer"><div className="section-shell footer-grid"><div className="footer-brand"><span className="temporary-mark"><span className="mark-dot" />BENGALURU PROPERTY</span><p>A more considered way to discover property across Bengaluru.</p></div><div><h3>Discover</h3><Link href="/properties">Properties</Link><Link href="/properties">Apartments</Link><Link href="/properties">Villas</Link><Link href="/properties">Houses</Link><Link href="/properties">Plots</Link><Link href="/properties">Explore Bengaluru</Link></div><div><h3>Sell</h3><Link href="/sell">Sell your property</Link><a href="#how-it-works">How it works</a><Link href="/login">Seller login</Link><Link href="/sell">Submit a property</Link></div><div><h3>Company</h3><a href="#story">About us</a><a href="#story">Our approach</a><a href="#contact">Contact</a><a href="#how-it-works">FAQ</a></div><div><h3>Reach us</h3><span>hello@YOURDOMAIN.com</span><span>[BUSINESS PHONE]</span><span>Bengaluru, Karnataka</span></div></div><div className="section-shell footer-bottom"><span>© 2026 Bengaluru Property. All rights reserved.</span><span><a href="#">Privacy</a><a href="#">Terms</a><a href="#">Seller terms</a></span></div></footer></>;
}
