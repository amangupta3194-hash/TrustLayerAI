import React, { useState, useEffect } from 'react';
import { Activity, RefreshCw, Eye, Shield, Search } from 'lucide-react';

export default function MonitorView() {
  const [actions, setActions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedAction, setSelectedAction] = useState(null);
  const [filter, setFilter] = useState('');

  const fetchActions = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/actions');
      if (res.ok) {
        const data = await res.json();
        setActions(data);
      }
    } catch (err) {
      console.error('Failed to fetch actions:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchActions();
  }, []);

  useEffect(() => {
    const handler = () => {
      fetchActions();
    };
    window.addEventListener('demoReset', handler);
    return () => window.removeEventListener('demoReset', handler);
  }, []);


  const filteredActions = actions.filter((act) => {
    if (!filter) return true;
    const term = filter.toLowerCase();
    return (
      act.action_id.toLowerCase().includes(term) ||
      act.tool.toLowerCase().includes(term) ||
      act.status.toLowerCase().includes(term) ||
      (act.user_prompt && act.user_prompt.toLowerCase().includes(term))
    );
  });

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Activity size={22} color="#06b6d4" />
            TrustLayer Real-Time Action Monitor
          </h2>
          <p style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
            Audit log of all action proposals evaluated by TrustLayer governance engines.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <div style={{ position: 'relative' }}>
            <Search size={16} color="#64748b" style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)' }} />
            <input
              type="text"
              placeholder="Search actions..."
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              style={{
                background: 'rgba(255,255,255,0.05)',
                border: '1px solid var(--border-color)',
                borderRadius: '8px',
                padding: '0.45rem 0.75rem 0.45rem 2.2rem',
                color: '#fff',
                fontSize: '0.85rem',
                outline: 'none'
              }}
            />
          </div>

          <button
            onClick={fetchActions}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              background: 'rgba(255,255,255,0.08)',
              border: '1px solid var(--border-color)',
              color: '#fff',
              padding: '0.45rem 0.85rem',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '0.85rem'
            }}
          >
            <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
            Refresh
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="glass-card" style={{ padding: 0, overflow: 'hidden' }}>
        <table className="enterprise-table">
          <thead>
            <tr>
              <th>Action ID</th>
              <th>Tool</th>
              <th>Operation</th>
              <th>Risk Level</th>
              <th>Risk Score</th>
              <th>Decision</th>
              <th>Status</th>
              <th>Timestamp</th>
              <th>Inspect</th>
            </tr>
          </thead>
          <tbody>
            {filteredActions.length === 0 ? (
              <tr>
                <td colSpan={9} style={{ textAlign: 'center', padding: '2rem', color: '#64748b' }}>
                  {loading ? 'Loading actions...' : 'No action proposals will appear here after the AI Agent processes a request.'}
                </td>
              </tr>
            ) : (
              filteredActions.map((act) => (
                <tr key={act.action_id}>
                  <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: '#a5b4fc' }}>
                    {act.action_id}
                  </td>
                  <td>
                    <span style={{ fontFamily: 'var(--font-mono)', color: '#38bdf8' }}>{act.tool}</span>
                  </td>
                  <td>{act.operation}</td>
                  <td>
                    <span className={`badge badge-${(act.risk_level || 'LOW').toLowerCase()}`}>
                      {act.risk_level}
                    </span>
                  </td>
                  <td style={{ fontWeight: 600 }}>{act.risk_score} / 100</td>
                  <td>
                    {act.decision === 'ALLOW' && <span className="badge badge-allow">ALLOW</span>}
                    {act.decision === 'REQUIRE_APPROVAL' && <span className="badge badge-approval">APPROVAL REQ</span>}
                    {act.decision === 'BLOCK' && <span className="badge badge-block">BLOCK</span>}
                  </td>
                  <td>
                    <span
                      style={{
                        fontSize: '0.75rem',
                        fontWeight: 600,
                        padding: '2px 8px',
                        borderRadius: '4px',
                        background:
                          act.status === 'EXECUTED'
                            ? 'rgba(16, 185, 129, 0.15)'
                            : act.status === 'BLOCKED'
                            ? 'rgba(239, 68, 68, 0.15)'
                            : 'rgba(245, 158, 11, 0.15)',
                        color:
                          act.status === 'EXECUTED'
                            ? '#10b981'
                            : act.status === 'BLOCKED'
                            ? '#ef4444'
                            : '#f59e0b'
                      }}
                    >
                      {act.status}
                    </span>
                  </td>
                  <td style={{ fontSize: '0.75rem', color: '#64748b' }}>
                    {new Date(act.requested_at).toLocaleTimeString()}
                  </td>
                  <td>
                    <button
                      onClick={() => setSelectedAction(act)}
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
                      <Eye size={14} /> Details
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Detail Modal */}
      {selectedAction && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0,0,0,0.75)',
            backdropFilter: 'blur(8px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 200
          }}
          onClick={() => setSelectedAction(null)}
        >
          <div
            className="glass-card"
            style={{ width: '600px', maxWidth: '90vw', maxHeight: '85vh', overflowY: 'auto' }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Shield size={18} color="#6366f1" />
                Governance Details: {selectedAction.action_id}
              </h3>
              <button
                onClick={() => setSelectedAction(null)}
                style={{ background: 'transparent', border: 'none', color: '#94a3b8', cursor: 'pointer', fontSize: '1.2rem' }}
              >
                ✕
              </button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
              <div>
                <span style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase' }}>USER PROMPT</span>
                <div style={{ background: 'rgba(0,0,0,0.3)', padding: '0.5rem 0.75rem', borderRadius: '6px', fontSize: '0.9rem' }}>
                  {selectedAction.user_prompt || 'N/A'}
                </div>
              </div>

              <div>
                <span style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase' }}>GOVERNANCE REASON</span>
                <div style={{ background: 'rgba(0,0,0,0.3)', padding: '0.5rem 0.75rem', borderRadius: '6px', fontSize: '0.85rem', color: '#a5b4fc' }}>
                  {selectedAction.reason}
                </div>
              </div>

              <div>
                <span style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase' }}>PROPOSAL PARAMETERS</span>
                <div className="code-block">
                  <pre>{JSON.stringify(selectedAction.parameters, null, 2)}</pre>
                </div>
              </div>

              {selectedAction.execution_result && (
                <div>
                  <span style={{ fontSize: '0.75rem', color: '#10b981', textTransform: 'uppercase', fontWeight: 700 }}>
                    EXECUTION RESULT
                  </span>
                  <div className="code-block">
                    <pre>{JSON.stringify(selectedAction.execution_result, null, 2)}</pre>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
