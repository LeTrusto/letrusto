export type CatalogCategoryNode = {
  id?: number;
  name: string;
  slug: string;
  icon?: string;
  children?: CatalogCategoryNode[];
};

export type CatalogBrandEntry = {
  name: string;
  slug: string;
  series: string[];
};

export type CatalogSubcategoryBrands = {
  subcategorySlug: string;
  subcategoryName: string;
  brands: CatalogBrandEntry[];
};
