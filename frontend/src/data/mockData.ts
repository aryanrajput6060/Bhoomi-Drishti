import { ResearchPaper, PolicyDocument, DatasetItem, GISDistrict, NotificationItem, ProjectWorkspaceItem, SimulationResult } from '../types';

export const DEMO_RESEARCH_PAPERS: ResearchPaper[] = [
  {
    id: "rp-1",
    title: "Urban Expansion and Agricultural Land Conversion in Bhopal Fringe Areas",
    authors: "Dr. K. Sharma, Dr. R. Verma, S. Nair",
    organization: "Maulana Azad National Institute of Technology (MANIT)",
    year: 2024,
    region: "Bhopal, Madhya Pradesh",
    topic: "Urban Expansion",
    abstract: "Satellite telemetry from 2015 to 2023 demonstrates that peri-urban agricultural zones in Kolar, Mandideep, and Bairagarh fringes have undergone 14.8% conversion to non-agricultural uses, primarily driven by arterial transport corridors.",
    source_url: "#",
    relevance: 96,
    citations: 48,
  },
  {
    id: "rp-2",
    title: "Climate Resilient Land Use Planning: Upper Lake Catchment Vulnerability Assessment",
    authors: "Dr. A. Pathak, M. Choudhary",
    organization: "Indian Institute of Forest Management (IIFM)",
    year: 2025,
    region: "Bhopal, Madhya Pradesh",
    topic: "Climate & Ecology",
    abstract: "Quantifies the hydrological runoff and water stress index across Bhoj Wetland buffer zones subject to residential encroachment, offering spatial zoning models for retention basins.",
    source_url: "#",
    relevance: 94,
    citations: 32,
  },
  {
    id: "rp-3",
    title: "GIS-Based Urban Growth Simulation and Predictive Cadastral Modeling",
    authors: "P. Iyer, T. Sengupta",
    organization: "Centre for Spatial Studies & Geospatial Survey of India",
    year: 2023,
    region: "Madhya Pradesh",
    topic: "GIS & Simulation",
    abstract: "Multi-temporal Landsat 8 and Sentinel-2 imagery analysis revealing cellular automata land transition probabilities across Tier-2 Indian urban agglomerations.",
    source_url: "#",
    relevance: 91,
    citations: 64,
  },
  {
    id: "rp-4",
    title: "Institutional Land Governance and Fragmented Peri-Urban Titles in Central India",
    authors: "Adv. S. Mishra, Dr. N. Rao",
    organization: "National Law Institute University (NLIU) Bhopal",
    year: 2024,
    region: "Madhya Pradesh",
    topic: "Legal & Governance",
    abstract: "Examines legal titling disputes arising from agricultural tenancy conversions under the MP Land Revenue Code, with recommendations for digital boundary reconciliation.",
    source_url: "#",
    relevance: 88,
    citations: 19,
  },
  {
    id: "rp-5",
    title: "Groundwater Depletion Correlation with Impervious Surface Expansion in Indore-Bhopal Corridor",
    authors: "R. Sen, K. Mukherjee",
    organization: "Central Ground Water Board (CGWB) & MANIT",
    year: 2024,
    region: "Indore-Bhopal Corridor",
    topic: "Hydrology & Environment",
    abstract: "Analyzes 10-year piezometric borehole data juxtaposed against built-up footprint expansion along the SH-18 economic corridor.",
    source_url: "#",
    relevance: 89,
    citations: 27,
  },
  {
    id: "rp-6",
    title: "Socio-Economic Impacts of Agricultural Land Reallocation on Smallholder Livelihoods",
    authors: "Dr. B. Das, P. Patel",
    organization: "Tata Institute of Social Sciences (TISS)",
    year: 2023,
    region: "Central India",
    topic: "Socio-Economic",
    abstract: "Survey of 450 peri-urban households in Sehore and Raisen evaluating income vulnerability following transition from agrarian to casual urban employment.",
    source_url: "#",
    relevance: 85,
    citations: 38,
  },
  {
    id: "rp-7",
    title: "Monitoring Urban Heat Island Intensification in Rapidly Developing Smart Cities",
    authors: "V. Gokhale, S. Trivedi",
    organization: "IIT Indore & Remote Sensing Applications Centre (RSAC)",
    year: 2025,
    region: "Indore, Madhya Pradesh",
    topic: "Climate & Ecology",
    abstract: "MODIS surface temperature analysis establishing a 2.8°C thermal differential between urban core and peripheral agricultural zones during summer peak months.",
    source_url: "#",
    relevance: 87,
    citations: 15,
  },
  {
    id: "rp-8",
    title: "Cadastral Boundary Reconciliation Utilizing High-Resolution UAV Drones",
    authors: "A. Joshi, K. Sundaram",
    organization: "Survey of India & SVAMITVA Technical Unit",
    year: 2024,
    region: "Madhya Pradesh",
    topic: "GIS & Simulation",
    abstract: "Evaluation of orthorectified imagery accuracy within pilot villages under SVAMITVA scheme, achieving <5cm positional horizontal accuracy for parcel demarcation.",
    source_url: "#",
    relevance: 92,
    citations: 51,
  },
  {
    id: "rp-9",
    title: "Industrial Land Demand Projection along Delhi-Mumbai Industrial Corridor (DMIC)",
    authors: "National Industrial Corridor Development Corporation (NICDC)",
    organization: "NICDC & NITI Aayog Research Cell",
    year: 2024,
    region: "National / MP Node",
    topic: "Infrastructure",
    abstract: "Econometric forecast of non-agricultural conversion demands for logistic nodes and ancillary manufacturing zones in Pithampur and Mandideep.",
    source_url: "#",
    relevance: 84,
    citations: 22,
  },
  {
    id: "rp-10",
    title: "Forest Fringe Dynamics and Wildlife Corridor Encroachment in Central Highlands",
    authors: "Wildlife Institute of India (WII) & State Forest Research Institute",
    organization: "WII Dehradun",
    year: 2023,
    region: "Madhya Pradesh",
    topic: "Forest & Conservation",
    abstract: "Spatial fragmentation metrics around Ratapani Wildlife Sanctuary illustrating the encroachment pressures induced by peripheral township expansion.",
    source_url: "#",
    relevance: 86,
    citations: 34,
  },
  {
    id: "rp-11",
    title: "Digital Land Records Modernization: Empirical Evaluation of DILRMP in Central India",
    authors: "Dr. H. Agrawal, R. N. Tiwari",
    organization: "Administrative Staff College of India (ASCI)",
    year: 2024,
    region: "Madhya Pradesh",
    topic: "Legal & Governance",
    abstract: "Audit of 52 district land registries assessing registration turnaround times, mutation backlog, and public grievance resolution post-digitization.",
    source_url: "#",
    relevance: 90,
    citations: 42,
  },
  {
    id: "rp-12",
    title: "Infrastructure Spillover Effects on Peri-Urban Real Estate Speculation",
    authors: "Prof. D. Chawla, A. Singhal",
    organization: "School of Planning and Architecture (SPA) Bhopal",
    year: 2025,
    region: "Bhopal Fringe",
    topic: "Urban Expansion",
    abstract: "Hedonic price modeling demonstrating land value escalation within a 3km buffer of the newly planned Bhopal Outer Ring Road.",
    source_url: "#",
    relevance: 93,
    citations: 17,
  },
  {
    id: "rp-13",
    title: "Wetland Preservation and Master Plan Integration: A Decadal Review of Bhoj Ramsar Site",
    authors: "Bhopal Municipal Corporation & Environmental Planning & Coordination Org (EPCO)",
    organization: "EPCO Madhya Pradesh",
    year: 2023,
    region: "Bhopal, Madhya Pradesh",
    topic: "Climate & Ecology",
    abstract: "Comprehensive review of the 2005 Master Plan environmental buffers versus ground reality, proposing dynamic GIS alert overlays for civic enforcement.",
    source_url: "#",
    relevance: 91,
    citations: 29,
  },
  {
    id: "rp-14",
    title: "Agro-Ecological Zoning Using Multi-Criteria Decision Analysis (MCDA) in Sehore",
    authors: "Indian Council of Agricultural Research (ICAR-CIAE)",
    organization: "ICAR Bhopal",
    year: 2024,
    region: "Madhya Pradesh",
    topic: "Socio-Economic",
    abstract: "AHP-weighted spatial GIS model categorizing prime fertile soils to be safeguarded from compulsory urban acquisition.",
    source_url: "#",
    relevance: 88,
    citations: 20,
  },
  {
    id: "rp-15",
    title: "Disaster Risk Governance: Urban Inundation Modeling for Tier-2 River Basins",
    authors: "National Institute of Disaster Management (NIDM)",
    organization: "NIDM New Delhi",
    year: 2025,
    region: "Central India",
    topic: "Climate & Ecology",
    abstract: "Hydrodynamic modeling of sudden extreme rainfall events across altered urban topography with compromised natural drainage channels.",
    source_url: "#",
    relevance: 86,
    citations: 31,
  }
];

