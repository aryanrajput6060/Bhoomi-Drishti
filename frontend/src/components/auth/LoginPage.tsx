import React, { useState } from 'react';
import { Shield, Lock, Mail, ArrowRight, UserCheck, ArrowLeft } from 'lucide-react';
import { UserRole } from '../../types';

interface LoginPageProps {
  onLoginSuccess: (role: UserRole, name: string) => void;
  onBackToLanding: () => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onLoginSuccess, onBackToLanding }) => {
  const [email, setEmail] = useState('k.sharma@gov.mp.in');
  const [password, setPassword] = useState('••••••••••••');
  const [rememberMe, setRememberMe] = useState(true);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onLoginSuccess('policymaker', 'Dr. Sharma');
  };

  const handleQuickDemoRole = (role: UserRole, name: string) => {
    onLoginSuccess(role, name);
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f8fafc', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', padding: '24px' }}>
      {/* Back button */}
      <button 
        onClick={onBackToLanding}
        style={{ position: 'absolute', top: '24px', left: '24px', display: 'flex', alignItems: 'center', gap: '6px', background: 'none', border: 'none', color: '#475569', fontSize: '13px', fontWeight: 600, cursor: 'pointer' }}
      >
        <ArrowLeft size={16} />
        <span>Back to Overview</span>
      </button>

      {/* Main Login Card */}
      <div style={{ maxWidth: '460px', width: '100%', background: '#ffffff', border: '1px solid #cbd5e1', borderRadius: '16px', boxShadow: '0 10px 25px -5px rgba(15, 23, 42, 0.08)', padding: '36px 32px' }}>
        {/* Brand Header */}
        <div style={{ textAlign: 'center', marginBottom: '28px' }}>
          <div style={{ width: '44px', height: '44px', margin: '0 auto 12px auto', borderRadius: '10px', background: 'linear-gradient(135deg, #059669 0%, #2563eb 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontWeight: 800, fontSize: '20px' }}>
            BI
          </div>
          <h1 style={{ fontSize: '22px', fontWeight: 800, color: '#0f172a', letterSpacing: '-0.3px' }}>
            BHUMI INSIGHT
          </h1>
          <p style={{ fontSize: '12.5px', color: '#64748b', marginTop: '2px' }}>
            National Land Governance Intelligence Platform
          </p>
        </div>

        {/* Standard Gov Auth Form */}
        <form onSubmit={handleSubmit} style={{ marginBottom: '24px' }}>
          <div className="form-group">
            <label className="form-label">Official Email Address:</label>
            <div style={{ position: 'relative' }}>
              <Mail size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#64748b' }} />
              <input 
                type="email"
                className="form-input"
                style={{ paddingLeft: '36px' }}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Password:</label>
            <div style={{ position: 'relative' }}>
              <Lock size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#64748b' }} />
              <input 
                type="password"
                className="form-input"
                style={{ paddingLeft: '36px' }}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', fontSize: '12.5px' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer', color: '#475569' }}>
              <input 
                type="checkbox" 
                checked={rememberMe} 
                onChange={(e) => setRememberMe(e.target.checked)} 
              />
              <span>Remember me</span>
            </label>
            <a href="#forgot" onClick={(e) => { e.preventDefault(); alert("Prototype: Password reset email dispatched to verified ministry address."); }} style={{ color: '#2563eb', fontWeight: 600 }}>
              Forgot password?
            </a>
          </div>

          <button 
            type="submit" 
            className="btn btn-primary btn-lg" 
            style={{ width: '100%' }}
          >
            <span>Sign In to Platform</span>
            <ArrowRight size={16} />
          </button>
        </form>

        {/* Demo Fast-Track Roles */}
        <div style={{ borderTop: '1px solid #e2e8f0', paddingTop: '20px' }}>
          <div style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', color: '#64748b', textAlign: 'center', letterSpacing: '0.8px', marginBottom: '12px' }}>
            Instant SIH 2026 Evaluation Logins:
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <button 
              type="button"
              className="btn btn-sm btn-secondary"
              style={{ justifyContent: 'flex-start', padding: '9px 14px', background: '#eff6ff', borderColor: '#bfdbfe' }}
              onClick={() => handleQuickDemoRole('policymaker', 'Dr. Sharma')}
            >
              <UserCheck size={16} style={{ color: '#2563eb' }} />
              <div style={{ textAlign: 'left', marginLeft: '6px' }}>
                <div style={{ fontWeight: 700, fontSize: '12.5px', color: '#1e40af' }}>Continue as Policymaker (Dr. Sharma)</div>
                <div style={{ fontSize: '10.5px', color: '#3b82f6' }}>Urban Development & Housing Department, MP</div>
              </div>
            </button>

            <button 
              type="button"
              className="btn btn-sm btn-secondary"
              style={{ justifyContent: 'flex-start', padding: '9px 14px', background: '#ecfdf5', borderColor: '#a7f3d0' }}
              onClick={() => handleQuickDemoRole('researcher', 'Dr. A. Pathak')}
            >
              <UserCheck size={16} style={{ color: '#059669' }} />
              <div style={{ textAlign: 'left', marginLeft: '6px' }}>
                <div style={{ fontWeight: 700, fontSize: '12.5px', color: '#065f46' }}>Continue as Researcher (Dr. Pathak)</div>
                <div style={{ fontSize: '10.5px', color: '#059669' }}>Indian Institute of Forest Management (IIFM)</div>
              </div>
            </button>

            <button 
              type="button"
              className="btn btn-sm btn-secondary"
              style={{ justifyContent: 'flex-start', padding: '9px 14px', background: '#fffbeb', borderColor: '#fde68a' }}
              onClick={() => handleQuickDemoRole('admin', 'R. N. Tiwari (Admin)')}
            >
              <UserCheck size={16} style={{ color: '#d97706' }} />
              <div style={{ textAlign: 'left', marginLeft: '6px' }}>
                <div style={{ fontWeight: 700, fontSize: '12.5px', color: '#92400e' }}>Continue as Administrator (R. N. Tiwari)</div>
                <div style={{ fontSize: '10.5px', color: '#b45309' }}>National Land Governance Mission</div>
              </div>
            </button>

            <button 
              type="button"
              className="btn btn-sm btn-secondary"
              style={{ justifyContent: 'flex-start', padding: '9px 14px' }}
              onClick={() => handleQuickDemoRole('public', 'Public Citizen User')}
            >
              <UserCheck size={16} style={{ color: '#64748b' }} />
              <div style={{ textAlign: 'left', marginLeft: '6px' }}>
                <div style={{ fontWeight: 700, fontSize: '12.5px', color: '#334155' }}>Continue as Public User / Citizen</div>
                <div style={{ fontSize: '10.5px', color: '#64748b' }}>Open Knowledge & Public GIS Access</div>
              </div>
            </button>
          </div>
        </div>
      </div>

      {/* Footer disclaimer */}
      <div style={{ marginTop: '20px', fontSize: '11px', color: '#94a3b8', textAlign: 'center' }}>
        BHUMI INSIGHT • Smart India Hackathon 2026 Prototype • Not an operational land registry
      </div>
    </div>
  );
};
