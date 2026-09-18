"""
BHUMI INSIGHT — FastAPI Backend
National Digital Platform for Research, Policy Innovation, and Evidence-Based Land Governance
Smart India Hackathon 2026 — PS26019
"""

import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="BHUMI INSIGHT API",
    description="AI-Powered Land-Governance Research & Decision-Intelligence Platform API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# DATA MODELS
# ---------------------------------------------------------
class ResearchPaper(BaseModel):
    id: str
    title: str
    authors: str
    organization: str
    year: int
    region: str
    topic: str
    abstract: str
    source_url: str = "#"
    relevance: int = 92
    citations: int = 24

class PolicyDocument(BaseModel):
    id: str
    title: str
    department: str
    year: int
    region: str
    description: str
    status: str  # Active, Under Evaluation, Draft, Archived
    sector: str

class Dataset(BaseModel):
    id: str
    name: str
    organization: str
    category: str
    geographic_coverage: str
    year: int
    format: str
    license: str
    last_updated: str
    size: str
    rows: int
    description: str

class SimulationInput(BaseModel):
    scenario_name: str = "Urban Land Conversion Scenario"
    region: str = "Bhopal"
    ag_conversion_pct: float = Field(10.0, ge=0.0, le=50.0)
    population_growth_pct: float = Field(15.0, ge=0.0, le=50.0)
    infrastructure_growth_pct: float = Field(20.0, ge=0.0, le=50.0)
    climate_risk: str = "Medium"  # Low, Medium, High

class SimulationResult(BaseModel):
    id: str
    scenario_name: str
    region: str
    timestamp: str
    inputs: SimulationInput
    land_use_impact: Dict[str, float]
    environmental_indicators: Dict[str, float]
    infrastructure_impact: Dict[str, float]
    affected_zones: List[str]
    disclaimer: str
    model_assumptions: List[str]

class AISearchQuery(BaseModel):
    query: str
    region: Optional[str] = None
    topic: Optional[str] = None

class AISearchResponse(BaseModel):
    query: str
    answer: str
    key_drivers: List[str]
    policy_implications: List[str]
    sources_used: List[ResearchPaper]
    confidence_score: float

class DocumentAnalysisRequest(BaseModel):
    filename: str
    file_type: str = "pdf"
    content_mock: Optional[str] = None

class DocumentAnalysisResponse(BaseModel):
    filename: str
    document_summary: str
    key_findings: List[str]
    methodology: str
    research_gaps: List[str]
    relevant_policies: List[str]
    related_studies: List[str]
    confidence: float

class ReportGenerateRequest(BaseModel):
    title: str = "Bhopal Urban Land Governance Assessment"
    region: str = "Bhopal"
    include_gis: bool = True
    include_research: bool = True
    include_climate: bool = True
    include_simulation: bool = True
    include_comparison: bool = True

class UserProfile(BaseModel):
    id: str
    name: str
    email: str
    role: str
    organization: str
    status: str
    last_active: str