export const DEMO_POLICIES: PolicyDocument[] = [
  {
    id: "pol-1",
    title: "Bhopal Master Plan 2031 (Draft Land Use Regulations)",
    department: "Urban Development & Housing Department (UDHD), MP",
    year: 2023,
    region: "Bhopal Metropolitan Area",
    description: "Statutory land use zoning guidelines outlining designated green belts, residential density caps, and commercial activity zones.",
    status: "Under Evaluation",
    sector: "Urban Planning"
  },
  {
    id: "pol-2",
    title: "Madhya Pradesh Land Revenue Code (Amendment) Act 2022",
    department: "Department of Revenue, Govt. of MP",
    year: 2022,
    region: "Madhya Pradesh",
    description: "Streamlined automated diversion of agricultural land for commercial/industrial purposes through digital portals.",
    status: "Active",
    sector: "Land Administration"
  },
  {
    id: "pol-3",
    title: "National Land Use Policy Framework (NLUP)",
    department: "Ministry of Rural Development, Govt. of India",
    year: 2021,
    region: "National",
    description: "National guidelines recommending protection of prime agricultural lands and optimizing non-arable lands for infrastructure.",
    status: "Active",
    sector: "National Policy"
  },
  {
    id: "pol-4",
    title: "State Wetland Conservation & Buffer Zone Guidelines",
    department: "State Wetland Authority & EPCO",
    year: 2023,
    region: "Madhya Pradesh",
    description: "Mandatory 500m construction-free buffer protection zones surrounding notified wetlands including Bhoj Wetland.",
    status: "Active",
    sector: "Ecology & Conservation"
  },
  {
    id: "pol-5",
    title: "MP Industrial Promotion Policy 2021 (Land Allocation Guidelines)",
    department: "Department of Industrial Policy & Investment Promotion",
    year: 2021,
    region: "Madhya Pradesh",
    description: "Concessional land lease terms and fast-track clearance for industrial parks along expressways.",
    status: "Active",
    sector: "Industry & Economy"
  },
  {
    id: "pol-6",
    title: "SVAMITVA Scheme Guidelines (Survey of Villages and Mapping with Improvised Technology)",
    department: "Ministry of Panchayati Raj, Govt. of India",
    year: 2020,
    region: "National",
    description: "Integrated drone survey and property card distribution framework for rural inhabited (Abadi) parcels.",
    status: "Active",
    sector: "Cadastral Mapping"
  },
  {
    id: "pol-7",
    title: "Bhopal Transit-Oriented Development (TOD) Policy",
    department: "Madhya Pradesh Metro Rail Corporation Limited",
    year: 2024,
    region: "Bhopal Metro Corridors",
    description: "High-density, mixed-use zoning within 500m of operational metro stations (Orange & Blue lines).",
    status: "Draft",
    sector: "Urban Planning"
  },
  {
    id: "pol-8",
    title: "Madhya Pradesh State Action Plan on Climate Change (SAPCC 2.0)",
    department: "Environment Department, Govt. of MP",
    year: 2023,
    region: "Madhya Pradesh",
    description: "Land use resilience targets, heat mitigation, and agro-forestry expansion across climate-vulnerable districts.",
    status: "Active",
    sector: "Climate Policy"
  },
  {
    id: "pol-9",
    title: "Guidelines for Agricultural Land Acquisition for Renewable Solar Parks",
    department: "New and Renewable Energy Department, MP",
    year: 2024,
    region: "Madhya Pradesh",
    description: "Regulates priority leasing of fallow/wastelands over double-cropped irrigated holdings for mega-solar installations.",
    status: "Active",
    sector: "Energy & Infrastructure"
  },
  {
    id: "pol-10",
    title: "Model Tenancy Act & State Agricultural Land Leasing Guidelines",
    department: "Department of Agriculture & Farmers Welfare, Govt. of India",
    year: 2022,
    region: "National",
    description: "Security of tenure for tenant cultivators and streamlined land lease agreements without ownership compromise.",
    status: "Under Evaluation",
    sector: "Agriculture & Tenancy"
  }
];

