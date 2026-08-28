export type UserRole = "user" | "admin";

export type AuthUser = {
  id: string;
  email: string | null;
  full_name: string;
  role: UserRole;
  avatar_url: string | null;
};

export type AuthState = {
  user: AuthUser | null;
  accessToken: string | null;
  refreshToken: string | null;
  isLoading: boolean;
};

export type AuthResponse = {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user_id: string;
  email: string | null;
  full_name: string;
  role: UserRole;
  avatar_url: string | null;
};

export type RegisterPayload = {
  email: string;
  password: string;
  full_name: string;
};

export type LoginPayload = {
  email: string;
  password: string;
};

