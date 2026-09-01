import { describe, expect, it } from "vitest";

import { addCartItem, cartItemsEqual, cartSubtotal, normalizeCartItems, updateCartItemQuantity, type CartCatalog } from "@/lib/cartRules";

const catalog: CartCatalog = {
  hoodie: {
    price: 4499,
    catalogVariants: [
      { id: "variant-1", label: "Black / M", price: 4499, available: true, inventory: 3 },
      { id: "variant-2", label: "Black / L", price: 4599, available: false, inventory: 0 },
    ],
  },
};

const podCatalog: CartCatalog = {
  hoodie: {
    price: 4499,
    madeToOrder: true,
    catalogVariants: ["S", "M", "L", "XL", "2XL"].map((size, index) => ({
      id: `variant-${index + 1}`,
      label: `Unisex Hoodie / ${size}`,
      price: 4499,
      available: true,
      inventory: 0,
    })),
  },
};

describe("cart rules", () => {
  it("clamps persisted quantities to live inventory", () => {
    expect(normalizeCartItems([{ productId: "hoodie", selectedVariantId: "variant-1", quantity: 9 }], catalog)).toEqual([
      { productId: "hoodie", selectedVariantId: "variant-1", quantity: 3 },
    ]);
  });

  it("drops unknown products and unavailable variants", () => {
    expect(normalizeCartItems([
      { productId: "missing", selectedVariantId: "variant-1", quantity: 1 },
      { productId: "hoodie", selectedVariantId: "variant-2", quantity: 1 },
    ], catalog)).toEqual([]);
  });

  it("prevents duplicate rapid adds from exceeding inventory", () => {
    const one = addCartItem([], catalog, "hoodie", 2, "variant-1");
    const two = addCartItem(one, catalog, "hoodie", 2, "variant-1");
    expect(two).toEqual([{ productId: "hoodie", selectedVariantId: "variant-1", quantity: 3 }]);
  });

  it("does not update quantities below one", () => {
    const items = [{ productId: "hoodie", selectedVariantId: "variant-1", quantity: 2 }];
    expect(updateCartItemQuantity(items, catalog, "hoodie", 0, "variant-1")).toEqual(items);
  });

  it("detects equivalent cart state after hydration normalization", () => {
    const items = [{ productId: "hoodie", selectedVariantId: "variant-1", quantity: 2 }];
    expect(cartItemsEqual(items, normalizeCartItems(items, catalog))).toBe(true);
  });

  it("uses live variant prices for subtotal display", () => {
    const items = [{ productId: "hoodie", selectedVariantId: "variant-1", quantity: 2 }];
    expect(cartSubtotal(items, catalog)).toBe(8998);
  });

  it("allows every mapped made-to-order variant with null inventory", () => {
    for (const variant of podCatalog.hoodie.catalogVariants ?? []) {
      expect(addCartItem([], podCatalog, "hoodie", 1, variant.id)).toEqual([
        { productId: "hoodie", selectedVariantId: variant.id, quantity: 1 },
      ]);
    }
  });
});