export const DEMO_DATASETS: DatasetItem[] = [
  {
    id: "ds-1",
    name: "Bhopal Metropolitan Land Use & Land Cover (LULC) 2025",
    organization: "Remote Sensing Applications Centre (RSAC) MP",
    category: "Geospatial",
    geographic_coverage: "Bhopal District (2,772 sq km)",
    year: 2025,
    format: "GeoJSON / GeoTIFF",
    license: "Open Govt Data (OGD) India",
    last_updated: "2025-11-15",
    size: "240 MB",
    rows: 14520,
    description: "10m Sentinel-2 derived 5-class LULC classification encompassing built-up, agriculture, water bodies, scrub, and forest."
  },
  {
    id: "ds-2",
    name: "Madhya Pradesh Cadastral Parcel Boundaries (Vector Layer)",
    organization: "Department of Land Records (Bhu-Abhilekh) MP",
    category: "Cadastral",
    geographic_coverage: "Madhya Pradesh (52 Districts)",
    year: 2024,
    format: "GeoJSON / Shapefile",
    license: "Restricted Government Research",
    last_updated: "2024-12-01",
    size: "1.8 GB",
    rows: 485000,
    description: "Vectorized Khasra parcel boundaries aligned with revenue village settlement maps."
  },
  {
    id: "ds-3",
    name: "Central India Groundwater Depth & Stress Index 2020-2025",
    organization: "Central Ground Water Board (CGWB)",
    category: "Hydrology",
    geographic_coverage: "Madhya Pradesh & Regional Basins",
    year: 2025,
    format: "CSV / Shapefile",
    license: "Creative Commons CC-BY 4.0",
    last_updated: "2025-08-20",
    size: "48 MB",
    rows: 12400,
    description: "Bimonthly groundwater table measurements, extraction ratios, and critical over-exploited blocks classification."
  },
  {
    id: "ds-4",
    name: "Bhopal Master Plan 2031 Proposed Zoning Boundary GeoJSON",
    organization: "Directorate of Town & Country Planning (T&CP) MP",
    category: "Urban Planning",
    geographic_coverage: "Bhopal Planning Area",
    year: 2023,
    format: "GeoJSON",
    license: "Public Domain / T&CP",
    last_updated: "2023-09-10",
    size: "32 MB",
    rows: 3200,
    description: "Proposed land use zoning polygons comprising residential, commercial, industrial, PSP, and green retention buffers."
  },
  {
    id: "ds-5",
    name: "District-Wise Climate Risk & Vulnerability Index",
    organization: "National Institute of Disaster Management (NIDM)",
    category: "Climate Risk",
    geographic_coverage: "Pan India (750 Districts)",
    year: 2024,
    format: "CSV / JSON",
    license: "Open Govt Data (OGD)",
    last_updated: "2024-06-15",
    size: "18 MB",
    rows: 750,
    description: "Composite vulnerability index synthesizing drought hazard, flood susceptibility, extreme heat exposure, and adaptive capacity."
  },
  {
    id: "ds-6",
    name: "Bhopal Metro Rail Phase-1 Influence Corridor (500m Buffer)",
    organization: "Madhya Pradesh Metro Rail Corporation Limited",
    category: "Infrastructure",
    geographic_coverage: "Bhopal Urban Alignment (27.87 km)",
    year: 2024,
    format: "GeoJSON",
    license: "Govt Research License",
    last_updated: "2024-10-05",
    size: "12 MB",
    rows: 450,
    description: "TOD zone demarcating 500m buffer circles and parcel redevelopment zones around stations."
  },
  {
    id: "ds-7",
    name: "Bhoj Wetland Catchment Hydrological Flow & Drainage Network",
    organization: "Environmental Planning & Coordination Org (EPCO)",
    category: "Hydrology & Environment",
    geographic_coverage: "Bhopal Upper Lake Catchment (361 sq km)",
    year: 2024,
    format: "Shapefile / GeoJSON",
    license: "Academic / Policy Research Only",
    last_updated: "2024-04-12",
    size: "85 MB",
    rows: 8900,
    description: "Micro-watershed boundaries, natural drainage channels, wetland high flood levels (HFL), and eco-sensitive contour buffers."
  },
  {
    id: "ds-8",
    name: "Urban Population Growth Projections 2021-2036 (Tier-1 & Tier-2)",
    organization: "Office of the Registrar General & Census Commissioner",
    category: "Demographics",
    geographic_coverage: "National / District Aggregates",
    year: 2023,
    format: "CSV / JSON",
    license: "Open Govt Data",
    last_updated: "2023-03-25",
    size: "6 MB",
    rows: 1500,
    description: "Decadal urban-rural population forecasts, migration estimates, and household density metrics."
  },
  {
    id: "ds-9",
    name: "Road Infrastructure & Highway Network Density (GIS Vector)",
    organization: "Madhya Pradesh Road Development Corporation (MPRDC)",
    category: "Infrastructure",
    geographic_coverage: "Madhya Pradesh",
    year: 2024,
    format: "GeoJSON",
    license: "Govt Research License",
    last_updated: "2024-07-30",
    size: "110 MB",
    rows: 23000,
    description: "National Highways, State Highways, Major District Roads, and Proposed Outer Ring Road spatial centerlines."
  },
  {
    id: "ds-10",
    name: "Agricultural Soil Fertility and Soil Health Card Spatial Matrix",
    organization: "Dept of Farmer Welfare & Agriculture Development MP",
    category: "Agriculture",
    geographic_coverage: "Central MP Agro-Climatic Zones",
    year: 2024,
    format: "CSV / GeoJSON",
    license: "Govt Research License",
    last_updated: "2024-05-18",
    size: "34 MB",
    rows: 6200,
    description: "Nitrogen, phosphorus, potassium, organic carbon index, and prime agricultural classification."
  },
  {
    id: "ds-11",
    name: "State Industrial Area Land Bank Allotment & Vacancy Records",
    organization: "MP Industrial Development Corporation (MPIDC)",
    category: "Industrial",
    geographic_coverage: "MP Industrial Parks",
    year: 2025,
    format: "JSON",
    license: "OGD India",
    last_updated: "2025-01-10",
    size: "9 MB",
    rows: 1400,
    description: "Industrial land plots, allotted vs available land hectarage, and active operational status."
  },
  {
    id: "ds-12",
    name: "Satellite Surface Temperature and Heat Stress Index",
    organization: "National Remote Sensing Centre (NRSC / ISRO)",
    category: "Climate & Environment",
    geographic_coverage: "Central India Agglomerations",
    year: 2024,
    format: "GeoTIFF / GeoJSON",
    license: "Open Data ISRO Bhuvan",
    last_updated: "2024-06-28",
    size: "175 MB",
    rows: 9400,
    description: "Summer land surface temperature anomalies, thermal emissivity, and canopy cooling deficit."
  }
];

