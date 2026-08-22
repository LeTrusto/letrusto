export type CustomerAccount = {
  email: string;
  full_name: string;
  phone: string | null;
  shipping_address: {
    address: string;
    city: string;
    state: string;
    postal_code: string;
    country: string;
  } | null;
  email_verified: boolean;
  created_at: string;
};