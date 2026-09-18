import React, { useState } from 'react';
import { 
  FileSearch, 
  Upload, 
  FileText, 
  CheckCircle2, 
  AlertCircle, 
  BookOpen, 
  Scale, 
  Layers, 
  Sparkles, 
  ArrowRight,
  HelpCircle,
  Clock
} from 'lucide-react';

interface RAGAssistantProps {
  onNavigate: (tab: string) => void;
}

export const RAGAssistant: React.FC<RAGAssistantProps> = ({ onNavigate }) => {
  const [selectedFile, setSelectedFile] = useState<string>('Urban Land Expansion Study.pdf');
  const [isProcessing, setIsProcessing] = useState(false);
  const [activeTab, setActiveTab] = useState<'summary' | 'findings' | 'gaps' | 'policies'>('summary');
  const [customQuestion, setCustomQuestion] = useState('');
  const [chatLog, setChatLog] = useState<Array<{ role: 'user' | 'assistant', text: string }>>([
    {
      role: 'assistant',
      text: "Document 'Urban Land Expansion Study.pdf' successfully parsed with 42 extracted tables and vector embeddings. Ask any analytical question or view synthesized findings."
    }
  ]);

  const handleUploadSample = (filename: string) => {
    setSelectedFile(filename);
    setIsProcessing(true);
    setTimeout(() => {
      setIsProcessing(false);
      setChatLog(prev => [
        ...prev,
        { role: 'assistant', text: `Completed semantic ingestion of '${filename}'. 14 key findings and 3 statutory policy intersections indexed.` }
      ]);
    }, 800);
  };

  const handleSendQuestion = (e: React.FormEvent) => {
    e.preventDefault();
    if (!customQuestion.trim()) return;

    const userQ = customQuestion;
    setCustomQuestion('');
    setChatLog(prev => [...prev, { role: 'user', text: userQ }]);

    setTimeout(() => {
      let reply = `Based on section 4.2 of '${selectedFile}': The study calculates an annual agrarian loss rate of 1.6% per annum across Class-I soils, primarily attributed to unapproved residential layouts along arterial highway bypasses.`;
      if (userQ.toLowerCase().includes('water') || userQ.toLowerCase().includes('lake')) {
        reply = `Page 18 notes that runoff imperviousness increased by 38% in the Upper Lake sub-catchment, reducing base groundwater infiltration from 142mm to 88mm annually.`;
      }
      setChatLog(prev => [...prev, { role: 'assistant', text: reply }]);
    }, 600);
  };

  return (
    <div className="page-container">
      {/* Header */}
      <div style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
          <span className="badge badge-green">Document Intelligence & Synthesis</span>
          <span style={{ fontSize: '11.5px', color: '#64748b' }}>PDF / Research Paper Parser</span>
        </div>
        <h1 style={{ fontSize: '26px', fontWeight: 800, color: '#0f172a' }}>RAG RESEARCH ASSISTANT</h1>
        <p style={{ fontSize: '14px', color: '#64748b', marginTop: '4px' }}>
          Upload land-governance studies, government gazettes, and master plans for automatic extraction of findings, methodology, and policy intersections.
        </p>
      </div>

      {/* Main Grid: Upload & Document Selector + Synthesis Panel */}
      <div className="grid-3" style={{ marginBottom: '24px' }}>
        {/* Left Column: Upload & Files */}
        <div className="card" style={{ gridColumn: 'span 1' }}>
          <h2 style={{ fontSize: '15px', fontWeight: 700, marginBottom: '12px' }}>Document Ingestion</h2>

          {/* Drag and drop mock zone */}
          <div 
            style={{ 
              border: '2px dashed #cbd5e1', 
              borderRadius: '8px', 
              padding: '24px 16px', 
              textAlign: 'center', 
              backgroundColor: '#f8fafc',
              cursor: 'pointer',
              marginBottom: '16px'
            }}
            onClick={() => handleUploadSample('Urban Land Expansion Study.pdf')}
          >
            <Upload size={32} style={{ color: '#2563eb', margin: '0 auto 8px auto' }} />
            <div style={{ fontWeight: 600, fontSize: '13px', color: '#0f172a' }}>Drop PDF or Report here</div>
            <div style={{ fontSize: '11px', color: '#64748b', marginTop: '4px' }}>Supports PDF, DOCX, GeoTIFF reports (Max 50MB)</div>
          </div>

          <div style={{ fontSize: '12px', fontWeight: 700, color: '#475569', marginBottom: '8px', textTransform: 'uppercase' }}>
            Loaded Studies (Click to Analyze):
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {[
              { name: 'Urban Land Expansion Study.pdf', size: '4.8 MB', pages: 36, active: selectedFile === 'Urban Land Expansion Study.pdf' },
              { name: 'Upper Lake Catchment Hydrology Report.pdf', size: '12.1 MB', pages: 84, active: selectedFile === 'Upper Lake Catchment Hydrology Report.pdf' },
              { name: 'Bhopal Master Plan 2031 Draft Gazetted Notice.pdf', size: '8.4 MB', pages: 112, active: selectedFile === 'Bhopal Master Plan 2031 Draft Gazetted Notice.pdf' },
            ].map((f, i) => (
              <div 
                key={i}
                style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'space-between', 
                  padding: '10px 12px', 
                  borderRadius: '6px', 
                  border: f.active ? '1px solid #93c5fd' : '1px solid #e2e8f0',
                  background: f.active ? '#eff6ff' : '#ffffff',
                  cursor: 'pointer'
                }}
                onClick={() => handleUploadSample(f.name)}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <FileText size={16} style={{ color: f.active ? '#2563eb' : '#64748b' }} />
                  <div>
                    <div style={{ fontSize: '12px', fontWeight: 600, color: '#0f172a' }}>{f.name}</div>
                    <div style={{ fontSize: '10.5px', color: '#64748b' }}>{f.size} • {f.pages} pages</div>
                  </div>
                </div>
                {f.active && <CheckCircle2 size={16} style={{ color: '#2563eb' }} />}
              </div>
            ))}
          </div>
        </div>

        {/* Right 2 Columns: Analysis Breakdown */}
        <div className="card" style={{ gridColumn: 'span 2' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', borderBottom: '1px solid #e2e8f0', paddingBottom: '12px' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span className="badge badge-green">Parsed Document</span>
                <span style={{ fontSize: '14px', fontWeight: 700, color: '#0f172a' }}>{selectedFile}</span>
              </div>
              <div style={{ fontSize: '11.5px', color: '#64748b', marginTop: '2px' }}>
                Author: Maulana Azad National Institute of Technology (MANIT) • 2024
              </div>
            </div>
            <div style={{ display: 'flex', gap: '6px' }}>
              <button 
                className={`btn btn-sm ${activeTab === 'summary' ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => setActiveTab('summary')}
              >
                Summary & Findings
              </button>
              <button 
                className={`btn btn-sm ${activeTab === 'gaps' ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => setActiveTab('gaps')}
              >
                Research Gaps
              </button>
              <button 
                className={`btn btn-sm ${activeTab === 'policies' ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => setActiveTab('policies')}
              >
                Relevant Policies
              </button>
            </div>
          </div>

          {isProcessing ? (
            <div style={{ padding: '40px', textAlign: 'center', color: '#2563eb' }}>
              Analyzing document structure and vectorizing citations...
            </div>
          ) : (
            <div>
              {activeTab === 'summary' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
                  <div>
                    <h3 style={{ fontSize: '14px', fontWeight: 700, color: '#0f172a', marginBottom: '6px' }}>
                      Document Summary:
                    </h3>
                    <p style={{ fontSize: '13px', color: '#334155', lineHeight: 1.6, background: '#f8fafc', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                      This empirical research study investigates multi-decadal land use transition dynamics across Bhopal metropolitan fringes. 
                      Utilizing Sentinel-2 telemetry combined with revenue Khasra parcel registers, the authors evaluate the conversion pressure exerted on prime 
                      agricultural soil, identifying key arterial transport corridors as the primary spatial vectors of informal subdivision.
                    </p>
                  </div>

                  <div>
                    <h3 style={{ fontSize: '14px', fontWeight: 700, color: '#0f172a', marginBottom: '8px' }}>
                      Key Empirical Findings:
                    </h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                      {[
                        "14.8% decrease in net cultivated arable land across the primary 15km urban fringe between 2015 and 2024.",
                        "Impervious surface expansion increased stormwater surface runoff coefficient by 38%, diminishing aquifer recharge.",
                        "Fragmented cadastral holdings (<1.5 acres) exhibit 3.4x higher conversion probability compared to consolidated holdings (>5 acres).",
                        "Informal developer layouts account for 54% of new residential development lacking municipal drainage hookups."
                      ].map((item, idx) => (
                        <div key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', fontSize: '12.5px', color: '#1e293b' }}>
                          <CheckCircle2 size={16} style={{ color: '#059669', flexShrink: 0, marginTop: '2px' }} />
                          <span>{item}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div>
                    <h3 style={{ fontSize: '14px', fontWeight: 700, color: '#0f172a', marginBottom: '6px' }}>
                      Methodology Employed:
                    </h3>
                    <div style={{ fontSize: '12.5px', color: '#475569', background: '#f1f5f9', padding: '10px 12px', borderRadius: '6px' }}>
                      Object-Based Image Analysis (OBIA) of Sentinel-2 (10m) stereo-imagery cross-verified against ground GPS surveys across 42 peri-urban revenue villages in Sehore and Bhopal districts.
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'gaps' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                  <h3 style={{ fontSize: '14px', fontWeight: 700, color: '#0f172a' }}>
                    Identified Research Gaps (Opportunities for Policy Innovation):
                  </h3>
                  {[
                    { title: "Longitudinal Aquifer Depletion Modeling", desc: "Absence of predictive hydrological recharge models simulating future IPCC SSP2-4.5 rainfall anomalies under continuous surface paving." },
                    { title: "Ecosystem Service & Carbon Valuation", desc: "No monetary valuation of lost carbon sequestration resulting from the conversion of agrarian orchards and peri-urban green belts." },
                    { title: "Revenue Court Mutation Pendency Audit", desc: "Lack of empirical data linking statutory diversion approval backlogs with unauthorized un-diverted agricultural plot sales." }
                  ].map((gap, i) => (
                    <div key={i} style={{ padding: '12px', borderRadius: '8px', border: '1px solid #fecaca', background: '#fef2f2' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontWeight: 700, fontSize: '13px', color: '#991b1b' }}>
                        <AlertCircle size={15} />
                        <span>{gap.title}</span>
                      </div>
                      <div style={{ fontSize: '12px', color: '#7f1d1d', marginTop: '4px' }}>{gap.desc}</div>
                    </div>
                  ))}
                </div>
              )}

              {activeTab === 'policies' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  <h3 style={{ fontSize: '14px', fontWeight: 700, color: '#0f172a' }}>
                    Statutory Intersections with Existing State/National Policies:
                  </h3>
                  {[
                    { title: "Bhopal Master Plan 2031 (Draft Land Use Regulations)", rel: "Direct Impact", note: "Author findings show draft 2031 residential expansion boundaries encroach upon designated agricultural retention greenbelts." },
                    { title: "Madhya Pradesh Land Revenue Code (Amendment) Act 2022", rel: "Compliance", note: "Section 172 automated diversion portal does not currently integrate high-resolution watershed buffer check constraints." },
                    { title: "State Wetland Conservation & Buffer Zone Guidelines (EPCO)", rel: "Eco Buffer", note: "Requires mandatory 500m construction-free buffer around Upper Lake, currently violated in 12 identified fringe clusters." }
                  ].map((pol, i) => (
                    <div key={i} style={{ padding: '12px', borderRadius: '8px', border: '1px solid #bfdbfe', background: '#eff6ff' }}>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <span style={{ fontWeight: 700, fontSize: '13px', color: '#1e40af' }}>{pol.title}</span>
                        <span className="badge badge-blue">{pol.rel}</span>
                      </div>
                      <div style={{ fontSize: '12px', color: '#334155', marginTop: '4px' }}>{pol.note}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Interactive Document Q&A Section */}
      <div className="card">
        <h3 style={{ fontSize: '15px', fontWeight: 700, marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Sparkles size={16} style={{ color: '#2563eb' }} />
          <span>Interactive Document Chat & Citation Inspection</span>
        </h3>

        <div style={{ maxHeight: '180px', overflowY: 'auto', background: '#f8fafc', padding: '14px', borderRadius: '8px', border: '1px solid #e2e8f0', marginBottom: '12px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {chatLog.map((msg, i) => (
            <div 
              key={i} 
              style={{ 
                alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                background: msg.role === 'user' ? '#2563eb' : '#ffffff',
                color: msg.role === 'user' ? '#ffffff' : '#1e293b',
                padding: '8px 14px',
                borderRadius: '8px',
                fontSize: '12.5px',
                maxWidth: '85%',
                boxShadow: '0 1px 2px rgba(0,0,0,0.05)',
                border: msg.role === 'user' ? 'none' : '1px solid #e2e8f0'
              }}
            >
              {msg.text}
            </div>
          ))}
        </div>

        <form onSubmit={handleSendQuestion} style={{ display: 'flex', gap: '8px' }}>
          <input 
            type="text"
            className="form-input"
            placeholder="Ask a specific question about this document (e.g. 'What is the aquifer recharge impact?')..."
            value={customQuestion}
            onChange={(e) => setCustomQuestion(e.target.value)}
          />
          <button type="submit" className="btn btn-primary" style={{ flexShrink: 0 }}>
            <span>Query Document</span>
          </button>
        </form>
      </div>
    </div>
  );
};
