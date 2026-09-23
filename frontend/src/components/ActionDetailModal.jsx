import React, { useState, useEffect } from 'react';
import { Shield, Clock, CheckCircle, AlertTriangle, XCircle, User, Bot, Cpu, FileText, ArrowDown } from 'lucide-react';

export default function ActionDetailModal({ actionId, onClose }) {
  const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!actionId) return;
    setLoading(true);
    fetch(`http://localhost:8000/api/actions/${actionId}`)
      .then((res) => res.json())
      .then((data) => {
        setDetail(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, [actionId]);

  if (!actionId) return null;

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        background: 'rgba(0,0,0,0.8)',
        backdropFilter: 'blur(8px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 300,
        padding: '1.5rem'
      }}
      onClick={onClose}
    >
      <div
        className="glass-card"
        style={{
          width: '720px',
          maxWidth: '95vw',
          maxHeight: '90vh',
          overflowY: 'auto',
          background: '#0d111a',
          border: '1px solid var(--border-color)',
          padding: '1.75rem'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.85rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Shield size={22} color="#6366f1" />
              <span style={{ fontSize: '1.15rem', fontWeight: 700, color: '#ffffff' }}>
                Governance Traceability: {actionId}
              </span>
            </div>
            <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
              Complete lifecycle audit trail from AI Agent proposal to tool execution gateway.
            </span>
          </div>

          <button
            onClick={onClose}
            style={{ background: 'transparent', border: 'none', color: '#94a3b8', fontSize: '1.4rem', cursor: 'pointer' }}
          >
            ✕
          </button>
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '3rem 0', color: '#64748b' }}>
            Fetching governance timeline from TrustLayer...
          </div>
        ) : !detail ? (
          <div style={{ textAlign: 'center', padding: '2rem 0', color: '#ef4444' }}>
            Action proposal not found.
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            {/* Overview Metadata */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '0.75rem', background: 'rgba(0,0,0,0.3)', padding: '0.85rem', borderRadius: '10px' }}>
              <div>
                <span style={{ fontSize: '0.7rem', color: '#64748b', display: 'block' }}>USER PROMPT</span>
                <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#fff' }}>"{detail.user_prompt || 'N/A'}"</span>
              </div>
              <div>
                <span style={{ fontSize: '0.7rem', color: '#64748b', display: 'block' }}>TOOL & OPERATION</span>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.85rem', color: '#38bdf8', fontWeight: 600 }}>
                  {detail.tool} ({detail.operation})
                </span>
              </div>
              <div>
                <span style={{ fontSize: '0.7rem', color: '#64748b', display: 'block' }}>RISK SCORE</span>
                <span className={`badge badge-${(detail.risk_level || 'LOW').toLowerCase()}`}>
                  {detail.risk_level} ({detail.risk_score}/100)
                </span>
              </div>
              <div>
                <span style={{ fontSize: '0.7rem', color: '#64748b', display: 'block' }}>GOVERNANCE DECISION</span>
                <span className={`badge badge-${detail.decision === 'ALLOW' ? 'allow' : detail.decision === 'REQUIRE_APPROVAL' ? 'approval' : 'block'}`}>
                  {detail.decision}
                </span>
              </div>
            </div>

            {/* Step-by-Step Lifecycle Timeline */}
            <div>
              <h4 style={{ fontSize: '0.9rem', fontWeight: 700, color: '#a5b4fc', marginBottom: '1rem', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Governance Lifecycle Pipeline
              </h4>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
                {detail.timeline.map((st, idx) => (
                  <div
                    key={idx}
                    style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '0.85rem',
                      background: 'rgba(255,255,255,0.02)',
                      border: '1px solid var(--border-color)',
                      borderRadius: '10px',
                      padding: '0.85rem 1rem'
                    }}
                  >
                    <div
                      style={{
                        width: '28px',
                        height: '28px',
                        borderRadius: '50%',
                        background:
                          st.status === 'COMPLETED' || st.status === 'APPROVED' || st.status === 'EXECUTED'
                            ? 'rgba(16, 185, 129, 0.2)'
                            : st.status === 'BLOCKED' || st.status === 'REJECTED'
                            ? 'rgba(239, 68, 68, 0.2)'
                            : 'rgba(245, 158, 11, 0.2)',
                        border: `1px solid ${
                          st.status === 'COMPLETED' || st.status === 'APPROVED' || st.status === 'EXECUTED'
                            ? '#10b981'
                            : st.status === 'BLOCKED' || st.status === 'REJECTED'
                            ? '#ef4444'
                            : '#f59e0b'
                        }`,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '0.75rem',
                        fontWeight: 700,
                        color: '#fff',
                        marginTop: '2px'
                      }}
                    >
                      {st.step}
                    </div>

                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.2rem' }}>
                        <span style={{ fontSize: '0.875rem', fontWeight: 700, color: '#ffffff' }}>{st.title}</span>
                        <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
                          <Clock size={12} style={{ display: 'inline', marginRight: '4px' }} />
                          {new Date(st.timestamp).toLocaleTimeString()}
                        </span>
                      </div>
                      <div style={{ fontSize: '0.8rem', color: '#cbd5e1', marginBottom: '0.2rem' }}>
                        <strong style={{ color: '#6366f1' }}>Actor:</strong> {st.actor}
                      </div>
                      <div style={{ fontSize: '0.825rem', color: '#94a3b8' }}>{st.explanation}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Proposal Parameters JSON */}
            <div>
              <span style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase', fontWeight: 600 }}>
                STRUCTURED ACTION PROPOSAL PARAMETERS
              </span>
              <div className="code-block" style={{ marginTop: '0.4rem' }}>
                <pre>{JSON.stringify(detail.parameters, null, 2)}</pre>
              </div>
            </div>

            {/* Tool Execution Result if any */}
            {detail.execution_result && (
              <div>
                <span style={{ fontSize: '0.75rem', color: '#10b981', textTransform: 'uppercase', fontWeight: 700 }}>
                  GATEWAY TOOL EXECUTION RESULT
                </span>
                <div className="code-block" style={{ marginTop: '0.4rem', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
                  <pre>{JSON.stringify(detail.execution_result, null, 2)}</pre>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