export const DEMO_GIS_DISTRICTS: GISDistrict[] = [
  {
    id: "bhopal-dist",
    name: "Bhopal District",
    coordinates: [23.2599, 77.4126],
    population: "2.4M",
    urbanization: "68%",
    ag_land: "41%",
    climate_risk: "Medium",
    urban_expansion: "High",
    infra_pressure: "Medium",
    primary_growth_corridors: ["Kolar Road", "Hoshangabad Road (NH-46)", "Raisen Road", "Bairagarh Airport Bypass"]
  },
  {
    id: "indore-dist",
    name: "Indore District",
    coordinates: [22.7196, 75.8577],
    population: "3.3M",
    urbanization: "79%",
    ag_land: "34%",
    climate_risk: "Medium-High",
    urban_expansion: "Very High",
    infra_pressure: "High",
    primary_growth_corridors: ["Super Corridor", "AB Road Bypass", "Pithampur Link"]
  },
  {
    id: "delhi-ncr",
    name: "National Capital Region (NCR)",
    coordinates: [28.6139, 77.2090],
    population: "21.5M",
    urbanization: "93%",
    ag_land: "12%",
    climate_risk: "High",
    urban_expansion: "Severe",
    infra_pressure: "Very High",
    primary_growth_corridors: ["Dwarka Expressway", "Faridabad Bypass", "Kundli-Manesar"]
  },
  {
    id: "ahmedabad-dist",
    name: "Ahmedabad District",
    coordinates: [23.0225, 72.5714],
    population: "8.4M",
    urbanization: "84%",
    ag_land: "28%",
    climate_risk: "High",
    urban_expansion: "High",
    infra_pressure: "High",
    primary_growth_corridors: ["SG Highway", "Sanand Industrial Link", "Dholera Expressway"]
  },
  {
    id: "bengaluru-dist",
    name: "Bengaluru Urban",
    coordinates: [12.9716, 77.5946],
    population: "13.1M",
    urbanization: "91%",
    ag_land: "15%",
    climate_risk: "Medium",
    urban_expansion: "Severe",
    infra_pressure: "Very High",
    primary_growth_corridors: ["Outer Ring Road", "Bellary Road", "Sarjapur Road"]
  }
];

