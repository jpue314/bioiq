"use client";
import { useQuery } from "@tanstack/react-query";
import { Heart, Moon, Activity, Zap } from "lucide-react";
import { api } from "@/lib/api";
import AppShell from "@/components/layout/AppShell";
import ReadinessScore from "@/components/dashboard/ReadinessScore";
import MetricCard from "@/components/dashboard/MetricCard";
import { getScoreColor, getScoreLabel } from "@/lib/utils";
import type { DailyScore } from "@/types";

export default function DashboardPage() {
  const { data: score, isLoading, isError } = useQuery<DailyScore>({
    queryKey: ["scores", "today"],
    queryFn: () => api.get("/api/scores/today/").then((r) => r.data),
  });

  return (
    <AppShell>
      <div className="flex flex-col items-center gap-12">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-white mb-2">Good morning</h1>
          <p className="text-slate-400">Your health snapshot for today.</p>
        </div>
        {isLoading && <p className="text-slate-400">Loading...</p>}
        {isError && (
          <div className="text-center">
            <p className="text-slate-500">No data for today. Connect a device to get started.</p>
          </div>
        )}
        {score && (
          <>
            <ReadinessScore score={score.readiness_score}
              label={getScoreLabel(score.readiness_score)}
              color={getScoreColor(score.readiness_score)} />
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 w-full">
              <MetricCard title="Sleep" value={score.sleep_score} icon={<Moon size={18} />} delay={0.1} />
              <MetricCard title="Recovery" value={score.recovery_score} icon={<Heart size={18} />} delay={0.2} />
              <MetricCard title="Activity" value={score.activity_score} icon={<Activity size={18} />} delay={0.3} />
              <MetricCard title="Readiness" value={score.readiness_score} icon={<Zap size={18} />} delay={0.4} />
            </div>
          </>
        )}
      </div>
    </AppShell>
  );
}
