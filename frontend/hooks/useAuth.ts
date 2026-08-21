"use client";

import { useRouter } from "next/navigation";
import { useCallback } from "react";

import { useAuthContext } from "@/lib/authContext";
import type { LoginPayload, OtpVerifyPayload, RegisterPayload } from "@/types/auth";

export function useAuth() {
  const ctx = useAuthContext();
  const router = useRouter();

  const loginAndRedirect = useCallback(
    async (payload: LoginPayload, redirectTo = "/dashboard") => {
      await ctx.login(payload);
      router.push(redirectTo);
    },
    [ctx, router]
  );

  const loginWithOtpAndRedirect = useCallback(
    async (payload: OtpVerifyPayload, redirectTo = "/dashboard") => {
      await ctx.loginWithOtp(payload);
      router.push(redirectTo);
    },
    [ctx, router]
  );

  const registerAndRedirect = useCallback(
    async (payload: RegisterPayload, redirectTo = "/dashboard") => {
      await ctx.register(payload);
      router.push(redirectTo);
    },
    [ctx, router]
  );

  const logoutAndRedirect = useCallback(
    async (redirectTo = "/") => {
      await ctx.logout();
      router.push(redirectTo);
    },
    [ctx, router]
  );

  return {
    user: ctx.user,
    accessToken: ctx.accessToken,
    isLoading: ctx.isLoading,
    isAuthenticated: Boolean(ctx.user),
    isAdmin: ctx.user?.role === "admin",
    login: loginAndRedirect,
    loginWithOtp: loginWithOtpAndRedirect,
    register: registerAndRedirect,
    logout: logoutAndRedirect,
  };
}