# ---------------------------------------------------------
# MOCK DATABASE
# ---------------------------------------------------------
RESEARCH_PAPERS: List[ResearchPaper] = [
    ResearchPaper(
        id="rp-1",
        title="Urban Expansion and Agricultural Land Conversion in Bhopal Fringe Areas",
        authors="Dr. K. Sharma, Dr. R. Verma, S. Nair",
        organization="Maulana Azad National Institute of Technology (MANIT)",
        year=2024,
        region="Bhopal, Madhya Pradesh",
        topic="Urban Expansion",
        abstract="Satellite telemetry from 2015 to 2023 demonstrates that peri-urban agricultural zones in Kolar, Mandideep, and Bairagarh fringes have undergone 14.8% conversion to non-agricultural uses, primarily driven by arterial transport corridors.",
        relevance=96,
        citations=48,
    ),
    ResearchPaper(
        id="rp-2",
        title="Climate Resilient Land Use Planning: Upper Lake Catchment Vulnerability Assessment",
        authors="Dr. A. Pathak, M. Choudhary",
        organization="Indian Institute of Forest Management (IIFM)",
        year=2025,
        region="Bhopal, Madhya Pradesh",
        topic="Climate & Ecology",
        abstract="Quantifies the hydrological runoff and water stress index across Bhoj Wetland buffer zones subject to residential encroachment, offering spatial zoning models for retention basins.",
        relevance=94,
        citations=32,
    ),
    ResearchPaper(
        id="rp-3",
        title="GIS-Based Urban Growth Simulation and Predictive Cadastral Modeling",
        authors="P. Iyer, T. Sengupta",
        organization="Centre for Spatial Studies & Geospatial Survey of India",
        year=2023,
        region="Madhya Pradesh",
        topic="GIS & Simulation",
        abstract="Multi-temporal Landsat 8 and Sentinel-2 imagery analysis revealing cellular automata land transition probabilities across Tier-2 Indian urban agglomerations.",
        relevance=91,
        citations=64,
    ),
    ResearchPaper(
        id="rp-4",
        title="Institutional Land Governance and Fragmented Peri-Urban Titles in Central India",
        authors="Adv. S. Mishra, Dr. N. Rao",
        organization="National Law Institute University (NLIU) Bhopal",
        year=2024,
        region="Madhya Pradesh",
        topic="Legal & Governance",
        abstract="Examines legal titling disputes arising from agricultural tenancy conversions under the MP Land Revenue Code, with recommendations for digital boundary reconciliation.",
        relevance=88,
        citations=19,
    ),
    ResearchPaper(
        id="rp-5",
        title="Groundwater Depletion Correlation with Impervious Surface Expansion in Indore-Bhopal Corridor",
        authors="R. Sen, K. Mukherjee",
        organization="Central Ground Water Board (CGWB) & MANIT",
        year=2024,
        region="Indore-Bhopal Corridor",
        topic="Hydrology & Environment",
        abstract="Analyzes 10-year piezometric borehole data juxtaposed against built-up footprint expansion along the SH-18 economic corridor.",
        relevance=89,
        citations=27,
    ),
    ResearchPaper(
        id="rp-6",
        title="Socio-Economic Impacts of Agricultural Land Reallocation on Smallholder Livelihoods",
        authors="Dr. B. Das, P. Patel",
        organization="Tata Institute of Social Sciences (TISS)",
        year=2023,
        region="Central India",
        topic="Socio-Economic",
        abstract="Survey of 450 peri-urban households in Sehore and Raisen evaluating income vulnerability following transition from agrarian to casual urban employment.",
        relevance=85,
        citations=38,
    ),
    ResearchPaper(
        id="rp-7",
        title="Monitoring Urban Heat Island Intensification in Rapidly Developing Smart Cities",
        authors="V. Gokhale, S. Trivedi",
        organization="IIT Indore & Remote Sensing Applications Centre (RSAC)",
        year=2025,
        region="Indore, Madhya Pradesh",
        topic="Climate & Ecology",
        abstract="MODIS surface temperature analysis establishing a 2.8°C thermal differential between urban core and peripheral agricultural zones during summer peak months.",
        relevance=87,
        citations=15,
    ),
    ResearchPaper(
        id="rp-8",
        title="Cadastral Boundary Reconciliation Utilizing High-Resolution UAV Drones",
        authors="A. Joshi, K. Sundaram",
        organization="Survey of India & SVAMITVA Technical Unit",
        year=2024,
        region="Madhya Pradesh",
        topic="GIS & Simulation",
        abstract="Evaluation of orthorectified imagery accuracy within pilot villages under SVAMITVA scheme, achieving <5cm positional horizontal accuracy for parcel demarcation.",
        relevance=92,
        citations=51,
    ),
    ResearchPaper(
        id="rp-9",
        title="Industrial Land Demand Projection along Delhi-Mumbai Industrial Corridor (DMIC)",
        authors="National Industrial Corridor Development Corporation (NICDC)",
        organization="NICDC & NITI Aayog Research Cell",
        year=2024,
        region="National / MP Node",
        topic="Infrastructure",
        abstract="Econometric forecast of non-agricultural conversion demands for logistic nodes and ancillary manufacturing zones in Pithampur and Mandideep.",
        relevance=84,
        citations=22,
    ),
    ResearchPaper(
        id="rp-10",
        title="Forest Fringe Dynamics and Wildlife Corridor Encroachment in Central Highlands",
        authors="Wildlife Institute of India (WII) & State Forest Research Institute",
        organization="WII Dehradun",
        year=2023,
        region="Madhya Pradesh",
        topic="Forest & Conservation",
        abstract="Spatial fragmentation metrics around Ratapani Wildlife Sanctuary illustrating the encroachment pressures induced by peripheral township expansion.",
        relevance=86,
        citations=34,
    ),
    ResearchPaper(
        id="rp-11",
        title="Digital Land Records Modernization: Empirical Evaluation of DILRMP in Central India",
        authors="Dr. H. Agrawal, R. N. Tiwari",
        organization="Administrative Staff College of India (ASCI)",
        year=2024,
        region="Madhya Pradesh",
        topic="Legal & Governance",
        abstract="Audit of 52 district land registries assessing registration turnaround times, mutation backlog, and public grievance resolution post-digitization.",
        relevance=90,
        citations=42,
    ),
    ResearchPaper(
        id="rp-12",
        title="Infrastructure Spillover Effects on Peri-Urban Real Estate Speculation",
        authors="Prof. D. Chawla, A. Singhal",
        organization="School of Planning and Architecture (SPA) Bhopal",
        year=2025,
        region="Bhopal Fringe",
        topic="Urban Expansion",
        abstract="Hedonic price modeling demonstrating land value escalation within a 3km buffer of the newly planned Bhopal Outer Ring Road.",
        relevance=93,
        citations=17,
    ),
    ResearchPaper(
        id="rp-13",
        title="Wetland Preservation and Master Plan Integration: A Decadal Review of Bhoj Ramsar Site",
        authors="Bhopal Municipal Corporation & Environmental Planning & Coordination Org (EPCO)",
        organization="EPCO Madhya Pradesh",
        year=2023,
        region="Bhopal, Madhya Pradesh",
        topic="Climate & Ecology",
        abstract="Comprehensive review of the 2005 Master Plan environmental buffers versus ground reality, proposing dynamic GIS alert overlays for civic enforcement.",
        relevance=91,
        citations=29,
    ),
    ResearchPaper(
        id="rp-14",
        title="Agro-Ecological Zoning Using Multi-Criteria Decision Analysis (MCDA) in Sehore",
        authors="Indian Council of Agricultural Research (ICAR-CIAE)",
        organization="ICAR Bhopal",
        year=2024,
        region="Madhya Pradesh",
        topic="Socio-Economic",
        abstract="AHP-weighted spatial GIS model categorizing prime fertile soils to be safeguarded from compulsory urban acquisition.",
        relevance=88,
        citations=20,
    ),
    ResearchPaper(
        id="rp-15",
        title="Disaster Risk Governance: Urban Inundation Modeling for Tier-2 River Basins",
        authors="National Institute of Disaster Management (NIDM)",
        organization="NIDM New Delhi",
        year=2025,
        region="Central India",
        topic="Climate & Ecology",
        abstract="Hydrodynamic modeling of sudden extreme rainfall events across altered urban topography with compromised natural drainage channels.",
        relevance=86,
        citations=31,
    )
]

