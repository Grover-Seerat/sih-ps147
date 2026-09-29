import React, { useState } from 'react';
import Header from './components/Header';
import Navigation from './components/Navigation';
import FileIngestionModule from './components/FileIngestion/FileIngestionModule';
import SpectralModule from './components/SpectralPanel/SpectralModule';
import ParameterModule from './components/ParameterDashboard/ParameterModule';
import DemodulationModule from './components/DemodulationPanel/DemodulationModule';
import FECModule from './components/FECDeinterleaving/FECModule';
import BitstreamModule from './components/BitstreamPanel/BitstreamModule';
import ReportingModule from './components/ExportReporting/ReportingModule';
import AuditLogDrawer from './components/Shared/AuditLogDrawer';
import Footer from './components/Footer';

export default function App() {
  const [activeTab, setActiveTab] = useState('ingestion');
  const [activeSignal, setActiveSignal] = useState(null);
  const [historyList, setHistoryList] = useState([]);
  const [isAuditLogOpen, setIsAuditLogOpen] = useState(false);
  const [fontSizeLevel, setFontSizeLevel] = useState('normal');
  const [auditLogs, setAuditLogs] = useState([]);

  const addAuditLog = (actionText) => {
    const newLog = {
      id: Date.now(),
      user: 'SYSTEM',
      timestamp: new Date().toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' }),
      action: actionText
    };
    setAuditLogs(prev => [newLog, ...prev]);
  };

  const handleSignalAnalyzed = (signal) => {
    setActiveSignal(signal);
    setHistoryList(prev => {
      const withoutDuplicate = prev.filter(item => item.id !== signal.id);
      return [signal, ...withoutDuplicate];
    });
    addAuditLog(`Backend analysis completed: ${signal.name} → ${signal.modulation}`);
  };

  const handleSearchSignal = (query) => {
    const q = query.trim().toLowerCase();
    if (!q) return;
    const found = historyList.find(s =>
      s.name?.toLowerCase().includes(q) || s.id?.toLowerCase().includes(q)
    );
    if (found) {
      setActiveSignal(found);
      addAuditLog(`Loaded analyzed session from current session history: ${found.name}`);
    } else {
      addAuditLog(`No analyzed session matched search: "${query}"`);
    }
  };

  const getScaleClass = () => {
    if (fontSizeLevel === 'small') return 'text-[92%] leading-normal';
    if (fontSizeLevel === 'large') return 'text-[118%] leading-relaxed font-medium';
    return 'text-[100%] leading-normal';
  };

  return (
    <div className={`min-h-screen bg-[#f8fafc] text-slate-900 flex flex-col font-sans selection:bg-indigo-600 selection:text-white transition-all duration-200 ${getScaleClass()}`}>
      <Header
        activeSignal={activeSignal}
        fontSizeLevel={fontSizeLevel}
        setFontSizeLevel={setFontSizeLevel}
        onSearchSignal={handleSearchSignal}
        onOpenAuditLog={() => setIsAuditLogOpen(true)}
      />

      <Navigation
        activeTab={activeTab}
        setActiveTab={(tab) => {
          setActiveTab(tab);
          addAuditLog(`Switched active module to: ${tab.toUpperCase()}`);
        }}
      />

      <main className="flex-1 w-full max-w-[1700px] mx-auto transition-all duration-300">
        {activeTab === 'ingestion' && (
          <FileIngestionModule
            activeSignal={activeSignal}
            setActiveSignal={setActiveSignal}
            historyList={historyList}
            onSignalAnalyzed={handleSignalAnalyzed}
            onLogAction={addAuditLog}
          />
        )}

        {activeTab === 'spectral' && (
          <SpectralModule activeSignal={activeSignal} onLogAction={addAuditLog} />
        )}

        {activeTab === 'parameters' && (
          <ParameterModule activeSignal={activeSignal} setActiveSignal={setActiveSignal} onLogAction={addAuditLog} />
        )}

        {activeTab === 'demodulation' && (
          <DemodulationModule activeSignal={activeSignal} onLogAction={addAuditLog} />
        )}

        {activeTab === 'fec' && (
          <FECModule activeSignal={activeSignal} onLogAction={addAuditLog} />
        )}

        {activeTab === 'bitstream' && (
          <BitstreamModule activeSignal={activeSignal} onLogAction={addAuditLog} />
        )}

        {activeTab === 'reporting' && (
          <ReportingModule activeSignal={activeSignal} onLogAction={addAuditLog} />
        )}
      </main>

      <Footer />

      <AuditLogDrawer
        isOpen={isAuditLogOpen}
        onClose={() => setIsAuditLogOpen(false)}
        auditLogs={auditLogs}
        onLogAction={addAuditLog}
      />
    </div>
  );
}
