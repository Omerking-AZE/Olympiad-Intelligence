export type SkillKey =
  | "algebra"
  | "geometry"
  | "number_theory"
  | "discrete_mathematics"
  | "proof"
  | "reasoning"
  | "calculation"
  | "case_analysis";

export type Skill = {
  code: string;
  name: string;
  key: SkillKey;
};

export type ProgressPoint = {
  id?: string;
  date?: string;
  contest?: string;
  rating?: number;
  overall_rating?: number;
};

export type StudentIntelligence = {
  student_id?: string;
  student_name: string;
  overall_rating: number;
  tier: string;
  problems_attempted: number;
  problems_solved: number;
  achievement: string;
  strongest_skills: string[];
  high_priority_weaknesses: string[];
  medium_priority_weaknesses: string[];
  unknown_skills: string[];
  skill_ratings: Record<
    SkillKey,
    number
  >;
};