import React, { useState } from 'react';
import { 
  Network, 
  Info, 
  ExternalLink, 
  CheckCircle2, 
  SlidersHorizontal, 
  Sparkles,
  ArrowRight
} from 'lucide-react';

interface KnowledgeGraphViewProps {
  onNavigate: (tab: string) => void;
}

export const KnowledgeGraphView: React.FC<KnowledgeGraphViewProps> = ({ onNavigate }) => {
  // Graph Nodes
  const nodes = [
    { id: 'policy', label: 'Bhopal Master Plan 2031', type: 'Policy', x: 80, y: 120, color: '#2563eb', desc: 'Statutory urban development framework outlining proposed residential density and green retention belts.' },
    { id: 'research', label: 'Urban Expansion Study (MANIT)', type: 'Research', x: 280, y: 80, color: '#059669', desc: 'Empirical telemetry proving 14.8% agricultural land conversion across Kolar and Mandideep fringes.' },
    { id: 'dataset', label: 'Sentinel-2 LULC 2025', type: 'Dataset', x: 280, y: 200, color: '#0891b2', desc: '10m resolution multispectral satellite raster capturing built-up expansion.' },
    { id: 'location', label: 'Bhopal Metropolitan Area', type: 'Location', x: 480, y: 140, color: '#7c3aed', desc: 'Central Madhya Pradesh urban agglomeration (2.4M population, 68% urbanization rate).' },
    { id: 'landuse', label: 'Agricultural Land Diversion', type: 'Land Use', x: 680, y: 80, color: '#d97706', desc: '10% to 20% agricultural land diversion into residential plot colonies.' },
    { id: 'climate', label: 'Upper Lake Bhoj Catchment', type: 'Climate & Eco', x: 680, y: 220, color: '#0284c7', desc: 'Ramsar wetland buffer subject to impervious surface runoff and aquifer recharge deficit.' },
    { id: 'outcome', label: 'Water Stress & Infrastructure Deficit', type: 'Outcome', x: 880, y: 140, color: '#dc2626', desc: 'Resultant +6.8% water extraction stress and +12% road congestion load.' }
  ];

  const links = [
    { source: 'policy', target: 'research' },
    { source: 'policy', target: 'dataset' },
    { source: 'research', target: 'location' },
    { source: 'dataset', target: 'location' },
    { source: 'location', target: 'landuse' },
    { source: 'location', target: 'climate' },
    { source: 'landuse', target: 'outcome' },
    { source: 'climate', target: 'outcome' }
  ];

  const [selectedNode, setSelectedNode] = useState(nodes[3]); // Bhopal default

  return (
    <div className="page-container">
      {/* Header */}
      <div style={{ marginBottom: '20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
          <span className="badge badge-blue">Causal Semantic Network</span>
          <span style={{ fontSize: '11.5px', color: '#64748b' }}>Ontology: Policy → Research → Dataset → Location → Land Use → Climate → Outcome</span>
        </div>
        <h1 style={{ fontSize: '26px', fontWeight: 800, color: '#0f172a' }}>AI KNOWLEDGE GRAPH</h1>
        <p style={{ fontSize: '14px', color: '#64748b', marginTop: '2px' }}>
          Explore interconnected causal relationships linking statutory regulations, academic telemetry, geospatial data, and ecological outcomes.
        </p>
      </div>

      {/* Main Graph Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: '20px' }}>
        {/* Interactive SVG Canvas */}
        <div className="card" style={{ padding: '20px', background: '#0f172a', border: '1px solid #1e293b', position: 'relative', overflow: 'hidden' }}>
          <div style={{ position: 'absolute', top: '16px', left: '16px', zIndex: 10, color: '#94a3b8', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ width: '8px', height: '8px', backgroundColor: '#34d399', borderRadius: '50%' }}></span>
            <span>Click any node to inspect evidence provenance</span>
          </div>

          <svg width="100%" height="480" viewBox="0 0 980 320" style={{ display: 'block' }}>
            <defs>
              <marker id="arrow" viewBox="0 0 10 10" refX="24" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#64748b" />
              </marker>
            </defs>

            {/* Connecting Edges */}
            {links.map((link, idx) => {
              const sNode = nodes.find(n => n.id === link.source)!;
              const tNode = nodes.find(n => n.id === link.target)!;
              const isHighlighted = selectedNode.id === sNode.id || selectedNode.id === tNode.id;

              return (
                <line
                  key={idx}
                  x1={sNode.x}
                  y1={sNode.y}
                  x2={tNode.x}
                  y2={tNode.y}
                  stroke={isHighlighted ? '#38bdf8' : '#334155'}
                  strokeWidth={isHighlighted ? 2.5 : 1.5}
                  strokeDasharray={isHighlighted ? 'none' : '4 2'}
                  markerEnd="url(#arrow)"
                />
              );
            })}

            {/* Nodes */}
            {nodes.map((node) => {
              const isSelected = selectedNode.id === node.id;

              return (
                <g 
                  key={node.id} 
                  transform={`translate(${node.x}, ${node.y})`}
                  onClick={() => setSelectedNode(node)}
                  style={{ cursor: 'pointer' }}
                >
                  {/* Outer pulse circle if selected */}
                  {isSelected && (
                    <circle r="36" fill="none" stroke="#38bdf8" strokeWidth="2" strokeDasharray="3 3" opacity="0.8" />
                  )}

                  {/* Main Node Circle */}
                  <circle
                    r="26"
                    fill={node.color}
                    stroke="#ffffff"
                    strokeWidth={isSelected ? 3 : 1.5}
                  />

                  {/* Node Label Above */}
                  <text
                    y="-34"
                    textAnchor="middle"
                    fill={isSelected ? '#38bdf8' : '#e2e8f0'}
                    fontSize="11"
                    fontWeight={isSelected ? 800 : 600}
                  >
                    {node.type}
                  </text>

                  {/* Node Title Inside/Under */}
                  <text
                    y="42"
                    textAnchor="middle"
                    fill="#cbd5e1"
                    fontSize="10"
                    width="120"
                    fontWeight="500"
                  >
                    {node.label.length > 20 ? node.label.substring(0, 18) + '...' : node.label}
                  </text>
                </g>
              );
            })}
          </svg>
        </div>

        {/* Right Node Inspector */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
              <span className="badge badge-blue">{selectedNode.type} Node</span>
              <span style={{ fontSize: '11px', color: '#64748b' }}>Causal Element</span>
            </div>
            <h2 style={{ fontSize: '18px', fontWeight: 800, color: '#0f172a', marginBottom: '8px' }}>
              {selectedNode.label}
            </h2>
            <p style={{ fontSize: '13px', color: '#334155', lineHeight: 1.6, background: '#f8fafc', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0', marginBottom: '16px' }}>
              {selectedNode.desc}
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '12px', color: '#475569' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <CheckCircle2 size={14} style={{ color: '#059669' }} />
                <span>Verified in National Knowledge Repository</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <CheckCircle2 size={14} style={{ color: '#059669' }} />
                <span>Calibrated with RSAC & CGWB Telemetry</span>
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '20px' }}>
            <button 
              className="btn btn-primary"
              onClick={() => onNavigate('policy-simulator')}
            >
              <SlidersHorizontal size={14} />
              <span>Simulate Impact in Simulator</span>
            </button>
            <button 
              className="btn btn-secondary"
              onClick={() => onNavigate('knowledge-hub')}
            >
              <ExternalLink size={14} />
              <span>Inspect Source Record</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