POLICIES: List[PolicyDocument] = [
    PolicyDocument(
        id="pol-1",
        title="Bhopal Master Plan 2031 (Draft Land Use Regulations)",
        department="Urban Development & Housing Department (UDHD), MP",
        year=2023,
        region="Bhopal Metropolitan Area",
        description="Statutory land use zoning guidelines outlining designated green belts, residential density caps, and commercial activity zones.",
        status="Under Evaluation",
        sector="Urban Planning"
    ),
    PolicyDocument(
        id="pol-2",
        title="Madhya Pradesh Land Revenue Code (Amendment) Act 2022",
        department="Department of Revenue, Govt. of MP",
        year=2022,
        region="Madhya Pradesh",
        description="Streamlined automated diversion of agricultural land for commercial/industrial purposes through digital portals.",
        status="Active",
        sector="Land Administration"
    ),
    PolicyDocument(
        id="pol-3",
        title="National Land Use Policy Framework (NLUP)",
        department="Ministry of Rural Development, Govt. of India",
        year=2021,
        region="National",
        description="National guidelines recommending protection of prime agricultural lands and optimizing non-arable lands for infrastructure.",
        status="Active",
        sector="National Policy"
    ),
    PolicyDocument(
        id="pol-4",
        title="State Wetland Conservation & Buffer Zone Guidelines",
        department="State Wetland Authority & EPCO",
        year=2023,
        region="Madhya Pradesh",
        description="Mandatory 500m construction-free buffer protection zones surrounding notified wetlands including Bhoj Wetland.",
        status="Active",
        sector="Ecology & Conservation"
    ),
    PolicyDocument(
        id="pol-5",
        title="MP Industrial Promotion Policy 2021 (Land Allocation Guidelines)",
        department="Department of Industrial Policy & Investment Promotion",
        year=2021,
        region="Madhya Pradesh",
        description="Concessional land lease terms and fast-track clearance for industrial parks along expressways.",
        status="Active",
        sector="Industry & Economy"
    ),
    PolicyDocument(
        id="pol-6",
        title="SVAMITVA Scheme Guidelines (Survey of Villages and Mapping with Improvised Technology)",
        department="Ministry of Panchayati Raj, Govt. of India",
        year=2020,
        region="National",
        description="Integrated drone survey and property card distribution framework for rural inhabited (Abadi) parcels.",
        status="Active",
        sector="Cadastral Mapping"
    ),
    PolicyDocument(
        id="pol-7",
        title="Bhopal Transit-Oriented Development (TOD) Policy",
        department="Madhya Pradesh Metro Rail Corporation Limited",
        year=2024,
        region="Bhopal Metro Corridors",
        description="High-density, mixed-use zoning within 500m of operational metro stations (Orange & Blue lines).",
        status="Draft",
        sector="Urban Planning"
    ),
    PolicyDocument(
        id="pol-8",
        title="Madhya Pradesh State Action Plan on Climate Change (SAPCC 2.0)",
        department="Environment Department, Govt. of MP",
        year=2023,
        region="Madhya Pradesh",
        description="Land use resilience targets, heat mitigation, and agro-forestry expansion across climate-vulnerable districts.",
        status="Active",
        sector="Climate Policy"
    ),
    PolicyDocument(
        id="pol-9",
        title="Guidelines for Agricultural Land Acquisition for Renewable Solar Parks",
        department="New and Renewable Energy Department, MP",
        year=2024,
        region="Madhya Pradesh",
        description="Regulates priority leasing of fallow/wastelands over double-cropped irrigated holdings for mega-solar installations.",
        status="Active",
        sector="Energy & Infrastructure"
    ),
    PolicyDocument(
        id="pol-10",
        title="Model Tenancy Act & State Agricultural Land Leasing Guidelines",
        department="Department of Agriculture & Farmers Welfare, Govt. of India",
        year=2022,
        region="National",
        description="Security of tenure for tenant cultivators and streamlined land lease agreements without ownership compromise.",
        status="Under Evaluation",
        sector="Agriculture & Tenancy"
    )
]