export const PREVIOUS_SIMULATIONS: SimulationResult[] = [
  {
    id: "SIM-BHP-001",
    scenario_name: "Bhopal Master Plan 2031 Base Projection",
    region: "Bhopal",
    timestamp: "2026-03-12 14:30:00",
    inputs: {
      scenario_name: "Bhopal Master Plan 2031 Base Projection",
      region: "Bhopal",
      ag_conversion_pct: 10,
      population_growth_pct: 15,
      infrastructure_growth_pct: 20,
      climate_risk: "Medium"
    },
    land_use_impact: {
      "Agricultural Land": -8.4,
      "Residential Area": 11.2,
      "Industrial Area": 5.6,
      "Forest Buffer": -4.6,
      "Water Body Retention": -3.6
    },
    environmental_indicators: {
      "Water Stress": 6.8,
      "Green Cover Pressure": 4.2,
      "Climate Exposure": 7.1,
      "Carbon Sink Deficit": 7.6
    },
    infrastructure_impact: {
      "Road Demand": 12.0,
      "Public Service Demand": 9.0,
      "Sewerage Network Pressure": 10.5,
      "Grid Power Demand": 13.0
    },
    affected_zones: ["Kolar Peri-Urban Fringe", "Mandideep Corridor", "Bairagarh Bypass", "Upper Lake Buffer"],
    disclaimer: "Scenario-based estimates generated from available research data and mathematical model assumptions.",
    model_assumptions: ["Linear conversion elasticity 0.72", "Medium climate vulnerability index", "5-year horizon"]
  },
  {
    id: "SIM-BHP-002",
    scenario_name: "Conservative Agricultural Protection (5% Conversion)",
    region: "Bhopal",
    timestamp: "2026-03-14 11:15:00",
    inputs: {
      scenario_name: "Conservative Agricultural Protection (5% Conversion)",
      region: "Bhopal",
      ag_conversion_pct: 5,
      population_growth_pct: 12,
      infrastructure_growth_pct: 15,
      climate_risk: "Low"
    },
    land_use_impact: {
      "Agricultural Land": -4.2,
      "Residential Area": 6.9,
      "Industrial Area": 3.9,
      "Forest Buffer": -3.0,
      "Water Body Retention": -1.9
    },
    environmental_indicators: {
      "Water Stress": 3.8,
      "Green Cover Pressure": 2.5,
      "Climate Exposure": 3.6,
      "Carbon Sink Deficit": 4.4
    },
    infrastructure_impact: {
      "Road Demand": 8.5,
      "Public Service Demand": 6.8,
      "Sewerage Network Pressure": 7.8,
      "Grid Power Demand": 9.2
    },
    affected_zones: ["Mandideep Fringe", "Berasia Road Corridor"],
    disclaimer: "Scenario-based estimates generated from available research data and mathematical model assumptions.",
    model_assumptions: ["Protection overlay applied", "Low climate vulnerability", "5-year horizon"]
  },
  {
    id: "SIM-BHP-003",
    scenario_name: "Rapid Urbanization & Expressway Corridor (20% Conversion)",
    region: "Bhopal",
    timestamp: "2026-03-15 16:45:00",
    inputs: {
      scenario_name: "Rapid Urbanization & Expressway Corridor (20% Conversion)",
      region: "Bhopal",
      ag_conversion_pct: 20,
      population_growth_pct: 25,
      infrastructure_growth_pct: 30,
      climate_risk: "High"
    },
    land_use_impact: {
      "Agricultural Land": -16.8,
      "Residential Area": 21.4,
      "Industrial Area": 9.0,
      "Forest Buffer": -7.8,
      "Water Body Retention": -7.5
    },
    environmental_indicators: {
      "Water Stress": 15.6,
      "Green Cover Pressure": 9.8,
      "Climate Exposure": 14.5,
      "Carbon Sink Deficit": 14.2
    },
    infrastructure_impact: {
      "Road Demand": 20.4,
      "Public Service Demand": 15.4,
      "Sewerage Network Pressure": 18.1,
      "Grid Power Demand": 20.6
    },
    affected_zones: ["Kolar Fringe", "Mandideep Corridor", "Outer Ring Road 3km Belt", "Upper Lake Watershed"],
    disclaimer: "Scenario-based estimates generated from available research data and mathematical model assumptions.",
    model_assumptions: ["Unregulated conversion trajectory", "High climate vulnerability", "5-year horizon"]
  }
];

