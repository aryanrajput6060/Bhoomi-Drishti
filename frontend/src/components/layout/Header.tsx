import React, { useState } from 'react';
import { Search, Bell, HelpCircle, Compass, CheckCircle2, Shield, User } from 'lucide-react';
import { UserRole } from '../../types';

interface HeaderProps {
  userRole: UserRole;
  setUserRole: (role: UserRole) => void;
  userName: string;
  setUserName: (name: string) => void;
  unreadCount: number;
  onOpenNotifications: () => void;
  onOpenDemoFlowModal: () => void;
  onGlobalSearch: (term: string) => void;
}

export const Header: React.FC<HeaderProps> = ({
  userRole,
  setUserRole,
  userName,
  setUserName,
  unreadCount,
  onOpenNotifications,
  onOpenDemoFlowModal,
  onGlobalSearch
}) => {
  const [searchTerm, setSearchTerm] = useState('');

  const handleRoleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const role = e.target.value as UserRole;
    setUserRole(role);
    if (role === 'policymaker') setUserName('Dr. Sharma');
    else if (role === 'researcher') setUserName('Dr. A. Pathak');
    else if (role === 'admin') setUserName('R. N. Tiwari (Admin)');
    else setUserName('Public Citizen User');
  };

  const handleSearchKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && searchTerm.trim()) {
      onGlobalSearch(searchTerm.trim());
    }
  };

  return (
    <header className="top-header">
      {/* Global Search */}
      <div className="header-search">
        <Search className="header-search-icon" size={16} />
        <input 
          type="text"
          placeholder="Search research, datasets, GIS layers, or policies... (Enter to query)"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          onKeyDown={handleSearchKeyDown}
        />
      </div>

      {/* Header Actions */}
      <div className="header-actions">
        {/* System Online Status Indicator */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11.5px', color: '#059669', background: '#ecfdf5', padding: '4px 10px', borderRadius: '9999px', border: '1px solid #a7f3d0' }}>
          <span style={{ width: '7px', height: '7px', borderRadius: '50%', backgroundColor: '#10b981', display: 'inline-block' }}></span>
          <span style={{ fontWeight: 600 }}>National Land Mesh: Connected</span>
        </div>

        {/* Demo Flow Quick Guide Button */}
        <button 
          className="btn btn-sm btn-secondary"
          onClick={onOpenDemoFlowModal}
          style={{ display: 'flex', alignItems: 'center', gap: '6px', borderColor: '#bfdbfe', background: '#eff6ff', color: '#1d4ed8' }}
          title="View Smart India Hackathon Demo Flow"
        >
          <Compass size={14} />
          <span>SIH Demo Guide</span>
        </button>

        {/* Role Switcher */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Shield size={14} style={{ color: '#475569' }} />
          <select 
            value={userRole} 
            onChange={handleRoleChange}
            className="role-switcher-select"
            title="Switch Prototype User Role"
          >
            <option value="policymaker">Role: Policymaker (Dr. Sharma)</option>
            <option value="researcher">Role: Researcher (Dr. Pathak)</option>
            <option value="admin">Role: Administrator (R. N. Tiwari)</option>
            <option value="public">Role: Public User</option>
          </select>
        </div>

        {/* Notifications Button */}
        <button 
          className="icon-button" 
          onClick={onOpenNotifications}
          title="System Notifications"
        >
          <Bell size={18} />
          {unreadCount > 0 && <span className="icon-badge">{unreadCount}</span>}
        </button>

        {/* User Chip */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', paddingLeft: '8px', borderLeft: '1px solid #e2e8f0' }}>
          <div style={{ width: '32px', height: '32px', borderRadius: '50%', backgroundColor: '#0f172a', color: '#34d399', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: '12px' }}>
            <User size={16} />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <span style={{ fontSize: '12.5px', fontWeight: 700, color: '#0f172a', lineHeight: 1.2 }}>{userName}</span>
            <span style={{ fontSize: '10.5px', color: '#64748b' }}>Govt. of Madhya Pradesh</span>
          </div>
        </div>
      </div>
    </header>
  );
};
