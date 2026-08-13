export type SkillRatings = {
  algebra: number;
  geometry: number;
  number_theory: number;
  discrete_mathematics: number;
  proof: number;
  reasoning: number;
  calculation: number;
  case_analysis: number;
};

export type StudentIntelligence = {
  student_id: string;
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
  skill_ratings: SkillRatings;
};

export type ProgressPoint = {
  attempts: number;
  solved: number;
  success_rate: number;
  overall_rating: number;
  tier: string;
};

export type Skill = {
  code: string;
  name: string;
  key: keyof SkillRatings;
};