export const DEMO_NOTIFICATIONS: NotificationItem[] = [
  {
    id: "notif-1",
    title: "New Research Paper Added",
    message: "New empirical study 'Urban Expansion and Agricultural Land Conversion in Bhopal Fringe Areas' added to Urban Planning.",
    timestamp: "10 mins ago",
    type: "research",
    read: false
  },
  {
    id: "notif-2",
    title: "Policy Simulation Completed",
    message: "Simulation SIM-BHP-001 for Bhopal Urban Land Conversion completed with 5 key indicators calculated.",
    timestamp: "45 mins ago",
    type: "simulation",
    read: false
  },
  {
    id: "notif-3",
    title: "GIS Layer Updated",
    message: "Bhopal Metropolitan Land Use & Land Cover (LULC) 2025 Sentinel-2 vector layer updated.",
    timestamp: "2 hours ago",
    type: "dataset",
    read: true
  },
  {
    id: "notif-4",
    title: "Research Project Invitation",
    message: "Dr. A. Pathak invited you to collaborate on 'Bhopal Urban Expansion Study'.",
    timestamp: "3 hours ago",
    type: "project",
    read: true
  },
  {
    id: "notif-5",
    title: "SVAMITVA Drone Survey Sync",
    message: "New cadastral boundaries synchronized for 42 peri-urban revenue villages in Sehore and Bhopal.",
    timestamp: "1 day ago",
    type: "system",
    read: true
  }
];