DATASETS: List[Dataset] = [
    Dataset(
        id="ds-1",
        name="Bhopal Metropolitan Land Use & Land Cover (LULC) 2025",
        organization="Remote Sensing Applications Centre (RSAC) MP",
        category="Geospatial",
        geographic_coverage="Bhopal District (2,772 sq km)",
        year=2025,
        format="GeoJSON / GeoTIFF",
        license="Open Govt Data (OGD) India",
        last_updated="2025-11-15",
        size="240 MB",
        rows=14520,
        description="10m Sentinel-2 derived 5-class LULC classification encompassing built-up, agriculture, water bodies, scrub, and forest.",
    ),
    Dataset(
        id="ds-2",
        name="Madhya Pradesh Cadastral Parcel Boundaries (Vector Layer)",
        organization="Department of Land Records (Bhu-Abhilekh) MP",
        category="Cadastral",
        geographic_coverage="Madhya Pradesh (52 Districts)",
        year=2024,
        format="GeoJSON / Shapefile",
        license="Restricted Government Research",
        last_updated="2024-12-01",
        size="1.8 GB",
        rows=485000,
        description="Vectorized Khasra parcel boundaries aligned with revenue village village settlement maps.",
    ),
    Dataset(
        id="ds-3",
        name="Central India Groundwater Depth & Stress Index 2020-2025",
        organization="Central Ground Water Board (CGWB)",
        category="Hydrology",
        geographic_coverage="Madhya Pradesh & Regional Basins",
        year=2025,
        format="CSV / Shapefile",
        license="Creative Commons CC-BY 4.0",
        last_updated="2025-08-20",
        size="48 MB",
        rows=12400,
        description="Bimonthly groundwater table measurements, extraction ratios, and critical over-exploited blocks classification.",
    ),
    Dataset(
        id="ds-4",
        name="Bhopal Master Plan 2031 Proposed Zoning Boundary GeoJSON",
        organization="Directorate of Town & Country Planning (T&CP) MP",
        category="Urban Planning",
        geographic_coverage="Bhopal Planning Area",
        year=2023,
        format="GeoJSON",
        license="Public Domain / T&CP",
        last_updated="2023-09-10",
        size="32 MB",
        rows=3200,
        description="Proposed land use zoning polygons comprising residential, commercial, industrial, PSP, and green retention buffers.",
    ),
    Dataset(
        id="ds-5",
        name="District-Wise Climate Risk & Vulnerability Index",
        organization="National Institute of Disaster Management (NIDM)",
        category="Climate Risk",
        geographic_coverage="Pan India (750 Districts)",
        year=2024,
        format="CSV / JSON",
        license="Open Govt Data (OGD)",
        last_updated="2024-06-15",
        size="18 MB",
        rows=750,
        description="Composite vulnerability index synthesizing drought hazard, flood susceptibility, extreme heat exposure, and adaptive capacity.",
    ),
    Dataset(
        id="ds-6",
        name="Bhopal Metro Rail Phase-1 Influence Corridor (500m Buffer)",
        organization="Madhya Pradesh Metro Rail Corporation Limited",
        category="Infrastructure",
        geographic_coverage="Bhopal Urban Alignment (27.87 km)",
        year=2024,
        format="GeoJSON",
        license="Govt Research License",
        last_updated="2024-10-05",
        size="12 MB",
        rows=450,
        description="TOD zone demarcating 500m buffer circles and parcel redevelopment zones around stations.",
    ),
    Dataset(
        id="ds-7",
        name="Bhoj Wetland Catchment Hydrological Flow & Drainage Network",
        organization="Environmental Planning & Coordination Org (EPCO)",
        category="Hydrology & Environment",
        geographic_coverage="Bhopal Upper Lake Catchment (361 sq km)",
        year=2024,
        format="Shapefile / GeoJSON",
        license="Academic / Policy Research Only",
        last_updated="2024-04-12",
        size="85 MB",
        rows=8900,
        description="Micro-watershed boundaries, natural drainage channels, wetland high flood levels (HFL), and eco-sensitive contour buffers.",
    ),
    Dataset(
        id="ds-8",
        name="Urban Population Growth Projections 2021-2036 (Tier-1 & Tier-2)",
        organization="Office of the Registrar General & Census Commissioner",
        category="Demographics",
        geographic_coverage="National / District Aggregates",
        year=2023,
        format="CSV / JSON",
        license="Open Govt Data",
        last_updated="2023-03-25",
        size="6 MB",
        rows=1500,
        description="Decadal urban-rural population forecasts, migration estimates, and household density metrics.",
    ),
    Dataset(
        id="ds-9",
        name="Road Infrastructure & Highway Network Density (GIS Vector)",
        organization="Madhya Pradesh Road Development Corporation (MPRDC)",
        category="Infrastructure",
        geographic_coverage="Madhya Pradesh",
        year=2024,
        format="GeoJSON",
        license="Govt Research License",
        last_updated="2024-07-30",
        size="110 MB",
        rows=23000,
        description="National Highways, State Highways, Major District Roads, and Proposed Outer Ring Road spatial centerlines.",
    ),
    Dataset(
        id="ds-10",
        name="Agricultural Soil Fertility and Soil Health Card Spatial Matrix",
        organization="Dept of Farmer Welfare & Agriculture Development MP",
        category="Agriculture",
        geographic_coverage="Central MP Agro-Climatic Zones",
        year=2024,
        format="CSV / GeoJSON",
        license="Govt Research License",
        last_updated="2024-05-18",
        size="34 MB",
        rows=6200,
        description="Nitrogen, phosphorus, potassium, organic carbon index, and prime agricultural classification.",
    ),
    Dataset(
        id="ds-11",
        name="State Industrial Area Land Bank Allotment & Vacancy Records",
        organization="MP Industrial Development Corporation (MPIDC)",
        category="Industrial",
        geographic_coverage="MP Industrial Parks",
        year=2025,
        format="JSON",
        license="OGD India",
        last_updated="2025-01-10",
        size="9 MB",
        rows=1400,
        description="Industrial land plots, allotted vs available land hectarage, and active operational status.",
    ),
    Dataset(
        id="ds-12",
        name="Satellite Surface Temperature and Heat Stress Index",
        organization="National Remote Sensing Centre (NRSC / ISRO)",
        category="Climate & Environment",
        geographic_coverage="Central India Agglomerations",
        year=2024,
        format="GeoTIFF / GeoJSON",
        license="Open Data ISRO Bhuvan",
        last_updated="2024-06-28",
        size="175 MB",
        rows=9400,
        description="Summer land surface temperature anomalies, thermal emissivity, and canopy cooling deficit.",
    )
]

