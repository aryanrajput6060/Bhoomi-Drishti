import React from 'react';
import { Bell, CheckCircle2, Clock, X, FileText, SlidersHorizontal, Database, FolderKanban } from 'lucide-react';
import { NotificationItem } from '../../types';

interface NotificationDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  notifications: NotificationItem[];
  onMarkAllRead: () => void;
  onNavigate: (tab: string) => void;
}

export const NotificationDrawer: React.FC<NotificationDrawerProps> = ({
  isOpen,
  onClose,
  notifications,
  onMarkAllRead,
  onNavigate
}) => {
  if (!isOpen) return null;

  const getIcon = (type: string) => {
    switch (type) {
      case 'research': return <FileText size={16} style={{ color: '#059669' }} />;
      case 'simulation': return <SlidersHorizontal size={16} style={{ color: '#2563eb' }} />;
      case 'dataset': return <Database size={16} style={{ color: '#0284c7' }} />;
      case 'project': return <FolderKanban size={16} style={{ color: '#d97706' }} />;
      default: return <Bell size={16} style={{ color: '#64748b' }} />;
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div 
        style={{ 
          position: 'fixed', 
          top: 0, 
          right: 0, 
          bottom: 0, 
          width: '380px', 
          background: '#ffffff', 
          boxShadow: '-4px 0 20px rgba(0,0,0,0.15)',
          zIndex: 1001,
          display: 'flex',
          flexDirection: 'column',
          animation: 'slideInRight 0.2s ease-out'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Drawer Header */}
        <div style={{ padding: '20px', borderBottom: '1px solid #e2e8f0', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <h2 style={{ fontSize: '16px', fontWeight: 800, color: '#0f172a' }}>
              Notifications & Alerts
            </h2>
            <div style={{ fontSize: '11.5px', color: '#64748b' }}>
              Real-time platform mesh events
            </div>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#64748b' }}>
            <X size={18} />
          </button>
        </div>

        {/* Action Bar */}
        <div style={{ padding: '10px 20px', background: '#f8fafc', borderBottom: '1px solid #e2e8f0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontSize: '12px', fontWeight: 600, color: '#475569' }}>
            {notifications.filter(n => !n.read).length} Unread Alerts
          </span>
          <button 
            style={{ background: 'none', border: 'none', color: '#2563eb', fontSize: '12px', fontWeight: 600, cursor: 'pointer' }}
            onClick={onMarkAllRead}
          >
            Mark all read
          </button>
        </div>

        {/* Notifications List */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '16px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {notifications.map((notif) => (
            <div 
              key={notif.id}
              style={{ 
                padding: '12px', 
                borderRadius: '8px', 
                border: notif.read ? '1px solid #e2e8f0' : '1px solid #bfdbfe',
                background: notif.read ? '#ffffff' : '#eff6ff',
                cursor: 'pointer',
                transition: 'all 0.15s ease'
              }}
              onClick={() => {
                if (notif.type === 'simulation') onNavigate('policy-simulator');
                else if (notif.type === 'research') onNavigate('knowledge-hub');
                else if (notif.type === 'dataset') onNavigate('data-explorer');
                else if (notif.type === 'project') onNavigate('workspace');
                onClose();
              }}
            >
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '10px' }}>
                <div style={{ marginTop: '2px' }}>{getIcon(notif.type)}</div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 700, fontSize: '13px', color: '#0f172a' }}>
                    {notif.title}
                  </div>
                  <p style={{ fontSize: '12px', color: '#334155', marginTop: '2px', lineHeight: 1.4 }}>
                    {notif.message}
                  </p>
                  <div style={{ fontSize: '10.5px', color: '#64748b', marginTop: '6px' }}>
                    {notif.timestamp}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
