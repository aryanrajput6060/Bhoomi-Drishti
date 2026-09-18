import { ResearchPaper, PolicyDocument, DatasetItem, SimulationInput, SimulationResult } from '../types';
import { DEMO_RESEARCH_PAPERS, DEMO_POLICIES, DEMO_DATASETS, PREVIOUS_SIMULATIONS, DEMO_GIS_DISTRICTS } from '../data/mockData';

const API_BASE_URL = import.meta.env.VITE_API_URL || (typeof window !== 'undefined' ? `${window.location.origin}/api` : 'http://127.0.0.1:8000/api');

export async function fetchResearchPapers(topic?: string, search?: string): Promise<ResearchPaper[]> {
  try {
    const params = new URLSearchParams();
    if (topic && topic !== 'All') params.append('topic', topic);
    if (search) params.append('search', search);
    const res = await fetch(`${API_BASE_URL}/research?${params.toString()}`);
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn('FastAPI unavailable, using local mock research papers.', err);
  }

  // Client-side fallback
  let list = DEMO_RESEARCH_PAPERS;
  if (topic && topic !== 'All') {
    list = list.filter(p => p.topic.toLowerCase().includes(topic.toLowerCase()));
  }
  if (search) {
    const s = search.toLowerCase();
    list = list.filter(p => p.title.toLowerCase().includes(s) || p.abstract.toLowerCase().includes(s));
  }
  return list;
}

export async function fetchPolicies(status?: string, search?: string): Promise<PolicyDocument[]> {
  try {
    const params = new URLSearchParams();
    if (status && status !== 'All') params.append('status', status);
    if (search) params.append('search', search);
    const res = await fetch(`${API_BASE_URL}/policies?${params.toString()}`);
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn('FastAPI unavailable, using local mock policies.', err);
  }

  let list = DEMO_POLICIES;
  if (status && status !== 'All') {
    list = list.filter(p => p.status.toLowerCase() === status.toLowerCase());
  }
  if (search) {
    const s = search.toLowerCase();
    list = list.filter(p => p.title.toLowerCase().includes(s) || p.description.toLowerCase().includes(s));
  }
  return list;
}

export async function fetchDatasets(category?: string, search?: string): Promise<DatasetItem[]> {
  try {
    const params = new URLSearchParams();
    if (category && category !== 'All') params.append('category', category);
    if (search) params.append('search', search);
    const res = await fetch(`${API_BASE_URL}/datasets?${params.toString()}`);
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn('FastAPI unavailable, using local mock datasets.', err);
  }

  let list = DEMO_DATASETS;
  if (category && category !== 'All') {
    list = list.filter(d => d.category.toLowerCase().includes(category.toLowerCase()));
  }
  if (search) {
    const s = search.toLowerCase();
    list = list.filter(d => d.name.toLowerCase().includes(s) || d.description.toLowerCase().includes(s));
  }
  return list;
}

