import React, { useState } from 'react';
import { 
  BarChart3, 
  TrendingUp, 
  MapPin, 
  Calendar, 
  Filter, 
  Layers, 
  AlertTriangle, 
  BookOpen, 
  Scale,
  Download,
  Info
} from 'lucide-react';

export const AnalyticsModule: React.FC = () => {
  const [selectedRegion, setSelectedRegion] = useState('Bhopal Metropolitan');
  const [selectedYearRange, setSelectedYearRange] = useState('2020-2026');

  // Urban expansion decadal growth data
  const urbanExpansionBars = [
    { period: '2016-18', builtUpSqKm: 142, agConverted: 68 },
    { period: '2018-20', builtUpSqKm: 184, agConverted: 94 },
    { period: '2020-22', builtUpSqKm: 236, agConverted: 128 },
    { period: '2022-24', builtUpSqKm: 298, agConverted: 172 },
    { period: '2024-26 (P)', builtUpSqKm: 364, agConverted: 215 },
  ];

  // Research publication count by year
  const researchTrends = [
    { year: 2020, count: 45 },
    { year: 2021, count: 68 },
    { year: 2022, count: 94 },
    { year: 2023, count: 132 },
    { year: 2024, count: 178 },
    { year: 2025, count: 215 },
  ];

  // Policies by sector
  const policiesBySector = [
    { sector: 'Urban Planning & Zoning', count: 34, pct: 42 },
    { sector: 'Cadastral & Digital Records', count: 22, pct: 27 },
    { sector: 'Wetland & Eco-Conservation', count: 14, pct: 17 },
    { sector: 'Industrial Corridors', count: 11, pct: 14 },
  ];

  // Infrastructure pressure matrix
  const infraMatrix = [
    { corridor: 'Kolar Road Peri-Urban Fringe', waterStress: 'High', trafficCongestion: 'Severe', sewageCoverage: '32%', riskLevel: 'Critical' },
    { corridor: 'Hoshangabad Road (NH-46)', waterStress: 'Medium', trafficCongestion: 'High', sewageCoverage: '58%', riskLevel: 'Moderate' },
    { corridor: 'Bairagarh Airport Bypass', waterStress: 'Medium-High', trafficCongestion: 'Medium', sewageCoverage: '44%', riskLevel: 'High' },
    { corridor: 'Mandideep Industrial Belt', waterStress: 'Severe', trafficCongestion: 'High', sewageCoverage: '49%', riskLevel: 'Critical' },
    { corridor: 'Berasia Agrarian Route', waterStress: 'Low', trafficCongestion: 'Low', sewageCoverage: '18%', riskLevel: 'Low-Medium' },
  ];

  return (
    <div className="page-container">
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span className="badge badge-blue">Longitudinal Macro Indicators</span>
            <span style={{ fontSize: '11.5px', color: '#64748b' }}>National Geospatial Telemetry Data</span>
          </div>
          <h1 style={{ fontSize: '26px', fontWeight: 800, color: '#0f172a' }}>LAND GOVERNANCE ANALYTICS</h1>
          <p style={{ fontSize: '14px', color: '#64748b', marginTop: '2px' }}>
            Multi-criteria statistical indicators tracking land-use transitions, urban built-up velocity, and research publication trends.
          </p>
        </div>

        {/* Filter Controls */}
        <div style={{ display: 'flex', gap: '10px' }}>
          <select 
            className="form-select"
            value={selectedRegion}
            onChange={(e) => setSelectedRegion(e.target.value)}
            style={{ width: 'auto' }}
          >
            <option value="Bhopal Metropolitan">Region: Bhopal Metropolitan</option>
            <option value="Indore Growth Node">Region: Indore Growth Node</option>
            <option value="Madhya Pradesh Aggregated">Region: MP Statewide</option>
          </select>
          <select 
            className="form-select"
            value={selectedYearRange}
            onChange={(e) => setSelectedYearRange(e.target.value)}
            style={{ width: 'auto' }}
          >
            <option value="2020-2026">Years: 2020–2026</option>
            <option value="2015-2025">Years: 2015–2025</option>
          </select>
        </div>
      </div>

      {/* Grid Row 1: Urban Expansion Bar Chart & Land Use Trajectory */}
      <div className="grid-2" style={{ marginBottom: '24px' }}>
        {/* Urban Built-Up Velocity (Bar Chart) */}
        <div className="card">
          <div className="card-header">
            <div>
              <h2 className="card-title">Urban Expansion & Net Agrarian Loss (Sq Km)</h2>
              <div className="card-subtitle">Bhopal Metropolitan Planning Area (2016–2026)</div>
            </div>
            <span className="badge badge-blue">RSAC Telemetry</span>
          </div>

          <div style={{ height: '220px', display: 'flex', alignItems: 'flex-end', justifyContent: 'space-around', gap: '12px', padding: '16px 8px', background: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
            {urbanExpansionBars.map((bar, idx) => {
              const heightPct = (bar.builtUpSqKm / 400) * 100;
              const agPct = (bar.agConverted / 400) * 100;

              return (
                <div key={idx} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', flex: 1, height: '100%', justifyContent: 'flex-end' }}>
                  <div style={{ fontSize: '10.5px', fontWeight: 700, color: '#0f172a', marginBottom: '4px' }}>
                    {bar.builtUpSqKm} sq km
                  </div>
                  <div style={{ width: '38px', display: 'flex', flexDirection: 'column', justifyContent: 'flex-end', height: '100%' }}>
                    {/* Built-up portion (Blue) */}
                    <div style={{ height: `${heightPct}%`, backgroundColor: '#2563eb', borderTopLeftRadius: '4px', borderTopRightRadius: '4px', position: 'relative' }}>
                      {/* Agricultural conversion slice (Red hatch) */}
                      <div style={{ height: `${agPct}%`, backgroundColor: '#ef4444', opacity: 0.85, position: 'absolute', bottom: 0, width: '100%' }}></div>
                    </div>
                  </div>
                  <div style={{ fontSize: '11px', color: '#64748b', marginTop: '6px', fontWeight: 600 }}>{bar.period}</div>
                </div>
              );
            })}
          </div>

          <div style={{ display: 'flex', justifyContent: 'center', gap: '20px', marginTop: '12px', fontSize: '11.5px', color: '#475569' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ width: '12px', height: '12px', backgroundColor: '#2563eb', borderRadius: '2px' }}></span>
              Total Built-Up Area Footprint
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ width: '12px', height: '12px', backgroundColor: '#ef4444', borderRadius: '2px' }}></span>
              Direct Agricultural Land Diverted
            </span>
          </div>
        </div>

        {/* Research Publication Trends (Bar/Line Chart) */}
        <div className="card">
          <div className="card-header">
            <div>
              <h2 className="card-title">Land Governance Research Velocity</h2>
              <div className="card-subtitle">Indexed peer-reviewed studies published per calendar year</div>
            </div>
            <span className="badge badge-green">+24% YoY Surge</span>
          </div>

          <div style={{ height: '220px', display: 'flex', alignItems: 'flex-end', justifyContent: 'space-around', gap: '12px', padding: '16px 8px', background: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
            {researchTrends.map((rt, idx) => {
              const heightPct = (rt.count / 240) * 100;
              return (
                <div key={idx} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', flex: 1, height: '100%', justifyContent: 'flex-end' }}>
                  <div style={{ fontSize: '11px', fontWeight: 700, color: '#059669', marginBottom: '4px' }}>
                    {rt.count}
                  </div>
                  <div style={{ width: '32px', height: `${heightPct}%`, backgroundColor: '#10b981', borderTopLeftRadius: '4px', borderTopRightRadius: '4px' }}></div>
                  <div style={{ fontSize: '11px', color: '#64748b', marginTop: '6px', fontWeight: 600 }}>{rt.year}</div>
                </div>
              );
            })}
          </div>

          <div style={{ fontSize: '12px', color: '#64748b', textAlign: 'center', marginTop: '12px' }}>
            Data source: Scopus, OGD India, National Knowledge Network, and MoRD Research Cell.
          </div>
        </div>
      </div>

      {/* Grid Row 2: Infrastructure Heatmap Matrix & Policy Distribution */}
      <div className="grid-2">
        {/* Infrastructure Pressure Matrix */}
        <div className="card">
          <div className="card-header">
            <div>
              <h2 className="card-title">Peri-Urban Infrastructure Pressure Matrix</h2>
              <div className="card-subtitle">Civic absorption load across primary radial growth corridors</div>
            </div>
          </div>

          <div className="data-table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Corridor Alignment</th>
                  <th>Water Stress</th>
                  <th>Traffic Load</th>
                  <th>Sewage</th>
                  <th>Vulnerability</th>
                </tr>
              </thead>
              <tbody>
                {infraMatrix.map((item, idx) => (
                  <tr key={idx}>
                    <td style={{ fontWeight: 600, color: '#0f172a' }}>{item.corridor}</td>
                    <td>
                      <span className={`badge ${item.waterStress === 'Severe' ? 'badge-red' : (item.waterStress === 'High' ? 'badge-amber' : 'badge-blue')}`}>
                        {item.waterStress}
                      </span>
                    </td>
                    <td>{item.trafficCongestion}</td>
                    <td><code>{item.sewageCoverage}</code></td>
                    <td>
                      <span className={`badge ${item.riskLevel === 'Critical' ? 'badge-red' : (item.riskLevel === 'High' ? 'badge-amber' : 'badge-green')}`}>
                        {item.riskLevel}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Policy Distribution by Sector */}
        <div className="card">
          <div className="card-header">
            <div>
              <h2 className="card-title">Policy Distribution by Regulatory Sector</h2>
              <div className="card-subtitle">Active statutory frameworks and administrative guidelines</div>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', padding: '10px 0' }}>
            {policiesBySector.map((sec, idx) => (
              <div key={idx}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px', fontSize: '13px' }}>
                  <span style={{ fontWeight: 600, color: '#0f172a' }}>{sec.sector}</span>
                  <span style={{ color: '#64748b' }}><strong>{sec.count}</strong> policies ({sec.pct}%)</span>
                </div>
                <div style={{ width: '100%', height: '8px', backgroundColor: '#e2e8f0', borderRadius: '4px', overflow: 'hidden' }}>
                  <div style={{ width: `${sec.pct}%`, height: '100%', backgroundColor: idx === 0 ? '#2563eb' : (idx === 1 ? '#059669' : (idx === 2 ? '#d97706' : '#64748b')), borderRadius: '4px' }}></div>
                </div>
              </div>
            ))}
          </div>

          <div style={{ background: '#f8fafc', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0', marginTop: '12px', fontSize: '12px', color: '#475569' }}>
            <strong>Regulatory Synthesis:</strong> 42% of regulatory initiatives address municipal master planning and urban fringes, highlighting the critical priority of spatial growth boundaries.
          </div>
        </div>
      </div>
    </div>
  );
};
