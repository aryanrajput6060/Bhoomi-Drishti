import React, { useState } from 'react';
import { 
  Database, 
  Search, 
  Filter, 
  Download, 
  ExternalLink, 
  Eye, 
  FileCode, 
  Layers, 
  SlidersHorizontal,
  Table as TableIcon
} from 'lucide-react';
import { DEMO_DATASETS } from '../../data/mockData';
import { DatasetItem } from '../../types';

interface DataExplorerProps {
  onNavigate: (tab: string) => void;
}

export const DataExplorer: React.FC<DataExplorerProps> = ({ onNavigate }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [previewDataset, setPreviewDataset] = useState<DatasetItem | null>(null);
  const [metadataModalDataset, setMetadataModalDataset] = useState<DatasetItem | null>(null);

  const filteredDatasets = DEMO_DATASETS.filter(ds => {
    const matchesSearch = searchTerm === '' ||
      ds.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ds.organization.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ds.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'All' || ds.category.toLowerCase().includes(selectedCategory.toLowerCase());
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="page-container">
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span className="badge badge-blue">National Land Data Mesh</span>
            <span style={{ fontSize: '11.5px', color: '#64748b' }}>Open Govt Data (OGD) & PostGIS Vectors</span>
          </div>
          <h1 style={{ fontSize: '26px', fontWeight: 800, color: '#0f172a' }}>DATA EXPLORER</h1>
          <p style={{ fontSize: '14px', color: '#64748b', marginTop: '2px' }}>
            Search, preview schemas, and access multi-resolution cadastral, hydrological, climate, and socioeconomic datasets.
          </p>
        </div>

        <button 
          className="btn btn-secondary"
          onClick={() => alert("Prototype Data Download: All 12 verified datasets packaged for spatial analysis.")}
        >
          <Download size={15} />
          <span>Export Catalog (CSV/JSON)</span>
        </button>
      </div>

      {/* Filter Bar */}
      <div className="card" style={{ marginBottom: '20px', padding: '16px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '12px' }}>
          <div style={{ position: 'relative' }}>
            <Search size={16} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: '#64748b' }} />
            <input 
              type="text"
              className="form-input"
              style={{ paddingLeft: '32px' }}
              placeholder="Search datasets by title, agency, or coverage..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          <div>
            <select 
              className="form-select"
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
            >
              <option value="All">All Categories ({DEMO_DATASETS.length})</option>
              <option value="Geospatial">Geospatial / LULC</option>
              <option value="Cadastral">Cadastral / Titles</option>
              <option value="Hydrology">Hydrology & Ground Water</option>
              <option value="Urban Planning">Urban Planning & Zoning</option>
              <option value="Climate Risk">Climate Risk</option>
              <option value="Infrastructure">Infrastructure</option>
              <option value="Agriculture">Agriculture & Soil</option>
            </select>
          </div>
        </div>
      </div>

      {/* Datasets Table */}
      <div className="data-table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>Dataset Name</th>
              <th>Organization</th>
              <th>Category</th>
              <th>Geographic Coverage</th>
              <th>Year</th>
              <th>Format</th>
              <th>License</th>
              <th>Last Updated</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredDatasets.map((ds) => (
              <tr key={ds.id}>
                <td style={{ fontWeight: 700, color: '#0f172a', maxWidth: '240px' }}>
                  {ds.name}
                  <div style={{ fontSize: '11px', color: '#64748b', fontWeight: 400 }}>{ds.rows.toLocaleString()} records • {ds.size}</div>
                </td>
                <td>{ds.organization}</td>
                <td>
                  <span className="badge badge-blue">{ds.category}</span>
                </td>
                <td style={{ fontSize: '12px' }}>{ds.geographic_coverage}</td>
                <td>{ds.year}</td>
                <td><code>{ds.format}</code></td>
                <td><span className="badge badge-gray">{ds.license}</span></td>
                <td style={{ fontSize: '12px', color: '#64748b' }}>{ds.last_updated}</td>
                <td>
                  <div style={{ display: 'flex', gap: '6px' }}>
                    <button 
                      className="btn btn-sm btn-secondary" 
                      onClick={() => setPreviewDataset(ds)}
                      title="Preview Dataset Sample Rows"
                    >
                      <Eye size={12} />
                      <span>Preview</span>
                    </button>
                    <button 
                      className="btn btn-sm btn-secondary" 
                      onClick={() => setMetadataModalDataset(ds)}
                      title="View Full Metadata"
                    >
                      <span>Metadata</span>
                    </button>
                    <button 
                      className="btn btn-sm btn-outline-primary"
                      onClick={() => onNavigate('policy-simulator')}
                      title="Load Dataset into Policy Simulator"
                    >
                      <SlidersHorizontal size={12} />
                      <span>Analyze</span>
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Dataset Preview Modal */}
      {previewDataset && (
        <div className="modal-backdrop" onClick={() => setPreviewDataset(null)}>
          <div className="modal-dialog" style={{ maxWidth: '820px' }} onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <TableIcon size={18} style={{ color: '#2563eb' }} />
                  <h3 style={{ fontSize: '17px', fontWeight: 800, color: '#0f172a' }}>
                    Dataset Sample Preview: {previewDataset.name}
                  </h3>
                </div>
                <div style={{ fontSize: '12px', color: '#64748b', marginTop: '2px' }}>
                  Format: <code>{previewDataset.format}</code> • Rows: {previewDataset.rows.toLocaleString()} • Size: {previewDataset.size}
                </div>
              </div>
              <button 
                onClick={() => setPreviewDataset(null)} 
                style={{ background: 'none', border: 'none', fontSize: '20px', cursor: 'pointer', color: '#64748b' }}
              >
                ✕
              </button>
            </div>

            <p style={{ fontSize: '13px', color: '#334155', marginBottom: '14px', background: '#f8fafc', padding: '10px 14px', borderRadius: '6px' }}>
              {previewDataset.description}
            </p>

            {/* Sample Table Preview */}
            <div style={{ overflowX: 'auto', border: '1px solid #e2e8f0', borderRadius: '8px', marginBottom: '16px' }}>
              <table className="data-table" style={{ fontSize: '12px' }}>
                <thead>
                  <tr>
                    <th>FID</th>
                    <th>PARCEL_ID</th>
                    <th>VILLAGE_NAME</th>
                    <th>KHASRA_NO</th>
                    <th>LAND_USE_CODE</th>
                    <th>AREA_HECTARES</th>
                    <th>AQUIFER_STRESS_INDEX</th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    { fid: 101, pid: 'MP-BHP-2024-0014', vil: 'Kolar Khurd', kh: '42/1-A', code: 'AGR-DOUBLE', area: '1.84', stress: '0.68' },
                    { fid: 102, pid: 'MP-BHP-2024-0015', vil: 'Kolar Khurd', kh: '42/1-B', code: 'AGR-DOUBLE', area: '0.92', stress: '0.68' },
                    { fid: 103, pid: 'MP-BHP-2024-0016', vil: 'Mandideep Peri', kh: '118/3', code: 'RES-PROPOSED', area: '3.40', stress: '0.84' },
                    { fid: 104, pid: 'MP-BHP-2024-0017', vil: 'Bairagarh Kalan', kh: '79/2', code: 'WTL-BUFFER', area: '5.12', stress: '0.92' },
                    { fid: 105, pid: 'MP-BHP-2024-0018', vil: 'Berasia Fringe', kh: '204/1', code: 'AGR-IRRIGATED', area: '4.20', stress: '0.34' },
                  ].map((row, idx) => (
                    <tr key={idx}>
                      <td>{row.fid}</td>
                      <td><code>{row.pid}</code></td>
                      <td>{row.vil}</td>
                      <td>{row.kh}</td>
                      <td><span className="badge badge-gray">{row.code}</span></td>
                      <td>{row.area} ha</td>
                      <td style={{ color: Number(row.stress) > 0.7 ? '#dc2626' : '#059669', fontWeight: 700 }}>{row.stress}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '11.5px', color: '#64748b' }}>
                Showing 5 sample rows of {previewDataset.rows.toLocaleString()} total records.
              </span>
              <div style={{ display: 'flex', gap: '8px' }}>
                <button 
                  className="btn btn-secondary"
                  onClick={() => alert(`Prototype Data Export: Simulated GeoJSON bundle for '${previewDataset.name}' downloaded.`)}
                >
                  <Download size={14} />
                  <span>Download Sample</span>
                </button>
                <button 
                  className="btn btn-primary"
                  onClick={() => {
                    setPreviewDataset(null);
                    onNavigate('policy-simulator');
                  }}
                >
                  <span>Inject into Policy Simulator</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Dataset Metadata Modal */}
      {metadataModalDataset && (
        <div className="modal-backdrop" onClick={() => setMetadataModalDataset(null)}>
          <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div>
                <h3 style={{ fontSize: '17px', fontWeight: 800, color: '#0f172a' }}>
                  {metadataModalDataset.name} — Technical Metadata
                </h3>
                <div style={{ fontSize: '12px', color: '#64748b' }}>Open Geospatial Consortium (OGC) Schema</div>
              </div>
              <button 
                onClick={() => setMetadataModalDataset(null)} 
                style={{ background: 'none', border: 'none', fontSize: '20px', cursor: 'pointer', color: '#64748b' }}
              >
                ✕
              </button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '13px' }}>
              <div><strong>Publishing Organization:</strong> {metadataModalDataset.organization}</div>
              <div><strong>Spatial Coverage:</strong> {metadataModalDataset.geographic_coverage}</div>
              <div><strong>Temporal Reference:</strong> Year {metadataModalDataset.year} (Synchronized {metadataModalDataset.last_updated})</div>
              <div><strong>Coordinate Reference System (CRS):</strong> EPSG:4326 (WGS 84) / EPSG:3857</div>
              <div><strong>License:</strong> {metadataModalDataset.license}</div>
              <div><strong>File Format:</strong> {metadataModalDataset.format} ({metadataModalDataset.size})</div>
              <div><strong>Abstract:</strong> {metadataModalDataset.description}</div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '16px' }}>
              <button className="btn btn-primary" onClick={() => setMetadataModalDataset(null)}>
                Close Metadata
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
