"use client";
import Link from "next/link";
import { useState, FormEvent } from "react";
import { useRouter } from "next/navigation";
import { api, setAccessToken } from "@/lib/api";

export default function RegisterPage() {
  const router = useRouter();
  const [form, setForm] = useState({ email: "", password: "", first_name: "", last_name: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await api.post("/api/auth/register/", form);
      setAccessToken(res.data.access);
      router.push("/dashboard");
    } catch {
      setError("Registration failed. Please check your details and try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">BioIQ</h1>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8">
          <h2 className="text-xl font-semibold text-white mb-6">Create account</h2>
          {error && <p className="text-rose-400 text-sm mb-4 bg-rose-950 border border-rose-800 rounded-lg p-3">{error}</p>}
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <div className="grid grid-cols-2 gap-3">
              <div className="flex flex-col gap-1">
                <label className="text-sm text-slate-400">First name</label>
                <input type="text" value={form.first_name} onChange={(e) => setForm({...form, first_name: e.target.value})}
                  className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2.5 text-white focus:outline-none focus:border-blue-500" />
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-sm text-slate-400">Last name</label>
                <input type="text" value={form.last_name} onChange={(e) => setForm({...form, last_name: e.target.value})}
                  className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2.5 text-white focus:outline-none focus:border-blue-500" />
              </div>
            </div>
            <div className="flex flex-col gap-1">
              <label className="text-sm text-slate-400">Email</label>
              <input type="email" value={form.email} required onChange={(e) => setForm({...form, email: e.target.value})}
                className="bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-blue-500" />
            </div>
            <div className="flex flex-col gap-1">
              <label className="text-sm text-slate-400">Password (12+ characters)</label>
              <input type="password" value={form.password} required onChange={(e) => setForm({...form, password: e.target.value})}
                className="bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-blue-500" />
            </div>
            <button type="submit" disabled={loading}
              className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-semibold rounded-lg py-2.5 transition-colors">
              {loading ? "Creating account..." : "Create account"}
            </button>
          </form>
          <p className="text-center text-sm text-slate-400 mt-6">
            Already have an account? <Link href="/login" className="text-blue-400 hover:text-blue-300">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
