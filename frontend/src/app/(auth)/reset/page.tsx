"use client";
import Link from "next/link";
import { useState, FormEvent } from "react";
import { api } from "@/lib/api";

export default function ResetPage() {
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    try { await api.post("/api/auth/password/reset/", { email }); } finally {
      setSent(true);
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center px-4">
      <div className="w-full max-w-sm bg-slate-900 border border-slate-800 rounded-2xl p-8">
        <h2 className="text-xl font-semibold text-white mb-4">Reset password</h2>
        {sent ? (
          <p className="text-slate-300 text-sm">If that email exists, a reset link is on its way.</p>
        ) : (
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required
              placeholder="you@example.com"
              className="bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-blue-500" />
            <button type="submit" disabled={loading}
              className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-semibold rounded-lg py-2.5 transition-colors">
              {loading ? "Sending..." : "Send reset link"}
            </button>
          </form>
        )}
        <p className="text-center text-sm text-slate-400 mt-6">
          <Link href="/login" className="text-blue-400 hover:text-blue-300">Back to sign in</Link>
        </p>
      </div>
    </div>
  );
}
