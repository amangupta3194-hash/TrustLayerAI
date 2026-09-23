import React, { useState, useEffect } from 'react';
import { CheckSquare, CheckCircle, XCircle, Clock, AlertTriangle, Shield, Trash2 } from 'lucide-react';

export default function ApprovalsView({ onApprovalProcessed }) {
  const [approvals, setApprovals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [processingId, setProcessingId] = useState(null);
  const [lastActionResult, setLastActionResult] = useState(null);

  const fetchApprovals = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/approvals');
      if (res.ok) {
        const data = await res.json();
        setApprovals(data);
      }
    } catch (err) {
      console.error('Failed to fetch approvals:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchApprovals();
  }, []);

  useEffect(() => {
    const handler = () => {
      fetchApprovals();
    };
    window.addEventListener('demoReset', handler);
    return () => window.removeEventListener('demoReset', handler);
  }, []);

  const handleAction = async (actionId, type) => {
    setProcessingId(actionId);
    setLastActionResult(null);
    try {
      const res = await fetch(`http://localhost:8000/api/approvals/${actionId}/${type}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reviewer_notes: `Human operator decision: ${type.toUpperCase()}` })
      });

      if (res.ok) {
        const data = await res.json();
        setLastActionResult(data);
        await fetchApprovals();
        if (onApprovalProcessed) onApprovalProcessed();
      }
    } catch (err) {
      alert(`Error performing approval action: ${err.message}`);
    } finally {
      setProcessingId(null);
    }
  };

  const handleRemove = async (actionId) => {
    if (!window.confirm("Are you sure you want to remove this pending approval request?")) return;
    setProcessingId(actionId);
    setLastActionResult(null);
    try {
      const res = await fetch(`http://localhost:8000/api/approvals/${actionId}`, {
        method: 'DELETE'
      });

      if (res.ok) {
        const data = await res.json();
        setLastActionResult({
          status: 'REJECTED',
          message: `Approval request for action '${actionId}' has been removed from queue.`
        });
        await fetchApprovals();
        if (onApprovalProcessed) onApprovalProcessed();
      }
    } catch (err) {
      alert(`Error deleting approval: ${err.message}`);
    } finally {
      setProcessingId(null);
    }
  };

  return (
    <div style={{ maxWidth: '1100px', margin: '0 auto' }}>
      <div style={{ marginBottom: '1.75rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 800, display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <CheckSquare size={26} color="#f59e0b" />
          Pending Human Approvals Queue
        </h2>
        <p style={{ fontSize: '0.95rem', color: '#94a3b8', marginTop: '0.2rem' }}>
          High-risk action proposals held by TrustLayer policy rules requiring human authorization before tool execution.
        </p>
      </div>

      {/* Execution Feedback Notification Banner */}
      {lastActionResult && (
        <div
          className="glass-card"
          style={{
            marginBottom: '1.5rem',
            background: lastActionResult.status === 'APPROVED' ? 'rgba(16, 185, 129, 0.12)' : 'rgba(239, 68, 68, 0.12)',
            borderColor: lastActionResult.status === 'APPROVED' ? 'rgba(16, 185, 129, 0.35)' : 'rgba(239, 68, 68, 0.35)',
            display: 'flex',
            alignItems: 'flex-start',
            gap: '1rem',
            padding: '1.25rem 1.5rem'
          }}
        >
          {lastActionResult.status === 'APPROVED' ? (
            <CheckCircle size={26} color="#10b981" style={{ marginTop: '2px' }} />
          ) : (
            <XCircle size={26} color="#ef4444" style={{ marginTop: '2px' }} />
          )}

          <div style={{ flex: 1 }}>
            <div style={{ fontSize: '1.05rem', fontWeight: 800, color: '#ffffff', marginBottom: '0.35rem' }}>
              {lastActionResult.status === 'APPROVED' ? 'Action Approved & Executed' : 'Action Rejected'}
            </div>
            <div style={{ fontSize: '0.95rem', color: '#cbd5e1' }}>{lastActionResult.message}</div>

            {lastActionResult.tool_result && (
              <div className="code-block" style={{ marginTop: '0.75rem' }}>
                <pre>{JSON.stringify(lastActionResult.tool_result, null, 2)}</pre>
              </div>
            )}
          </div>

          <button
            onClick={() => setLastActionResult(null)}
            style={{ background: 'transparent', border: 'none', color: '#94a3b8', cursor: 'pointer', fontSize: '1.2rem' }}
          >
            ✕
          </button>
        </div>
      )}

      {loading ? (
        <div className="glass-card" style={{ textAlign: 'center', color: '#94a3b8', padding: '3rem' }}>
          Loading pending approvals queue...
        </div>
      ) : approvals.length === 0 ? (
        <div className="glass-card" style={{ textAlign: 'center', padding: '3.5rem 1rem' }}>
          <CheckCircle size={48} color="#10b981" style={{ margin: '0 auto 1rem auto' }} />
          <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#f3f4f6' }}>No pending approvals.</h3>
          <p style={{ fontSize: '0.95rem', color: '#94a3b8', marginTop: '0.35rem' }}>
            Actions requiring human approval will appear here.
          </p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {approvals.map((app) => {
            const details = app.action_details || {};
            const isProc = processingId === app.action_id;

            return (
              <div
                key={app.approval_id}
                className="glass-card"
                style={{
                  borderLeft: '5px solid #f59e0b',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '1.5rem'
                }}
              >
                <div style={{ flex: 1, paddingRight: '2rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem', marginBottom: '0.65rem' }}>
                    <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 800, color: '#a5b4fc', fontSize: '1.05rem' }}>
                      {app.action_id}
                    </span>
                    <span className={`badge badge-${(details.risk_level || 'HIGH').toLowerCase()}`}>
                      {details.risk_level || 'HIGH'} RISK ({details.risk_score || 80}/100)
                    </span>
                    <span style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
                      <Clock size={14} style={{ display: 'inline', marginRight: '4px' }} />
                      {new Date(app.requested_at).toLocaleTimeString()}
                    </span>
                  </div>

                  <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#ffffff', marginBottom: '0.5rem' }}>
                    User Request: "{details.user_prompt || 'N/A'}"
                  </div>

                  <div style={{ fontSize: '0.95rem', color: '#cbd5e1', marginBottom: '0.85rem', lineHeight: 1.5 }}>
                    <strong style={{ color: '#f59e0b' }}>Reason:</strong> {details.reason}
                  </div>

                  <div className="code-block" style={{ fontSize: '0.85rem' }}>
                    <strong>Tool:</strong> {details.tool} | <strong>Operation:</strong> {details.operation}
                    <pre style={{ marginTop: '0.4rem' }}>{JSON.stringify(details.parameters, null, 2)}</pre>
                  </div>
                </div>

                {/* Approve / Reject Action Buttons */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', minWidth: '170px' }}>
                  <button
                    onClick={() => handleAction(app.action_id, 'approve')}
                    disabled={isProc}
                    style={{
                      padding: '0.75rem 1.25rem',
                      background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                      color: '#fff',
                      border: 'none',
                      borderRadius: '10px',
                      fontWeight: 800,
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '0.5rem',
                      fontSize: '0.95rem',
                      boxShadow: '0 4px 14px rgba(16, 185, 129, 0.3)'
                    }}
                  >
                    <CheckCircle size={18} /> APPROVE ACTION
                  </button>

                  <button
                    onClick={() => handleAction(app.action_id, 'reject')}
                    disabled={isProc}
                    style={{
                      padding: '0.75rem 1.25rem',
                      background: 'rgba(239, 68, 68, 0.15)',
                      color: '#ef4444',
                      border: '1px solid rgba(239, 68, 68, 0.4)',
                      borderRadius: '10px',
                      fontWeight: 700,
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '0.5rem',
                      fontSize: '0.95rem'
                    }}
                  >
                    <XCircle size={18} /> REJECT ACTION
                  </button>

                  <button
                    onClick={() => handleRemove(app.action_id)}
                    disabled={isProc}
                    style={{
                      padding: '0.75rem 1.25rem',
                      background: 'rgba(100, 116, 139, 0.15)',
                      color: '#94a3b8',
                      border: '1px solid rgba(100, 116, 139, 0.4)',
                      borderRadius: '10px',
                      fontWeight: 700,
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '0.5rem',
                      fontSize: '0.95rem'
                    }}
                  >
                    <Trash2 size={18} /> DELETE / CLEAR
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
