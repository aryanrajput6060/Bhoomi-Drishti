import React from 'react';
import { FileText, X, MapPin, Calendar, Building, BookOpen, ExternalLink } from 'lucide-react';
import { ResearchPaper } from '../../types';

interface EvidenceModalProps {
  paper: ResearchPaper | null;
  onClose: () => void;
  onNavigateToSimulator: () => void;
}

export const EvidenceModal: React.FC<EvidenceModalProps> = ({ paper, onClose, onNavigateToSimulator }) => {
  if (!paper) return null;

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <span className="badge badge-green">Empirical Evidence Dossier</span>
              <span className="badge badge-blue">{paper.topic}</span>
            </div>
            <h3 style={{ fontSize: '18px', fontWeight: 800, color: '#0f172a', lineHeight: 1.3 }}>
              {paper.title}
            </h3>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', fontSize: '20px', cursor: 'pointer', color: '#64748b' }}>
            <X size={18} />
          </button>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', fontSize: '13px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px', background: '#f8fafc', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
            <div>
              <span style={{ color: '#64748b', fontSize: '11px', display: 'block' }}>Primary Authors:</span>
              <strong style={{ color: '#0f172a' }}>{paper.authors}</strong>
            </div>
            <div>
              <span style={{ color: '#64748b', fontSize: '11px', display: 'block' }}>Research Institution:</span>
              <strong style={{ color: '#0f172a' }}>{paper.organization}</strong>
            </div>
            <div>
              <span style={{ color: '#64748b', fontSize: '11px', display: 'block' }}>Geographic Region:</span>
              <strong style={{ color: '#0f172a' }}>{paper.region}</strong>
            </div>
            <div>
              <span style={{ color: '#64748b', fontSize: '11px', display: 'block' }}>Year & Citations:</span>
              <strong style={{ color: '#0f172a' }}>{paper.year} ({paper.citations} citations)</strong>
            </div>
          </div>

          <div>
            <div style={{ fontWeight: 700, color: '#0f172a', marginBottom: '6px' }}>Abstract & Telemetry Analysis:</div>
            <p style={{ color: '#334155', lineHeight: 1.6, background: '#ffffff', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
              {paper.abstract}
            </p>
          </div>

          <div style={{ background: '#eff6ff', padding: '12px', borderRadius: '8px', border: '1px solid #bfdbfe' }}>
            <div style={{ fontWeight: 700, color: '#1e40af', fontSize: '12.5px', marginBottom: '4px' }}>
              Policy Implication for Bhopal:
            </div>
            <div style={{ fontSize: '12px', color: '#1e3a8a' }}>
              Directly supports the establishment of a 10-year statutory Urban Growth Boundary and 500m construction-free buffer around Upper Lake.
            </div>
          </div>

          <div className="disclaimer-box" style={{ margin: 0 }}>
            <strong>Evidence Provenance:</strong> Verified in UGC-CARE / National Knowledge Network index. Embedded into BHUMI INSIGHT RAG vector index.
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px', marginTop: '18px' }}>
          <button className="btn btn-secondary" onClick={onClose}>
            Close
          </button>
          <button 
            className="btn btn-primary"
            onClick={() => {
              onClose();
              onNavigateToSimulator();
            }}
          >
            <span>Test in Policy Simulator</span>
          </button>
        </div>
      </div>
    </div>
  );
};
