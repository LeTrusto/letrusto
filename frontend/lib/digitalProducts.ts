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
    name: "Small Business Finance & Pricing Toolkit",
    slug: "small-business-finance-pricing-toolkit",
    description: "A practical spreadsheet system for turning everyday costs into clearer pricing and monthly decisions.",
    valueProposition: "Move from one-off calculations to a repeatable monthly finance routine.",
    category: DIGITAL_PRODUCT_CATEGORIES[0],
    format: "Editable CSV spreadsheet (.csv), compatible with Excel and Google Sheets",
    price: 499,
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
      { question: "Can I edit the workbook?", answer: "Yes. It is designed as an editable spreadsheet rather than a read-only PDF." },
      { question: "Is this accounting software?", answer: "No. It is a planning and decision-support workbook, not a replacement for bookkeeping or tax advice." },
      { question: "What currency does it use?", answer: "The templates are labelled for INR, but the spreadsheet structure can be adapted to another currency." },
    ],
  },
    {
      id: "dpt-freelancer-rate-project-pricing-toolkit",
      name: "Freelancer Rate & Project Pricing Toolkit",
      slug: "freelancer-rate-project-pricing-toolkit",
      description: "An editable spreadsheet for turning income goals, operating costs and project hours into clearer freelance rates and quotes.",
      valueProposition: "Set a sustainable rate, price projects with a buffer and review your freelance pipeline every month.",
      category: DIGITAL_PRODUCT_CATEGORIES[1],
      format: "Editable CSV spreadsheet (.csv), compatible with Excel and Google Sheets",
      price: 399,
      currency: "INR",
      previewLabel: "Rate planner preview",
      included: ["Start-here setup instructions", "Monthly rate planner for income, expenses and billable hours", "Project quote worksheet with revision and admin buffer", "Monthly review section for booked work and rate decisions"],
      audience: ["Freelancers and consultants", "Small creative or technical agencies", "People moving from hourly work to project pricing"],
      usage: ["Enter your monthly target, costs and realistic billable hours.", "Use the suggested hourly rate as a floor for new conversations.", "Estimate project quotes with a visible buffer for uncertainty and revisions."],
      status: "published",
      delivery: "protected-download",
      assetVersion: "1.0",
      faq: [
        { question: "Can I edit the spreadsheet?", answer: "Yes. It is an editable CSV that you can extend in Excel or Google Sheets." },
        { question: "Does it set my market rate?", answer: "No. It helps you understand the minimum rate your own targets and working pattern require; market positioning still needs judgment." },
        { question: "Is this tax or financial advice?", answer: "No. It is a planning worksheet, not tax, accounting or investment advice." },
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