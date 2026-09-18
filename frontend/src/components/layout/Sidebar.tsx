import React from 'react';
import { 
  LayoutDashboard, 
  Sparkles, 
  BookOpen, 
  MapPin, 
  SlidersHorizontal, 
  BarChart3, 
  FolderKanban, 
  FileText, 
  Database, 
  Bell, 
  Network, 
  ShieldCheck, 
  LogOut,
  Layers,
  FileSearch
} from 'lucide-react';
import { UserRole } from '../../types';

interface SidebarProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
  userRole: UserRole;
  userName: string;
  onLogout: () => void;
  unreadCount: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  setCurrentTab,
  userRole,
  userName,
  onLogout,
  unreadCount
}) => {
  const getRoleDisplayName = (role: UserRole) => {
    switch (role) {
      case 'policymaker': return 'Policymaker (Gov. Official)';
      case 'researcher': return 'Senior Land Researcher';
      case 'admin': return 'System Administrator';
      case 'public': return 'Public Citizen / Scholar';
    }
  };

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, section: 'Core' },
    { id: 'ai-research', label: 'AI Research', icon: Sparkles, section: 'Intelligence', badge: 'RAG' },
    { id: 'rag-assistant', label: 'Research Assistant', icon: FileSearch, section: 'Intelligence' },
    { id: 'knowledge-hub', label: 'Knowledge Hub', icon: BookOpen, section: 'Intelligence' },
    { id: 'gis-intelligence', label: 'GIS Intelligence', icon: MapPin, section: 'Geospatial' },
    { id: 'policy-simulator', label: 'Policy Simulator', icon: SlidersHorizontal, section: 'Decision Support', hero: true },
    { id: 'analytics', label: 'Analytics', icon: BarChart3, section: 'Decision Support' },
    { id: 'workspace', label: 'Research Workspace', icon: FolderKanban, section: 'Collaboration' },
    { id: 'reports', label: 'Reports Generator', icon: FileText, section: 'Outputs' },
    { id: 'data-explorer', label: 'Data Explorer', icon: Database, section: 'Data Assets' },
    { id: 'knowledge-graph', label: 'Knowledge Graph', icon: Network, section: 'Data Assets' },
    { id: 'notifications', label: 'Notifications', icon: Bell, section: 'System', count: unreadCount },
    { id: 'admin', label: 'Admin Panel', icon: ShieldCheck, section: 'System', adminOnly: true },
  ];

  return (
    <aside className="sidebar">
      {/* Brand Header */}
      <div className="sidebar-header">
        <div className="brand-badge">
          <Layers size={12} />
          <span>SIH 2026 PS26019</span>
        </div>
        <div className="brand-title-wrap">
          <div className="brand-logo-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
              <rect x="3" y="3" width="8" height="8" rx="1.5" stroke="currentColor" />
              <rect x="13" y="3" width="8" height="8" rx="1.5" stroke="#34d399" />
              <rect x="3" y="13" width="8" height="8" rx="1.5" stroke="#60a5fa" />
              <circle cx="17" cy="17" r="4" fill="#34d399" />
            </svg>
          </div>
          <div>
            <div className="brand-name">BHUMI INSIGHT</div>
            <div style={{ fontSize: '10.5px', color: '#94a3b8', fontWeight: 500 }}>National Land Intelligence</div>
          </div>
        </div>
        <div className="brand-tagline">
          From Land Data to Policy Intelligence
        </div>
      </div>

      {/* Navigation List */}
      <div className="sidebar-nav">
        {navItems.map((item) => {
          // If public user, restrict some admin or workspace features visually
          const isActive = currentTab === item.id;
          const Icon = item.icon;

          return (
            <div
              key={item.id}
              className={`nav-item ${isActive ? 'active' : ''}`}
              onClick={() => setCurrentTab(item.id)}
              title={item.label}
            >
              <Icon size={17} style={{ color: isActive ? '#60a5fa' : (item.hero ? '#34d399' : '#94a3b8') }} />
              <span>{item.label}</span>
              {item.badge && (
                <span style={{ marginLeft: 'auto', fontSize: '10px', background: 'rgba(59, 130, 246, 0.25)', color: '#93c5fd', padding: '1px 6px', borderRadius: '4px', fontWeight: 700 }}>
                  {item.badge}
                </span>
              )}
              {item.count !== undefined && item.count > 0 && (
                <span className="nav-item-badge">{item.count}</span>
              )}
              {item.hero && !item.badge && (
                <span style={{ marginLeft: 'auto', fontSize: '9.5px', background: 'rgba(16, 185, 129, 0.2)', color: '#34d399', padding: '1px 5px', borderRadius: '4px', fontWeight: 700 }}>
                  HERO
                </span>
              )}
            </div>
          );
        })}
      </div>

      {/* Footer / User Profile */}
      <div className="sidebar-footer">
        <div className="user-profile-widget">
          <div className="user-avatar">
            {userName.substring(0, 2).toUpperCase()}
          </div>
          <div className="user-info">
            <div className="user-name">{userName}</div>
            <span className="user-role-badge">{getRoleDisplayName(userRole)}</span>
          </div>
          <button 
            onClick={onLogout} 
            title="Switch User / Logout"
            style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer', padding: '4px' }}
          >
            <LogOut size={16} />
          </button>
        </div>
      </div>
    </aside>
  );
};
