import React, { useState, useEffect } from 'react';
import { Shield, Activity, CheckCircle, Clock, OctagonAlert, PieChart, ArrowUpRight, Eye, RefreshCw, AlertTriangle } from 'lucide-react';
import ActionDetailModal from './ActionDetailModal';

export default function DashboardView({ onNavigateTab }) {
  const [stats, setStats] = useState({
    total_actions: 0,
    allowed_count: 0,
    pending_approval_count: 0,
    blocked_count: 0,
    average_risk_score: 0.0
  });

  const [riskDist, setRiskDist] = useState({
    low_risk: 0,
    medium_risk: 0,
    high_risk: 0,
    average_score: 0.0,
    highest_risk_action: null
  });

  const [decisions, setDecisions] = useState({
    ALLOW: 0,
    REQUIRE_APPROVAL: 0,
    BLOCK: 0
  });

  const [recentActions, setRecentActions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedActionId, setSelectedActionId] = useState(null);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const [sRes, rRes, dRes, aRes] = await Promise.all([
        fetch('http://localhost:8000/api/dashboard/stats'),
        fetch('http://localhost:8000/api/dashboard/risk-distribution'),
        fetch('http://localhost:8000/api/dashboard/decisions'),
        fetch('http://localhost:8000/api/actions?limit=10')
      ]);

      if (sRes.ok) setStats(await sRes.json());
      if (rRes.ok) setRiskDist(await rRes.json());
      if (dRes.ok) setDecisions(await dRes.json());
      if (aRes.ok) setRecentActions(await aRes.json());
    } catch (err) {
      console.error('Error loading dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleClearAuditLogs = async () => {
    if (!window.confirm("Are you sure you want to clear all audit logs? This action is irreversible.")) {
      return;
    }
    try {
      const res = await fetch('http://localhost:8000/api/audit/clear', {
        method: 'POST'
      });
      if (res.ok) {
        alert("Audit logs cleared successfully.");
        fetchDashboardData();
      } else {
        const data = await res.json();
        alert(`Failed to clear audit logs: ${data.detail || 'Unknown error'}`);
      }
    } catch (err) {
      alert(`Error clearing audit logs: ${err.message}`);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const totalDist = riskDist.low_risk + riskDist.medium_risk + riskDist.high_risk || 1;
  const lowPct = Math.round((riskDist.low_risk / totalDist) * 100);
  const medPct = Math.round((riskDist.medium_risk / totalDist) * 100);
  const highPct = Math.round((riskDist.high_risk / totalDist) * 100);

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      {/* Hero Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 800, background: 'linear-gradient(90deg, #ffffff, #a5b4fc)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            TrustLayer AI Governance Dashboard
          </h1>
          <p style={{ fontSize: '0.875rem', color: '#94a3b8' }}>
            Real-time policy enforcement, risk scoring, and zero-trust tool access control for enterprise agentic AI.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div className="status-pill">
            <span className="status-dot"></span>
            TrustLayer Operational
          </div>

          <button
            onClick={handleClearAuditLogs}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              background: 'rgba(239, 68, 68, 0.15)',
              border: '1px solid rgba(239, 68, 68, 0.4)',
              color: '#ef4444',
              padding: '0.45rem 0.85rem',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '0.85rem',
              fontWeight: '700'
            }}
          >
            Clear Audit Logs
          </button>

          <button
            onClick={fetchDashboardData}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              background: 'rgba(255,255,255,0.06)',
              border: '1px solid var(--border-color)',
              color: '#fff',
              padding: '0.45rem 0.85rem',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '0.85rem'
            }}
          >
            <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
            Refresh Data
          </button>
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '1rem' }}>
        {/* TOTAL ACTIONS */}
        <div className="glass-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
            <span style={{ fontSize: '0.75rem', color: '#64748b', fontWeight: 700 }}>TOTAL ACTIONS</span>
            <Activity size={16} color="#6366f1" />
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#ffffff' }}>{stats.total_actions}</div>
          <span style={{ fontSize: '0.7rem', color: '#94a3b8' }}>Evaluated by TrustLayer</span>
        </div>

        {/* ALLOWED */}
        <div className="glass-card" style={{ borderColor: 'rgba(16, 185, 129, 0.3)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
            <span style={{ fontSize: '0.75rem', color: '#10b981', fontWeight: 700 }}>ALLOWED</span>
            <CheckCircle size={16} color="#10b981" />
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#10b981' }}>{stats.allowed_count}</div>
          <span style={{ fontSize: '0.7rem', color: '#94a3b8' }}>Executed safely</span>
        </div>

        {/* PENDING APPROVAL */}
        <div
          className="glass-card"
          style={{ borderColor: 'rgba(245, 158, 11, 0.3)', cursor: 'pointer' }}
          onClick={() => onNavigateTab && onNavigateTab('approvals')}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
            <span style={{ fontSize: '0.75rem', color: '#f59e0b', fontWeight: 700 }}>PENDING APPROVAL</span>
            <Clock size={16} color="#f59e0b" />
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#f59e0b' }}>{stats.pending_approval_count}</div>
          <span style={{ fontSize: '0.7rem', color: '#cbd5e1', display: 'flex', alignItems: 'center', gap: '2px' }}>
            Awaiting Review <ArrowUpRight size={12} />
          </span>
        </div>

        {/* BLOCKED */}
        <div className="glass-card" style={{ borderColor: 'rgba(239, 68, 68, 0.3)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
            <span style={{ fontSize: '0.75rem', color: '#ef4444', fontWeight: 700 }}>BLOCKED</span>
            <OctagonAlert size={16} color="#ef4444" />
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#ef4444' }}>{stats.blocked_count}</div>
          <span style={{ fontSize: '0.7rem', color: '#94a3b8' }}>Prohibited actions</span>
        </div>

        {/* AVERAGE RISK */}
        <div className="glass-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
            <span style={{ fontSize: '0.75rem', color: '#64748b', fontWeight: 700 }}>AVERAGE RISK</span>
            <Shield size={16} color="#38bdf8" />
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#38bdf8' }}>
            {stats.average_risk_score} <span style={{ fontSize: '0.85rem', color: '#64748b' }}>/100</span>
          </div>
          <span style={{ fontSize: '0.7rem', color: '#94a3b8' }}>Deterministic Mean</span>
        </div>
      </div>

      {/* Risk Distribution & Decision Summary */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1.25rem' }}>
        {/* Risk Distribution Panel */}
        <div className="glass-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#ffffff' }}>Risk Assessment Distribution</h3>
            <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Mean Risk: {riskDist.average_score}/100</span>
          </div>

          {/* Bar Visual */}
          <div style={{ height: '14px', background: 'rgba(255,255,255,0.06)', borderRadius: '7px', display: 'flex', overflow: 'hidden', marginBottom: '1rem' }}>
            <div style={{ width: `${lowPct}%`, background: '#10b981' }} title={`Low Risk: ${riskDist.low_risk}`} />
            <div style={{ width: `${medPct}%`, background: '#f59e0b' }} title={`Medium Risk: ${riskDist.medium_risk}`} />
            <div style={{ width: `${highPct}%`, background: '#ef4444' }} title={`High Risk: ${riskDist.high_risk}`} />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.75rem', textAlign: 'center' }}>
            <div style={{ background: 'rgba(16, 185, 129, 0.08)', padding: '0.6rem', borderRadius: '8px', border: '1px solid rgba(16, 185, 129, 0.2)' }}>
              <span style={{ fontSize: '0.7rem', color: '#10b981', fontWeight: 700, display: 'block' }}>LOW RISK (0-30)</span>
              <span style={{ fontSize: '1.1rem', fontWeight: 800, color: '#fff' }}>{riskDist.low_risk}</span>
            </div>
            <div style={{ background: 'rgba(245, 158, 11, 0.08)', padding: '0.6rem', borderRadius: '8px', border: '1px solid rgba(245, 158, 11, 0.2)' }}>
              <span style={{ fontSize: '0.7rem', color: '#f59e0b', fontWeight: 700, display: 'block' }}>MEDIUM RISK (31-70)</span>
              <span style={{ fontSize: '1.1rem', fontWeight: 800, color: '#fff' }}>{riskDist.medium_risk}</span>
            </div>
            <div style={{ background: 'rgba(239, 68, 68, 0.08)', padding: '0.6rem', borderRadius: '8px', border: '1px solid rgba(239, 68, 68, 0.2)' }}>
              <span style={{ fontSize: '0.7rem', color: '#ef4444', fontWeight: 700, display: 'block' }}>HIGH RISK (71-100)</span>
              <span style={{ fontSize: '1.1rem', fontWeight: 800, color: '#fff' }}>{riskDist.high_risk}</span>
            </div>
          </div>
        </div>

        {/* Decision Breakdown Summary */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#ffffff', marginBottom: '0.75rem' }}>Decision Breakdown</h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(0,0,0,0.3)', padding: '0.5rem 0.75rem', borderRadius: '6px' }}>
              <span style={{ fontSize: '0.825rem', fontWeight: 600, color: '#10b981' }}>ALLOW</span>
              <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, fontSize: '0.95rem' }}>{decisions.ALLOW}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(0,0,0,0.3)', padding: '0.5rem 0.75rem', borderRadius: '6px' }}>
              <span style={{ fontSize: '0.825rem', fontWeight: 600, color: '#f59e0b' }}>REQUIRE_APPROVAL</span>
              <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, fontSize: '0.95rem' }}>{decisions.REQUIRE_APPROVAL}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(0,0,0,0.3)', padding: '0.5rem 0.75rem', borderRadius: '6px' }}>
              <span style={{ fontSize: '0.825rem', fontWeight: 600, color: '#ef4444' }}>BLOCK</span>
              <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, fontSize: '0.95rem' }}>{decisions.BLOCK}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity Table */}
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Activity size={18} color="#06b6d4" />
            Recent Governed Activity
          </h3>

          <button
            onClick={() => onNavigateTab && onNavigateTab('monitor')}
            style={{ background: 'transparent', border: 'none', color: '#6366f1', fontSize: '0.85rem', cursor: 'pointer', fontWeight: 600 }}
          >
            View All Action Logs →
          </button>
        </div>

        <div className="glass-card" style={{ padding: 0, overflow: 'hidden' }}>
          <table className="enterprise-table">
            <thead>
              <tr>
                <th>Action ID</th>
                <th>Tool</th>
                <th>Operation</th>
                <th>User Request</th>
                <th>Risk</th>
                <th>Decision</th>
                <th>Time</th>
                <th>Traceability</th>
              </tr>
            </thead>
            <tbody>
              {recentActions.length === 0 ? (
                <tr>
                  <td colSpan={8} style={{ textAlign: 'center', padding: '2rem', color: '#64748b' }}>
                    No actions recorded yet.
                  </td>
                </tr>
              ) : (
                recentActions.map((act) => (
                  <tr key={act.action_id}>
                    <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: '#a5b4fc' }}>
                      {act.action_id}
                    </td>
                    <td style={{ fontFamily: 'var(--font-mono)', color: '#38bdf8' }}>{act.tool}</td>
                    <td>{act.operation}</td>
                    <td style={{ fontSize: '0.825rem', color: '#cbd5e1', maxWidth: '220px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      "{act.user_prompt || 'N/A'}"
                    </td>
                    <td>
                      <span className={`badge badge-${(act.risk_level || 'LOW').toLowerCase()}`}>
                        {act.risk_level} ({act.risk_score})
                      </span>
                    </td>
                    <td>
                      {act.decision === 'ALLOW' && <span className="badge badge-allow">ALLOW</span>}
                      {act.decision === 'REQUIRE_APPROVAL' && <span className="badge badge-approval">APPROVAL REQ</span>}
                      {act.decision === 'BLOCK' && <span className="badge badge-block">BLOCK</span>}
                    </td>
                    <td style={{ fontSize: '0.75rem', color: '#64748b' }}>
                      {new Date(act.requested_at).toLocaleTimeString()}
                    </td>
                    <td>
                      <button
                        onClick={() => setSelectedActionId(act.action_id)}
                        style={{
                          background: 'transparent',
                          border: 'none',
                          color: '#6366f1',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.2rem',
                          fontWeight: 600,
                          fontSize: '0.8rem'
                        }}
                      >
                        <Eye size={14} /> Inspect
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Action Detail Modal */}
      {selectedActionId && (
        <ActionDetailModal
          actionId={selectedActionId}
          onClose={() => setSelectedActionId(null)}
        />
      )}
    </div>
  );
}
