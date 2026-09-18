import React, { useState } from 'react';
import { 
  FileText, 
  Download, 
  Printer, 
  CheckSquare, 
  Square, 
  Sparkles, 
  MapPin, 
  SlidersHorizontal, 
  Layers, 
  CheckCircle2,
  AlertCircle,
  Building2,
  Calendar
} from 'lucide-react';
import { SimulationResult } from '../../types';

interface ReportGeneratorProps {
  simulationContext?: SimulationResult | null;
}

export const ReportGenerator: React.FC<ReportGeneratorProps> = ({ simulationContext }) => {
  const [reportTitle, setReportTitle] = useState('Bhopal Urban Land Governance Assessment');
  const [region, setRegion] = useState('Bhopal Metropolitan Area');
  
  // Selection checkboxes
  const [includeGIS, setIncludeGIS] = useState(true);
  const [includeResearch, setIncludeResearch] = useState(true);
  const [includeClimate, setIncludeClimate] = useState(true);
  const [includeSimulation, setIncludeSimulation] = useState(true);
  const [includeComparison, setIncludeComparison] = useState(true);

  const [isGenerated, setIsGenerated] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);

  const handleGenerateReport = () => {
    setIsGenerating(true);
    setTimeout(() => {
      setIsGenerating(false);
      setIsGenerated(true);
    }, 700);
  };

  const handlePrintPDF = () => {
    window.print();
  };

  return (
    <div className="page-container">
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span className="badge badge-green">Statutory Decision Intelligence</span>
            <span style={{ fontSize: '11.5px', color: '#64748b' }}>Automated Policy Brief Synthesis</span>
          </div>
          <h1 style={{ fontSize: '26px', fontWeight: 800, color: '#0f172a' }}>REPORT GENERATOR</h1>
          <p style={{ fontSize: '14px', color: '#64748b', marginTop: '2px' }}>
            Synthesize multi-modal research evidence, GIS telemetry, and simulation outcomes into a formal Cabinet-ready policy brief.
          </p>
        </div>

        {isGenerated && (
          <div style={{ display: 'flex', gap: '8px' }}>
            <button className="btn btn-secondary" onClick={handlePrintPDF}>
              <Printer size={15} />
              <span>Print Brief</span>
            </button>
            <button className="btn btn-primary" onClick={handlePrintPDF}>
              <Download size={15} />
              <span>Export PDF</span>
            </button>
          </div>
        )}
      </div>

      {/* Report Synthesis Controls Card */}
      <div className="card" style={{ marginBottom: '24px', padding: '20px' }}>
        <h2 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '14px', color: '#0f172a' }}>
          Policy Brief Parameters & Evidence Modules
        </h2>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px', marginBottom: '18px' }}>
          <div className="form-group" style={{ margin: 0 }}>
            <label className="form-label">Report Title:</label>
            <input 
              type="text" 
              className="form-input" 
              value={reportTitle} 
              onChange={(e) => setReportTitle(e.target.value)} 
            />
          </div>

          <div className="form-group" style={{ margin: 0 }}>
            <label className="form-label">Target Administrative Geography:</label>
            <input 
              type="text" 
              className="form-input" 
              value={region} 
              onChange={(e) => setRegion(e.target.value)} 
            />
          </div>
        </div>

        {/* Checkbox Selectors */}
        <div style={{ marginBottom: '18px' }}>
          <label className="form-label" style={{ marginBottom: '8px' }}>
            Select Component Modules to Include:
          </label>
          <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap' }}>
            {[
              { label: 'GIS Analysis', state: includeGIS, set: setIncludeGIS },
              { label: 'Research Evidence', state: includeResearch, set: setIncludeResearch },
              { label: 'Climate Indicators', state: includeClimate, set: setIncludeClimate },
              { label: 'Policy Simulation', state: includeSimulation, set: setIncludeSimulation },
              { label: 'Scenario Comparison', state: includeComparison, set: setIncludeComparison },
            ].map((chk, i) => (
              <div 
                key={i} 
                style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', cursor: 'pointer', userSelect: 'none' }}
                onClick={() => chk.set(!chk.state)}
              >
                {chk.state ? (
                  <CheckSquare size={16} style={{ color: '#059669' }} />
                ) : (
                  <Square size={16} style={{ color: '#94a3b8' }} />
                )}
                <span>{chk.label}</span>
              </div>
            ))}
          </div>
        </div>

        <button 
          className="btn btn-primary"
          style={{ background: 'linear-gradient(135deg, #059669 0%, #2563eb 100%)', padding: '10px 24px' }}
          onClick={handleGenerateReport}
          disabled={isGenerating}
        >
          {isGenerating ? (
            <span>Compiling Brief...</span>
          ) : (
            <>
              <Sparkles size={16} />
              <span>GENERATE REPORT</span>
            </>
          )}
        </button>
      </div>

      {/* Formal 9-Section Report Preview */}
      {isGenerated && (
        <div className="card" style={{ padding: '36px 40px', background: '#ffffff', border: '1px solid #cbd5e1', boxShadow: '0 4px 20px rgba(0,0,0,0.06)' }}>
          {/* Government Brief Header */}
          <div style={{ borderBottom: '2px solid #0f172a', paddingBottom: '16px', marginBottom: '24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
              <div style={{ fontSize: '12px', fontWeight: 800, color: '#059669', letterSpacing: '1px', textTransform: 'uppercase' }}>
                BHUMI INSIGHT • DECISION INTELLIGENCE BRIEF
              </div>
              <div style={{ fontSize: '12px', color: '#64748b' }}>
                Ref: MP-GOV-LULC-2026-089B
              </div>
            </div>
            <h2 style={{ fontSize: '24px', fontWeight: 800, color: '#0f172a', lineHeight: 1.2 }}>
              {reportTitle}
            </h2>
            <div style={{ fontSize: '13px', color: '#475569', marginTop: '6px' }}>
              Prepared for: <strong>High-Level Inter-Ministerial Working Group on Land Governance</strong> • Geography: <strong>{region}</strong> • Date: <strong>September 2026</strong>
            </div>
          </div>

          {/* Section 1: Executive Summary */}
          <section style={{ marginBottom: '24px' }}>
            <h3 style={{ fontSize: '15px', fontWeight: 800, color: '#0f172a', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '6px' }}>
              1. Executive Summary
            </h3>
            <p style={{ fontSize: '13.5px', color: '#334155', lineHeight: 1.6 }}>
              This policy assessment examines land transition velocities across the Bhopal Metropolitan Region, evaluating the trade-offs between 
              planned residential expansion and agrarian resource preservation. Empirical telemetry confirms that peri-urban agricultural conversion 
              exceeds 1.4% annually along radial highway corridors. A simulated 10% agricultural diversion indicates an 8.4% contraction in food-producing 
              holding capacity and a 6.8% escalation in local aquifer stress. A statutory Urban Growth Boundary (UGB) coupled with Transferable Development 
              Rights (TDR) is urgently recommended before the notification of the Bhopal Master Plan 2031.
            </p>
          </section>

          {/* Section 2: Problem Context */}
          <section style={{ marginBottom: '24px' }}>
            <h3 style={{ fontSize: '15px', fontWeight: 800, color: '#0f172a', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '6px' }}>
              2. Problem Context
            </h3>
            <p style={{ fontSize: '13.5px', color: '#334155', lineHeight: 1.6 }}>
              The expansion of Tier-2 metropolitan hubs in Central India has catalyzed intense conversion pressure on Class-I and Class-II agrarian 
              soils. Arterial corridors—specifically NH-46 (Hoshangabad Road), Kolar Road, and the proposed Outer Ring Road—exhibit uncoordinated parcel 
              subdivision under the MP Land Revenue Code Section 172. This fragmentation disrupts micro-watersheds feeding the Bhoj Wetland Ramsar site and 
              diminishes smallholder farming security.
            </p>
          </section>

          {/* Section 3: Data Sources */}
          {includeResearch && (
            <section style={{ marginBottom: '24px' }}>
              <h3 style={{ fontSize: '15px', fontWeight: 800, color: '#0f172a', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '6px' }}>
                3. Data Sources & Empirical Calibration
              </h3>
              <ul style={{ paddingLeft: '20px', fontSize: '13px', color: '#334155', lineHeight: 1.6 }}>
                <li><strong>Remote Sensing Applications Centre (RSAC) MP:</strong> Sentinel-2 10m LULC classification (2015–2025).</li>
                <li><strong>Central Ground Water Board (CGWB):</strong> Decadal piezometric borehole telemetry across 42 peri-urban monitoring points.</li>
                <li><strong>Department of Land Records (Bhu-Abhilekh):</strong> Vectorized Khasra cadastral boundary shapefiles.</li>
                <li><strong>Directorate of Town & Country Planning (T&CP):</strong> Draft Bhopal Master Plan 2031 zoning overlays.</li>
              </ul>
            </section>
          )}

          {/* Section 4: GIS Analysis */}
          {includeGIS && (
            <section style={{ marginBottom: '24px' }}>
              <h3 style={{ fontSize: '15px', fontWeight: 800, color: '#0f172a', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '6px' }}>
                4. GIS Geospatial Analysis
              </h3>
              <p style={{ fontSize: '13.5px', color: '#334155', lineHeight: 1.6 }}>
                Spatial buffering reveals that 64% of ongoing residential conversions occur within 2.5km of designated eco-sensitive water bodies. 
                The 500m mandatory buffer surrounding the Upper Lake catchment exhibits 18 discrete informal settlement incursions.
              </p>
            </section>
          )}

          {/* Section 5: AI Insights */}
          <section style={{ marginBottom: '24px' }}>
            <h3 style={{ fontSize: '15px', fontWeight: 800, color: '#0f172a', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '6px' }}>
              5. Synthesized AI Research Insights
            </h3>
            <div style={{ background: '#f8fafc', padding: '14px', borderRadius: '8px', borderLeft: '4px solid #2563eb', fontSize: '13px', color: '#1e293b', lineHeight: 1.6 }}>
              Multi-agent literature evaluation confirms that peripheral land values appreciate 220–340% within 36 months of expressway notification, 
              rendering voluntary agricultural continuation economically unviable for marginal landowners without institutional land-pooling incentives.
            </div>
          </section>

          {/* Section 6: Scenario Analysis */}
          {includeSimulation && (
            <section style={{ marginBottom: '24px' }}>
              <h3 style={{ fontSize: '15px', fontWeight: 800, color: '#0f172a', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '6px' }}>
                6. Scenario Simulation Analysis (10% Agricultural Conversion Baseline)
              </h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', background: '#f1f5f9', padding: '14px', borderRadius: '8px' }}>
                <div>
                  <div style={{ fontSize: '11.5px', color: '#64748b' }}>Agricultural Land Impact</div>
                  <div style={{ fontSize: '18px', fontWeight: 800, color: '#dc2626' }}>-8.4%</div>
                </div>
                <div>
                  <div style={{ fontSize: '11.5px', color: '#64748b' }}>Residential Footprint Growth</div>
                  <div style={{ fontSize: '18px', fontWeight: 800, color: '#2563eb' }}>+11.2%</div>
                </div>
                <div>
                  <div style={{ fontSize: '11.5px', color: '#64748b' }}>Hydrological Water Stress</div>
                  <div style={{ fontSize: '18px', fontWeight: 800, color: '#d97706' }}>+6.8%</div>
                </div>
              </div>
            </section>
          )}

          {/* Section 7: Policy Considerations */}
          <section style={{ marginBottom: '24px' }}>
            <h3 style={{ fontSize: '15px', fontWeight: 800, color: '#0f172a', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '6px' }}>
              7. Strategic Policy Considerations
            </h3>
            <ol style={{ paddingLeft: '20px', fontSize: '13px', color: '#334155', lineHeight: 1.6 }}>
              <li><strong>Statutory Urban Growth Boundary:</strong> Demarcate a binding 10-year ring beyond which no automatic Section 172 agricultural diversion permits may be granted.</li>
              <li><strong>Bhoj Catchment Conservation Overlay:</strong> Institute strict Transferable Development Rights (TDR) granting developers equivalent FAR inside brownfield metro corridors.</li>
              <li><strong>Integration of SVAMITVA Vectors:</strong> Automate cross-referencing between Revenue Department e-Registries and GIS master plans to prevent unapproved layout sales.</li>
            </ol>
          </section>

          {/* Section 8: Limitations */}
          <section style={{ marginBottom: '24px' }}>
            <h3 style={{ fontSize: '15px', fontWeight: 800, color: '#0f172a', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '6px' }}>
              8. Methodological Limitations & Disclaimer
            </h3>
            <div className="disclaimer-box" style={{ margin: 0 }}>
              <strong>Scientific Notice:</strong> Scenario-based estimates generated from available data and model assumptions. Results are intended for decision support and should not be interpreted as guaranteed predictions.
            </div>
          </section>

          {/* Section 9: References */}
          <section>
            <h3 style={{ fontSize: '15px', fontWeight: 800, color: '#0f172a', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '6px' }}>
              9. Primary Evidence References
            </h3>
            <div style={{ fontSize: '12px', color: '#64748b', lineHeight: 1.6 }}>
              [1] Sharma, K., Verma, R., & Nair, S. (2024). <em>Urban Expansion and Agricultural Land Conversion in Bhopal Fringe Areas</em>. MANIT Research Series.<br />
              [2] Pathak, A., & Choudhary, M. (2025). <em>Climate Resilient Land Use Planning: Upper Lake Catchment</em>. IIFM Journal of Environmental Policy.<br />
              [3] Central Ground Water Board (2024). <em>Piezometric Ground Water Year Book: Madhya Pradesh</em>. Ministry of Jal Shakti.<br />
              [4] Directorate of Town & Country Planning (2023). <em>Bhopal Master Plan 2031 (Draft Land Use Regulations)</em>. Govt. of Madhya Pradesh.
            </div>
          </section>
        </div>
      )}
    </div>
  );
};
