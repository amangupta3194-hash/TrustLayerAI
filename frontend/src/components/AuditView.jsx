import React, { useState, useEffect } from 'react';
import { Search, RefreshCw, Eye, Shield, Trash2 } from 'lucide-react';

export default function AuditView() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedLog, setSelectedLog] = useState(null);

  const fetchAuditLogs = async () => {
    setLoading(true);
    try {
      const url = search
        ? `/api/audit?search=${encodeURIComponent(search)}`
        : '/api/audit';

      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setLogs(data);
      }
    } catch (err) {
      console.error('Failed to fetch audit logs:', err);
    } finally {
      setLoading(false);
    }
  };

  const resetDemoData = async () => {
    if (!window.confirm('This will clear existing demo actions, approvals and audit events from the local development database. Continue?')) return;
    try {
      const res = await fetch('/api/demo/reset', { method: 'POST' });
      if (res.ok) {
        await fetchAuditLogs();
        window.dispatchEvent(new Event('demoReset'));
      } else {
        alert('Failed to reset demo data');
      }
    } catch (e) {
      console.error(e);
      alert('Error resetting demo data');
    }
  };

  useEffect(() => {
    fetchAuditLogs();
  }, [search]);

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Search size={22} color="#a5b4fc" />
            TrustLayer System Audit Explorer
          </h2>
          <p style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
            Chronological audit trail recording all governance checks, policy decisions, approvals, and tool execution events.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <div style={{ position: 'relative' }}>
            <Search size={16} color="#64748b" style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)' }} />
            <input
              type="text"
              placeholder="Search audit logs..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{
                background: 'rgba(255,255,1,0.05)',
                border: '1px solid var(--border-color)',
                borderRadius: '8px',
                padding: '0.45rem 0.75rem 0.45rem 2.2rem',
                color: '#fff',
                fontSize: '0.85rem',
                outline: 'none',
                width: '240px',
              }}
            />
          </div>
          <button
            onClick={resetDemoData}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              background: 'rgba(239, 68, 68, 0.1)',
              border: '1px solid rgba(239, 68, 68, 0.2)',
              color: '#f87171',
              padding: '0.45rem 0.85rem',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '0.85rem',
            }}
          >
            <Trash2 size={14} />
            Reset Data
          </button>
          <button
            onClick={fetchAuditLogs}
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
              fontSize: '0.85rem',
            }}
          >
            <RefreshCw size={14} className={loading ? 'animate-spin' : ''} /> Refresh Logs
          </button>
        </div>
      </div>
      {/* Audit Log Table */}
      <div className="glass-card" style={{ padding: 0, overflow: 'hidden' }}>
        <table className="enterprise-table">
          <thead>
            <tr>
              <th>Log ID</th>
              <th>Action ID</th>
              <th>Actor</th>
              <th>Event Type</th>
              <th>Timestamp</th>
              <th>Details Preview</th>
              <th>Inspect</th>
            </tr>
          </thead>
          <tbody>
            {logs.length === 0 ? (
              <tr>
                <td colSpan={7} style={{ textAlign: 'center', padding: '2rem', color: '#64748b' }}>
                  {loading ? 'Fetching audit trail from secure ledger...' : search ? 'No logs match your current search criteria.' : 'No audit events yet. Governed actions will appear here after the AI Agent processes a request.'}
                </td>
              </tr>
            ) : (
              logs.map((log) => (
                <tr key={log.id}>
                  <td style={{ fontFamily: 'var(--font-mono)', color: '#64748b', fontSize: '0.75rem' }}>#{log.id}</td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: '#a5b4fc' }}>{log.action_id}</td>
                  <td>
                    <span style={{
                      fontSize: '0.75rem',
                      fontWeight: 600,
                      padding: '2px 8px',
                      borderRadius: '4px',
                      background: log.actor === 'AI_AGENT' ? 'rgba(99,102,241,0.15)' : log.actor === 'TRUSTLAYER' ? 'rgba(6,182,212,0.15)' : 'rgba(245,158,11,0.15)',
                      color: log.actor === 'AI_AGENT' ? '#a5b4fc' : log.actor === 'TRUSTLAYER' ? '#38bdf8' : '#f59e0b',
                    }}>
                      {log.actor}
                    </span>
                  </td>
                  <td style={{ fontWeight: 600, fontSize: '0.825rem' }}>{log.event_type}</td>
                  <td style={{ fontSize: '0.75rem', color: '#64748b' }}>{new Date(log.timestamp).toLocaleTimeString()}</td>
                  <td style={{ fontSize: '0.75rem', color: '#cbd5e1', maxWidth: '240px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{JSON.stringify(log.details)}</td>
                  <td>
                    <button
                      onClick={() => setSelectedLog(log)}
                      style={{
                        background: 'transparent',
                        border: 'none',
                        color: '#6366f1',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.2rem',
                        fontWeight: 600,
                        fontSize: '0.8rem',
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
      {/* Log Detail Inspector Modal */}
      {selectedLog && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0,0,0,0.75)',
            backdropFilter: 'blur(8px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 300,
          }}
          onClick={() => setSelectedLog(null)}
        >
          <div className="glass-card" style={{ width: '560px', maxWidth: '90vw' }} onClick={(e) => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h3 style={{ fontSize: '1.05rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Shield size={18} color="#a5b4fc" />
                Audit Event #{selectedLog.id}
              </h3>
              <button onClick={() => setSelectedLog(null)} style={{ background: 'transparent', border: 'none', color: '#94a3b8', cursor: 'pointer', fontSize: '1.2rem' }}>✕</button>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.5rem', background: 'rgba(0,0,0,0.3)', padding: '0.75rem', borderRadius: '6px' }}>
                <div>
                  <span style={{ fontSize: '0.7rem', color: '#64748b', display: 'block' }}>ACTION ID</span>
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.85rem', color: '#a5b4fc', fontWeight: 600 }}>{selectedLog.action_id}</span>
                </div>
                <div>
                  <span style={{ fontSize: '0.7rem', color: '#64748b', display: 'block' }}>ACTOR</span>
                  <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#38bdf8' }}>{selectedLog.actor}</span>
                </div>
                <div>
                  <span style={{ fontSize: '0.7rem', color: '#64748b', display: 'block' }}>EVENT TYPE</span>
                  <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#10b981' }}>{selectedLog.event_type}</span>
                </div>
              </div>
              <div>
                <span style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase', fontWeight: 600 }}>EVENT DETAILS JSON</span>
                <div className="code-block" style={{ marginTop: '0.3rem' }}>
                  <pre>{JSON.stringify(selectedLog.details, null, 2)}</pre>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
