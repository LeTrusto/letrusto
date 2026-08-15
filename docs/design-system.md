# LeTrusto — Design System

## Colour Tokens

Defined as CSS custom properties in `frontend/app/globals.css` and exposed via Tailwind `@theme`.

| Token | CSS Variable | Value |
|-------|-------------|-------|
| Primary | `--lt-primary` | `#18181b` |
| Accent | `--lt-accent` | `#d4a574` |
| Accent Dark | `--lt-accent-dark` | `#b8915e` |
| Rose | `--lt-rose` | `#e11d48` |
| Success | `--lt-success` | `#16a34a` |
| Background | `--background` | `#ffffff` |
| Surface | `--surface` | `#ffffff` |
| Surface Soft | `--surface-soft` | `#fafaf9` |
| Surface Muted | `--surface-muted` | `#f5f5f4` |
| Text Primary | `--text-primary` | `#18181b` |
| Text Secondary | `--text-secondary` | `#52525b` |
| Text Muted | `--text-muted` | `#a1a1aa` |
| Border | `--border` | `#e4e4e7` |
| Border Hover | `--border-hover` | `#d4d4d8` |

## Typography

### Font Stack
- Primary: `Inter` (Google Fonts, variable)
- Mono: `Geist Mono` (existing, for prices/codes)

### Heading Scale

| Class | Mobile | Desktop | Weight | Tracking |
|-------|--------|---------|--------|----------|
| `.lt-heading-1` | 2.25rem / 36px | 3rem / 48px | 900 | -0.025em |
| `.lt-heading-2` | 1.5rem / 24px | 1.875rem / 30px | 800 | -0.02em |
| `.lt-heading-3` | 1.125rem / 18px | 1.25rem / 20px | 700 | normal |

### Body

| Class | Size | Line Height |
|-------|------|-------------|
| `.lt-body` | 0.9375rem / 15px | 1.7 |
| `.lt-body-sm` | 0.8125rem / 13px | 1.6 |
| `.lt-label` | 0.75rem / 12px | — | uppercase, 600 weight, 0.05em tracking |

## Spacing

Tailwind default scale. Key usage:
- Section padding: `py-12 md:py-16`
- Container: `max-w-7xl mx-auto px-4`
- Card padding: `p-4` (mobile) / `p-6` (desktop)
- Gap in grids: `gap-4` (mobile) / `gap-6` (desktop)

## Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| `--radius-sm` | 0.5rem | Small controls, badges |
| `--radius-md` | 0.75rem | Inputs, buttons |
| `--radius-lg` | 1rem | Cards, panels |
| `--radius-xl` | 1.25rem | Featured cards |
| `--radius-2xl` | 1.5rem | Hero elements |

## Shadows

| Token | Value | Usage |
|-------|-------|-------|
| `--shadow-sm` | `0 1px 2px rgba(24,24,27,0.05)` | Subtle elevation |
| `--shadow-md` | `0 4px 16px -4px rgba(24,24,27,0.1)` | Cards, dropdowns |
| `--shadow-lg` | `0 12px 40px -12px rgba(24,24,27,0.15)` | Modals, popovers |

## Buttons

| Variant | Background | Text | Border | Hover |
|---------|-----------|------|--------|-------|
| `.lt-btn-primary` | `--lt-primary` | white | primary | lighten |
| `.lt-btn-accent` | `--lt-accent` | `--lt-primary` | transparent | accent-dark bg |
| `.lt-btn-secondary` | white | primary | border | soft bg |
| `.lt-btn-ghost` | transparent | secondary | none | muted bg |

Sizes: `.lt-btn-sm`, `.lt-btn-md`, `.lt-btn-lg`

## Cards

| Class | Description |
|-------|------------|
| `.lt-card` | White bg, border, radius-lg, padding |
| `.lt-card-hover:hover` | Subtle shadow lift, border darken |

## Badges

| Variant | Usage |
|---------|-------|
| `.lt-badge` | Default (muted bg) |
| `.lt-badge-accent` | Accent bg, dark text — trending, new |
| `.lt-badge-sale` | Rose bg, white text — discounts |
| `.lt-badge-success` | Green bg, white text — in stock |

## Price Display

- Current price: `text-lg font-bold text-[var(--text-primary)]`
- Compare-at price: `line-through text-[var(--text-muted)]`
- Savings: `text-[var(--lt-rose)] font-semibold`
- Currency: ₹ (INR), no decimals for round amounts

## Forms

| Class | Description |
|-------|------------|
| `.lt-input` | Full-width, border, radius-md, focus ring in accent |
| `.lt-select` | Same as input with custom chevron |

## States

### Loading
- Shimmer skeletons (`.shimmer` class with animation)
- Rounded placeholder shapes matching content layout

### Empty
- Centered icon + heading + body + optional CTA

### Error
- Rose accent, icon, message, retry button

## Navigation

### Desktop
- Sticky top bar: Logo | Search | Shop | Offers | Wishlist | Cart | Account
- Height: 64px

### Mobile
- Top bar: Logo | Search | Cart (compact, 56px)
- Bottom tab bar: Home | Discover | Categories | Orders | Account (fixed, 64px)

## Responsive Breakpoints

Standard Tailwind: `sm` (640), `md` (768), `lg` (1024), `xl` (1280)

Mobile-first: all base styles target mobile, progressively enhanced.
