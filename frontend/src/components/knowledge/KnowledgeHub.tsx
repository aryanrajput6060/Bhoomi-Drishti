import React, { useState } from 'react';
import { 
  BookOpen, 
  Search, 
  Filter, 
  FileText, 
  ExternalLink, 
  Download, 
  Building, 
  MapPin, 
  Calendar, 
  Layers,
  ChevronRight,
  ShieldAlert,
  Database
} from 'lucide-react';
import { DEMO_RESEARCH_PAPERS, DEMO_POLICIES, DEMO_DATASETS } from '../../data/mockData';
import { ResearchPaper, PolicyDocument, DatasetItem } from '../../types';

interface KnowledgeHubProps {
  onOpenEvidence: (paper: ResearchPaper) => void;
}

export const KnowledgeHub: React.FC<KnowledgeHubProps> = ({ onOpenEvidence }) => {
  const [activeTab, setActiveTab] = useState<'papers' | 'policies' | 'reports' | 'datasets' | 'case_studies' | 'legal'>('papers');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTopic, setSelectedTopic] = useState('All');
  const [selectedRegion, setSelectedRegion] = useState('All');
  const [selectedYear, setSelectedYear] = useState('All');
  const [inspectItem, setInspectItem] = useState<any>(null);

  // Filter research papers
  const filteredPapers = DEMO_RESEARCH_PAPERS.filter(p => {
    const matchesSearch = searchQuery === '' || 
      p.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
      p.abstract.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.authors.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesTopic = selectedTopic === 'All' || p.topic.toLowerCase().includes(selectedTopic.toLowerCase());
    const matchesRegion = selectedRegion === 'All' || p.region.toLowerCase().includes(selectedRegion.toLowerCase());
    const matchesYear = selectedYear === 'All' || p.year.toString() === selectedYear;
    return matchesSearch && matchesTopic && matchesRegion && matchesYear;
  });

  // Filter policies
  const filteredPolicies = DEMO_POLICIES.filter(p => {
    const matchesSearch = searchQuery === '' ||
      p.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.department.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesRegion = selectedRegion === 'All' || p.region.toLowerCase().includes(selectedRegion.toLowerCase());
    return matchesSearch && matchesRegion;
  });

  // Filter datasets
  const filteredDatasets = DEMO_DATASETS.filter(d => {
    const matchesSearch = searchQuery === '' ||
      d.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      d.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesSearch;
  });

  return (
    <div className="page-container">
      {/* Page Title */}
      <div style={{ marginBottom: '20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
          <span className="badge badge-green">National Land Governance Repository</span>
          <span style={{ fontSize: '11.5px', color: '#64748b' }}>Cross-Institutional Knowledge Vault</span>
        </div>
        <h1 style={{ fontSize: '26px', fontWeight: 800, color: '#0f172a' }}>KNOWLEDGE HUB</h1>
        <p style={{ fontSize: '14px', color: '#64748b', marginTop: '4px' }}>
          Search, explore and inspect verified land-governance studies, policy acts, cadastral datasets, and legal precedents.
        </p>
      </div>

      {/* Tabs Navigation */}
      <div className="tabs-nav">
        <button 
          className={`tab-btn ${activeTab === 'papers' ? 'active' : ''}`}
          onClick={() => setActiveTab('papers')}
        >
          Research Papers ({filteredPapers.length})
        </button>
        <button 
          className={`tab-btn ${activeTab === 'policies' ? 'active' : ''}`}
          onClick={() => setActiveTab('policies')}
        >
          Policy Documents ({filteredPolicies.length})
        </button>
        <button 
          className={`tab-btn ${activeTab === 'reports' ? 'active' : ''}`}
          onClick={() => setActiveTab('reports')}
        >
          Government Reports (18)
        </button>
        <button 
          className={`tab-btn ${activeTab === 'datasets' ? 'active' : ''}`}
          onClick={() => setActiveTab('datasets')}
        >
          Datasets ({filteredDatasets.length})
        </button>
        <button 
          className={`tab-btn ${activeTab === 'case_studies' ? 'active' : ''}`}
          onClick={() => setActiveTab('case_studies')}
        >
          Case Studies (9)
        </button>
        <button 
          className={`tab-btn ${activeTab === 'legal' ? 'active' : ''}`}
          onClick={() => setActiveTab('legal')}
        >
          Legal & Regulatory (14)
        </button>
      </div>

      {/* Search & Filters Bar */}
      <div className="card" style={{ marginBottom: '20px', padding: '16px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px' }}>
          {/* Keyword Search */}
          <div style={{ position: 'relative' }}>
            <Search size={16} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: '#64748b' }} />
            <input 
              type="text" 
              className="form-input" 
              style={{ paddingLeft: '32px' }}
              placeholder="Search by keywords, title, or authors..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          {/* Topic Filter */}
          <div>
            <select 
              className="form-select"
              value={selectedTopic}
              onChange={(e) => setSelectedTopic(e.target.value)}
            >
              <option value="All">All Topics</option>
              <option value="Urban Expansion">Urban Expansion</option>
              <option value="Climate & Ecology">Climate & Ecology</option>
              <option value="GIS & Simulation">GIS & Simulation</option>
              <option value="Legal & Governance">Legal & Governance</option>
              <option value="Hydrology">Hydrology & Environment</option>
              <option value="Socio-Economic">Socio-Economic</option>
            </select>
          </div>

          {/* Region Filter */}
          <div>
            <select 
              className="form-select"
              value={selectedRegion}
              onChange={(e) => setSelectedRegion(e.target.value)}
            >
              <option value="All">All Geographies (India)</option>
              <option value="Bhopal">Bhopal, Madhya Pradesh</option>
              <option value="Indore">Indore, Madhya Pradesh</option>
              <option value="Madhya Pradesh">Madhya Pradesh (Statewide)</option>
              <option value="National">National / Central</option>
            </select>
          </div>

          {/* Year Filter */}
          <div>
            <select 
              className="form-select"
              value={selectedYear}
              onChange={(e) => setSelectedYear(e.target.value)}
            >
              <option value="All">All Years</option>
              <option value="2025">2025</option>
              <option value="2024">2024</option>
              <option value="2023">2023</option>
              <option value="2022">2022</option>
            </select>
          </div>
        </div>
      </div>

      {/* Tab Content: Research Papers */}
      {activeTab === 'papers' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {filteredPapers.map((paper) => (
            <div key={paper.id} className="card" style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '10px', flexWrap: 'wrap' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                    <span className="badge badge-blue">{paper.topic}</span>
                    <span className="badge badge-gray" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <Calendar size={12} /> {paper.year}
                    </span>
                    <span className="badge badge-green">Relevance: {paper.relevance}%</span>
                  </div>
                  <h2 style={{ fontSize: '16px', fontWeight: 700, color: '#0f172a' }}>
                    {paper.title}
                  </h2>
                </div>
                <button 
                  className="btn btn-sm btn-outline-primary"
                  onClick={() => onOpenEvidence(paper)}
                >
                  <span>Inspect Full Evidence</span>
                  <ExternalLink size={14} />
                </button>
              </div>

              <div style={{ fontSize: '12px', color: '#475569' }}>
                Authors: <strong>{paper.authors}</strong> • Institution: <strong>{paper.organization}</strong> • Region: <strong>{paper.region}</strong>
              </div>

              <p style={{ fontSize: '13px', color: '#334155', lineHeight: 1.5, background: '#f8fafc', padding: '10px 14px', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
                {paper.abstract}
              </p>

              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '11.5px', color: '#64748b', paddingTop: '6px' }}>
                <div>Citations: <strong>{paper.citations}</strong> • Peer Reviewed Index: OGD/UGC Care</div>
                <div style={{ display: 'flex', gap: '10px' }}>
                  <button 
                    style={{ background: 'none', border: 'none', color: '#2563eb', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '11.5px', fontWeight: 600 }}
                    onClick={() => setInspectItem(paper)}
                  >
                    View Citations & Schema
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Tab Content: Policy Documents */}
      {activeTab === 'policies' && (
        <div className="data-table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Policy Title</th>
                <th>Department / Agency</th>
                <th>Region</th>
                <th>Year</th>
                <th>Sector</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredPolicies.map((pol) => (
                <tr key={pol.id}>
                  <td style={{ fontWeight: 700, color: '#0f172a' }}>{pol.title}</td>
                  <td>{pol.department}</td>
                  <td>{pol.region}</td>
                  <td>{pol.year}</td>
                  <td><span className="badge badge-gray">{pol.sector}</span></td>
                  <td>
                    <span className={`badge ${pol.status === 'Active' ? 'badge-green' : (pol.status === 'Under Evaluation' ? 'badge-amber' : 'badge-blue')}`}>
                      {pol.status}
                    </span>
                  </td>
                  <td>
                    <button 
                      className="btn btn-sm btn-secondary"
                      onClick={() => setInspectItem(pol)}
                    >
                      Inspect
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Tab Content: Datasets */}
      {activeTab === 'datasets' && (
        <div className="data-table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Dataset Name</th>
                <th>Source Organization</th>
                <th>Category</th>
                <th>Coverage</th>
                <th>Format</th>
                <th>License</th>
                <th>Updated</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredDatasets.map((ds) => (
                <tr key={ds.id}>
                  <td style={{ fontWeight: 700, color: '#0f172a' }}>{ds.name}</td>
                  <td>{ds.organization}</td>
                  <td><span className="badge badge-blue">{ds.category}</span></td>
                  <td>{ds.geographic_coverage}</td>
                  <td><code>{ds.format}</code></td>
                  <td><span className="badge badge-gray">{ds.license}</span></td>
                  <td>{ds.last_updated}</td>
                  <td>
                    <button 
                      className="btn btn-sm btn-secondary"
                      onClick={() => setInspectItem(ds)}
                    >
                      Preview
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Tab Content: Government Reports / Case Studies / Legal */}
      {(activeTab === 'reports' || activeTab === 'case_studies' || activeTab === 'legal') && (
        <div className="card" style={{ padding: '24px' }}>
          <h2 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '8px' }}>
            Curated Institutional Gazette & Records
          </h2>
          <p style={{ fontSize: '13px', color: '#64748b', marginBottom: '16px' }}>
            Official publications from Town & Country Planning Directorate, National Green Tribunal orders, and SVAMITVA implementation dossiers.
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {[
              { title: "Bhopal Master Plan 2031 Comprehensive Environmental Appraisal Dossier", date: "2024-11", type: "Gazette Notification", org: "UDHD Madhya Pradesh" },
              { title: "National Green Tribunal (Central Bench) Order on Bhoj Wetland Eco-Buffer Protection", date: "2023-08", type: "Judicial Precedent", org: "NGT New Delhi" },
              { title: "SVAMITVA Drone Survey Settlement Report: District Sehore (140 Villages)", date: "2024-05", type: "Cadastral Audit", org: "Survey of India" },
              { title: "High-Level Inter-Ministerial Committee Recommendations on Agricultural Land Leasing", date: "2023-02", type: "Policy Whitepaper", org: "NITI Aayog" }
            ].map((rep, idx) => (
              <div key={idx} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                <div>
                  <div style={{ fontWeight: 700, fontSize: '13.5px', color: '#0f172a' }}>{rep.title}</div>
                  <div style={{ fontSize: '11.5px', color: '#64748b' }}>{rep.org} • {rep.date} • <span className="badge badge-gray">{rep.type}</span></div>
                </div>
                <button 
                  className="btn btn-sm btn-secondary"
                  onClick={() => alert(`Prototype Document Download: '${rep.title}' would be securely retrieved from Gov OGD repository.`)}
                >
                  <Download size={13} />
                  <span>Download PDF</span>
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Inspect Item Modal */}
      {inspectItem && (
        <div className="modal-backdrop" onClick={() => setInspectItem(null)}>
          <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div>
                <h3 style={{ fontSize: '17px', fontWeight: 800, color: '#0f172a' }}>
                  {inspectItem.title || inspectItem.name}
                </h3>
                <div style={{ fontSize: '12px', color: '#64748b' }}>
                  Metadata & Provenance Inspection
                </div>
              </div>
              <button 
                onClick={() => setInspectItem(null)} 
                style={{ background: 'none', border: 'none', fontSize: '20px', cursor: 'pointer', color: '#64748b' }}
              >
                ✕
              </button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '13px' }}>
              <div>
                <strong>Description / Abstract:</strong>
                <p style={{ marginTop: '4px', color: '#334155', lineHeight: 1.5, background: '#f8fafc', padding: '10px', borderRadius: '6px' }}>
                  {inspectItem.abstract || inspectItem.description}
                </p>
              </div>

              {inspectItem.department && (
                <div><strong>Department:</strong> {inspectItem.department}</div>
              )}
              {inspectItem.organization && (
                <div><strong>Source Organization:</strong> {inspectItem.organization}</div>
              )}
              {inspectItem.geographic_coverage && (
                <div><strong>Geographic Coverage:</strong> {inspectItem.geographic_coverage}</div>
              )}
              {inspectItem.format && (
                <div><strong>File Format / Schema:</strong> <code>{inspectItem.format}</code> ({inspectItem.size || 'N/A'})</div>
              )}
              {inspectItem.license && (
                <div><strong>License / Access Restrictions:</strong> {inspectItem.license}</div>
              )}

              <div className="disclaimer-box">
                This record is cataloged in the National Land Digital Repository for policy research and evidence-backed governance simulations.
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '16px' }}>
              <button className="btn btn-primary" onClick={() => setInspectItem(null)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