# ---------------------------------------------------------
# DETERMINISTIC SIMULATION ENGINE
# ---------------------------------------------------------
def compute_simulation_metrics(inputs: SimulationInput) -> SimulationResult:
    """
    Scientifically parameterized deterministic policy simulation engine.
    Computes Land Use Impact, Environmental Stress, and Infrastructure Demand
    given agricultural conversion %, population growth %, infrastructure growth %, and climate baseline.
    """
    ag_conv = inputs.ag_conversion_pct
    pop_gr = inputs.population_growth_pct
    infra_gr = inputs.infrastructure_growth_pct
    climate_factor = 1.0 if inputs.climate_risk == "Low" else (1.25 if inputs.climate_risk == "Medium" else 1.55)

    # 1. Land Use Changes (percentage delta)
    ag_land_change = -round(ag_conv * 0.84, 2)
    residential_change = +round(ag_conv * 0.72 + (pop_gr * 0.28), 2)
    industrial_change = +round((infra_gr * 0.22) + (ag_conv * 0.12), 2)
    forest_pressure = -round(ag_conv * 0.18 + (infra_gr * 0.14), 2)
    water_body_stress = -round((ag_conv * 0.11 + infra_gr * 0.09) * climate_factor, 2)

    # 2. Environmental Indicators
    water_stress = +round((ag_conv * 0.42 + pop_gr * 0.31) * climate_factor * 0.65, 2)
    green_cover_pressure = +round((ag_conv * 0.34 + infra_gr * 0.28) * 0.7, 2)
    climate_exposure = +round((pop_gr * 0.25 + ag_conv * 0.35) * climate_factor * 0.75, 2)
    carbon_sink_deficit = +round((abs(ag_land_change) * 0.45 + abs(forest_pressure) * 0.85), 2)

    # 3. Infrastructure Impact
    road_demand = +round(infra_gr * 0.48 + pop_gr * 0.24, 2)
    public_service_demand = +round(pop_gr * 0.52 + ag_conv * 0.12, 2)
    sewerage_pressure = +round(pop_gr * 0.58 + ag_conv * 0.18, 2)
    grid_power_demand = +round(pop_gr * 0.44 + infra_gr * 0.32, 2)

    zones_map = {
        "Bhopal": ["Kolar Peri-Urban Fringe", "Mandideep Corridor", "Bairagarh Bypass", "Upper Lake Buffer", "Berasia Road Corridor"],
        "Indore": ["Super Corridor AB Bypass", "Pithampur Industrial Fringe", "Sanwer Road Zone", "Ujjain Road Cluster"],
        "Delhi": ["Najafgarh Rural Fringe", "Bawana Industrial Buffer", "Yamuna Floodplain Zone", "Gurugram-Faridabad Transit Ridge"],
        "Ahmedabad": ["Sanand Industrial Expansion Zone", "SP Ring Road Agricultural Fringe", "Dholera Corridor Node"],
        "Bengaluru": ["Anekal Agrarian Transition Belt", "Sarjapur Peri-Urban Fringe", "Devanahalli Airport Aerotropolis Buffer"]
    }
    affected_zones = zones_map.get(inputs.region, ["Peri-Urban Agricultural Belt", "Outer Ring Road Fringe", "Hydrological Catchment Zone"])

    sim_id = f"SIM-{inputs.region[:3].upper()}-{uuid.uuid4().hex[:6].upper()}"

    return SimulationResult(
        id=sim_id,
        scenario_name=inputs.scenario_name,
        region=inputs.region,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        inputs=inputs,
        land_use_impact={
            "Agricultural Land": ag_land_change,
            "Residential Area": residential_change,
            "Industrial Area": industrial_change,
            "Forest Buffer": forest_pressure,
            "Water Body Retention": water_body_stress
        },
        environmental_indicators={
            "Water Stress": water_stress,
            "Green Cover Pressure": green_cover_pressure,
            "Climate Exposure": climate_exposure,
            "Carbon Sink Deficit": carbon_sink_deficit
        },
        infrastructure_impact={
            "Road Demand": road_demand,
            "Public Service Demand": public_service_demand,
            "Sewerage Network Pressure": sewerage_pressure,
            "Grid Power Demand": grid_power_demand
        },
        affected_zones=affected_zones,
        disclaimer="Scenario-based estimates generated from available research data and mathematical model assumptions. Results are intended for decision support and policy exploration and should not be interpreted as guaranteed predictions.",
        model_assumptions=[
            f"Baseline elasticity of residential conversion per percentage point of agricultural diversion: 0.72.",
            f"Climate multiplier applied: {climate_factor}x based on '{inputs.climate_risk}' climate vulnerability baseline.",
            f"Infrastructure absorption threshold assumed constant over a 5-year simulation horizon.",
            "Water extraction stress calibrated against Central Ground Water Board (CGWB) district baselines."
        ]
    )

