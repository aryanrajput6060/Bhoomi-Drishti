export type UserRole = 'public' | 'researcher' | 'policymaker' | 'admin';

export interface UserProfile {
  id: string;
  name: string;
  email: string;
  role: string;
  roleType: UserRole;
  organization: string;
  status: string;
  last_active: string;
}

export interface ResearchPaper {
  id: string;
  title: string;
  authors: string;
  organization: string;
  year: number;
  region: string;
  topic: string;
  abstract: string;
  source_url?: string;
  relevance: number;
  citations: number;
}

export interface PolicyDocument {
  id: string;
  title: string;
  department: string;
  year: number;
  region: string;
  description: string;
  status: 'Active' | 'Under Evaluation' | 'Draft' | 'Archived';
  sector: string;
}

export interface DatasetItem {
  id: string;
  name: string;
  organization: string;
  category: string;
  geographic_coverage: string;
  year: number;
  format: string;
  license: string;
  last_updated: string;
  size: string;
  rows: number;
  description: string;
}

export interface SimulationInput {
  scenario_name: string;
  region: string;
  ag_conversion_pct: number;
  population_growth_pct: number;
  infrastructure_growth_pct: number;
  climate_risk: 'Low' | 'Medium' | 'High';
}

export interface SimulationResult {
  id: string;
  scenario_name: string;
  region: string;
  timestamp: string;
  inputs: SimulationInput;
  land_use_impact: {
    [key: string]: number;
  };
  environmental_indicators: {
    [key: string]: number;
  };
  infrastructure_impact: {
    [key: string]: number;
  };
  affected_zones: string[];
  disclaimer: string;
  model_assumptions: string[];
}

export interface NotificationItem {
  id: string;
  title: string;
  message: string;
  timestamp: string;
  type: 'research' | 'simulation' | 'dataset' | 'system' | 'project';
  read: boolean;
}

export interface ProjectTask {
  id: string;
  title: string;
  assignee: string;
  completed: boolean;
}

export interface ProjectComment {
  author: string;
  time: string;
  text: string;
}

export interface ProjectWorkspaceItem {
  id: string;
  title: string;
  region: string;
  lead: string;
  members: string[];
  status: string;
  progress: number;
  description: string;
  tasks: ProjectTask[];
  comments: ProjectComment[];
}

export interface GISDistrict {
  id: string;
  name: string;
  coordinates: [number, number];
  population: string;
  urbanization: string;
  ag_land: string;
  climate_risk: string;
  urban_expansion: string;
  infra_pressure: string;
  primary_growth_corridors: string[];
}
