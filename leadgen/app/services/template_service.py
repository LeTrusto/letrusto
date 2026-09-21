from urllib.parse import quote

TEMPLATES = {
    "founder": {
        "subject": "Quick idea for {company}",
        "body": "Hi {name},\n\nI came across {company} and noticed {observation}.\n\nI'm building LeTrusto - a simple tool that helps businesses turn their existing customer reviews and testimonials into a widget that displays live on their website, building instant trust for new visitors.\n\nFor {company}, that could mean {why_fit}.\n\nWe're currently working with a small number of early customers and I'd be happy to set you up with a free trial - no card required.\n\nWould a quick look be useful?\n\n{link}\n\nBest,\nFounder, LeTrusto\n\nIf you don't want to receive messages from me like this, just let me know and I won't contact you again.",
    },
    "opportunity": {
        "subject": "A customer-proof idea for {company}",
        "body": "Hi {name},\n\nI noticed {observation}. That's exactly the kind of trust signal that converts best when it's visible the moment a new visitor lands on your site, not buried on a separate page.\n\nLeTrusto turns your existing reviews and testimonials into a lightweight widget you can drop onto any page in minutes. For {company}, that could mean {why_fit}.\n\nWould a short look be useful?\n\n{link}\n\nBest,\nFounder, LeTrusto\n\nIf you don't want to receive messages from me like this, just let me know and I won't contact you again.",
    },
    "expo": {
        "subject": "Following up on {company}",
        "body": "Hi {name},\n\nI found {company} through {source}. Based on what I saw - {observation} - LeTrusto may be a quick win for making that customer proof visible where it counts: your homepage and product pages.\n\nWould you be open to a free trial and sharing feedback?\n\n{link}\n\nBest,\nFounder, LeTrusto\n\nIf you don't want to receive messages from me like this, just let me know and I won't contact you again.",
    },
}


def render_email(lead: dict, founder: str, template: str = "founder", followup: int = 0) -> tuple[str, str]:
    name = lead.get("contact_name") or "there"
    observation = lead.get("review_signal") or lead.get("social_proof_signal") or "customer feedback is not yet verified"
    why_fit = lead.get("why_fit") or "an easy way to turn that trust into more signups and sales"
    campaign_tag = quote(str(lead.get("niche") or "general").strip() or "general")
    lead_tag = quote(str(lead.get("id") or ""))
    link = f"https://letrusto.com/register?utm_source=leadgen&utm_medium=email&utm_campaign={campaign_tag}&utm_content={lead_tag}"
    values = {**lead, "name": name, "company": lead.get("company_name", ""), "founder": founder, "observation": observation, "why_fit": why_fit, "niche": lead.get("niche") or "your industry", "link": link}
    if followup == 1:
        return f"Re: Quick idea for {lead.get('company_name', '')}", f"Hi {name},\n\nJust following up on my note below.\n\nI thought LeTrusto could be useful for {lead.get('company_name', '')} because {why_fit}.\n\nHappy to show you how it works if you're interested.\n\n{link}\n\nBest,\nFounder, LeTrusto"
    if followup == 2:
        return f"Re: Quick idea for {lead.get('company_name', '')}", f"Hi {name},\n\nI'll close the loop here.\n\nIf customer reviews or social proof is something you're working on, I'd be happy to show you LeTrusto.\n\n{link}\n\nEither way, thanks for your time.\n\nBest,\nFounder, LeTrusto"
    selected = TEMPLATES.get(template, TEMPLATES["founder"])
    return selected["subject"].format(**values), selected["body"].format(**values)


def gmail_compose_url(email: str, subject: str, body: str) -> str:
    return "https://mail.google.com/mail/?view=cm&fs=1&to=" + quote(email or "") + "&su=" + quote(subject) + "&body=" + quote(body)