# ---------------------------------------------------------
# API ROUTES
# ---------------------------------------------------------
@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "platform": "BHUMI INSIGHT",
        "tagline": "From Land Data to Policy Intelligence",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/research", response_model=List[ResearchPaper])
def get_research_papers(
    topic: Optional[str] = None,
    region: Optional[str] = None,
    search: Optional[str] = None
):
    results = RESEARCH_PAPERS
    if topic and topic.lower() != "all":
        results = [p for p in results if topic.lower() in p.topic.lower()]
    if region and region.lower() != "all":
        results = [p for p in results if region.lower() in p.region.lower()]
    if search:
        s = search.lower()
        results = [p for p in results if s in p.title.lower() or s in p.abstract.lower() or s in p.authors.lower()]
    return results

@app.get("/api/policies", response_model=List[PolicyDocument])
def get_policies(
    status: Optional[str] = None,
    sector: Optional[str] = None,
    search: Optional[str] = None
):
    results = POLICIES
    if status and status.lower() != "all":
        results = [p for p in results if p.status.lower() == status.lower()]
    if sector and sector.lower() != "all":
        results = [p for p in results if p.sector.lower() == sector.lower()]
    if search:
        s = search.lower()
        results = [p for p in results if s in p.title.lower() or s in p.description.lower() or s in p.department.lower()]
    return results

@app.get("/api/datasets", response_model=List[Dataset])
def get_datasets(
    category: Optional[str] = None,
    search: Optional[str] = None
):
    results = DATASETS
    if category and category.lower() != "all":
        results = [d for d in results if category.lower() in d.category.lower()]
    if search:
        s = search.lower()
        results = [d for d in results if s in d.name.lower() or s in d.description.lower() or s in d.organization.lower()]
    return results

@app.get("/api/analytics")
def get_analytics():
    return {
        "land_use_trends": [
            {"year": 2020, "agricultural": 62.4, "residential": 14.8, "industrial": 5.2, "forest": 12.1, "water": 5.5},
            {"year": 2021, "agricultural": 60.8, "residential": 16.1, "industrial": 5.7, "forest": 11.9, "water": 5.5},
            {"year": 2022, "agricultural": 58.9, "residential": 17.6, "industrial": 6.3, "forest": 11.8, "water": 5.4},
            {"year": 2023, "agricultural": 56.7, "residential": 19.4, "industrial": 7.0, "forest": 11.6, "water": 5.3},
            {"year": 2024, "agricultural": 54.5, "residential": 21.2, "industrial": 7.6, "forest": 11.5, "water": 5.2},
            {"year": 2025, "agricultural": 52.1, "residential": 23.1, "industrial": 8.4, "forest": 11.3, "water": 5.1},
            {"year": 2026, "agricultural": 49.8, "residential": 25.0, "industrial": 9.2, "forest": 11.0, "water": 5.0},
        ],
        "regional_risk": [
            {"region": "Bhopal", "land_use_pressure": 78, "climate_risk": 64, "urbanization_rate": 68, "infrastructure_load": 74, "risk_level": "Medium-High"},
            {"region": "Indore", "land_use_pressure": 86, "climate_risk": 58, "urbanization_rate": 79, "infrastructure_load": 82, "risk_level": "High"},
            {"region": "Jabalpur", "land_use_pressure": 54, "climate_risk": 60, "urbanization_rate": 51, "infrastructure_load": 56, "risk_level": "Medium"},
            {"region": "Gwalior", "land_use_pressure": 62, "climate_risk": 72, "urbanization_rate": 59, "infrastructure_load": 61, "risk_level": "Medium-High"},
            {"region": "Ujjain", "land_use_pressure": 65, "climate_risk": 55, "urbanization_rate": 54, "infrastructure_load": 58, "risk_level": "Medium"},
            {"region": "Sehore", "land_use_pressure": 70, "climate_risk": 49, "urbanization_rate": 42, "infrastructure_load": 52, "risk_level": "Medium"},
        ],
        "publications_trend": [
            {"year": 2019, "count": 28},
            {"year": 2020, "count": 45},
            {"year": 2021, "count": 68},
            {"year": 2022, "count": 94},
            {"year": 2023, "count": 132},
            {"year": 2024, "count": 178},
            {"year": 2025, "count": 215},
        ]
    }

