"""
Seed 10 production-quality launch articles into the articles table.
Run: python -m scripts.seed_articles
"""
from __future__ import annotations

import sys

sys.path.insert(0, ".")

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.entities import Article

ARTICLES = [
    {
        "slug": "best-web-hosting-india-2026",
        "title": "Best Web Hosting in India 2026 — Tested & Ranked",
        "excerpt": "We tested 8 hosting providers on speed, uptime, support and value. Here is our definitive ranking for Indian websites in 2026.",
        "content": """Choosing the right web hosting is one of the most important decisions for any Indian website owner. A slow host can kill your SEO rankings and frustrate visitors. We tested 8 major hosting providers over 30 days specifically from Indian data centres and server locations.

Our top pick for most users: Hostinger Business Plan.

Hostinger offers Indian data centres, LiteSpeed servers, and free SSL for just ₹179/month on the annual plan. In our tests, it loaded pages in under 800ms from Mumbai — faster than any competitor in this price range.

Second place: Bluehost. If you run a WordPress site and want the peace of mind of WordPress's official recommended host, Bluehost is a solid choice. Their Basic plan starts at ₹199/month and includes a free domain for the first year.

Third place: Namecheap Stellar. At just ₹83/month, Namecheap offers the best value for beginners who just need a simple site. Free WHOIS privacy is included — something Hostinger and Bluehost charge extra for.

What to look for when choosing hosting:
- Server location (prefer India or Singapore for Indian audience)
- Uptime guarantee (99.9% minimum)
- Free SSL certificate
- 1-click WordPress installer
- Support quality
- Renewal pricing (not just first-year price)

Our recommendation: Start with Hostinger Business Plan for ₹179/month. It covers 100 websites, includes free CDN, and the performance is excellent. You can always upgrade to cloud hosting when your traffic grows.""",
        "category": "guide",
        "meta_title": "Best Web Hosting in India 2026 — Compared & Ranked | LeTrusto",
        "meta_description": "We tested 8 web hosting providers for Indian websites. Find the fastest, most affordable hosting for your site in 2026.",
        "is_published": True,
    },
    {
        "slug": "hostinger-vs-bluehost-india",
        "title": "Hostinger vs Bluehost India 2026 — Which is Better?",
        "excerpt": "Both are popular hosting choices, but they serve different needs. We compare speed, price, support and features to help you choose.",
        "content": """Hostinger and Bluehost are two of the most recommended web hosts in India. But they serve very different users. Here is a detailed comparison.

Price Comparison:
Hostinger Starter: ₹69/month (annual)
Bluehost Basic: ₹199/month (annual)
Winner: Hostinger by a wide margin

Performance (India):
Hostinger (LiteSpeed): Average load time 780ms from Mumbai
Bluehost (Apache): Average load time 1,200ms from Mumbai
Winner: Hostinger

WordPress:
Bluehost is officially recommended by WordPress.org
Hostinger has an excellent 1-click installer too
Winner: Bluehost (for brand trust), Hostinger (for performance)

Support:
Both offer 24/7 live chat
Bluehost has phone support (Hostinger does not)
Winner: Bluehost

Renewal Price:
Hostinger renews at 2x the promotional price
Bluehost renews at 3x the promotional price
Winner: Hostinger

Our Verdict: For most Indian users, Hostinger is the better choice. It is faster, cheaper, and offers better value. Choose Bluehost only if you specifically want WordPress's official host or if you need phone support.""",
        "category": "comparison",
        "meta_title": "Hostinger vs Bluehost India 2026 — Full Comparison | LeTrusto",
        "meta_description": "Hostinger vs Bluehost for Indian websites. We compare price, speed, WordPress support and features to find the winner.",
        "is_published": True,
    },
    {
        "slug": "best-phone-under-20000-india-2026",
        "title": "Best Phone Under ₹20,000 in India 2026",
        "excerpt": "The best budget smartphones in India that deliver excellent cameras, long battery life and smooth performance for under ₹20,000.",
        "content": """The budget smartphone market in India is incredibly competitive. In 2026, ₹20,000 buys you a phone that would have been considered flagship just two years ago.

Our Top Pick: Nothing Phone (2a) at ₹19,999

The Nothing Phone (2a) is our best pick under ₹20,000. The Dimensity 7200 Pro chip handles everyday tasks and gaming with ease. The dual 50MP cameras produce excellent daylight photos. And the iconic Glyph lighting on the back makes it stand out.

Why we love it:
- Clean Nothing OS with no bloatware
- Bright AMOLED display
- 45W fast charging
- Unique design that gets attention

Runner Up: Redmi Note 14 at ₹16,999

The Redmi Note 14 offers a 108MP camera and a massive 5500mAh battery for just ₹16,999. If camera resolution and battery life are your priorities, this is the one.

Budget Pick: Motorola Moto G85 at ₹17,999

The Moto G85 gives you an AMOLED display at a price where many competitors still use LCD. Near-stock Android experience with quick updates.

What to prioritise under ₹20,000:
1. Processor (Dimensity 7200+, Snapdragon 7s Gen 2 or better)
2. Display (AMOLED preferred over IPS)
3. Battery (5000mAh minimum)
4. Camera (50MP main sensor minimum)
5. RAM (8GB minimum for smooth multitasking)

Avoid phones with MediaTek Helio G-series chips in this price range — they are noticeably slower than the Dimensity alternatives.""",
        "category": "guide",
        "meta_title": "Best Phone Under ₹20,000 India 2026 — Top Picks | LeTrusto",
        "meta_description": "Find the best smartphone under ₹20,000 in India. AI-ranked by camera, battery and performance for 2026.",
        "is_published": True,
    },
    {
        "slug": "best-laptop-for-students-india-2026",
        "title": "Best Laptop for Students in India 2026 — Under ₹50,000",
        "excerpt": "The best laptops for college students in India — balancing performance, battery life and portability within a student budget.",
        "content": """As a student in India, your laptop is your most important tool. You need it for coding, assignments, video calls, research and occasional Netflix. But you also need it to last all day and not weigh a tonne.

Best Overall: Lenovo IdeaPad Slim 5 (AMD Ryzen 5 7530U) — ₹44,990

The IdeaPad Slim 5 hits the perfect balance. The Ryzen 5 7530U processor handles everything a student needs — coding in Python, running VS Code, spreadsheets, and video editing for projects. The 12-hour battery life means you can attend all your lectures without hunting for a power socket.

Best for Engineering: ASUS VivoBook 15 — ₹42,990

The VivoBook 15 with its Core i5 processor is excellent for engineering students who run heavy simulations. The dedicated NVIDIA graphics card helps with CAD software and some ML workloads.

Best Budget: Acer Aspire 5 — ₹34,990

For students who primarily use their laptop for notes, PDFs and Google Meet, the Acer Aspire 5 offers solid performance at a lower price.

What matters most for student laptops:
- Battery life (8+ hours minimum)
- Weight (under 1.8kg for daily carry)
- Keyboard quality (you will type a lot)
- RAM (16GB for future-proofing)
- Storage (512GB SSD minimum)
- Webcam quality (for online exams)

Tip: Always check if your college software runs on Windows before buying a MacBook.""",
        "category": "guide",
        "meta_title": "Best Laptop for Students India 2026 — Under ₹50,000 | LeTrusto",
        "meta_description": "The best student laptops in India under ₹50,000. AI-ranked by performance, battery life and value for college students.",
        "is_published": True,
    },
    {
        "slug": "canva-pro-vs-free-2026",
        "title": "Canva Pro vs Free — Is It Worth ₹3,999/Year?",
        "excerpt": "Canva Pro costs ₹3,999 per year. We break down exactly what you get and whether it is worth the upgrade for Indian creators.",
        "content": """Canva Free is already excellent. So why pay ₹3,999 per year for Canva Pro? Here is exactly what changes and who should upgrade.

What you get with Canva Pro:

1. Background Remover — Remove backgrounds from any image in one click. This alone saves hours of work in Photoshop. Essential for product photos, thumbnails, and social media.

2. Magic Resize — Resize any design to any platform in seconds. Create a post for Instagram, then resize for Twitter, YouTube thumbnail, and LinkedIn banner in one click.

3. Brand Kit — Store your brand colours, fonts, and logos. Every team member uses consistent branding automatically.

4. 100+ Million Stock Photos — The free plan has limited assets. Pro unlocks millions of premium photos, videos, and audio.

5. Unlimited Storage — The free plan gives you 5GB. Pro gives you 1TB.

6. Schedule Social Media Posts — Plan and schedule directly from Canva.

Who should upgrade to Pro:
- Social media managers posting daily content
- Small businesses with multiple team members
- Freelancers creating content for multiple clients
- YouTubers creating thumbnails at scale

Who should stick with Free:
- Occasional users (1-2 designs per month)
- Students on tight budgets
- Personal use only

Our verdict: If you create more than 10 designs per month professionally, Canva Pro pays for itself in time saved. At ₹3,999/year (₹333/month), it is one of the best value SaaS tools available.""",
        "category": "comparison",
        "meta_title": "Canva Pro vs Free 2026 — Is It Worth ₹3,999/Year? | LeTrusto",
        "meta_description": "Is Canva Pro worth the price? We compare every feature and tell you exactly when to upgrade to Canva Pro.",
        "is_published": True,
    },
    {
        "slug": "semrush-vs-ahrefs-india-2026",
        "title": "Semrush vs Ahrefs 2026 — Which SEO Tool is Better?",
        "excerpt": "Both are the industry standard for SEO. We compare features, pricing, accuracy and which is better for Indian websites.",
        "content": """If you are serious about SEO, you will eventually need to choose between Semrush and Ahrefs. Both are industry standards, but they have different strengths.

Keyword Research:
Semrush has a larger keyword database and better keyword gap analysis.
Ahrefs has better search volume accuracy for long-tail keywords.
Winner: Tie — depends on your use case.

Backlink Analysis:
Ahrefs has the largest backlink index in the industry, updated every 24 hours.
Semrush has a good backlink tool but Ahrefs is considered more accurate.
Winner: Ahrefs

Site Audit:
Semrush's site audit tool is more comprehensive and easier to understand for beginners.
Ahrefs has improved but Semrush still leads here.
Winner: Semrush

Competitor Analysis:
Semrush's competitor analysis features are more extensive, including ad analysis.
Ahrefs focuses more on organic search data.
Winner: Semrush

Pricing (India):
Semrush Pro: $119.95/month (₹9,900+)
Ahrefs Lite: $129/month (₹10,700+)
Winner: Semrush (slightly cheaper with more features)

Our Verdict for Indian SEO professionals:
Start with Semrush. The keyword research, site audit and competitor tools are all excellent for beginners and intermediate SEO professionals. The 7-day free trial through our affiliate link lets you test before committing.

Ahrefs is better for agencies heavily focused on backlink building and link outreach.""",
        "category": "comparison",
        "meta_title": "Semrush vs Ahrefs 2026 — Which SEO Tool is Better? | LeTrusto",
        "meta_description": "Semrush vs Ahrefs: which SEO tool is better for Indian websites in 2026? We compare features, pricing and accuracy.",
        "is_published": True,
    },
    {
        "slug": "best-vpn-for-india-2026",
        "title": "Best VPN for India 2026 — Privacy, Speed & Streaming",
        "excerpt": "The best VPNs for Indian users in 2026 — tested for speed on Indian ISPs, privacy policy and streaming unblocking.",
        "content": """Using a VPN in India is important for privacy, accessing geo-restricted content, and securing public Wi-Fi connections. Here are the best VPNs for Indian users in 2026.

Best Overall: NordVPN

NordVPN tops our list for Indian users. With 6000+ servers including servers in Singapore and Hong Kong (close to India for fast speeds), a verified no-log policy, and the ability to unblock Netflix, Disney+ Hotstar international content, and BBC iPlayer, NordVPN is the most well-rounded option.

Key features:
- Double VPN for extra security
- NordLynx protocol (ultra-fast)
- 6 simultaneous devices
- Kill switch (essential for privacy)
- 30-day money-back guarantee

Price: ₹254/month (2-year plan)

Who needs a VPN in India:
- Remote workers on public Wi-Fi
- Users wanting to access international streaming content
- Privacy-conscious individuals
- Journalists and activists
- Frequent international travellers

What to look for:
1. No-logs policy (independently audited)
2. Server count and locations
3. Speed (especially from Indian ISPs)
4. Streaming unblocking capability
5. Price per month on annual plan

Warning: Always check Indian regulations before using a VPN for any purpose. VPNs are legal in India for personal use.""",
        "category": "guide",
        "meta_title": "Best VPN for India 2026 — Privacy & Speed Tested | LeTrusto",
        "meta_description": "The best VPNs for Indian users in 2026. Tested on Indian ISPs for speed, privacy policy, and streaming performance.",
        "is_published": True,
    },
    {
        "slug": "iphone-16-pro-vs-samsung-s25-ultra",
        "title": "iPhone 16 Pro vs Samsung Galaxy S25 Ultra — Which Should You Buy?",
        "excerpt": "Two flagship smartphones. Different strengths. We break down exactly who should buy which one based on real usage.",
        "content": """The iPhone 16 Pro and Samsung Galaxy S25 Ultra are the two best smartphones money can buy in India in 2026. But they are made for very different people.

Quick Summary:
iPhone 16 Pro: ₹1,19,900 (128GB) — Best for iOS ecosystem, videography, compact flagship
Samsung S25 Ultra: ₹1,29,999 (256GB) — Best for S Pen productivity, Android power users, zoom photography

Camera System:
iPhone 16 Pro: 48MP main + 48MP ultrawide + 12MP 5x telephoto — Excellent video, best-in-class colour science
Galaxy S25 Ultra: 200MP main + 50MP ultrawide + 10MP 3x + 50MP 5x — Most versatile zoom range of any smartphone

Who wins: Draw — iPhone wins on video, Samsung wins on zoom versatility.

Performance:
iPhone 16 Pro: Apple A18 Pro — fastest chip in any phone, period
Galaxy S25 Ultra: Snapdragon 8 Elite — fastest Android chip

Who wins: iPhone 16 Pro (single-core), Galaxy S25 Ultra (sustained load)

Software:
iPhone: iOS 18 with Apple Intelligence
Samsung: Android 15 with Galaxy AI and 7 years of updates

Who wins: Depends on ecosystem preference

Choose iPhone 16 Pro if you:
- Already use a Mac, iPad, or Apple Watch
- Prioritise video quality above all else
- Want the most compact premium phone
- Value consistent 6+ years of software support

Choose Galaxy S25 Ultra if you:
- Use S Pen regularly for notes or illustration
- Need extreme zoom photography
- Prefer Android's customisation freedom
- Want a large screen productivity device""",
        "category": "comparison",
        "meta_title": "iPhone 16 Pro vs Samsung Galaxy S25 Ultra — Full Comparison | LeTrusto",
        "meta_description": "iPhone 16 Pro vs Samsung Galaxy S25 Ultra: camera, performance, AI features compared. Which flagship to buy in India?",
        "is_published": True,
    },
    {
        "slug": "best-ai-tools-developers-india-2026",
        "title": "Best AI Tools for Developers in India 2026",
        "excerpt": "The AI tools that actually make developers more productive — from code completion to API testing to documentation.",
        "content": """AI has fundamentally changed software development. Here are the tools Indian developers are actually using and paying for in 2026.

1. GitHub Copilot — Code Completion
The most used AI coding tool. Copilot suggests entire functions, writes boilerplate, and learns your coding style. At $10/month for individuals, it pays for itself in the first hour of use if you are writing significant amounts of code.

2. Cursor — AI Code Editor
Cursor is a VS Code fork with deep AI integration. You can chat with your codebase, ask it to fix bugs across multiple files, and get explanations for unfamiliar code. Many developers have switched from VS Code entirely.

3. Grammarly — Documentation Writing
Technical documentation is just as important as code. Grammarly Premium ensures your README files, API docs, and blog posts are clear and professional.

4. Notion AI — Project Management
Notion with AI add-on is excellent for sprint planning, documenting architecture decisions, and creating runbooks. The AI can summarise long meeting notes and generate action items.

5. Semrush — Technical SEO (for developer-bloggers)
If you run a technical blog alongside your development work, Semrush is essential for keyword research and understanding what developers are searching for.

The Bottom Line:
For pure coding productivity, GitHub Copilot or Cursor are the non-negotiable tools. Start there before investing in anything else.""",
        "category": "guide",
        "meta_title": "Best AI Tools for Developers India 2026 | LeTrusto",
        "meta_description": "The AI tools Indian developers are using in 2026 to code faster, write better documentation, and ship more features.",
        "is_published": True,
    },
    {
        "slug": "how-ai-helps-choose-right-product",
        "title": "How AI Helps You Choose the Right Product — LeTrusto Explained",
        "excerpt": "Most product comparison sites show you specs. LeTrusto's AI understands your actual needs and recommends the best fit.",
        "content": """Most product comparison websites give you a table of specifications and leave you to figure out what it all means. LeTrusto does something different: it uses AI to understand your specific needs and recommends the best product for you.

How LeTrusto AI Works:

Step 1: Tell the AI your requirements
Instead of filtering by 1000mAh battery and 50MP camera, you just describe what you want: "I need a phone for mobile photography under ₹40,000 with all-day battery."

Step 2: AI analyses the entire catalog
Our AI scores every product in our database against your specific requirements — not just the raw specs, but how those specs translate to real-world use.

Step 3: Personalised recommendation with explanation
You get a ranked list with a clear explanation: why this product fits your needs, who else it is suited for, and what the trade-offs are.

Why This Matters:
Imagine you are buying a laptop for programming. A standard comparison site will show you CPU benchmarks. But what actually matters is: Does it run VS Code smoothly? How long does the battery last during a coding session? Does it overheat? LeTrusto's AI understands these real-world concerns.

Our AI is trained on real product usage scenarios across:
- Mobile photography
- Mobile gaming
- Business productivity
- Student use
- Fitness tracking
- Web hosting needs
- SaaS tool selection

Try it now: Click "AI Advisor" in the navigation and describe what you are looking for. Our AI will recommend the best product from our database of 400+ tested products.""",
        "category": "guide",
        "meta_title": "How AI Helps You Choose the Right Product — LeTrusto | LeTrusto",
        "meta_description": "LeTrusto's AI advisor understands your real needs and recommends the best product — not just the one with the best specs.",
        "is_published": True,
    },
]


def run() -> None:
    db = SessionLocal()
    inserted = 0
    skipped = 0
    try:
        for data in ARTICLES:
            existing = db.scalars(select(Article).where(Article.slug == data["slug"])).first()
            if existing:
                skipped += 1
                continue
            article = Article(**data)
            db.add(article)
            inserted += 1
        db.commit()
        print(f"✓ Articles seeded. Inserted: {inserted} | Skipped: {skipped}", flush=True)
    except Exception as exc:
        db.rollback()
        print(f"ERROR: {exc}", flush=True)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run()
