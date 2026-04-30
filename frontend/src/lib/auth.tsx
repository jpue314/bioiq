"use client";
import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { api, setAccessToken } from "./api";
import type { User } from "@/types";

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.post("/api/auth/token/refresh/")
      .then((res) => { setAccessToken(res.data.access); return api.get<User>("/api/auth/me/"); })
      .then((res) => setUser(res.data))
      .catch(() => setUser(null))
      .finally(() => setLoading(false));
  }, []);

  async function login(email: string, password: string) {
    const res = await api.post("/api/auth/login/", { email, password });
    setAccessToken(res.data.access);
    const me = await api.get<User>("/api/auth/me/");
    setUser(me.data);
  }

  async function logout() {
    await api.post("/api/auth/logout/");
    setAccessToken(null);
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}
