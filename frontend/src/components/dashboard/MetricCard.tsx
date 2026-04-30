"use client";
import { motion } from "framer-motion";

interface Props { title: string; value: number | null; icon: React.ReactNode; delay?: number; }

export default function MetricCard({ title, value, icon, delay = 0 }: Props) {
  return (
    <motion.div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 flex flex-col gap-3"
      initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.4 }}>
      <div className="flex items-center justify-between">
        <span className="text-slate-400 text-sm font-medium">{title}</span>
        <span className="text-slate-500">{icon}</span>
      </div>
      <span className="text-3xl font-bold text-white">{value ?? "--"}</span>
    </motion.div>
  );
}
