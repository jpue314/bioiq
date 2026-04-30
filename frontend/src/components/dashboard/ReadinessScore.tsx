"use client";
import { motion } from "framer-motion";

interface Props { score: number; label: string; color: string; }

export default function ReadinessScore({ score, label, color }: Props) {
  const radius = 80;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className="flex flex-col items-center gap-3">
      <div className="relative">
        <svg width="200" height="200" className="-rotate-90">
          <circle cx="100" cy="100" r={radius} fill="none" stroke="#1e293b" strokeWidth="12" />
          <motion.circle cx="100" cy="100" r={radius} fill="none" stroke="currentColor"
            strokeWidth="12" strokeLinecap="round" strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }} animate={{ strokeDashoffset: offset }}
            transition={{ duration: 1.2, ease: "easeOut" }} className={color} />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <motion.span className="text-5xl font-bold text-white"
            initial={{ opacity: 0, scale: 0.5 }} animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.4, duration: 0.5 }}>
            {score}
          </motion.span>
          <span className="text-sm text-slate-400">/ 100</span>
        </div>
      </div>
      <span className={"text-lg font-semibold " + color}>{label}</span>
      <p className="text-slate-400 text-sm">Daily Readiness</p>
    </div>
  );
}
