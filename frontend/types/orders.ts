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
  product_image_url?: string | null;
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
  payment_provider?: "CASHFREE" | "RAZORPAY" | "STRIPE" | null;
  tracking_number?: string | null;
  tracking_carrier?: string | null;
  shipped_at?: string | null;
  delivered_at?: string | null;
  cancelled_at?: string | null;
  cancellation_reason?: string | null;
  refund_status?: string | null;
  refund_amount?: number | null;
  refund_message?: string | null;
};

export type OrderList = {
  items: Order[];
  page: number;
  page_size: number;
  total: number;
  has_next: boolean;
};

export type CancellationStatus = {
  order_id: string;
  order_status: string;
  payment_status: string;
  fulfillment_status: string;
  cancellation_reason?: string | null;
  cancelled_at?: string | null;
  refund_status?: string | null;
  refund_amount?: number | null;
  refund_message?: string | null;
};

export type PaymentSession = {
  order_id: string;
  provider: "CASHFREE";
  provider_order_id: string;
  payment_session_id: string;
  amount: number;
  currency: string;
};

export type RazorpayOrder = {
  order_id: string;
  provider: "RAZORPAY";
  key_id: string;
  razorpay_order_id: string;
  amount: number;
  currency: "INR";
};

export type PaymentStatus = {
  order_id: string;
  payment_status: string;
  order_status: string;
  fulfillment_status: string;
  provider_reference?: string | null;
};
