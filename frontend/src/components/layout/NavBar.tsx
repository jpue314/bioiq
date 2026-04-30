"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { cn } from "@/lib/utils";

const links = [
  { href: "/dashboard", label: "Home" },
  { href: "/metrics", label: "Metrics" },
  { href: "/devices", label: "Devices" },
  { href: "/ai", label: "BioIQ AI" },
  { href: "/providers", label: "Providers" },
  { href: "/settings", label: "Settings" },
];

export default function NavBar() {
  const pathname = usePathname();
  const { logout } = useAuth();
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-slate-950/80 backdrop-blur border-b border-slate-800">
      <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
        <span className="text-xl font-bold text-white tracking-tight">BioIQ</span>
        <div className="flex items-center gap-6">
          {links.map((link) => (
            <Link key={link.href} href={link.href}
              className={cn("text-sm font-medium transition-colors",
                pathname.startsWith(link.href) ? "text-white" : "text-slate-400 hover:text-white")}>
              {link.label}
            </Link>
          ))}
          <button onClick={logout} className="text-sm text-slate-400 hover:text-white transition-colors">
            Sign out
          </button>
        </div>
      </div>
    </nav>
  );
}
