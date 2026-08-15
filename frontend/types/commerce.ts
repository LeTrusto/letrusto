export type CommerceCategory =
  | "jewellery"
  | "hair-style"
  | "beauty-tools"
  | "accessories"
  | "gifts";

export type CommerceProduct = {
  id: string;
  slug: string;
  name: string;
  description: string;
  price: number;
  compareAtPrice?: number;
  currency: "INR";
  images: string[];
  category: CommerceCategory;
  categoryLabel: string;
  variants?: ProductVariant[];
  availability: "in-stock" | "limited" | "out-of-stock";
  tags: string[];
  specs?: { label: string; value: string }[];
  isTrending?: boolean;
  isNewDrop?: boolean;
  isLetrustoPick?: boolean;
  bundleProducts?: string[];
  estimatedDelivery?: string;
  returnInfo?: string;
};

export type ProductVariant = {
  id: string;
  label: string;
  options: string[];
};

export type CartItem = {
  productId: string;
  quantity: number;
  selectedVariants?: Record<string, string>;
};

export type CartState = {
  items: CartItem[];
  addItem: (productId: string, quantity?: number) => void;
  removeItem: (productId: string) => void;
  updateQuantity: (productId: string, quantity: number) => void;
  clearCart: () => void;
  itemCount: number;
  subtotal: number;
  savings: number;
};

export const CATEGORY_MAP: Record<CommerceCategory, string> = {
  jewellery: "Jewellery",
  "hair-style": "Hair & Style",
  "beauty-tools": "Beauty Tools",
  accessories: "Accessories",
  gifts: "Gifts",
};
