import React, { useState } from 'react';
import { 
  TrendingUp, 
  FileText, 
  Database, 
  BookOpen, 
  MapPin, 
  SlidersHorizontal, 
  Sparkles, 
  ArrowUpRight, 
  ArrowRight,
  CheckCircle2, 
  AlertTriangle, 
  ChevronRight,
  Layers,
  Filter,
  ExternalLink,
  ShieldAlert,
  Info
} from 'lucide-react';
import { DEMO_RESEARCH_PAPERS, DEMO_POLICIES } from '../../data/mockData';
import { ResearchPaper } from '../../types';

interface DashboardProps {
  userName: string;
  onNavigate: (tab: string) => void;
  onOpenEvidence: (paper: ResearchPaper) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ userName, onNavigate, onOpenEvidence }) => {
  const [selectedRiskFilter, setSelectedRiskFilter] = useState<'all' | 'land_use' | 'climate' | 'urbanization' | 'infrastructure' | 'disputes'>('land_use');
  const [activeTrendMetric, setActiveTrendMetric] = useState<'all' | 'agricultural' | 'residential'>('all');
  const [evidenceModalOpen, setEvidenceModalOpen] = useState(false);

  // Realistic Land Use Trends (2020-2026)
  const trendsData = [
    { year: '2020', ag: 62.4, res: 14.8, ind: 5.2, for: 12.1, wat: 5.5 },
    { year: '2021', ag: 60.8, res: 16.1, ind: 5.7, for: 11.9, wat: 5.5 },
    { year: '2022', ag: 58.9, res: 17.6, ind: 6.3, for: 11.8, wat: 5.4 },
    { year: '2023', ag: 56.7, res: 19.4, ind: 7.0, for: 11.6, wat: 5.3 },
    { year: '2024', ag: 54.5, res: 21.2, ind: 7.6, for: 11.5, wat: 5.2 },
    { year: '2025', ag: 52.1, res: 23.1, ind: 8.4, for: 11.3, wat: 5.1 },
    { year: '2026 (Est)', ag: 49.8, res: 25.0, ind: 9.2, for: 11.0, wat: 5.0 },
  ];

  // State risk profiles
  const stateRisks = [
    { state: 'Madhya Pradesh (Bhopal)', risk: 'High', score: 78, primeIssue: 'Peri-urban agricultural encroachment along NH-46', agLoss: '-12.6%', status: 'Urgent Action' },
    { state: 'Maharashtra (Pune-Thane)', risk: 'High', score: 84, primeIssue: 'Western Ghats fringe watershed deforestation', agLoss: '-16.2%', status: 'Critical' },
    { state: 'Karnataka (Bengaluru Rural)', risk: 'Severe', score: 89, primeIssue: 'Groundwater depletion & lake buffer diversion', agLoss: '-19.4%', status: 'Critical' },
    { state: 'Gujarat (Ahmedabad-Sanand)', risk: 'Medium-High', score: 72, primeIssue: 'Industrial zoning sprawl over alluvial tracts', agLoss: '-10.8%', status: 'Monitored' },
    { state: 'Uttar Pradesh (NCR Fringe)', risk: 'Severe', score: 91, primeIssue: 'Yamuna floodway settlement & high plot turnover', agLoss: '-22.1%', status: 'Critical' },
    { state: 'Telangana (Hyderabad ORR)', risk: 'Medium-High', score: 76, primeIssue: 'Pharma corridor conversion of dryland farming', agLoss: '-11.5%', status: 'Monitored' },
  ];

  return (
    <div className="page-container">
      {/* Platform Workflow Banner */}
      <div className="workflow-banner">
        <div>
          <div className="workflow-tagline">
            Platform Framework: <strong>DATA → KNOWLEDGE → INSIGHT → SIMULATION → POLICY</strong>
          </div>
          <div style={{ fontSize: '11.5px', color: '#94a3b8', marginTop: '2px' }}>
            National Digital Platform for Research, Policy Innovation & Evidence-Based Land Governance
          </div>
        </div>
        <div className="workflow-steps">
          <span className="workflow-step-pill active">1. DATA</span>
          <span className="workflow-arrow">→</span>
          <span className="workflow-step-pill active">2. KNOWLEDGE</span>
          <span className="workflow-arrow">→</span>
          <span className="workflow-step-pill active">3. INSIGHT</span>
          <span className="workflow-arrow">→</span>
          <span className="workflow-step-pill active">4. SIMULATION</span>
          <span className="workflow-arrow">→</span>
          <span className="workflow-step-pill active">5. POLICY</span>
        </div>
      </div>

      {/* Header Section */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '24px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h1 style={{ fontSize: '26px', fontWeight: 800, color: '#0f172a', letterSpacing: '-0.5px' }}>
            Good morning, {userName}
          </h1>
          <p style={{ fontSize: '14px', color: '#64748b', marginTop: '4px' }}>
            Here is your land-governance intelligence overview. All indicators reflect synchronized national datasets as of September 2026.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button 
            className="btn btn-outline-primary"
            onClick={() => onNavigate('gis-intelligence')}
          >
            <MapPin size={16} />
            <span>Open GIS Map</span>
          </button>
          <button 
            className="btn btn-success"
            onClick={() => onNavigate('policy-simulator')}
          >
            <SlidersHorizontal size={16} />
            <span>Run Policy Simulation</span>
          </button>
        </div>
      </div>

      {/* Top 6 KPI Cards */}
      <div className="kpi-grid">
        <div className="kpi-card green">
          <div className="kpi-title">Research Resources</div>
          <div className="kpi-value">12,540</div>
          <div className="kpi-subtext">
            <span style={{ color: '#059669', fontWeight: 600 }}>+8.4%</span> peer-reviewed studies
          </div>
        </div>

        <div className="kpi-card navy">
          <div className="kpi-title">Datasets</div>
          <div className="kpi-value">1,245</div>
          <div className="kpi-subtext">
            <span style={{ color: '#2563eb', fontWeight: 600 }}>78 GIS / OGD</span> verified catalogs
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-title">Policy Documents</div>
          <div className="kpi-value">820</div>
          <div className="kpi-subtext">
            <span style={{ color: '#059669', fontWeight: 600 }}>42 active</span> state & central acts
          </div>
        </div>

        <div className="kpi-card amber">
          <div className="kpi-title">Active Projects</div>
          <div className="kpi-value">146</div>
          <div className="kpi-subtext">
            <span style={{ color: '#d97706', fontWeight: 600 }}>18 cross-ministry</span> labs
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-title">GIS Layers</div>
          <div className="kpi-value">78</div>
          <div className="kpi-subtext">
            <span style={{ color: '#2563eb', fontWeight: 600 }}>10m resolution</span> Sentinel/ISRO
          </div>
        </div>

        <div className="kpi-card green">
          <div className="kpi-title">Policy Scenarios</div>
          <div className="kpi-value">342</div>
          <div className="kpi-subtext">
            <span style={{ color: '#059669', fontWeight: 600 }}>12 validated</span> this week
          </div>
        </div>
      </div>

      {/* C. Highlighted AI Insight Card */}
      <div className="ai-insight-card">
        <div className="ai-insight-icon">
          <Sparkles size={22} />
        </div>
        <div className="ai-insight-content">
          <div className="ai-insight-title">
            <span>SYNTHESIZED AI POLICY ALERT: Peri-Urban Land Conversion Pressure in Central India</span>
            <span className="badge badge-amber">Action Recommended</span>
          </div>
          <p className="ai-insight-text">
            "Urban expansion around selected regions indicates increasing pressure on agricultural land. Further analysis is recommended before approving large-scale land-use conversion in the Bhopal-Indore metropolitan corridor."
          </p>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
            <button 
              className="btn btn-sm btn-primary"
              onClick={() => setEvidenceModalOpen(true)}
            >
              <FileText size={14} />
              <span>View Evidence (4 Papers & 2 Datasets)</span>
            </button>
            <button 
              className="btn btn-sm btn-secondary"
              onClick={() => onNavigate('policy-simulator')}
            >
              <SlidersHorizontal size={14} />
              <span>Test 10% Conversion Scenario</span>
            </button>
            <span style={{ fontSize: '11.5px', color: '#64748b' }}>
              Synthesized from MANIT Bhopal, CGWB, and Sentinel-2 LULC telemetry.
            </span>
          </div>
        </div>
      </div>

      {/* Two Column Grid: Charts & Regional Risk */}
      <div className="grid-2" style={{ marginBottom: '24px' }}>
        {/* A. Land Use Trend Interactive Chart */}
        <div className="card">
          <div className="card-header">
            <div>
              <h2 className="card-title">A. Land Use Trend (2020–2026)</h2>
              <div className="card-subtitle">Aggregated multi-temporal land classification change (%)</div>
            </div>
            <div style={{ display: 'flex', gap: '6px' }}>
              <button 
                className={`btn btn-sm ${activeTrendMetric === 'all' ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => setActiveTrendMetric('all')}
              >
                All Classes
              </button>
              <button 
                className={`btn btn-sm ${activeTrendMetric === 'agricultural' ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => setActiveTrendMetric('agricultural')}
              >
                Agriculture Only
              </button>
            </div>
          </div>

          {/* SVG Visual Chart */}
          <div style={{ background: '#f8fafc', borderRadius: '8px', padding: '16px', border: '1px solid #e2e8f0', height: '230px', position: 'relative' }}>
            <svg width="100%" height="100%" viewBox="0 0 500 180" preserveAspectRatio="none">
              {/* Horizontal Grid lines */}
              <line x1="40" y1="20" x2="480" y2="20" stroke="#e2e8f0" strokeDasharray="3 3" />
              <line x1="40" y1="60" x2="480" y2="60" stroke="#e2e8f0" strokeDasharray="3 3" />
              <line x1="40" y1="100" x2="480" y2="100" stroke="#e2e8f0" strokeDasharray="3 3" />
              <line x1="40" y1="140" x2="480" y2="140" stroke="#e2e8f0" strokeDasharray="3 3" />
              
              {/* Y Axis Labels */}
              <text x="10" y="24" fontSize="10" fill="#64748b">70%</text>
              <text x="10" y="64" fontSize="10" fill="#64748b">50%</text>
              <text x="10" y="104" fontSize="10" fill="#64748b">30%</text>
              <text x="10" y="144" fontSize="10" fill="#64748b">10%</text>

              {/* Line 1: Agricultural (Declining from 62.4% to 49.8%) */}
              {(activeTrendMetric === 'all' || activeTrendMetric === 'agricultural') && (
                <>
                  <polyline
                    fill="none"
                    stroke="#059669"
                    strokeWidth="3"
                    points="60,35 125,38 190,42 255,47 320,51 385,56 450,60"
                  />
                  {/* Points */}
                  <circle cx="60" cy="35" r="4" fill="#059669" />
                  <circle cx="255" cy="47" r="4" fill="#059669" />
                  <circle cx="450" cy="60" r="5" fill="#059669" />
                  <text x="455" y="58" fontSize="11" fill="#059669" fontWeight="700">Agri: 49.8%</text>
                </>
              )}

              {/* Line 2: Residential (Rising from 14.8% to 25.0%) */}
              {(activeTrendMetric === 'all' || activeTrendMetric === 'residential') && (
                <>
                  <polyline
                    fill="none"
                    stroke="#2563eb"
                    strokeWidth="3"
                    points="60,130 125,127 190,124 255,120 320,116 385,112 450,108"
                  />
                  <circle cx="60" cy="130" r="4" fill="#2563eb" />
                  <circle cx="255" cy="120" r="4" fill="#2563eb" />
                  <circle cx="450" cy="108" r="5" fill="#2563eb" />
                  <text x="455" y="112" fontSize="11" fill="#2563eb" fontWeight="700">Res: 25.0%</text>
                </>
              )}

              {/* Line 3: Industrial (5.2% to 9.2%) */}
              {activeTrendMetric === 'all' && (
                <polyline
                  fill="none"
                  stroke="#d97706"
                  strokeWidth="2"
                  strokeDasharray="4 2"
                  points="60,150 125,149 190,147 255,146 320,144 385,143 450,140"
                />
              )}

              {/* Line 4: Forest (12.1% to 11.0%) */}
              {activeTrendMetric === 'all' && (
                <polyline
                  fill="none"
                  stroke="#16a34a"
                  strokeWidth="2"
                  strokeDasharray="2 2"
                  points="60,136 125,136 190,137 255,137 320,137 385,138 450,138"
                />
              )}

              {/* X Axis Labels */}
              <text x="50" y="170" fontSize="10.5" fill="#64748b">2020</text>
              <text x="115" y="170" fontSize="10.5" fill="#64748b">2021</text>
              <text x="180" y="170" fontSize="10.5" fill="#64748b">2022</text>
              <text x="245" y="170" fontSize="10.5" fill="#64748b">2023</text>
              <text x="310" y="170" fontSize="10.5" fill="#64748b">2024</text>
              <text x="375" y="170" fontSize="10.5" fill="#64748b">2025</text>
              <text x="435" y="170" fontSize="10.5" fill="#0f172a" fontWeight="700">2026 (Est)</text>
            </svg>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '12px', fontSize: '12px', color: '#64748b' }}>
            <div style={{ display: 'flex', gap: '16px' }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                <span style={{ width: '10px', height: '10px', backgroundColor: '#059669', borderRadius: '2px' }}></span>
                Agricultural (Down 12.6%)
              </span>
              <span style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                <span style={{ width: '10px', height: '10px', backgroundColor: '#2563eb', borderRadius: '2px' }}></span>
                Residential (Up 10.2%)
              </span>
              <span style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                <span style={{ width: '10px', height: '10px', backgroundColor: '#d97706', borderRadius: '2px' }}></span>
                Industrial
              </span>
            </div>
            <span style={{ fontWeight: 600, color: '#0f172a' }}>Source: RSAC & Sentinel Telemetry</span>
          </div>
        </div>

        {/* B. Regional Risk Overview */}
        <div className="card">
          <div className="card-header">
            <div>
              <h2 className="card-title">B. Regional Risk Overview (India Focus)</h2>
              <div className="card-subtitle">Vulnerability matrix calibrated by land pressure & environmental stress</div>
            </div>
            <div style={{ display: 'flex', gap: '4px' }}>
              <button 
                className={`btn btn-sm ${selectedRiskFilter === 'land_use' ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => setSelectedRiskFilter('land_use')}
              >
                Land Use
              </button>
              <button 
                className={`btn btn-sm ${selectedRiskFilter === 'climate' ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => setSelectedRiskFilter('climate')}
              >
                Climate
              </button>
              <button 
                className={`btn btn-sm ${selectedRiskFilter === 'urbanization' ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => setSelectedRiskFilter('urbanization')}
              >
                Urban
              </button>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', maxHeight: '275px', overflowY: 'auto' }}>
            {stateRisks.map((item, idx) => (
              <div 
                key={idx}
                style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'space-between',
                  padding: '10px 12px',
                  borderRadius: '8px',
                  border: '1px solid #e2e8f0',
                  background: item.risk === 'Severe' ? '#fff5f5' : (item.risk === 'High' ? '#fffbeb' : '#ffffff'),
                  cursor: 'pointer'
                }}
                onClick={() => onNavigate('gis-intelligence')}
                title="Click to view district in GIS Module"
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ fontWeight: 700, fontSize: '13px', color: '#0f172a' }}>{item.state}</span>
                    <span className={`badge ${item.risk === 'Severe' ? 'badge-red' : (item.risk === 'High' ? 'badge-amber' : 'badge-blue')}`}>
                      Risk Score: {item.score}/100
                    </span>
                  </div>
                  <div style={{ fontSize: '11.5px', color: '#64748b', marginTop: '2px' }}>
                    {item.primeIssue}
                  </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '12.5px', fontWeight: 700, color: '#dc2626' }}>{item.agLoss}</div>
                  <div style={{ fontSize: '10px', color: '#64748b' }}>Net Arable Change</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Lower Two Column Grid: Recent Research & Policy Monitoring */}
      <div className="grid-2">
        {/* D. Recent Research */}
        <div className="card">
          <div className="card-header">
            <div>
              <h2 className="card-title">D. Recent Land-Governance Research</h2>
              <div className="card-subtitle">Peer-reviewed publications and institutional studies</div>
            </div>
            <button 
              className="btn btn-sm btn-secondary"
              onClick={() => onNavigate('knowledge-hub')}
            >
              <span>View All 15+ Studies</span>
              <ChevronRight size={14} />
            </button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {DEMO_RESEARCH_PAPERS.slice(0, 4).map((paper) => (
              <div 
                key={paper.id}
                style={{ 
                  padding: '12px', 
                  borderRadius: '8px', 
                  border: '1px solid #e2e8f0',
                  background: '#ffffff',
                  transition: 'all 0.15s ease'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '8px' }}>
                  <div style={{ fontWeight: 700, fontSize: '13px', color: '#0f172a', lineHeight: 1.3 }}>
                    {paper.title}
                  </div>
                  <span className="badge badge-green" style={{ flexShrink: 0 }}>
                    {paper.relevance}% Match
                  </span>
                </div>
                <div style={{ fontSize: '11.5px', color: '#64748b', marginTop: '4px' }}>
                  {paper.authors} • <strong>{paper.organization}</strong> ({paper.year})
                </div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '8px', paddingTop: '6px', borderTop: '1px solid #f1f5f9' }}>
                  <span className="badge badge-gray">{paper.region}</span>
                  <button 
                    className="btn btn-sm btn-outline-primary"
                    onClick={() => onOpenEvidence(paper)}
                    style={{ padding: '3px 8px', fontSize: '11px' }}
                  >
                    <span>Inspect Evidence</span>
                    <ExternalLink size={12} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* E. Policy Monitoring */}
        <div className="card">
          <div className="card-header">
            <div>
              <h2 className="card-title">E. Policy Monitoring & Regulatory Pipeline</h2>
              <div className="card-subtitle">Active statutory policies, draft regulations & simulations</div>
            </div>
            <button 
              className="btn btn-sm btn-secondary"
              onClick={() => onNavigate('knowledge-hub')}
            >
              <span>Policy Registry</span>
              <ChevronRight size={14} />
            </button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {DEMO_POLICIES.slice(0, 4).map((policy) => (
              <div 
                key={policy.id}
                style={{ 
                  padding: '12px', 
                  borderRadius: '8px', 
                  border: '1px solid #e2e8f0',
                  background: '#ffffff'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '8px' }}>
                  <div style={{ fontWeight: 700, fontSize: '13px', color: '#0f172a' }}>
                    {policy.title}
                  </div>
                  <span className={`badge ${policy.status === 'Active' ? 'badge-green' : (policy.status === 'Under Evaluation' ? 'badge-amber' : 'badge-blue')}`}>
                    {policy.status}
                  </span>
                </div>
                <div style={{ fontSize: '11.5px', color: '#64748b', marginTop: '3px' }}>
                  {policy.department} • ({policy.region})
                </div>
                <p style={{ fontSize: '12px', color: '#334155', marginTop: '6px', lineHeight: 1.4 }}>
                  {policy.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Primary SIH Demo Flow Bar at bottom */}
      <div style={{ marginTop: '24px', background: '#eff6ff', border: '1px solid #bfdbfe', borderRadius: '12px', padding: '14px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ width: '28px', height: '28px', borderRadius: '50%', backgroundColor: '#2563eb', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Sparkles size={16} />
          </div>
          <div>
            <div style={{ fontWeight: 700, fontSize: '13px', color: '#1e3a8a' }}>
              Ready to execute the 3-Minute SIH Evaluation Demo Flow?
            </div>
            <div style={{ fontSize: '11.5px', color: '#3b82f6' }}>
              Start by searching "Bhopal Urban Expansion" in the AI Research Module → Inspect Evidence → GIS Map → Policy Simulator (10% conversion) → Report Generation.
            </div>
          </div>
        </div>
        <button 
          className="btn btn-primary"
          onClick={() => onNavigate('ai-research')}
        >
          <span>Begin Demo Flow (Step 1: AI Research)</span>
          <ArrowRight size={15} />
        </button>
      </div>

      {/* Evidence Modal */}
      {evidenceModalOpen && (
        <div className="modal-backdrop" onClick={() => setEvidenceModalOpen(false)}>
          <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div>
                <h3 style={{ fontSize: '18px', fontWeight: 800, color: '#0f172a' }}>
                  Supporting Evidence & Empirical Sources
                </h3>
                <p style={{ fontSize: '12px', color: '#64748b', marginTop: '2px' }}>
                  Provenance backing the Peri-Urban Land Conversion Alert
                </p>
              </div>
              <button 
                onClick={() => setEvidenceModalOpen(false)}
                style={{ background: 'none', border: 'none', fontSize: '20px', cursor: 'pointer', color: '#64748b' }}
              >
                ✕
              </button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div style={{ background: '#f8fafc', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                <div style={{ fontWeight: 700, color: '#0f172a', fontSize: '13.5px' }}>
                  1. MANIT Bhopal Study (Sharma et al., 2024)
                </div>
                <div style={{ fontSize: '12px', color: '#475569', marginTop: '3px' }}>
                  Telemetry verified a 14.8% drop in net arable acreage across southern fringes (Kolar / Mandideep) between 2015 and 2024.
                </div>
              </div>

              <div style={{ background: '#f8fafc', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                <div style={{ fontWeight: 700, color: '#0f172a', fontSize: '13.5px' }}>
                  2. Central Ground Water Board (CGWB) Piezometric Audit 2025
                </div>
                <div style={{ fontSize: '12px', color: '#475569', marginTop: '3px' }}>
                  Bhopal rural fringe borewells registered a 4.2m average water table decline correlated with impervious surface build-up.
                </div>
              </div>

              <div style={{ background: '#f8fafc', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                <div style={{ fontWeight: 700, color: '#0f172a', fontSize: '13.5px' }}>
                  3. Indian Institute of Forest Management (IIFM, 2025)
                </div>
                <div style={{ fontSize: '12px', color: '#475569', marginTop: '3px' }}>
                  Bhoj Wetland catchment vulnerability model indicating rapid sedimentation risks if peripheral agricultural retention zones are developed.
                </div>
              </div>

              <div className="disclaimer-box">
                <strong>Scientific Responsibility Note:</strong> These empirical findings are sourced from academic telemetry and verified governmental repositories. They do not constitute statutory policy prohibitions unless ratified by the State Town & Country Planning Board.
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '16px' }}>
              <button className="btn btn-primary" onClick={() => setEvidenceModalOpen(false)}>
                Close Evidence
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
