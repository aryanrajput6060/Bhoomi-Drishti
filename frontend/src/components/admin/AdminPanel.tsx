import React, { useState } from 'react';
import { 
  ShieldCheck, 
  Users, 
  Database, 
  FileText, 
  FolderKanban, 
  CheckCircle2, 
  XCircle, 
  AlertCircle,
  Clock,
  Search,
  Filter
} from 'lucide-react';

export const AdminPanel: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'users' | 'datasets' | 'approvals'>('approvals');

  // Content Approvals State
  const [approvals, setApprovals] = useState([
    { id: "app-1", title: "Study on Outer Ring Road Real Estate Inflation", author: "SPA Bhopal Research Cell", type: "Research Paper", status: "Pending Review", date: "Today" },
    { id: "app-2", title: "Groundwater Table Monitoring (Piezometric 2026)", author: "Central Ground Water Board (CGWB)", type: "Dataset", status: "Pending Review", date: "Yesterday" },
    { id: "app-3", title: "Bhopal Metro TOD Corridor Land Pooling Guidelines", author: "UDHD Madhya Pradesh", type: "Policy Gazette", status: "Pending Review", date: "2 days ago" },
    { id: "app-4", title: "Sehore Peri-Urban Farmer Resettlement Survey", author: "TISS Mumbai", type: "Socio-Economic Study", status: "Approved", date: "3 days ago" },
  ]);

  const handleAction = (id: string, newStatus: 'Approved' | 'Rejected') => {
    setApprovals(prev => prev.map(a => a.id === id ? { ...a, status: newStatus } : a));
  };

  const usersList = [
    { name: "Dr. Sharma", role: "Policymaker / Government Official", org: "Urban Development Dept, MP", status: "Active", lastActive: "Online Now" },
    { name: "Dr. A. Pathak", role: "Researcher", org: "Indian Institute of Forest Management (IIFM)", status: "Active", lastActive: "15m ago" },
    { name: "P. Iyer", role: "Researcher (GIS Lead)", org: "Survey of India / SAC", status: "Active", lastActive: "1h ago" },
    { name: "R. N. Tiwari", role: "Administrator", org: "National Land Governance Mission", status: "Active", lastActive: "2h ago" },
    { name: "Adv. S. Mishra", role: "Researcher (Legal)", org: "National Law Institute University (NLIU)", status: "Active", lastActive: "1d ago" },
    { name: "Citizen Scholar", role: "Public User", org: "Civil Society Forum", status: "Active", lastActive: "3d ago" },
  ];

  const datasetsList = [
    { name: "Bhopal Metropolitan LULC 2025", owner: "RSAC Madhya Pradesh", status: "Published", updated: "2025-11-15" },
    { name: "MP Cadastral Parcel Boundaries Vector", owner: "Dept of Land Records", status: "Published", updated: "2024-12-01" },
    { name: "Central India Groundwater Depth 2025", owner: "CGWB", status: "Published", updated: "2025-08-20" },
    { name: "Bhopal Master Plan 2031 Proposed Boundary", owner: "Directorate of T&CP", status: "Draft Review", updated: "2023-09-10" },
  ];

  return (
    <div className="page-container">
      {/* Header */}
      <div style={{ marginBottom: '20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
          <span className="badge badge-green">Administrative Control Center</span>
          <span style={{ fontSize: '11.5px', color: '#64748b' }}>Platform Governance & Auditing</span>
        </div>
        <h1 style={{ fontSize: '26px', fontWeight: 800, color: '#0f172a' }}>ADMIN PANEL</h1>
        <p style={{ fontSize: '14px', color: '#64748b', marginTop: '2px' }}>
          Manage user permissions, dataset verifications, content approval queues, and institutional access credentials.
        </p>
      </div>

      {/* Admin KPI Cards */}
      <div className="kpi-grid" style={{ marginBottom: '24px' }}>
        <div className="kpi-card navy">
          <div className="kpi-title">Total Users</div>
          <div className="kpi-value">1,480</div>
          <div className="kpi-subtext">Across 42 ministries & institutes</div>
        </div>
        <div className="kpi-card green">
          <div className="kpi-title">Researchers</div>
          <div className="kpi-value">642</div>
          <div className="kpi-subtext">Verified academic credentials</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-title">Policymakers</div>
          <div className="kpi-value">184</div>
          <div className="kpi-subtext">State & central IAS officers</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-title">Datasets</div>
          <div className="kpi-value">1,245</div>
          <div className="kpi-subtext">Validated spatial catalogs</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-title">Documents</div>
          <div className="kpi-value">8,420</div>
          <div className="kpi-subtext">Vectorized in RAG mesh</div>
        </div>
        <div className="kpi-card amber">
          <div className="kpi-title">Active Projects</div>
          <div className="kpi-value">146</div>
          <div className="kpi-subtext">Inter-agency working groups</div>
        </div>
      </div>

      {/* Admin Sub Navigation */}
      <div className="tabs-nav">
        <button 
          className={`tab-btn ${activeTab === 'approvals' ? 'active' : ''}`}
          onClick={() => setActiveTab('approvals')}
        >
          Content Approval Queue ({approvals.filter(a => a.status === 'Pending Review').length} Pending)
        </button>
        <button 
          className={`tab-btn ${activeTab === 'users' ? 'active' : ''}`}
          onClick={() => setActiveTab('users')}
        >
          User Role Management ({usersList.length})
        </button>
        <button 
          className={`tab-btn ${activeTab === 'datasets' ? 'active' : ''}`}
          onClick={() => setActiveTab('datasets')}
        >
          Dataset Catalog Moderation ({datasetsList.length})
        </button>
      </div>

      {/* Content Approvals Table */}
      {activeTab === 'approvals' && (
        <div className="card">
          <div className="card-header">
            <div>
              <h2 className="card-title">Pending Content & Research Verification</h2>
              <div className="card-subtitle">Review research papers and datasets submitted by external institutions</div>
            </div>
          </div>

          <div className="data-table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Resource Title</th>
                  <th>Submitted By</th>
                  <th>Type</th>
                  <th>Submitted</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {approvals.map((app) => (
                  <tr key={app.id}>
                    <td style={{ fontWeight: 700, color: '#0f172a' }}>{app.title}</td>
                    <td>{app.author}</td>
                    <td><span className="badge badge-gray">{app.type}</span></td>
                    <td>{app.date}</td>
                    <td>
                      <span className={`badge ${app.status === 'Approved' ? 'badge-green' : (app.status === 'Rejected' ? 'badge-red' : 'badge-amber')}`}>
                        {app.status}
                      </span>
                    </td>
                    <td>
                      {app.status === 'Pending Review' ? (
                        <div style={{ display: 'flex', gap: '6px' }}>
                          <button 
                            className="btn btn-sm btn-success"
                            onClick={() => handleAction(app.id, 'Approved')}
                          >
                            <CheckCircle2 size={13} />
                            <span>Approve</span>
                          </button>
                          <button 
                            className="btn btn-sm btn-secondary"
                            onClick={() => handleAction(app.id, 'Rejected')}
                            style={{ color: '#dc2626' }}
                          >
                            <XCircle size={13} />
                            <span>Reject</span>
                          </button>
                        </div>
                      ) : (
                        <span style={{ fontSize: '11.5px', color: '#64748b' }}>Processed</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* User Management Table */}
      {activeTab === 'users' && (
        <div className="card">
          <div className="card-header">
            <div>
              <h2 className="card-title">Platform User Accounts & Role Permissions</h2>
              <div className="card-subtitle">Enforce institutional role-based access control (RBAC)</div>
            </div>
          </div>

          <div className="data-table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>User Name</th>
                  <th>Assigned Role</th>
                  <th>Organization</th>
                  <th>Status</th>
                  <th>Last Active</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {usersList.map((u, i) => (
                  <tr key={i}>
                    <td style={{ fontWeight: 700, color: '#0f172a' }}>{u.name}</td>
                    <td>
                      <span className={`badge ${u.role.includes('Policymaker') ? 'badge-blue' : (u.role.includes('Admin') ? 'badge-amber' : 'badge-green')}`}>
                        {u.role}
                      </span>
                    </td>
                    <td>{u.org}</td>
                    <td><span className="badge badge-green">{u.status}</span></td>
                    <td>{u.lastActive}</td>
                    <td>
                      <button 
                        className="btn btn-sm btn-secondary"
                        onClick={() => alert(`Prototype: Managing permissions for ${u.name}`)}
                      >
                        Edit Role
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Dataset Management Table */}
      {activeTab === 'datasets' && (
        <div className="card">
          <div className="card-header">
            <div>
              <h2 className="card-title">Dataset Moderation & Provenance Compliance</h2>
              <div className="card-subtitle">Track metadata schemas and spatial layer synchronizations</div>
            </div>
          </div>

          <div className="data-table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Dataset Name</th>
                  <th>Data Custodian / Owner</th>
                  <th>Status</th>
                  <th>Last Refreshed</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {datasetsList.map((d, i) => (
                  <tr key={i}>
                    <td style={{ fontWeight: 700, color: '#0f172a' }}>{d.name}</td>
                    <td>{d.owner}</td>
                    <td><span className="badge badge-green">{d.status}</span></td>
                    <td>{d.updated}</td>
                    <td>
                      <button 
                        className="btn btn-sm btn-secondary"
                        onClick={() => alert(`Prototype: Resynchronizing ${d.name}`)}
                      >
                        Resync Vector
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
