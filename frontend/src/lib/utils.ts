import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function getScoreColor(score: number): string {
  if (score >= 80) return "text-emerald-400";
  if (score >= 60) return "text-amber-400";
  return "text-rose-400";
}

export function getScoreLabel(score: number): string {
  if (score >= 80) return "Optimal";
  if (score >= 60) return "Good";
  if (score >= 40) return "Moderate";
  return "Low";
}
