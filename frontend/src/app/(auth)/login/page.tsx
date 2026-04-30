"use client";
import Link from "next/link";
import { useState, FormEvent } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      router.push("/dashboard");
    } catch {
      setError("Invalid email or password.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">BioIQ</h1>
          <p className="text-slate-400">Your health intelligence hub</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8">
          <h2 className="text-xl font-semibold text-white mb-6">Sign in</h2>
          {error && <p className="text-rose-400 text-sm mb-4 bg-rose-950 border border-rose-800 rounded-lg p-3">{error}</p>}
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <div className="flex flex-col gap-1">
              <label className="text-sm text-slate-400">Email</label>
              <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required
                className="bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-blue-500"
                placeholder="you@example.com" />
            </div>
            <div className="flex flex-col gap-1">
              <label className="text-sm text-slate-400">Password</label>
              <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required
                className="bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-blue-500" />
            </div>
            <button type="submit" disabled={loading}
              className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-semibold rounded-lg py-2.5 transition-colors">
              {loading ? "Signing in..." : "Sign in"}
            </button>
          </form>
          <p className="text-center text-sm text-slate-400 mt-6">
            No account? <Link href="/register" className="text-blue-400 hover:text-blue-300">Create one</Link>
          </p>
          <p className="text-center text-sm text-slate-400 mt-2">
            <Link href="/reset" className="text-blue-400 hover:text-blue-300">Forgot password?</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
