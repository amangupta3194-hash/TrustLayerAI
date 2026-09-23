import React, { useState, useEffect } from 'react';
import { Shield, LayoutDashboard, MessageSquare, Activity, CheckSquare, FileText, Search, Cpu } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, pendingCount }) {
  const [health, setHealth] = useState({
    backend_api: 'ONLINE',
    trustlayer: 'ACTIVE',
    database: 'CONNECTED',
    ai_agent: 'READY'
  });

  const checkHealth = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/health');
      if (res.ok) {
        const data = await res.json();
        setHealth(data.components);
      }
    } catch (e) {
      setHealth({
        backend_api: 'OFFLINE',
        trustlayer: 'INACTIVE',
        database: 'DISCONNECTED',
        ai_agent: 'UNAVAILABLE'
      });
    }
  };

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <nav className="navbar">
      <div className="nav-brand">
        <div className="brand-icon">
          <Shield size={22} color="#ffffff" />
        </div>
        <div>
          <div className="brand-title">TrustLayer AI</div>
          <div className="brand-subtitle">Governance & Control Platform</div>
        </div>
      </div>

      <div className="nav-tabs">
        <button
          className={`tab-btn ${activeTab === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActiveTab('dashboard')}
        >
          <LayoutDashboard size={16} />
          Overview Dashboard
        </button>

        <button
          className={`tab-btn ${activeTab === 'chat' ? 'active' : ''}`}
          onClick={() => setActiveTab('chat')}
        >
          <MessageSquare size={16} />
          AI Agent Chat
        </button>

        <button
          className={`tab-btn ${activeTab === 'approvals' ? 'active' : ''}`}
          onClick={() => setActiveTab('approvals')}
        >
          <CheckSquare size={16} />
          Approvals Queue
          {pendingCount > 0 && (
            <span style={{
              background: '#f59e0b',
              color: '#000',
              borderRadius: '10px',
              padding: '2px 7px',
              fontSize: '0.7rem',
              fontWeight: '700',
              marginLeft: '4px'
            }}>
              {pendingCount}
            </span>
          )}
        </button>

        <button
          className={`tab-btn ${activeTab === 'monitor' ? 'active' : ''}`}
          onClick={() => setActiveTab('monitor')}
        >
          <Activity size={16} />
          Action Monitor
        </button>

        <button
          className={`tab-btn ${activeTab === 'audit' ? 'active' : ''}`}
          onClick={() => setActiveTab('audit')}
        >
          <Search size={16} />
          Audit Explorer
        </button>

        <button
          className={`tab-btn ${activeTab === 'policies' ? 'active' : ''}`}
          onClick={() => setActiveTab('policies')}
        >
          <FileText size={16} />
          Policies & Tools
        </button>
      </div>

      <div className="nav-status" style={{ display: 'flex', gap: '0.6rem', fontSize: '0.7rem' }}>
        <div className="status-pill" style={{ background: health.backend_api === 'ONLINE' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)', color: health.backend_api === 'ONLINE' ? '#10b981' : '#ef4444', border: `1px solid ${health.backend_api === 'ONLINE' ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}` }}>
          <span className="status-dot" style={{ background: health.backend_api === 'ONLINE' ? '#10b981' : '#ef4444' }}></span>
          API: {health.backend_api}
        </div>

        <div className="status-pill" style={{ background: 'rgba(99, 102, 241, 0.1)', color: '#a5b4fc', border: '1px solid rgba(99, 102, 241, 0.3)' }}>
          TrustLayer: {health.trustlayer}
        </div>
      </div>
    </nav>
  );
}