@app.get("/api/gis/layers")
def get_gis_layers():
    return {
        "districts": [
            {
                "id": "bhopal-dist",
                "name": "Bhopal District",
                "coordinates": [23.2599, 77.4126],
                "population": "2.4M",
                "urbanization": "68%",
                "ag_land": "41%",
                "climate_risk": "Medium",
                "urban_expansion": "High",
                "infra_pressure": "Medium",
                "primary_growth_corridors": ["Kolar Road", "Hoshangabad Road (NH-46)", "Raisen Road", "Bairagarh Airport Bypass"]
            },
            {
                "id": "indore-dist",
                "name": "Indore District",
                "coordinates": [22.7196, 75.8577],
                "population": "3.3M",
                "urbanization": "79%",
                "ag_land": "34%",
                "climate_risk": "Medium-High",
                "urban_expansion": "Very High",
                "infra_pressure": "High",
                "primary_growth_corridors": ["Super Corridor", "AB Road Bypass", "Pithampur Link"]
            },
            {
                "id": "delhi-ncr",
                "name": "National Capital Region (NCR)",
                "coordinates": [28.6139, 77.2090],
                "population": "21.5M",
                "urbanization": "93%",
                "ag_land": "12%",
                "climate_risk": "High",
                "urban_expansion": "Severe",
                "infra_pressure": "Very High",
                "primary_growth_corridors": ["Dwarka Expressway", "Faridabad Bypass", "Kundli-Manesar"]
            },
            {
                "id": "ahmedabad-dist",
                "name": "Ahmedabad District",
                "coordinates": [23.0225, 72.5714],
                "population": "8.4M",
                "urbanization": "84%",
                "ag_land": "28%",
                "climate_risk": "High",
                "urban_expansion": "High",
                "infra_pressure": "High",
                "primary_growth_corridors": ["SG Highway", "Sanand Industrial Link", "Dholera Expressway"]
            },
            {
                "id": "bengaluru-dist",
                "name": "Bengaluru Urban",
                "coordinates": [12.9716, 77.5946],
                "population": "13.1M",
                "urbanization": "91%",
                "ag_land": "15%",
                "climate_risk": "Medium",
                "urban_expansion": "Severe",
                "infra_pressure": "Very High",
                "primary_growth_corridors": ["Outer Ring Road", "Bellary Road", "Sarjapur Road"]
            }
        ],
        "layers_catalog": [
            {"category": "Land Use", "layers": ["Agricultural Parcel Polygons", "Residential Built-Up Footprint", "Industrial Parks & Corridors", "Forest & Protected Reserve", "Water Bodies & Wetlands"]},
            {"category": "Climate Risk", "layers": ["Upper Lake Flood Inundation Buffer", "Drought Susceptibility Index", "Urban Heat Island Intensity", "Groundwater Critical Depletion Blocks"]},
            {"category": "Infrastructure", "layers": ["Expressways & National Highways", "Metro Influence Zones (TOD)", "Healthcare & Educational Facilities", "Logistics & Freight Hubs"]},
            {"category": "Development", "layers": ["Bhopal Master Plan 2031 Proposed Boundaries", "Outer Ring Road 3km Corridor", "SVAMITVA Rural Abadi Mapping", "High-Priority Conservation Zones"]}
        ]
    }

@app.post("/api/ai/search", response_model=AISearchResponse)
def ai_search(payload: AISearchQuery):
    q = payload.query.lower()

    if "bhopal" in q or "conversion" in q or "urban" in q:
        answer = (
            "Urban land conversion in Bhopal is primarily driven by arterial transportation corridor expansion "
            "(notably NH-46 Hoshangabad Road and Kolar Bypass), high returns on residential plot subdivision relative "
            "to agrarian yield, and anticipatory speculation preceding the Bhopal Master Plan 2031 approval. "
            "Satellite telemetry (2015–2024) indicates a 14.8% reduction in prime double-cropped land across southern "
            "and eastern peri-urban rings. Compounding this, the absence of finalized T&CP master plan statutory enforcement "
            "has fostered fragmented developments that stress regional aquifers and encroach upon Upper Lake catchment corridors."
        )
        drivers = [
            "Arterial Highway Corridors: NH-46, Kolar Road, and Bairagarh Bypass catalyzing rapid land parcel aggregation.",
            "Real Estate Speculation & Land Price Gradient: Agricultural land values rising by 220–340% within 3km of proposed Outer Ring Road.",
            "Statutory Lag in Master Plan Notification: Delays in final notification of Bhopal Master Plan 2031 creating informal conversion windows.",
            "Groundwater Depletion & Reduced Agrarian Margins: Piezometric drops in peri-urban tube wells pushing marginal farmers towards land sale."
        ]
        implications = [
            "Establish statutory eco-sensitive buffer around Upper Lake (Bhoj Wetland Ramsar site) strictly restricting land-use diversion.",
            "Implement Transferable Development Rights (TDR) to compensate agricultural landholders in designated green belts.",
            "Fast-track integration of SVAMITVA cadastral drone layers with MP Bhu-Abhilekh to eliminate unapproved parcel subdivision."
        ]
        sources = [RESEARCH_PAPERS[0], RESEARCH_PAPERS[1], RESEARCH_PAPERS[3], RESEARCH_PAPERS[11]]
        confidence = 0.94
    else:
        answer = (
            f"Evidence-based synthesis for query: '{payload.query}'. Multi-temporal spatial analysis reveals significant "
            "interplay between transport infrastructure investments, tenancy structure transitions, and ecological vulnerabilities. "
            "Evidence indicates that unplanned peri-urban conversions without commensurate drainage and water-harvesting safeguards "
            "compound urban flood risks and reduce agricultural output."
        )
        drivers = [
            "Infrastructure spillover driving non-agricultural parcel conversion.",
            "Decoupling of land market values from agricultural productivity index.",
            "Ecosystem service degradation in watershed zones."
        ]
        implications = [
            "Mandate Comprehensive Spatial Environmental Impact Assessments (SEIA) prior to major land conversions.",
            "Synchronize digital land registries with GIS zoning master plans.",
            "Formulate district-level agro-ecological conservation thresholds."
        ]
        sources = [RESEARCH_PAPERS[2], RESEARCH_PAPERS[4], RESEARCH_PAPERS[7]]
        confidence = 0.88

    return AISearchResponse(
        query=payload.query,
        answer=answer,
        key_drivers=drivers,
        policy_implications=implications,
        sources_used=sources,
        confidence_score=confidence
    )

