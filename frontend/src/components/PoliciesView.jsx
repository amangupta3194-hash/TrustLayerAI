import React, { useState, useEffect } from 'react';
import { FileText, Cpu, ShieldCheck, AlertCircle } from 'lucide-react';

export default function PoliciesView() {
  const [policies, setPolicies] = useState([]);
  const [tools, setTools] = useState([]);

  useEffect(() => {
    fetch('http://localhost:8000/api/policies')
      .then((res) => res.json())
      .then((data) => setPolicies(data))
      .catch((err) => console.error(err));

    fetch('http://localhost:8000/api/tools')
      .then((res) => res.json())
      .then((data) => setTools(data))
      .catch((err) => console.error(err));
  }, []);

  return (
    <div style={{ maxWidth: '1100px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Policy Rules Section */}
      <div>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
          <FileText size={22} color="#6366f1" />
          Active TrustLayer Security Policies
        </h2>
        <p style={{ fontSize: '0.85rem', color: '#94a3b8', marginBottom: '1rem' }}>
          Configurable rule-based security policies evaluated on every AI Agent action proposal.
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1rem' }}>
          {policies.map((p) => (
            <div key={p.policy_id} className="glass-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                  <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: '#a5b4fc', fontSize: '0.9rem' }}>
                    {p.policy_id}
                  </span>
                  <span className={`badge badge-${p.severity.toLowerCase()}`}>{p.severity} SEVERITY</span>
                </div>

                <div style={{ fontSize: '0.95rem', fontWeight: 700, color: '#ffffff', marginBottom: '0.4rem' }}>
                  {p.policy_name}
                </div>

                <p style={{ fontSize: '0.825rem', color: '#94a3b8', lineHeight: 1.4 }}>
                  {p.description}
                </p>
              </div>

              <div style={{ marginTop: '1rem', paddingTop: '0.75rem', borderTop: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '0.75rem', color: '#64748b' }}>VIOLATION ACTION</span>
                <span className={`badge badge-${p.action_on_violation === 'BLOCK' ? 'block' : 'approval'}`}>
                  {p.action_on_violation}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Enterprise Tools Registry */}
      <div>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
          <Cpu size={22} color="#06b6d4" />
          Registered Enterprise Tools Gateway
        </h2>
        <p style={{ fontSize: '0.85rem', color: '#94a3b8', marginBottom: '1rem' }}>
          Simulated enterprise capabilities protected behind mandatory TrustLayer evaluation.
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1rem' }}>
          {tools.map((t) => (
            <div key={t.name} className="glass-card">
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.4rem' }}>
                <ShieldCheck size={18} color="#10b981" />
                <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: '#38bdf8', fontSize: '0.95rem' }}>
                  {t.name}
                </span>
              </div>
              <p style={{ fontSize: '0.825rem', color: '#cbd5e1' }}>
                {t.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
