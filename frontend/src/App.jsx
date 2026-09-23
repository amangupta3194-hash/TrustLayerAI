import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import DashboardView from './components/DashboardView';
import ChatView from './components/ChatView';
import MonitorView from './components/MonitorView';
import ApprovalsView from './components/ApprovalsView';
import AuditView from './components/AuditView';
import PoliciesView from './components/PoliciesView';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [pendingCount, setPendingCount] = useState(0);

  const checkPendingCount = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/approvals');
      if (res.ok) {
        const data = await res.json();
        setPendingCount(data.length);
      }
    } catch (e) {
      // Backend loading/offline
    }
  };

  useEffect(() => {
    checkPendingCount();
    const interval = setInterval(checkPendingCount, 4000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="app-container">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        pendingCount={pendingCount}
      />

      <main className="main-content">
        {activeTab === 'dashboard' && (
          <DashboardView onNavigateTab={(tab) => setActiveTab(tab)} />
        )}
        {activeTab === 'chat' && <ChatView onNewAction={checkPendingCount} />}
        {activeTab === 'approvals' && <ApprovalsView onApprovalProcessed={checkPendingCount} />}
        {activeTab === 'monitor' && <MonitorView />}
        {activeTab === 'audit' && <AuditView />}
        {activeTab === 'policies' && <PoliciesView />}
      </main>
    </div>
  );
}
