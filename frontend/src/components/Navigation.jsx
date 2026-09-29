import React from 'react';
import { 
  FolderOpen, 
  Activity, 
  Sliders, 
  Radio, 
  ShieldCheck, 
  Binary, 
  FileSpreadsheet
} from 'lucide-react';

export default function Navigation({ activeTab, setActiveTab }) {
  const tabs = [
    { id: 'ingestion', label: 'FILE INGESTION', icon: FolderOpen },
    { id: 'spectral', label: 'SPECTRAL ANALYSIS', icon: Activity },
    { id: 'parameters', label: 'PARAMETER DASHBOARD', icon: Sliders },
    { id: 'demodulation', label: 'DEMODULATION', icon: Radio },
    { id: 'fec', label: 'FEC & DE-INTERLEAVING', icon: ShieldCheck },
    { id: 'bitstream', label: 'BITSTREAM SEARCH', icon: Binary },
    { id: 'reporting', label: 'REPORTS & EXPORT', icon: FileSpreadsheet }
  ];

  return (
    <nav className="w-full bg-white border-y border-slate-200 shadow-2xs relative z-20 font-sans">
      <div className="max-w-[1750px] mx-auto px-4 flex items-center justify-start space-x-1 overflow-x-auto no-scrollbar scroll-smooth">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center space-x-1.5 px-3 py-2.5 text-[11px] md:text-xs font-semibold transition-all duration-150 whitespace-nowrap border-b-2 ${
                isActive
                  ? 'text-[#002147] border-[#002147] bg-slate-50/90 font-bold'
                  : 'text-slate-600 hover:text-[#002147] hover:bg-slate-50/50 border-transparent font-medium'
              }`}
            >
              <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-amber-600' : 'text-slate-400'}`} />
              <span className="tracking-tight">{tab.label}</span>
            </button>
          );
        })}
      </div>
    </nav>
  );
}