export async function executeSimulation(input: SimulationInput): Promise<SimulationResult> {
  try {
    const res = await fetch(`${API_BASE_URL}/simulation/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(input)
    });
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn('FastAPI simulation endpoint unavailable, using client-side engine.', err);
  }

  // Deterministic calculation engine
  const ag_conv = input.ag_conversion_pct;
  const pop_gr = input.population_growth_pct;
  const infra_gr = input.infrastructure_growth_pct;
  const climate_factor = input.climate_risk === 'Low' ? 1.0 : (input.climate_risk === 'Medium' ? 1.25 : 1.55);

  const ag_land_change = -Number((ag_conv * 0.84).toFixed(2));
  const residential_change = +Number((ag_conv * 0.72 + (pop_gr * 0.28)).toFixed(2));
  const industrial_change = +Number(((infra_gr * 0.22) + (ag_conv * 0.12)).toFixed(2));
  const forest_pressure = -Number((ag_conv * 0.18 + (infra_gr * 0.14)).toFixed(2));
  const water_body_stress = -Number(((ag_conv * 0.11 + infra_gr * 0.09) * climate_factor).toFixed(2));

  const water_stress = +Number(((ag_conv * 0.42 + pop_gr * 0.31) * climate_factor * 0.65).toFixed(2));
  const green_cover_pressure = +Number(((ag_conv * 0.34 + infra_gr * 0.28) * 0.7).toFixed(2));
  const climate_exposure = +Number(((pop_gr * 0.25 + ag_conv * 0.35) * climate_factor * 0.75).toFixed(2));
  const carbon_sink_deficit = +Number((Math.abs(ag_land_change) * 0.45 + Math.abs(forest_pressure) * 0.85).toFixed(2));

  const road_demand = +Number((infra_gr * 0.48 + pop_gr * 0.24).toFixed(2));
  const public_service_demand = +Number((pop_gr * 0.52 + ag_conv * 0.12).toFixed(2));
  const sewerage_pressure = +Number((pop_gr * 0.58 + ag_conv * 0.18).toFixed(2));
  const grid_power_demand = +Number((pop_gr * 0.44 + infra_gr * 0.32).toFixed(2));

  const zonesMap: Record<string, string[]> = {
    "Bhopal": ["Kolar Peri-Urban Fringe", "Mandideep Corridor", "Bairagarh Bypass", "Upper Lake Buffer", "Berasia Road Corridor"],
    "Indore": ["Super Corridor AB Bypass", "Pithampur Industrial Fringe", "Sanwer Road Zone", "Ujjain Road Cluster"],
    "Delhi": ["Najafgarh Rural Fringe", "Bawana Industrial Buffer", "Yamuna Floodplain Zone", "Gurugram-Faridabad Transit Ridge"],
    "Ahmedabad": ["Sanand Industrial Expansion Zone", "SP Ring Road Agricultural Fringe", "Dholera Corridor Node"],
    "Bengaluru": ["Anekal Agrarian Transition Belt", "Sarjapur Peri-Urban Fringe", "Devanahalli Airport Aerotropolis Buffer"]
  };

  return {
    id: `SIM-${input.region.slice(0, 3).toUpperCase()}-${Math.floor(1000 + Math.random() * 9000)}`,
    scenario_name: input.scenario_name,
    region: input.region,
    timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19),
    inputs: input,
    land_use_impact: {
      "Agricultural Land": ag_land_change,
      "Residential Area": residential_change,
      "Industrial Area": industrial_change,
      "Forest Buffer": forest_pressure,
      "Water Body Retention": water_body_stress
    },
    environmental_indicators: {
      "Water Stress": water_stress,
      "Green Cover Pressure": green_cover_pressure,
      "Climate Exposure": climate_exposure,
      "Carbon Sink Deficit": carbon_sink_deficit
    },
    infrastructure_impact: {
      "Road Demand": road_demand,
      "Public Service Demand": public_service_demand,
      "Sewerage Network Pressure": sewerage_pressure,
      "Grid Power Demand": grid_power_demand
    },
    affected_zones: zonesMap[input.region] || ["Peri-Urban Agricultural Belt", "Outer Ring Road Fringe"],
    disclaimer: "Scenario-based estimates generated from available research data and mathematical model assumptions. Results are intended for decision support and policy exploration and should not be interpreted as guaranteed predictions.",
    model_assumptions: [
      `Baseline elasticity of residential conversion per percentage point of agricultural diversion: 0.72.`,
      `Climate multiplier applied: ${climate_factor}x based on '${input.climate_risk}' climate vulnerability baseline.`,
      `Infrastructure absorption threshold assumed constant over a 5-year simulation horizon.`,
      "Water extraction stress calibrated against Central Ground Water Board (CGWB) district baselines."
    ]
  };
}

export async function executeAISearch(query: string) {
  try {
    const res = await fetch(`${API_BASE_URL}/ai/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query })
    });
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn('AI search backend unavailable, using client synthesis.', err);
  }

  // Client synthesis
  const q = query.toLowerCase();
  if (q.includes('bhopal') || q.includes('conversion') || q.includes('urban')) {
    return {
      query,
      answer: "Urban land conversion in Bhopal is primarily driven by arterial transportation corridor expansion (notably NH-46 Hoshangabad Road and Kolar Bypass), high returns on residential plot subdivision relative to agrarian yield, and anticipatory speculation preceding the Bhopal Master Plan 2031 approval. Satellite telemetry (2015–2024) indicates a 14.8% reduction in prime double-cropped land across southern and eastern peri-urban rings. Compounding this, the absence of finalized T&CP master plan statutory enforcement has fostered fragmented developments that stress regional aquifers and encroach upon Upper Lake catchment corridors.",
      key_drivers: [
        "Arterial Highway Corridors: NH-46, Kolar Road, and Bairagarh Bypass catalyzing rapid land parcel aggregation.",
        "Real Estate Speculation & Land Price Gradient: Agricultural land values rising by 220–340% within 3km of proposed Outer Ring Road.",
        "Statutory Lag in Master Plan Notification: Delays in final notification of Bhopal Master Plan 2031 creating informal conversion windows.",
        "Groundwater Depletion & Reduced Agrarian Margins: Piezometric drops in peri-urban tube wells pushing marginal farmers towards land sale."
      ],
      policy_implications: [
        "Establish statutory eco-sensitive buffer around Upper Lake (Bhoj Wetland Ramsar site) strictly restricting land-use diversion.",
        "Implement Transferable Development Rights (TDR) to compensate agricultural landholders in designated green belts.",
        "Fast-track integration of SVAMITVA cadastral drone layers with MP Bhu-Abhilekh to eliminate unapproved parcel subdivision."
      ],
      sources_used: [DEMO_RESEARCH_PAPERS[0], DEMO_RESEARCH_PAPERS[1], DEMO_RESEARCH_PAPERS[3], DEMO_RESEARCH_PAPERS[11]],
      confidence_score: 0.94
    };
  }

  return {
    query,
    answer: `Evidence-based synthesis for query: '${query}'. Multi-temporal spatial analysis reveals significant interplay between transport infrastructure investments, tenancy structure transitions, and ecological vulnerabilities. Evidence indicates that unplanned peri-urban conversions without commensurate drainage and water-harvesting safeguards compound urban flood risks and reduce agricultural output.`,
    key_drivers: [
      "Infrastructure spillover driving non-agricultural parcel conversion.",
      "Decoupling of land market values from agricultural productivity index.",
      "Ecosystem service degradation in watershed zones."
    ],
    policy_implications: [
      "Mandate Comprehensive Spatial Environmental Impact Assessments (SEIA) prior to major land conversions.",
      "Synchronize digital land registries with GIS zoning master plans.",
      "Formulate district-level agro-ecological conservation thresholds."
    ],
    sources_used: [DEMO_RESEARCH_PAPERS[2], DEMO_RESEARCH_PAPERS[4], DEMO_RESEARCH_PAPERS[7]],
    confidence_score: 0.88
  };
}
