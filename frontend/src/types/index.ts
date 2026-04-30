export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  is_verified: boolean;
  health_profile: HealthProfile | null;
}

export interface HealthProfile {
  date_of_birth: string | null;
  biological_sex: string;
  height_cm: number | null;
  weight_kg: string | null;
  fitness_goals: string[];
}

export interface DailyScore {
  id: number;
  date: string;
  readiness_score: number;
  sleep_score: number | null;
  recovery_score: number | null;
  activity_score: number | null;
  score_breakdown: Record<string, number>;
}

export interface AIMessage {
  role: "user" | "assistant";
  content: string;
}
