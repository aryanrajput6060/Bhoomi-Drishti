import React, { useState } from 'react';
import { 
  FolderKanban, 
  Users, 
  CheckSquare, 
  Square, 
  MessageSquare, 
  FileText, 
  Database, 
  MapPin, 
  SlidersHorizontal, 
  Plus, 
  Clock, 
  Send,
  CheckCircle2,
  Calendar
} from 'lucide-react';
import { DEMO_WORKSPACE_PROJECT } from '../../data/mockData';
import { ProjectTask, ProjectComment } from '../../types';

interface ResearchWorkspaceProps {
  onNavigate: (tab: string) => void;
}

export const ResearchWorkspace: React.FC<ResearchWorkspaceProps> = ({ onNavigate }) => {
  const [project, setProject] = useState(DEMO_WORKSPACE_PROJECT);
  const [activeSection, setActiveSection] = useState<'overview' | 'tasks' | 'comments' | 'data'>('overview');
  const [newComment, setNewComment] = useState('');
  const [newTaskTitle, setNewTaskTitle] = useState('');

  const toggleTask = (taskId: string) => {
    setProject(prev => {
      const updatedTasks = prev.tasks.map(t => 
        t.id === taskId ? { ...t, completed: !t.completed } : t
      );
      const completedCount = updatedTasks.filter(t => t.completed).length;
      const progress = Math.round((completedCount / updatedTasks.length) * 100);
      return { ...prev, tasks: updatedTasks, progress };
    });
  };

  const handleAddComment = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    const commentItem: ProjectComment = {
      author: "Dr. Sharma (You)",
      time: "Just now",
      text: newComment.trim()
    };

    setProject(prev => ({
      ...prev,
      comments: [commentItem, ...prev.comments]
    }));
    setNewComment('');
  };

  const handleAddTask = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTaskTitle.trim()) return;

    const taskItem: ProjectTask = {
      id: `t-${Date.now()}`,
      title: newTaskTitle.trim(),
      assignee: "Unassigned",
      completed: false
    };

    setProject(prev => ({
      ...prev,
      tasks: [...prev.tasks, taskItem]
    }));
    setNewTaskTitle('');
  };

  return (
    <div className="page-container">
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span className="badge badge-green">Collaborative Research Workspace</span>
            <span style={{ fontSize: '11.5px', color: '#64748b' }}>Inter-Agency Working Group</span>
          </div>
          <h1 style={{ fontSize: '26px', fontWeight: 800, color: '#0f172a' }}>{project.title}</h1>
          <p style={{ fontSize: '14px', color: '#64748b', marginTop: '2px' }}>
            {project.region} • Lead Investigator: <strong>{project.lead}</strong>
          </p>
        </div>

        <div style={{ display: 'flex', gap: '8px' }}>
          <button 
            className="btn btn-primary"
            onClick={() => onNavigate('policy-simulator')}
          >
            <SlidersHorizontal size={14} />
            <span>Launch Simulation for Project</span>
          </button>
          <button 
            className="btn btn-secondary"
            onClick={() => onNavigate('reports')}
          >
            <FileText size={14} />
            <span>Compile Project Report</span>
          </button>
        </div>
      </div>

      {/* Progress & Meta Bar */}
      <div className="card" style={{ marginBottom: '20px', padding: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px', flexWrap: 'wrap', gap: '10px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span style={{ fontWeight: 700, fontSize: '13px', color: '#0f172a' }}>Project Health & Progress:</span>
            <span className="badge badge-blue">{project.progress}% Completed</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12.5px', color: '#475569' }}>
            <Users size={15} style={{ color: '#2563eb' }} />
            <span>{project.members.length} Multidisciplinary Collaborators</span>
          </div>
        </div>

        {/* Progress Bar */}
        <div style={{ width: '100%', height: '8px', backgroundColor: '#e2e8f0', borderRadius: '4px', overflow: 'hidden' }}>
          <div style={{ width: `${project.progress}%`, height: '100%', backgroundColor: '#059669', borderRadius: '4px', transition: 'width 0.3s ease' }}></div>
        </div>
      </div>

      {/* Sub Navigation Tabs */}
      <div className="tabs-nav">
        <button 
          className={`tab-btn ${activeSection === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveSection('overview')}
        >
          Project Overview & Team
        </button>
        <button 
          className={`tab-btn ${activeSection === 'tasks' ? 'active' : ''}`}
          onClick={() => setActiveSection('tasks')}
        >
          Investigation Tasks ({project.tasks.filter(t => !t.completed).length} Pending)
        </button>
        <button 
          className={`tab-btn ${activeSection === 'comments' ? 'active' : ''}`}
          onClick={() => setActiveSection('comments')}
        >
          Expert Discussion & Feedback ({project.comments.length})
        </button>
        <button 
          className={`tab-btn ${activeSection === 'data' ? 'active' : ''}`}
          onClick={() => setActiveSection('data')}
        >
          Linked Documents & Datasets
        </button>
      </div>

      {/* Section: Overview */}
      {activeSection === 'overview' && (
        <div className="grid-2">
          <div className="card">
            <h2 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '10px', color: '#0f172a' }}>
              Study Context & Research Mandate
            </h2>
            <p style={{ fontSize: '13.5px', color: '#334155', lineHeight: 1.6, marginBottom: '14px' }}>
              {project.description}
            </p>
            <p style={{ fontSize: '13px', color: '#475569', lineHeight: 1.5 }}>
              The study synthesizes remote sensing satellite imagery with cadastral Khasra maps to formulate empirical recommendations 
              for the Town & Country Planning Directorate before the final gazette notification of the Bhopal Master Plan 2031.
            </p>

            <div style={{ marginTop: '16px', paddingTop: '12px', borderTop: '1px solid #e2e8f0' }}>
              <div style={{ fontWeight: 700, fontSize: '12.5px', color: '#0f172a', marginBottom: '8px' }}>
                Key Research Inquiries:
              </div>
              <ul style={{ paddingLeft: '20px', fontSize: '12.5px', color: '#334155', lineHeight: 1.5 }}>
                <li>Quantify rate of agricultural conversion along Kolar & Mandideep bypasses.</li>
                <li>Evaluate hydrologic stress on Bhoj Wetland 500m buffer.</li>
                <li>Model 10% vs 20% agricultural land conversion trade-offs using Policy Simulator.</li>
              </ul>
            </div>
          </div>

          <div className="card">
            <h2 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '12px', color: '#0f172a' }}>
              Interdisciplinary Team Members
            </h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {project.members.map((m, idx) => (
                <div key={idx} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 12px', borderRadius: '8px', border: '1px solid #e2e8f0', background: '#f8fafc' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <div style={{ width: '32px', height: '32px', borderRadius: '50%', backgroundColor: '#0f172a', color: '#34d399', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: '12px' }}>
                      {m.substring(0, 2).toUpperCase()}
                    </div>
                    <div>
                      <div style={{ fontSize: '13px', fontWeight: 700, color: '#0f172a' }}>{m}</div>
                      <div style={{ fontSize: '11px', color: '#64748b' }}>Authorized Research Contributor</div>
                    </div>
                  </div>
                  <span className="badge badge-green">Active</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Section: Tasks Checklist */}
      {activeSection === 'tasks' && (
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
            <h2 style={{ fontSize: '16px', fontWeight: 700, color: '#0f172a' }}>
              Project Milestone Tasks
            </h2>
            <span style={{ fontSize: '12px', color: '#64748b' }}>
              Click checkbox to toggle completion
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '20px' }}>
            {project.tasks.map((task) => (
              <div 
                key={task.id}
                style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'space-between', 
                  padding: '12px', 
                  borderRadius: '8px', 
                  border: task.completed ? '1px solid #bbf7d0' : '1px solid #e2e8f0',
                  background: task.completed ? '#f0fdf4' : '#ffffff',
                  cursor: 'pointer'
                }}
                onClick={() => toggleTask(task.id)}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  {task.completed ? (
                    <CheckSquare size={18} style={{ color: '#059669' }} />
                  ) : (
                    <Square size={18} style={{ color: '#94a3b8' }} />
                  )}
                  <span style={{ fontSize: '13.5px', color: task.completed ? '#166534' : '#0f172a', textDecoration: task.completed ? 'line-through' : 'none', fontWeight: task.completed ? 500 : 600 }}>
                    {task.title}
                  </span>
                </div>
                <span className="badge badge-gray">{task.assignee}</span>
              </div>
            ))}
          </div>

          {/* Add Task Form */}
          <form onSubmit={handleAddTask} style={{ display: 'flex', gap: '8px', borderTop: '1px solid #e2e8f0', paddingTop: '16px' }}>
            <input 
              type="text" 
              className="form-input"
              placeholder="Add new research investigation task..."
              value={newTaskTitle}
              onChange={(e) => setNewTaskTitle(e.target.value)}
            />
            <button type="submit" className="btn btn-primary" style={{ flexShrink: 0 }}>
              <Plus size={15} />
              <span>Add Task</span>
            </button>
          </form>
        </div>
      )}

      {/* Section: Comments & Collaboration */}
      {activeSection === 'comments' && (
        <div className="card">
          <h2 style={{ fontSize: '16px', fontWeight: 700, color: '#0f172a', marginBottom: '14px' }}>
            Collaborative Technical Discussion
          </h2>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '20px' }}>
            {project.comments.map((comment, idx) => (
              <div key={idx} style={{ padding: '12px 14px', borderRadius: '8px', border: '1px solid #e2e8f0', background: '#f8fafc' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <span style={{ fontWeight: 700, fontSize: '13px', color: '#0f172a' }}>{comment.author}</span>
                  <span style={{ fontSize: '11px', color: '#64748b' }}>{comment.time}</span>
                </div>
                <p style={{ fontSize: '12.5px', color: '#334155', lineHeight: 1.5 }}>
                  {comment.text}
                </p>
              </div>
            ))}
          </div>

          <form onSubmit={handleAddComment} style={{ display: 'flex', gap: '8px', borderTop: '1px solid #e2e8f0', paddingTop: '16px' }}>
            <input 
              type="text"
              className="form-input"
              placeholder="Post a comment or peer review observation to the working group..."
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
            />
            <button type="submit" className="btn btn-primary" style={{ flexShrink: 0 }}>
              <Send size={14} />
              <span>Post Comment</span>
            </button>
          </form>
        </div>
      )}

      {/* Section: Linked Data & Maps */}
      {activeSection === 'data' && (
        <div className="grid-2">
          <div className="card">
            <h2 style={{ fontSize: '15px', fontWeight: 700, color: '#0f172a', marginBottom: '12px' }}>
              Linked Datasets
            </h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {[
                { name: "Bhopal Metropolitan LULC 2025", type: "GeoJSON / Sentinel-2", id: "ds-1" },
                { name: "Bhoj Wetland Catchment Flow & Drainage Network", type: "Shapefile / Vector", id: "ds-7" },
                { name: "MP Cadastral Parcel Boundaries", type: "Vector Khasra", id: "ds-2" }
              ].map((d, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 12px', border: '1px solid #e2e8f0', borderRadius: '6px' }}>
                  <div>
                    <div style={{ fontSize: '13px', fontWeight: 600, color: '#0f172a' }}>{d.name}</div>
                    <div style={{ fontSize: '11px', color: '#64748b' }}>{d.type}</div>
                  </div>
                  <button className="btn btn-sm btn-secondary" onClick={() => onNavigate('data-explorer')}>
                    Inspect
                  </button>
                </div>
              ))}
            </div>
          </div>

          <div className="card">
            <h2 style={{ fontSize: '15px', fontWeight: 700, color: '#0f172a', marginBottom: '12px' }}>
              Associated Policy Documents
            </h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {[
                { name: "Bhopal Master Plan 2031 (Draft Land Use Regulations)", status: "Under Evaluation" },
                { name: "State Wetland Conservation & Buffer Zone Guidelines", status: "Active" },
                { name: "Madhya Pradesh Land Revenue Code (Amendment) Act 2022", status: "Active" }
              ].map((p, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 12px', border: '1px solid #e2e8f0', borderRadius: '6px' }}>
                  <div>
                    <div style={{ fontSize: '13px', fontWeight: 600, color: '#0f172a' }}>{p.name}</div>
                    <span className="badge badge-gray" style={{ marginTop: '2px' }}>{p.status}</span>
                  </div>
                  <button className="btn btn-sm btn-secondary" onClick={() => onNavigate('knowledge-hub')}>
                    View
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
