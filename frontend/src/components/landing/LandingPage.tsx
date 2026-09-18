import React from 'react';
import { 
  Layers, 
  MapPin, 
  Sparkles, 
  SlidersHorizontal, 
  ShieldCheck, 
  ArrowRight, 
  Database, 
  FileText, 
  Compass,
  CheckCircle2
} from 'lucide-react';

interface LandingPageProps {
  onEnterPlatform: () => void;
  onOpenLogin: () => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onEnterPlatform, onOpenLogin }) => {
  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#0f172a', color: '#ffffff', display: 'flex', flexDirection: 'column' }}>
      {/* Top Gov Nav */}
      <header style={{ height: '70px', borderBottom: '1px solid rgba(255, 255, 255, 0.1)', padding: '0 40px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ width: '38px', height: '38px', borderRadius: '8px', background: 'linear-gradient(135deg, #059669 0%, #2563eb 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontWeight: 800, fontSize: '18px' }}>
            BI
          </div>
          <div>
            <div style={{ fontSize: '18px', fontWeight: 800, letterSpacing: '-0.3px', color: '#ffffff' }}>BHUMI INSIGHT</div>
            <div style={{ fontSize: '11px', color: '#94a3b8' }}>National Land Governance Intelligence Platform</div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span className="badge badge-green" style={{ background: 'rgba(16, 185, 129, 0.15)', color: '#34d399', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
            Smart India Hackathon 2026 • PS26019 Prototype
          </span>
          <button 
            className="btn btn-secondary" 
            style={{ background: 'transparent', color: '#ffffff', borderColor: 'rgba(255, 255, 255, 0.2)' }}
            onClick={onOpenLogin}
          >
            Sign In / Demo Roles
          </button>
          <button 
            className="btn btn-primary"
            onClick={onEnterPlatform}
          >
            <span>Launch Platform</span>
            <ArrowRight size={15} />
          </button>
        </div>
      </header>

      {/* Hero Section */}
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', padding: '60px 40px', maxWidth: '1200px', margin: '0 auto', width: '100%' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 0.8fr', gap: '48px', alignItems: 'center' }}>
          {/* Left Column Text */}
          <div>
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '6px 14px', borderRadius: '9999px', background: 'rgba(37, 99, 235, 0.15)', border: '1px solid rgba(59, 130, 246, 0.3)', color: '#60a5fa', fontSize: '12px', fontWeight: 700, marginBottom: '20px' }}>
              <Sparkles size={14} />
              <span>National Digital Platform for Research, Policy Innovation & Evidence-Based Land Governance</span>
            </div>

            <h1 style={{ fontSize: '46px', fontWeight: 800, lineHeight: 1.15, letterSpacing: '-1px', color: '#ffffff', marginBottom: '16px' }}>
              BHUMI INSIGHT
            </h1>

            <h2 style={{ fontSize: '24px', fontWeight: 600, color: '#34d399', marginBottom: '20px', letterSpacing: '-0.3px' }}>
              "From Land Data to Policy Intelligence."
            </h2>

            <p style={{ fontSize: '16px', color: '#cbd5e1', lineHeight: 1.6, maxWidth: '620px', marginBottom: '32px' }}>
              An AI-powered national platform connecting land research, geospatial intelligence, datasets and policy simulation for evidence-based land governance. 
              Positioned as an intelligence and research layer that converts authorized land, GIS, climate, and socioeconomic datasets into actionable insights.
            </p>

            {/* CTAs */}
            <div style={{ display: 'flex', gap: '14px', flexWrap: 'wrap' }}>
              <button 
                className="btn btn-primary btn-lg"
                style={{ padding: '14px 28px', fontSize: '16px', background: 'linear-gradient(135deg, #059669 0%, #2563eb 100%)' }}
                onClick={onEnterPlatform}
              >
                <span>Explore Platform</span>
                <ArrowRight size={18} />
              </button>
              <button 
                className="btn btn-secondary btn-lg"
                style={{ padding: '14px 28px', fontSize: '16px', background: 'rgba(255, 255, 255, 0.08)', color: '#ffffff', borderColor: 'rgba(255, 255, 255, 0.2)' }}
                onClick={onOpenLogin}
              >
                <span>View Demo (Choose Role)</span>
              </button>
            </div>
          </div>

          {/* Right Column: Subtle India / Map Cadastral Visual */}
          <div style={{ background: 'rgba(30, 41, 59, 0.7)', borderRadius: '16px', border: '1px solid rgba(255, 255, 255, 0.1)', padding: '24px', boxShadow: '0 20px 40px rgba(0,0,0,0.4)', position: 'relative' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
              <div style={{ fontSize: '13px', fontWeight: 700, color: '#34d399' }}>
                Spatial Cadastre & Transition Simulation
              </div>
              <span className="badge badge-gray" style={{ background: 'rgba(255, 255, 255, 0.1)', color: '#cbd5e1' }}>
                Focus: Bhopal / MP
              </span>
            </div>

            {/* SVG Visual Grid Representation */}
            <div style={{ background: '#090d16', borderRadius: '10px', height: '240px', padding: '16px', border: '1px solid rgba(255, 255, 255, 0.08)', position: 'relative', overflow: 'hidden' }}>
              <svg width="100%" height="100%" viewBox="0 0 360 200">
                {/* Cadastral Grid Polygons */}
                <rect x="20" y="20" width="80" height="60" fill="#059669" opacity="0.3" stroke="#10b981" strokeWidth="1.5" />
                <rect x="110" y="20" width="100" height="60" fill="#2563eb" opacity="0.3" stroke="#3b82f6" strokeWidth="1.5" />
                <rect x="220" y="20" width="120" height="60" fill="#d97706" opacity="0.25" stroke="#f59e0b" strokeWidth="1.5" />

                <rect x="20" y="90" width="120" height="90" fill="#059669" opacity="0.4" stroke="#10b981" strokeWidth="1.5" />
                <rect x="150" y="90" width="90" height="90" fill="#0284c7" opacity="0.4" stroke="#38bdf8" strokeWidth="1.5" />
                <rect x="250" y="90" width="90" height="90" fill="#dc2626" opacity="0.25" stroke="#ef4444" strokeWidth="1.5" />

                {/* Corridor Highway Line */}
                <path d="M 10 180 Q 160 80 350 40" fill="none" stroke="#ef4444" strokeWidth="3" strokeDasharray="5 4" />

                {/* Node Markers */}
                <circle cx="150" cy="90" r="6" fill="#34d399" />
                <circle cx="210" cy="110" r="5" fill="#60a5fa" />
                <circle cx="280" cy="60" r="5" fill="#f59e0b" />

                <text x="160" y="95" fill="#ffffff" fontSize="11" fontWeight="700">Bhopal Node</text>
                <text x="220" y="115" fill="#94a3b8" fontSize="9">Upper Lake Buffer</text>
              </svg>
            </div>

            <div style={{ marginTop: '16px', display: 'flex', justifyContent: 'space-between', fontSize: '11.5px', color: '#94a3b8' }}>
              <span>Verified Data Sources: <strong>1,245</strong></span>
              <span>Research Papers: <strong>12,540</strong></span>
              <span>Policy Scenarios: <strong>342</strong></span>
            </div>
          </div>
        </div>

        {/* 5-Step Workflow Banner */}
        <div style={{ marginTop: '50px', background: 'rgba(255, 255, 255, 0.04)', borderRadius: '12px', border: '1px solid rgba(255, 255, 255, 0.1)', padding: '20px 28px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
          <div style={{ fontSize: '14px', fontWeight: 700, color: '#f8fafc' }}>
            Complete Evidence-Based Architecture:
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
            <span style={{ padding: '6px 14px', borderRadius: '9999px', background: 'rgba(5, 150, 105, 0.2)', border: '1px solid #059669', color: '#34d399', fontSize: '12.5px', fontWeight: 700 }}>
              1. DATA
            </span>
            <span style={{ color: '#64748b' }}>→</span>
            <span style={{ padding: '6px 14px', borderRadius: '9999px', background: 'rgba(37, 99, 235, 0.2)', border: '1px solid #2563eb', color: '#60a5fa', fontSize: '12.5px', fontWeight: 700 }}>
              2. KNOWLEDGE
            </span>
            <span style={{ color: '#64748b' }}>→</span>
            <span style={{ padding: '6px 14px', borderRadius: '9999px', background: 'rgba(217, 119, 6, 0.2)', border: '1px solid #d97706', color: '#fbbf24', fontSize: '12.5px', fontWeight: 700 }}>
              3. INSIGHT
            </span>
            <span style={{ color: '#64748b' }}>→</span>
            <span style={{ padding: '6px 14px', borderRadius: '9999px', background: 'rgba(16, 185, 129, 0.2)', border: '1px solid #10b981', color: '#6ee7b7', fontSize: '12.5px', fontWeight: 700 }}>
              4. SIMULATION
            </span>
            <span style={{ color: '#64748b' }}>→</span>
            <span style={{ padding: '6px 14px', borderRadius: '9999px', background: 'rgba(59, 130, 246, 0.2)', border: '1px solid #3b82f6', color: '#93c5fd', fontSize: '12.5px', fontWeight: 700 }}>
              5. POLICY
            </span>
          </div>
        </div>
      </main>
    </div>
  );
};
