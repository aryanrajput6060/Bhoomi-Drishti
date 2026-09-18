import React, { useState } from 'react';
import { 
  Sparkles, 
  Search, 
  BookOpen, 
  FileText, 
  Database, 
  CheckCircle2, 
  ExternalLink, 
  Layers, 
  Compass,
  ArrowRight,
  ShieldCheck,
  Building2,
  MapPin,
  SlidersHorizontal
} from 'lucide-react';
import { executeAISearch } from '../../services/api';
import { DEMO_RESEARCH_PAPERS } from '../../data/mockData';
import { ResearchPaper } from '../../types';

interface AIResearchProps {
  onNavigate: (tab: string) => void;
  onOpenEvidenceModal: (paper: ResearchPaper) => void;
}

export const AIResearch: React.FC<AIResearchProps> = ({ onNavigate, onOpenEvidenceModal }) => {
  const [searchQuery, setSearchQuery] = useState('What factors are driving urban land conversion in Bhopal?');
  const [loading, setLoading] = useState(false);
  const [searchResult, setSearchResult] = useState<any>(null);

  const sampleQueries = [
    "What factors are driving urban land conversion in Bhopal?",
    "How does impervious surface expansion impact Upper Lake Bhoj wetland?",
    "What are the statutory legal limits under MP Land Revenue Code 2022 for agricultural diversion?",
    "Evaluate groundwater stress trends along the Indore-Bhopal industrial corridor."
  ];

  const handleRunSearch = async (queryText?: string) => {
    const q = queryText || searchQuery;
    if (!q.trim()) return;
    setLoading(true);

    try {
      const res = await executeAISearch(q);
      setSearchResult(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container">
      {/* Page Header */}
      <div style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
          <span className="badge badge-blue">Evidence-Backed Retrieval Augmented Generation (RAG)</span>
          <span style={{ fontSize: '11px', color: '#64748b' }}>National Digital Land Repository</span>
        </div>
        <h1 style={{ fontSize: '26px', fontWeight: 800, color: '#0f172a' }}>AI RESEARCH MODULE</h1>
        <p style={{ fontSize: '14px', color: '#64748b', marginTop: '4px' }}>
          Synthesize empirical research papers, GIS telemetry, cadastral databases, and policy gazettes into verifiable decision intelligence.
        </p>
      </div>

      {/* Main Search Box */}
      <div className="card" style={{ marginBottom: '24px', background: '#ffffff', border: '1px solid #cbd5e1', boxShadow: '0 4px 12px -2px rgba(15, 23, 42, 0.06)' }}>
        <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
          <Search size={22} style={{ position: 'absolute', left: '16px', color: '#2563eb' }} />
          <input 
            type="text"
            className="form-input"
            style={{ 
              padding: '16px 140px 16px 50px', 
              fontSize: '15.5px', 
              fontWeight: 500,
              borderRadius: '10px',
              border: '1px solid #93c5fd'
            }}
            placeholder="Ask anything about land governance, urban expansion, cadastral laws, or ecology..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter') handleRunSearch(); }}
          />
          <button 
            className="btn btn-primary"
            style={{ position: 'absolute', right: '10px', padding: '10px 20px', borderRadius: '8px' }}
            onClick={() => handleRunSearch()}
            disabled={loading}
          >
            {loading ? (
              <span>Analyzing...</span>
            ) : (
              <>
                <Sparkles size={16} />
                <span>Synthesize</span>
              </>
            )}
          </button>
        </div>

        {/* Example Query Pills */}
        <div style={{ marginTop: '14px', display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '12px', fontWeight: 600, color: '#475569' }}>SIH Demo Queries:</span>
          {sampleQueries.map((q, idx) => (
            <button
              key={idx}
              style={{
                background: searchQuery === q ? '#eff6ff' : '#f1f5f9',
                border: searchQuery === q ? '1px solid #93c5fd' : '1px solid #e2e8f0',
                color: searchQuery === q ? '#1d4ed8' : '#334155',
                fontSize: '11.5px',
                padding: '4px 10px',
                borderRadius: '9999px',
                cursor: 'pointer',
                fontWeight: 500,
                textAlign: 'left'
              }}
              onClick={() => {
                setSearchQuery(q);
                handleRunSearch(q);
              }}
            >
              {q}
            </button>
          ))}
        </div>
      </div>

      {/* Loading Skeleton */}
      {loading && (
        <div className="card" style={{ padding: '30px', textAlign: 'center' }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '10px', color: '#2563eb', fontWeight: 700 }}>
            <span style={{ width: '20px', height: '20px', border: '3px solid #bfdbfe', borderTopColor: '#2563eb', borderRadius: '50%', animation: 'spin 1s linear infinite' }}></span>
            <span>Synthesizing peer-reviewed sources, cadastral layers, and policy gazettes...</span>
          </div>
        </div>
      )}

      {/* Search Results Display */}
      {searchResult && !loading && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {/* AI Structured Answer Card */}
          <div className="card" style={{ borderLeft: '4px solid #2563eb', background: '#ffffff' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', flexWrap: 'wrap', gap: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <div style={{ width: '32px', height: '32px', borderRadius: '8px', backgroundColor: '#0f172a', color: '#34d399', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Sparkles size={18} />
                </div>
                <div>
                  <h2 style={{ fontSize: '17px', fontWeight: 800, color: '#0f172a' }}>
                    Evidence-Backed Synthesis
                  </h2>
                  <div style={{ fontSize: '11.5px', color: '#64748b' }}>
                    Retrieved across 12,540 research papers, 1,245 datasets & statutory master plans
                  </div>
                </div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span className="badge badge-green">Confidence Score: {(searchResult.confidence_score * 100).toFixed(0)}%</span>
                <span className="badge badge-blue">Verified Provenance</span>
              </div>
            </div>

            {/* Core Answer */}
            <p style={{ fontSize: '14.5px', color: '#1e293b', lineHeight: 1.6, marginBottom: '18px', padding: '12px 16px', backgroundColor: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
              {searchResult.answer}
            </p>

            {/* Key Drivers Section */}
            <div style={{ marginBottom: '18px' }}>
              <div style={{ fontSize: '13px', fontWeight: 700, color: '#0f172a', textTransform: 'uppercase', letterSpacing: '0.4px', marginBottom: '8px' }}>
                Key Empirical Drivers Identified:
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '10px' }}>
                {searchResult.key_drivers?.map((driver: string, idx: number) => (
                  <div key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', padding: '8px 12px', background: '#f1f5f9', borderRadius: '6px', fontSize: '12.5px', color: '#334155' }}>
                    <CheckCircle2 size={16} style={{ color: '#059669', flexShrink: 0, marginTop: '2px' }} />
                    <span>{driver}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Policy Implications */}
            <div>
              <div style={{ fontSize: '13px', fontWeight: 700, color: '#0f172a', textTransform: 'uppercase', letterSpacing: '0.4px', marginBottom: '8px' }}>
                Evidence-Based Policy Considerations:
              </div>
              <ul style={{ paddingLeft: '20px', fontSize: '13px', color: '#334155', lineHeight: 1.5 }}>
                {searchResult.policy_implications?.map((imp: string, idx: number) => (
                  <li key={idx} style={{ marginBottom: '4px' }}>{imp}</li>
                ))}
              </ul>
            </div>

            {/* Next Steps in Demo Workflow */}
            <div style={{ marginTop: '20px', paddingTop: '16px', borderTop: '1px solid #e2e8f0', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '10px' }}>
              <div style={{ fontSize: '12.5px', color: '#64748b' }}>
                Next in Primary Demo Flow: <strong>Inspect GIS Spatial Footprint for Bhopal District</strong>
              </div>
              <button 
                className="btn btn-sm btn-primary"
                onClick={() => onNavigate('gis-intelligence')}
              >
                <span>Proceed to GIS Intelligence</span>
                <ArrowRight size={14} />
              </button>
            </div>
          </div>

          {/* Sources Used Section (CRITICAL FOR EVIDENCE-BACKED AI) */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
              <div>
                <h3 style={{ fontSize: '16px', fontWeight: 800, color: '#0f172a' }}>
                  Sources & Supporting Evidence Utilized ({searchResult.sources_used?.length || 0})
                </h3>
                <p style={{ fontSize: '12px', color: '#64748b' }}>
                  All citations are linked directly to academic institutions, government portals, or telemetry records.
                </p>
              </div>
              <span className="badge badge-gray">Multi-Agent RAG Pipeline</span>
            </div>

            <div className="grid-2">
              {searchResult.sources_used?.map((source: ResearchPaper) => (
                <div key={source.id} className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '8px', marginBottom: '8px' }}>
                      <span className="badge badge-green">{source.relevance}% Relevance</span>
                      <span className="badge badge-gray">{source.year}</span>
                    </div>
                    <div style={{ fontWeight: 700, fontSize: '14px', color: '#0f172a', lineHeight: 1.3, marginBottom: '6px' }}>
                      {source.title}
                    </div>
                    <div style={{ fontSize: '12px', color: '#475569', marginBottom: '8px' }}>
                      {source.authors} • <strong>{source.organization}</strong>
                    </div>
                    <p style={{ fontSize: '12px', color: '#64748b', lineHeight: 1.4, marginBottom: '12px' }}>
                      {source.abstract}
                    </p>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingTop: '10px', borderTop: '1px solid #f1f5f9' }}>
                    <span style={{ fontSize: '11px', color: '#64748b', display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <MapPin size={12} />
                      {source.region}
                    </span>
                    <button 
                      className="btn btn-sm btn-outline-primary"
                      onClick={() => onOpenEvidenceModal(source)}
                    >
                      <span>Open Document Evidence</span>
                      <ExternalLink size={12} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