export const DEMO_WORKSPACE_PROJECT: ProjectWorkspaceItem = {
  id: "proj-1",
  title: "Bhopal Urban Expansion & Agricultural Land Protection Study",
  region: "Bhopal Metropolitan Region",
  lead: "Dr. K. Sharma",
  members: ["Dr. K. Sharma (Policymaker)", "Dr. A. Pathak (Researcher)", "P. Iyer (GIS Analyst)", "Adv. S. Mishra (Legal)"],
  status: "Active",
  progress: 72,
  description: "Cross-institutional investigation into fringe land conversion rates, Upper Lake hydrological protection, and 2031 Master Plan alignment.",
  tasks: [
    { id: "t-1", title: "Analyze 2015-2024 Sentinel-2 LULC transitions across Kolar corridor", assignee: "P. Iyer", completed: true },
    { id: "t-2", title: "Synthesize piezometric borehole data from CGWB for Upper Lake catchment", assignee: "Dr. A. Pathak", completed: true },
    { id: "t-3", title: "Run Policy Simulator for 10% vs 20% agricultural conversion scenarios", assignee: "Dr. K. Sharma", completed: false },
    { id: "t-4", title: "Draft final evidence brief for Cabinet Sub-Committee on Land Governance", assignee: "Team", completed: false }
  ],
  comments: [
    { author: "P. Iyer", time: "2 hours ago", text: "Completed the 10m LULC raster reconciliation. Noticing severe Kolar Road cluster encroachment on Class-II agricultural parcels." },
    { author: "Dr. Sharma", time: "1 hour ago", text: "Excellent. We will simulate a 10% vs 20% agricultural conversion scenario in the simulator to evaluate water stress index before Tuesday's briefing." },
    { author: "Dr. A. Pathak", time: "30 mins ago", text: "I have uploaded the Upper Lake vulnerability dataset (ds-7) to the workspace for spatial overlay." }
  ]
};
