import React from 'react';
import { Compass, CheckCircle2, ArrowRight, X, Play } from 'lucide-react';

interface DemoGuideModalProps {
  isOpen: boolean;
  onClose: () => void;
  onJumpToStep: (tab: string) => void;
}

export const DemoGuideModal: React.FC<DemoGuideModalProps> = ({ isOpen, onClose, onJumpToStep }) => {
  if (!isOpen) return null;

  const steps = [
    { num: 1, label: "Login & Role Context", desc: "Select 'Policymaker (Dr. Sharma)' to examine executive decision tools.", tab: "dashboard" },
    { num: 2, label: "Dashboard Macro View", desc: "Inspect Land Use Trend (2020-2026), Regional Risk Map, and AI Insight Alert.", tab: "dashboard" },
    { num: 3, label: "AI Research & Evidence", desc: "Query 'What factors are driving urban land conversion in Bhopal?' and inspect visible citations.", tab: "ai-research" },
    { num: 4, label: "GIS Geospatial Intelligence", desc: "Toggle Land Use, Climate, and Infrastructure layers over Bhopal District; click district marker.", tab: "gis-intelligence" },
    { num: 5, label: "Policy Simulator (Hero Feature)", desc: "Set Agricultural Conversion to 10%, click RUN SIMULATION, view 5-step animated execution pipeline.", tab: "policy-simulator" },
    { num: 6, label: "Scenario Comparison", desc: "Compare Scenario A (5%) vs Scenario B (10%) vs Scenario C (20%) across 5 indicators.", tab: "policy-simulator" },
    { num: 7, label: "Report Generator", desc: "Generate 9-section Cabinet-ready Evidence Brief and export to PDF/Print.", tab: "reports" }
  ];

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-dialog" style={{ maxWidth: '640px' }} onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ width: '32px', height: '32px', borderRadius: '8px', backgroundColor: '#eff6ff', color: '#2563eb', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Compass size={18} />
            </div>
            <div>
              <h3 style={{ fontSize: '18px', fontWeight: 800, color: '#0f172a' }}>
                SIH 2026 Evaluation Demo Flow (3–4 Min Guide)
              </h3>
              <div style={{ fontSize: '12px', color: '#64748b' }}>
                Problem Statement PS26019 • National Land Governance Intelligence
              </div>
            </div>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', fontSize: '20px', cursor: 'pointer', color: '#64748b' }}>
            <X size={18} />
          </button>
        </div>

        <p style={{ fontSize: '13px', color: '#475569', marginBottom: '16px' }}>
          Follow this structured sequence to demonstrate the entire <strong>DATA → KNOWLEDGE → INSIGHT → SIMULATION → POLICY</strong> workflow to evaluators:
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '20px' }}>
          {steps.map((s) => (
            <div 
              key={s.num}
              style={{ 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'space-between',
                padding: '10px 14px', 
                borderRadius: '8px', 
                border: '1px solid #e2e8f0',
                background: '#f8fafc'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <span style={{ width: '24px', height: '24px', borderRadius: '50%', backgroundColor: '#0f172a', color: '#34d399', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 800, fontSize: '11px' }}>
                  {s.num}
                </span>
                <div>
                  <div style={{ fontWeight: 700, fontSize: '13px', color: '#0f172a' }}>{s.label}</div>
                  <div style={{ fontSize: '11.5px', color: '#64748b' }}>{s.desc}</div>
                </div>
              </div>

              <button 
                className="btn btn-sm btn-outline-primary"
                onClick={() => {
                  onJumpToStep(s.tab);
                  onClose();
                }}
              >
                <span>Jump</span>
                <ArrowRight size={12} />
              </button>
            </div>
          ))}
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
          <button className="btn btn-primary" onClick={onClose}>
            Close Guide
          </button>
        </div>
      </div>
    </div>
  );
};