@app.post("/api/documents/upload", response_model=DocumentAnalysisResponse)
def analyze_document(payload: DocumentAnalysisRequest):
    return DocumentAnalysisResponse(
        filename=payload.filename,
        document_summary=(
            f"Synthesized analysis of '{payload.filename}'. This empirical study evaluates multi-temporal land use transition dynamics, "
            "quantifying the conversion rate of Class-I/II agricultural soil into residential layouts across peri-urban corridors over the past decade."
        ),
        key_findings=[
            "14.8% decrease in net cultivated arable land across the primary 15km urban fringe between 2015 and 2024.",
            "Runoff coefficient increased by 38% due to impervious surface expansion, diminishing sub-surface aquifer recharge by 22%.",
            "Fragmented cadastral holdings (<1.5 acres) exhibit 3.4x higher conversion probability than consolidated holdings (>5 acres).",
            "Informal colonizer developments account for 54% of new residential layouts without statutory municipal service connections."
        ],
        methodology="Object-Based Image Analysis (OBIA) of Sentinel-2 and Cartosat-3 stereo-imagery combined with ground-truthed GPS surveying and Khasra title reconciliation across 42 peri-urban villages.",
        research_gaps=[
            "Longitudinal assessment of groundwater recharge alteration under future climate IPCC SSP2-4.5 rainfall anomalies.",
            "Valuation of lost ecosystem services and carbon sink degradation attributable to wetland buffer encroachment.",
            "Legal audit of revenue court mutation pendency and compliance with MP Land Revenue Code Section 172 diversion mandates."
        ],
        relevant_policies=[
            "Bhopal Master Plan 2031 (Draft Land Use Regulations)",
            "Madhya Pradesh Land Revenue Code (Amendment) Act 2022",
            "State Wetland Conservation & Buffer Zone Guidelines (EPCO)"
        ],
        related_studies=[
            "Climate Resilient Land Use Planning: Upper Lake Catchment (Pathak et al., 2025)",
            "GIS-Based Urban Growth Simulation and Predictive Cadastral Modeling (Iyer & Sengupta, 2023)",
            "Institutional Land Governance & Fragmented Peri-Urban Titles (Mishra & Rao, 2024)"
        ],
        confidence=0.96
    )

@app.post("/api/simulation/run", response_model=SimulationResult)
def run_simulation(inputs: SimulationInput):
    return compute_simulation_metrics(inputs)

@app.get("/api/users", response_model=List[UserProfile])
def get_users():
    return [
        UserProfile(id="usr-1", name="Dr. Sharma", email="k.sharma@gov.mp.in", role="Policymaker / Government Official", organization="Urban Development Department, MP", status="Active", last_active="Just now"),
        UserProfile(id="usr-2", name="Dr. A. Pathak", email="pathak.a@iifm.ac.in", role="Researcher", organization="Indian Institute of Forest Management (IIFM)", status="Active", last_active="15 mins ago"),
        UserProfile(id="usr-3", name="P. Iyer", email="iyer.gis@surveyofindia.gov.in", role="Researcher", organization="Geospatial Survey / SAC", status="Active", last_active="1 hour ago"),
        UserProfile(id="usr-4", name="R. N. Tiwari", email="tiwari.admin@bhumi.nic.in", role="Administrator", organization="National Land Governance Mission", status="Active", last_active="2 hours ago"),
        UserProfile(id="usr-5", name="Citizen User", email="citizen.research@public.org", role="Public User", organization="Civil Society Research Forum", status="Active", last_active="Yesterday"),
    ]

@app.get("/api/projects")
def get_projects():
    return [
        {
            "id": "proj-1",
            "title": "Bhopal Urban Expansion & Agricultural Land Protection Study",
            "region": "Bhopal Metropolitan Region",
            "lead": "Dr. K. Sharma",
            "members": ["Dr. K. Sharma (Policymaker)", "Dr. A. Pathak (Researcher)", "P. Iyer (GIS Analyst)", "Adv. S. Mishra (Legal)"],
            "status": "Active",
            "progress": 72,
            "description": "Cross-institutional investigation into fringe land conversion rates, Upper Lake hydrological protection, and 2031 Master Plan alignment.",
            "tasks": [
                {"id": "t-1", "title": "Analyze 2015-2024 Sentinel-2 LULC transitions", "assignee": "P. Iyer", "completed": True},
                {"id": "t-2", "title": "Synthesize piezometric borehole data from CGWB", "assignee": "Dr. A. Pathak", "completed": True},
                {"id": "t-3", "title": "Run Policy Simulator for 10% vs 20% agricultural conversion", "assignee": "Dr. K. Sharma", "completed": False},
                {"id": "t-4", "title": "Draft final evidence brief for Cabinet Sub-Committee", "assignee": "Team", "completed": False}
            ],
            "comments": [
                {"author": "P. Iyer", "time": "2 hours ago", "text": "Completed the 10m LULC raster reconciliation. Noticing severe Kolar Road cluster encroachment on Class-II agricultural parcels."},
                {"author": "Dr. Sharma", "time": "1 hour ago", "text": "Excellent. We will simulate a 10% vs 20% agricultural conversion scenario in the simulator to evaluate water stress index before Tuesday's briefing."}
            ]
        }
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
