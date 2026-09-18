import React, { useState } from 'react';
import { Sidebar } from './components/layout/Sidebar';
import { Header } from './components/layout/Header';
import { Dashboard } from './components/dashboard/Dashboard';
import { AIResearch } from './components/ai/AIResearch';
import { RAGAssistant } from './components/ai/RAGAssistant';
import { KnowledgeHub } from './components/knowledge/KnowledgeHub';
import { GISIntelligence } from './components/gis/GISIntelligence';
import { PolicySimulator } from './components/simulator/PolicySimulator';
import { AnalyticsModule } from './components/analytics/AnalyticsModule';
import { DataExplorer } from './components/data/DataExplorer';
import { ResearchWorkspace } from './components/workspace/ResearchWorkspace';
import { ReportGenerator } from './components/reports/ReportGenerator';
import { AdminPanel } from './components/admin/AdminPanel';
import { KnowledgeGraphView } from './components/graph/KnowledgeGraphView';
import { LandingPage } from './components/landing/LandingPage';
import { LoginPage } from './components/auth/LoginPage';
import { DemoGuideModal } from './components/common/DemoGuideModal';
import { EvidenceModal } from './components/common/EvidenceModal';
import { NotificationDrawer } from './components/notifications/NotificationDrawer';
import { DEMO_NOTIFICATIONS } from './data/mockData';
import { UserRole, ResearchPaper, SimulationResult } from './types';

export function App() {
  // Main View Mode: 'landing' | 'login' | 'app'
  const [viewMode, setViewMode] = useState<'landing' | 'login' | 'app'>('app');
  
  // Active Sidebar Tab
  const [currentTab, setCurrentTab] = useState<string>('dashboard');

  // Active User Persona & Role
  const [userRole, setUserRole] = useState<UserRole>('policymaker');
  const [userName, setUserName] = useState<string>('Dr. Sharma');

  // Notifications
  const [notifications, setNotifications] = useState(DEMO_NOTIFICATIONS);
  const [isNotificationDrawerOpen, setIsNotificationDrawerOpen] = useState(false);

  // Modals
  const [isDemoGuideOpen, setIsDemoGuideOpen] = useState(false);
  const [inspectPaper, setInspectPaper] = useState<ResearchPaper | null>(null);

  // Shared context between Simulator and Report Generator
  const [simulationContext, setSimulationContext] = useState<SimulationResult | null>(null);

  const unreadNotificationsCount = notifications.filter(n => !n.read).length;

  const handleMarkAllNotificationsRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })));
  };

  const handleGlobalSearch = (term: string) => {
    setCurrentTab('ai-research');
  };

  const handleLoginSuccess = (role: UserRole, name: string) => {
    setUserRole(role);
    setUserName(name);
    setViewMode('app');
    setCurrentTab('dashboard');
  };

  // If user is on landing or login view
  if (viewMode === 'landing') {
    return (
      <LandingPage 
        onEnterPlatform={() => setViewMode('app')}
        onOpenLogin={() => setViewMode('login')}
      />
    );
  }

  if (viewMode === 'login') {
    return (
      <LoginPage 
        onLoginSuccess={handleLoginSuccess}
        onBackToLanding={() => setViewMode('landing')}
      />
    );
  }

  return (
    <div className="app-layout">
      {/* Persistent Sidebar Navigation */}
      <Sidebar 
        currentTab={currentTab}
        setCurrentTab={setCurrentTab}
        userRole={userRole}
        userName={userName}
        onLogout={() => setViewMode('login')}
        unreadCount={unreadNotificationsCount}
      />

      {/* Main Content Area */}
      <div className="main-wrapper">
        <Header 
          userRole={userRole}
          setUserRole={setUserRole}
          userName={userName}
          setUserName={setUserName}
          unreadCount={unreadNotificationsCount}
          onOpenNotifications={() => setIsNotificationDrawerOpen(true)}
          onOpenDemoFlowModal={() => setIsDemoGuideOpen(true)}
          onGlobalSearch={handleGlobalSearch}
        />

        {/* Tab Modules */}
        <main style={{ flex: 1 }}>
          {currentTab === 'dashboard' && (
            <Dashboard 
              userName={userName}
              onNavigate={setCurrentTab}
              onOpenEvidence={(paper) => setInspectPaper(paper)}
            />
          )}

          {currentTab === 'ai-research' && (
            <AIResearch 
              onNavigate={setCurrentTab}
              onOpenEvidenceModal={(paper) => setInspectPaper(paper)}
            />
          )}

          {currentTab === 'rag-assistant' && (
            <RAGAssistant 
              onNavigate={setCurrentTab}
            />
          )}

          {currentTab === 'knowledge-hub' && (
            <KnowledgeHub 
              onOpenEvidence={(paper) => setInspectPaper(paper)}
            />
          )}

          {currentTab === 'gis-intelligence' && (
            <GISIntelligence 
              onNavigate={setCurrentTab}
            />
          )}

          {currentTab === 'policy-simulator' && (
            <PolicySimulator 
              onNavigate={setCurrentTab}
              onSetGeneratedReportContext={setSimulationContext}
            />
          )}

          {currentTab === 'analytics' && (
            <AnalyticsModule />
          )}

          {currentTab === 'workspace' && (
            <ResearchWorkspace 
              onNavigate={setCurrentTab}
            />
          )}

          {currentTab === 'reports' && (
            <ReportGenerator 
              simulationContext={simulationContext}
            />
          )}

          {currentTab === 'data-explorer' && (
            <DataExplorer 
              onNavigate={setCurrentTab}
            />
          )}

          {currentTab === 'knowledge-graph' && (
            <KnowledgeGraphView 
              onNavigate={setCurrentTab}
            />
          )}

          {currentTab === 'notifications' && (
            <div className="page-container">
              <div style={{ marginBottom: '20px' }}>
                <h1 style={{ fontSize: '26px', fontWeight: 800 }}>NOTIFICATIONS</h1>
                <p style={{ fontSize: '14px', color: '#64748b' }}>Platform activity stream and alerts</p>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {notifications.map(n => (
                  <div key={n.id} className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <div style={{ fontWeight: 700, fontSize: '14px' }}>{n.title}</div>
                      <div style={{ fontSize: '13px', color: '#334155', marginTop: '2px' }}>{n.message}</div>
                      <div style={{ fontSize: '11px', color: '#64748b', marginTop: '4px' }}>{n.timestamp}</div>
                    </div>
                    <span className="badge badge-gray">{n.type}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {currentTab === 'admin' && (
            <AdminPanel />
          )}
        </main>
      </div>

      {/* Global Modals & Drawers */}
      <DemoGuideModal 
        isOpen={isDemoGuideOpen}
        onClose={() => setIsDemoGuideOpen(false)}
        onJumpToStep={setCurrentTab}
      />

      <EvidenceModal 
        paper={inspectPaper}
        onClose={() => setInspectPaper(null)}
        onNavigateToSimulator={() => setCurrentTab('policy-simulator')}
      />

      <NotificationDrawer 
        isOpen={isNotificationDrawerOpen}
        onClose={() => setIsNotificationDrawerOpen(false)}
        notifications={notifications}
        onMarkAllRead={handleMarkAllNotificationsRead}
        onNavigate={setCurrentTab}
      />
    </div>
  );
}

export default App;
