import React, { useState } from 'react';
import { 
  SlidersHorizontal, 
  Play, 
  CheckCircle2, 
  RotateCcw, 
  FileText, 
  AlertTriangle, 
  MapPin, 
  TrendingDown, 
  TrendingUp, 
  ShieldAlert, 
  Layers, 
  BarChart3, 
  ArrowRight,
  GitCompare,
  Sparkles,
  Info
} from 'lucide-react';
import confetti from 'canvas-confetti';
import { SimulationInput, SimulationResult } from '../../types';
import { executeSimulation } from '../../services/api';
import { PREVIOUS_SIMULATIONS } from '../../data/mockData';

interface PolicySimulatorProps {
  onNavigate: (tab: string) => void;
  onSetGeneratedReportContext?: (result: SimulationResult) => void;
}

export const PolicySimulator: React.FC<PolicySimulatorProps> = ({ 
  onNavigate, 
  onSetGeneratedReportContext 
}) => {
  // Scenario Creation Inputs
  const [scenarioName, setScenarioName] = useState('Urban Land Conversion Scenario');
  const [region, setRegion] = useState('Bhopal');
  const [agConversion, setAgConversion] = useState(10); // 0-50%, default 10%
  const [popGrowth, setPopGrowth] = useState(15); // 0-50%, default 15%
  const [infraGrowth, setInfraGrowth] = useState(20); // 0-50%, default 20%
  const [climateRisk, setClimateRisk] = useState<'Low' | 'Medium' | 'High'>('Medium');

  // Simulation execution pipeline states (5 steps)
  const [isSimulating, setIsSimulating] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [activeTab, setActiveTab] = useState<'simulator' | 'comparison' | 'history'>('simulator');

  // Results
  const [result, setResult] = useState<SimulationResult | null>(PREVIOUS_SIMULATIONS[0]);

  const simulationSteps = [
    "1. Loading datasets (LULC 2025, CGWB, Master Plan)...",
    "2. Analyzing historical trends (2015-2024 telemetry)...",
    "3. Running scenario mathematical elasticity model...",
    "4. Generating GIS spatial impact & affected zones...",
    "5. Preparing decision-intelligence indicators..."
  ];

  const handleRunSimulation = async () => {
    setIsSimulating(true);
    setCurrentStep(0);

    // Animate 5-step processing state
    for (let i = 0; i < 5; i++) {
      setCurrentStep(i);
      await new Promise((r) => setTimeout(r, 650));
    }

    const input: SimulationInput = {
      scenario_name: scenarioName,
      region,
      ag_conversion_pct: agConversion,
      population_growth_pct: popGrowth,
      infrastructure_growth_pct: infraGrowth,
      climate_risk: climateRisk
    };

    const simResult = await executeSimulation(input);
    setResult(simResult);
    setIsSimulating(false);

    // Subtle celebratory confetti for simulation run
    try {
      confetti({
        particleCount: 35,
        spread: 60,
        origin: { y: 0.7 }
      });
    } catch (e) {
      // ignore
    }
  };

  const handleResetDefaults = () => {
    setAgConversion(10);
    setPopGrowth(15);
    setInfraGrowth(20);
    setClimateRisk('Medium');
    setRegion('Bhopal');
  };

  const handleExportToReport = () => {
    if (result && onSetGeneratedReportContext) {
      onSetGeneratedReportContext(result);
    }
    onNavigate('reports');
  };

  return (
    <div className="page-container">
      {/* Signature Feature Banner */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span className="badge badge-green" style={{ background: '#ecfdf5', color: '#047857', border: '1px solid #a7f3d0' }}>
              SIH Signature Feature
            </span>
            <span style={{ fontSize: '11.5px', color: '#64748b' }}>Deterministic Land Transition Engine</span>
          </div>
          <h1 style={{ fontSize: '26px', fontWeight: 800, color: '#0f172a' }}>POLICY SIMULATOR</h1>
          <p style={{ fontSize: '14px', color: '#64748b', marginTop: '2px' }}>
            Test policy scenarios before implementation. Experiment with land-use conversion thresholds and evaluate environmental trade-offs.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '8px' }}>
          <button 
            className={`btn btn-sm ${activeTab === 'simulator' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveTab('simulator')}
          >
            <SlidersHorizontal size={14} />
            <span>Scenario Engine</span>
          </button>
          <button 
            className={`btn btn-sm ${activeTab === 'comparison' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveTab('comparison')}
          >
            <GitCompare size={14} />
            <span>Scenario Comparison (5% vs 10% vs 20%)</span>
          </button>
        </div>
      </div>

      {activeTab === 'simulator' && (
        <div className="grid-3" style={{ gap: '24px' }}>
          {/* Left Column: Scenario Creation Form */}
          <div className="card" style={{ gridColumn: 'span 1' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
              <h2 style={{ fontSize: '16px', fontWeight: 700, color: '#0f172a' }}>
                Scenario Parameters
              </h2>
              <button 
                onClick={handleResetDefaults}
                style={{ background: 'none', border: 'none', color: '#64748b', fontSize: '11.5px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px' }}
                title="Reset to SIH Demo Defaults"
              >
                <RotateCcw size={12} />
                <span>Reset Defaults</span>
              </button>
            </div>

            {/* Scenario Title */}
            <div className="form-group">
              <label className="form-label">Scenario Title:</label>
              <input 
                type="text" 
                className="form-input" 
                value={scenarioName} 
                onChange={(e) => setScenarioName(e.target.value)} 
              />
            </div>

            {/* Region Dropdown */}
            <div className="form-group">
              <label className="form-label">Target Region:</label>
              <select 
                className="form-select"
                value={region}
                onChange={(e) => setRegion(e.target.value)}
              >
                <option value="Bhopal">Bhopal (Primary SIH Demo)</option>
                <option value="Indore">Indore (Industrial Corridor)</option>
                <option value="Delhi">Delhi (NCR Metropolitan)</option>
                <option value="Ahmedabad">Ahmedabad (Western Agglomeration)</option>
                <option value="Bengaluru">Bengaluru (Southern Tech Fringe)</option>
              </select>
            </div>

            {/* Input 1: Agricultural Land Conversion Slider (0-50%, Default 10%) */}
            <div className="range-slider-wrap">
              <div className="range-slider-header">
                <span className="form-label">Agricultural Land Conversion:</span>
                <span className="range-slider-value">{agConversion}%</span>
              </div>
              <input 
                type="range" 
                min="0" 
                max="50" 
                step="1"
                value={agConversion} 
                onChange={(e) => setAgConversion(Number(e.target.value))} 
              />
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10.5px', color: '#94a3b8', marginTop: '2px' }}>
                <span>0% (Strict Retention)</span>
                <span>Default: 10%</span>
                <span>50% (Extreme)</span>
              </div>
            </div>

            {/* Input 2: Population Growth Slider (0-50%, Default 15%) */}
            <div className="range-slider-wrap">
              <div className="range-slider-header">
                <span className="form-label">Population Growth Rate:</span>
                <span className="range-slider-value">{popGrowth}%</span>
              </div>
              <input 
                type="range" 
                min="0" 
                max="50" 
                step="1"
                value={popGrowth} 
                onChange={(e) => setPopGrowth(Number(e.target.value))} 
              />
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10.5px', color: '#94a3b8', marginTop: '2px' }}>
                <span>0%</span>
                <span>Default: 15%</span>
                <span>50%</span>
              </div>
            </div>

            {/* Input 3: Infrastructure Growth Slider (0-50%, Default 20%) */}
            <div className="range-slider-wrap">
              <div className="range-slider-header">
                <span className="form-label">Infrastructure Growth:</span>
                <span className="range-slider-value">{infraGrowth}%</span>
              </div>
              <input 
                type="range" 
                min="0" 
                max="50" 
                step="1"
                value={infraGrowth} 
                onChange={(e) => setInfraGrowth(Number(e.target.value))} 
              />
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10.5px', color: '#94a3b8', marginTop: '2px' }}>
                <span>0%</span>
                <span>Default: 20%</span>
                <span>50%</span>
              </div>
            </div>

            {/* Input 4: Climate Risk Dropdown */}
            <div className="form-group" style={{ marginTop: '12px' }}>
              <label className="form-label">Climate Risk Baseline:</label>
              <select 
                className="form-select"
                value={climateRisk}
                onChange={(e) => setClimateRisk(e.target.value as any)}
              >
                <option value="Low">Low (Resilient Aquifers)</option>
                <option value="Medium">Medium (Seasonal Stress - Baseline)</option>
                <option value="High">High (Critical Over-Exploited Basin)</option>
              </select>
            </div>

            {/* RUN SIMULATION Button */}
            <button 
              className="btn btn-primary btn-lg"
              style={{ width: '100%', marginTop: '16px', background: 'linear-gradient(135deg, #059669 0%, #2563eb 100%)' }}
              onClick={handleRunSimulation}
              disabled={isSimulating}
            >
              {isSimulating ? (
                <span>Simulating...</span>
              ) : (
                <>
                  <Play size={18} fill="white" />
                  <span>RUN SIMULATION</span>
                </>
              )}
            </button>

            <div style={{ fontSize: '11px', color: '#64748b', textAlign: 'center', marginTop: '10px' }}>
              Simulates 5-year spatial equilibrium across revenue parcels
            </div>
          </div>

          {/* Right 2 Columns: Animated Processing State OR Scenario Results */}
          <div className="card" style={{ gridColumn: 'span 2' }}>
            {isSimulating ? (
              /* Animated 5-Step Processing State */
              <div style={{ padding: '40px 20px', textAlign: 'center' }}>
                <div style={{ marginBottom: '24px' }}>
                  <div style={{ width: '48px', height: '48px', margin: '0 auto 16px auto', border: '4px solid #e2e8f0', borderTopColor: '#059669', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }}></div>
                  <h3 style={{ fontSize: '18px', fontWeight: 800, color: '#0f172a' }}>
                    Executing Multi-Criteria Land Policy Simulation...
                  </h3>
                  <p style={{ fontSize: '13px', color: '#64748b', marginTop: '4px' }}>
                    Reconciling cadastral vectors with environmental constraints
                  </p>
                </div>

                {/* 5 Stepper Visual */}
                <div style={{ maxWidth: '440px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '12px', textAlign: 'left' }}>
                  {simulationSteps.map((stepText, idx) => {
                    const isDone = idx < currentStep;
                    const isCurrent = idx === currentStep;

                    return (
                      <div 
                        key={idx}
                        style={{ 
                          display: 'flex', 
                          alignItems: 'center', 
                          gap: '12px',
                          padding: '10px 14px',
                          borderRadius: '8px',
                          background: isCurrent ? '#eff6ff' : (isDone ? '#f0fdf4' : '#f8fafc'),
                          border: isCurrent ? '1px solid #93c5fd' : (isDone ? '1px solid #bbf7d0' : '1px solid #e2e8f0')
                        }}
                      >
                        {isDone ? (
                          <CheckCircle2 size={18} style={{ color: '#059669', flexShrink: 0 }} />
                        ) : isCurrent ? (
                          <span style={{ width: '16px', height: '16px', border: '2px solid #2563eb', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 0.6s linear infinite', display: 'inline-block', flexShrink: 0 }}></span>
                        ) : (
                          <span style={{ width: '16px', height: '16px', borderRadius: '50%', border: '2px solid #cbd5e1', display: 'inline-block', flexShrink: 0 }}></span>
                        )}
                        <span style={{ fontSize: '12.5px', fontWeight: isCurrent ? 700 : (isDone ? 600 : 400), color: isCurrent ? '#1d4ed8' : (isDone ? '#166534' : '#64748b') }}>
                          {stepText}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            ) : result ? (
              /* Scenario Results Display */
              <div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', flexWrap: 'wrap', gap: '10px', borderBottom: '1px solid #e2e8f0', paddingBottom: '12px' }}>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span className="badge badge-green">Simulation Computed</span>
                      <span style={{ fontSize: '11px', color: '#64748b' }}>ID: {result.id}</span>
                    </div>
                    <h2 style={{ fontSize: '18px', fontWeight: 800, color: '#0f172a', marginTop: '2px' }}>
                      Scenario Results: {result.scenario_name} ({result.region})
                    </h2>
                  </div>
                  <button 
                    className="btn btn-sm btn-outline-primary"
                    onClick={handleExportToReport}
                  >
                    <FileText size={14} />
                    <span>Generate Evidence Brief from this Run</span>
                  </button>
                </div>

                {/* Metric Categories Grid */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '20px' }}>
                  {/* Category 1: Land Use Impact */}
                  <div style={{ background: '#f8fafc', padding: '14px', borderRadius: '10px', border: '1px solid #e2e8f0' }}>
                    <div style={{ fontSize: '12.5px', fontWeight: 700, color: '#0f172a', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <Layers size={15} style={{ color: '#059669' }} />
                      <span>Land Use Impact</span>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontSize: '12px', color: '#475569' }}>Agricultural Land:</span>
                        <span style={{ fontSize: '14px', fontWeight: 800, color: '#dc2626', display: 'flex', alignItems: 'center', gap: '2px' }}>
                          <TrendingDown size={14} />
                          {result.land_use_impact["Agricultural Land"]}%
                        </span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontSize: '12px', color: '#475569' }}>Residential Area:</span>
                        <span style={{ fontSize: '14px', fontWeight: 800, color: '#2563eb', display: 'flex', alignItems: 'center', gap: '2px' }}>
                          <TrendingUp size={14} />
                          +{result.land_use_impact["Residential Area"]}%
                        </span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontSize: '12px', color: '#475569' }}>Industrial Sprawl:</span>
                        <span style={{ fontSize: '13px', fontWeight: 700, color: '#d97706' }}>
                          +{result.land_use_impact["Industrial Area"]}%
                        </span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontSize: '12px', color: '#475569' }}>Forest Buffer Deficit:</span>
                        <span style={{ fontSize: '13px', fontWeight: 700, color: '#dc2626' }}>
                          {result.land_use_impact["Forest Buffer"]}%
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Category 2: Environmental Indicators */}
                  <div style={{ background: '#f8fafc', padding: '14px', borderRadius: '10px', border: '1px solid #e2e8f0' }}>
                    <div style={{ fontSize: '12.5px', fontWeight: 700, color: '#0f172a', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <AlertTriangle size={15} style={{ color: '#d97706' }} />
                      <span>Environmental Indicators</span>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontSize: '12px', color: '#475569' }}>Water Stress:</span>
                        <span style={{ fontSize: '14px', fontWeight: 800, color: '#d97706' }}>
                          +{result.environmental_indicators["Water Stress"]}%
                        </span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontSize: '12px', color: '#475569' }}>Green Cover Pressure:</span>
                        <span style={{ fontSize: '14px', fontWeight: 800, color: '#d97706' }}>
                          +{result.environmental_indicators["Green Cover Pressure"]}%
                        </span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontSize: '12px', color: '#475569' }}>Climate Exposure:</span>
                        <span style={{ fontSize: '14px', fontWeight: 800, color: '#dc2626' }}>
                          +{result.environmental_indicators["Climate Exposure"]}%
                        </span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontSize: '12px', color: '#475569' }}>Carbon Sink Deficit:</span>
                        <span style={{ fontSize: '13px', fontWeight: 700, color: '#475569' }}>
                          +{result.environmental_indicators["Carbon Sink Deficit"]}%
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Category 3: Infrastructure Impact */}
                  <div style={{ background: '#f8fafc', padding: '14px', borderRadius: '10px', border: '1px solid #e2e8f0' }}>
                    <div style={{ fontSize: '12.5px', fontWeight: 700, color: '#0f172a', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <BarChart3 size={15} style={{ color: '#2563eb' }} />
                      <span>Infrastructure Impact</span>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontSize: '12px', color: '#475569' }}>Road Demand:</span>
                        <span style={{ fontSize: '14px', fontWeight: 800, color: '#2563eb' }}>
                          +{result.infrastructure_impact["Road Demand"]}%
                        </span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontSize: '12px', color: '#475569' }}>Public Service Demand:</span>
                        <span style={{ fontSize: '14px', fontWeight: 800, color: '#2563eb' }}>
                          +{result.infrastructure_impact["Public Service Demand"]}%
                        </span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontSize: '12px', color: '#475569' }}>Sewerage Load:</span>
                        <span style={{ fontSize: '13px', fontWeight: 700, color: '#475569' }}>
                          +{result.infrastructure_impact["Sewerage Network Pressure"]}%
                        </span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontSize: '12px', color: '#475569' }}>Grid Power Demand:</span>
                        <span style={{ fontSize: '13px', fontWeight: 700, color: '#475569' }}>
                          +{result.infrastructure_impact["Grid Power Demand"]}%
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Affected Spatial Zones */}
                <div style={{ marginBottom: '16px' }}>
                  <div style={{ fontSize: '13px', fontWeight: 700, color: '#0f172a', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <MapPin size={15} style={{ color: '#dc2626' }} />
                    <span>High-Vulnerability Spatial Zones in {result.region}:</span>
                  </div>
                  <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                    {result.affected_zones?.map((zone, i) => (
                      <span key={i} className="badge badge-gray" style={{ border: '1px solid #cbd5e1', padding: '5px 10px', fontSize: '12px' }}>
                        📍 {zone}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Model Assumptions Note */}
                <div style={{ background: '#f1f5f9', padding: '10px 14px', borderRadius: '8px', fontSize: '11.5px', color: '#475569', marginBottom: '14px' }}>
                  <strong>Model Assumptions Applied:</strong> Elasticity multiplier 0.72; Climate coefficient {climateRisk === 'High' ? '1.55x' : '1.25x'}; 5-year planning horizon; Calibrated against CGWB Central India borehole data.
                </div>

                {/* MANDATORY SCIENTIFIC RESPONSIBILITY DISCLAIMER */}
                <div className="disclaimer-box">
                  <strong>SCIENTIFIC INTEGRITY NOTICE:</strong> "Scenario-based estimates generated from available data and model assumptions. Results are intended for decision support and should not be interpreted as guaranteed predictions."
                </div>
              </div>
            ) : null}
          </div>
        </div>
      )}

      {/* Tab 2: Scenario Comparison (5% vs 10% vs 20%) */}
      {activeTab === 'comparison' && (
        <div>
          <div className="card" style={{ marginBottom: '20px' }}>
            <h2 style={{ fontSize: '18px', fontWeight: 800, color: '#0f172a', marginBottom: '4px' }}>
              Multi-Scenario Policy Trade-Off Comparison (Bhopal Metropolitan Area)
            </h2>
            <p style={{ fontSize: '13px', color: '#64748b' }}>
              Evaluate how conservative agricultural retention (5%) compares with baseline master plan (10%) and rapid urban conversion (20%).
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px', marginBottom: '24px' }}>
            {/* Scenario A (5% Conversion) */}
            <div className="card" style={{ borderTop: '4px solid #059669' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span className="badge badge-green">Scenario A (Conservative)</span>
                <span style={{ fontSize: '11px', color: '#64748b' }}>Ag Conv: 5%</span>
              </div>
              <h3 style={{ fontSize: '16px', fontWeight: 800, color: '#0f172a', marginBottom: '12px' }}>
                Eco-Retention Model
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '12.5px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Agricultural Impact:</span>
                  <strong style={{ color: '#059669' }}>-4.2%</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Urban Growth:</span>
                  <strong style={{ color: '#2563eb' }}>+6.9%</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Water Stress:</span>
                  <strong style={{ color: '#059669' }}>+3.8% (Mild)</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Climate Exposure:</span>
                  <strong style={{ color: '#059669' }}>+3.6%</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Infra Pressure:</span>
                  <strong style={{ color: '#475569' }}>+8.5%</strong>
                </div>
              </div>
              <div style={{ marginTop: '14px', paddingTop: '10px', borderTop: '1px solid #e2e8f0', fontSize: '11.5px', color: '#64748b' }}>
                Maximum preservation of Bhoj catchment and prime agrarian parcels.
              </div>
            </div>

            {/* Scenario B (10% Conversion - Baseline) */}
            <div className="card" style={{ borderTop: '4px solid #2563eb', boxShadow: '0 4px 12px rgba(37, 99, 235, 0.12)' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span className="badge badge-blue">Scenario B (Balanced)</span>
                <span style={{ fontSize: '11px', color: '#64748b' }}>Ag Conv: 10%</span>
              </div>
              <h3 style={{ fontSize: '16px', fontWeight: 800, color: '#0f172a', marginBottom: '12px' }}>
                Master Plan 2031 Trajectory
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '12.5px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Agricultural Impact:</span>
                  <strong style={{ color: '#d97706' }}>-8.4%</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Urban Growth:</span>
                  <strong style={{ color: '#2563eb' }}>+11.2%</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Water Stress:</span>
                  <strong style={{ color: '#d97706' }}>+6.8% (Moderate)</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Climate Exposure:</span>
                  <strong style={{ color: '#d97706' }}>+7.1%</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Infra Pressure:</span>
                  <strong style={{ color: '#2563eb' }}>+12.0%</strong>
                </div>
              </div>
              <div style={{ marginTop: '14px', paddingTop: '10px', borderTop: '1px solid #e2e8f0', fontSize: '11.5px', color: '#64748b' }}>
                Moderate housing expansion with manageable municipal capital expenditure.
              </div>
            </div>

            {/* Scenario C (20% Conversion) */}
            <div className="card" style={{ borderTop: '4px solid #dc2626' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span className="badge badge-red">Scenario C (Intensive)</span>
                <span style={{ fontSize: '11px', color: '#64748b' }}>Ag Conv: 20%</span>
              </div>
              <h3 style={{ fontSize: '16px', fontWeight: 800, color: '#0f172a', marginBottom: '12px' }}>
                Rapid Expressway Sprawl
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '12.5px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Agricultural Impact:</span>
                  <strong style={{ color: '#dc2626' }}>-16.8% (Severe)</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Urban Growth:</span>
                  <strong style={{ color: '#2563eb' }}>+21.4%</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Water Stress:</span>
                  <strong style={{ color: '#dc2626' }}>+15.6% (Critical)</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Climate Exposure:</span>
                  <strong style={{ color: '#dc2626' }}>+14.5%</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Infra Pressure:</span>
                  <strong style={{ color: '#dc2626' }}>+20.4%</strong>
                </div>
              </div>
              <div style={{ marginTop: '14px', paddingTop: '10px', borderTop: '1px solid #e2e8f0', fontSize: '11.5px', color: '#64748b' }}>
                Severe aquifer depletion risk; requires statutory urban growth boundary.
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'center' }}>
            <button 
              className="btn btn-primary btn-lg"
              onClick={handleExportToReport}
            >
              <FileText size={16} />
              <span>Compile Scenario Comparison into Decision Brief</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
