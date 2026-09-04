import type { DigitalProduct, DigitalProductCategory } from "@/types/digital-products";

export const DIGITAL_PRODUCT_CATEGORIES: DigitalProductCategory[] = [
  { slug: "business", name: "Business", description: "Templates and systems for clearer business decisions." },
  { slug: "freelancer-agency", name: "Freelancer & Agency", description: "Practical resources for client work and delivery." },
  { slug: "creator-marketing", name: "Creator & Marketing", description: "Planning tools for consistent content and campaigns." },
  { slug: "career", name: "Career", description: "Resources for a more focused job search and career story." },
  { slug: "finance-productivity", name: "Finance & Productivity", description: "Simple systems for planning, tracking and follow-through." },
];

export const DIGITAL_PRODUCTS: DigitalProduct[] = [
  {
    id: "dpt-small-business-finance-pricing-toolkit",
    name: "Small Business Finance & Pricing Kit",
    slug: "small-business-finance-pricing-toolkit",
    description: "A complete workbook, finance manual, editable templates and checklists for clearer pricing and monthly decisions.",
    valueProposition: "Move from one-off calculations to a repeatable monthly finance routine.",
    category: DIGITAL_PRODUCT_CATEGORIES[0],
    format: "Excel workbook, PDF manual, editable DOCX templates and practical resources",
    price: 199,
    currency: "INR",
    previewLabel: "Workbook preview",
    included: [
      "Start-here instructions and setup checklist",
      "Pricing decision worksheet with cost, margin and price scenarios",
      "Monthly expense tracker with category totals",
      "Break-even planning section for fixed and variable costs",
      "Monthly finance dashboard for revenue, costs and operating profit",
    ],
    audience: ["Small business owners", "Solo operators and freelancers", "People validating a new offer"],
    usage: [
      "Duplicate the workbook for each month or keep one rolling file.",
      "Enter your own figures in the highlighted input cells.",
      "Use the dashboard to review pricing and costs before making the next decision.",
    ],
    status: "published",
    delivery: "protected-download",
    assetVersion: "1.0",
    faq: [
      { question: "Can I edit the workbook?", answer: "Yes. It is an editable Excel workbook rather than a read-only PDF." },
      { question: "Is this accounting software?", answer: "No. It is a planning and decision-support workbook, not a replacement for bookkeeping or tax advice." },
      { question: "What currency does it use?", answer: "The templates are labelled for INR, but the spreadsheet structure can be adapted to another currency." },
    ],
  },
    {
      id: "dpt-freelancer-rate-project-pricing-toolkit",
      name: "Freelancer Rate & Project Pricing Kit",
      slug: "freelancer-rate-project-pricing-toolkit",
      description: "A complete pricing workbook, practical guide, editable client resources and communication scripts for confident freelance quotes.",
      valueProposition: "Set a sustainable rate, price projects with a buffer and review your freelance pipeline every month.",
      category: DIGITAL_PRODUCT_CATEGORIES[1],
      format: "Excel workbook, PDF guide, editable DOCX templates and practical resources",
      price: 99,
      currency: "INR",
      previewLabel: "Rate planner preview",
      included: ["Start-here setup instructions", "Monthly rate planner for income, expenses and billable hours", "Project quote worksheet with revision and admin buffer", "Monthly review section for booked work and rate decisions"],
      audience: ["Freelancers and consultants", "Small creative or technical agencies", "People moving from hourly work to project pricing"],
      usage: ["Enter your monthly target, costs and realistic billable hours.", "Use the suggested hourly rate as a floor for new conversations.", "Estimate project quotes with a visible buffer for uncertainty and revisions."],
      status: "published",
      delivery: "protected-download",
      assetVersion: "1.0",
      faq: [
        { question: "Can I edit the spreadsheet?", answer: "Yes. It is an editable Excel workbook that you can extend in Excel or Google Sheets." },
        { question: "Does it set my market rate?", answer: "No. It helps you understand the minimum rate your own targets and working pattern require; market positioning still needs judgment." },
        { question: "Is this tax or financial advice?", answer: "No. It is a planning worksheet, not tax, accounting or investment advice." },
      ],
    },
  {
    id: "dpt-freelancer-agency-client-work-workbook",
    name: "Freelancer & Agency Client Operating Kit",
    slug: "freelancer-agency-client-work-workbook",
    description: "A complete client operating workbook, document pack, workflow guides and communication library for profitable delivery.",
    valueProposition: "Keep the client-work lifecycle visible from first conversation to paid, profitable delivery.",
    category: DIGITAL_PRODUCT_CATEGORIES[1],
    format: "Excel workbook, PDF guide, editable DOCX templates and practical resources",
    price: 299,
    currency: "INR",
    previewLabel: "Client-work flow preview",
    included: ["Start-here setup instructions and status key", "Client and project scope tracker", "Quote planner with revision buffer", "Delivery milestone log", "Invoice, outstanding payment and follow-up tracker", "Project profitability review and monthly operating check"],
    audience: ["Freelancers and consultants", "Small creative or technical agencies", "Service businesses managing several client projects"],
    usage: ["Replace the clearly marked DEMO rows with your own client and project records.", "Move each project through scope, quote, delivery, invoice and follow-up reviews.", "Use the quote and profitability formulas as decision support, then confirm the final scope and payment terms yourself."],
    status: "published",
    delivery: "protected-download",
    assetVersion: "1.0",
    faq: [
      { question: "What format is the workbook?", answer: "It is an editable Excel workbook that can be opened and extended in Excel or Google Sheets." },
      { question: "Does it send invoices or reminders?", answer: "No. It helps you track the workflow and prepare decisions; sending invoices and follow-ups still happens through your chosen tools." },
      { question: "Is it project-management or accounting software?", answer: "No. It is a lightweight planning workbook for client work, pricing, delivery and review, not a replacement for accounting or project-management software." },
    ],
  },
];

export function getPublishedDigitalProducts() {
  return DIGITAL_PRODUCTS.filter((product) => product.status === "published");
}

export function getDigitalProductBySlug(slug: string) {
  return DIGITAL_PRODUCTS.find((product) => product.slug === slug && product.status === "published");
}

export function formatDigitalProductPrice(product: Pick<DigitalProduct, "price" | "currency">) {
  return new Intl.NumberFormat("en-IN", { style: "currency", currency: product.currency, maximumFractionDigits: 0 }).format(product.price);
}