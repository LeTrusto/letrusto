"use client";

import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";

import { introspectAccessToken, loginUser, logoutUser, registerUser } from "@/services/auth.service";
import type { AuthResponse, AuthState, AuthUser, LoginPayload, RegisterPayload } from "@/types/auth";
import {
  ACCESS_TOKEN_KEY,
  publishAuthSession,
  publishLogout,
  refreshSessionAcrossTabs,
  REFRESH_TOKEN_KEY,
  subscribeToAuthEvents,
} from "@/lib/authSession";

type AuthContextValue = AuthState & {
  register: (payload: RegisterPayload) => Promise<void>;
  login: (payload: LoginPayload) => Promise<void>;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

function userFromResponse(r: AuthResponse): AuthUser {
  return {
    id: r.user_id,
    email: r.email,
    full_name: r.full_name,
    role: r.role,
    avatar_url: r.avatar_url,
  };
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  // Always start as isLoading:true so server and client render identically (no hydration mismatch)
  const [state, setState] = useState<AuthState>({
    user: null,
    accessToken: null,
    refreshToken: null,
    isLoading: true,
  });

  useEffect(() => {
    const access = localStorage.getItem(ACCESS_TOKEN_KEY);
    const refresh = localStorage.getItem(REFRESH_TOKEN_KEY);
    if (!access || !refresh) {
      // Defer via microtask so this is never a synchronous setState in the effect body
      void Promise.resolve().then(() =>
        setState({ user: null, accessToken: null, refreshToken: null, isLoading: false })
      );
      return;
    }
    refreshSessionAcrossTabs(refresh)
      .then(async (r) => {
        const session = await introspectAccessToken(r.access_token);
        if (session.subject !== r.user_id) throw new Error("Session user mismatch");
        localStorage.setItem(ACCESS_TOKEN_KEY, r.access_token);
        localStorage.setItem(REFRESH_TOKEN_KEY, r.refresh_token);
        setState({
          user: userFromResponse(r),
          accessToken: r.access_token,
          refreshToken: r.refresh_token,
          isLoading: false,
        });
      })
      .catch(() => clearStoredSession());
    return subscribeToAuthEvents(
      (r) => {
        localStorage.setItem(ACCESS_TOKEN_KEY, r.access_token);
        localStorage.setItem(REFRESH_TOKEN_KEY, r.refresh_token);
        setState({ user: userFromResponse(r), accessToken: r.access_token, refreshToken: r.refresh_token, isLoading: false });
      },
      () => clearStoredSession(false),
    );
  }, []);

  function clearStoredSession(broadcast = true) {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem("token");
    [ACCESS_TOKEN_KEY, REFRESH_TOKEN_KEY, "token", "access_token", "refresh_token"].forEach((key) => {
      sessionStorage.removeItem(key);
    });
    document.cookie.split(";").forEach((cookie) => {
      const name = cookie.split("=")[0]?.trim();
      if (name) document.cookie = `${name}=; Max-Age=0; path=/`;
    });
    if (broadcast) publishLogout();
    setState({ user: null, accessToken: null, refreshToken: null, isLoading: false });
  }

  const applyAuth = useCallback((r: AuthResponse) => {
    localStorage.setItem(ACCESS_TOKEN_KEY, r.access_token);
    localStorage.setItem(REFRESH_TOKEN_KEY, r.refresh_token);
    publishAuthSession(r);
    setState({
      user: userFromResponse(r),
      accessToken: r.access_token,
      refreshToken: r.refresh_token,
      isLoading: false,
    });
  }, []);

  const register = useCallback(
    async (payload: RegisterPayload) => {
      const r = await registerUser(payload);
      applyAuth(r);
    },
    [applyAuth]
  );

  const login = useCallback(
    async (payload: LoginPayload) => {
      const r = await loginUser(payload);
      applyAuth(r);
    },
    [applyAuth]
  );

  const logout = useCallback(async () => {
    const refresh = localStorage.getItem(REFRESH_TOKEN_KEY);
    if (refresh) await logoutUser(refresh);
    clearStoredSession();
  }, []);

  return (
    <AuthContext.Provider value={{ ...state, register, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuthContext(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuthContext must be used inside AuthProvider");
  return ctx;
}
