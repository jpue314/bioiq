import NavBar from "./NavBar";
export default function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-slate-950">
      <NavBar />
      <main className="max-w-6xl mx-auto px-4 pt-24 pb-16">{children}</main>
    </div>
  );
}
