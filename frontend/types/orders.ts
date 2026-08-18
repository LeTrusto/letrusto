export type CustomerDetails = {
  name: string;
  email: string;
  phone: string;
};

export type ShippingAddress = {
  address: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
};

export type CreateOrderPayload = {
  items: Array<{ product_id: string; variant_id: string; quantity: number }>;
  customer: CustomerDetails;
  shipping_address: ShippingAddress;
  idempotency_key: string;
};

export type OrderItem = {
  id: string;
  product_name: string;
  variant_name: string;
  quantity: number;
  unit_price: number;
  line_total: number;
};

export type Order = {
  id: string;
  order_number: string;
  status: string;
  payment_status: string;
  fulfillment_status: string;
  subtotal: number;
  shipping_amount: number;
  total: number;
  currency: string;
  customer_name: string;
  customer_email: string;
  customer_phone: string;
  shipping_address: ShippingAddress;
  items: OrderItem[];
  created_at: string;
};
