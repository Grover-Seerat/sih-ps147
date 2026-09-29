import React from 'react';
import { FileText, X, Shield, Clock, ShieldCheck, Download } from 'lucide-react';

export default function AuditLogDrawer({ isOpen, onClose, auditLogs, onLogAction }) {
  if (!isOpen) return null;

  const handleExportLogs = () => {
    const text = auditLogs.map(l => `[${l.timestamp}] [${l.user}] ${l.action}`).join('\n');
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `NTRO_Audit_Log_${new Date().toISOString().substring(0, 10)}.log`;
    a.click();
    onLogAction(`Exported analyst audit logs to file.`);
  };

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/50 backdrop-blur-xs animate-fadeIn font-mono">
      <div className="w-full max-w-md bg-white border-l border-slate-300 h-full p-6 flex flex-col justify-between shadow-2xl">
        
        {/* Drawer Header */}
        <div className="space-y-4">
          <div className="flex items-center justify-between border-b border-slate-200 pb-3">
            <div className="flex items-center space-x-2">
              <Shield className="w-5 h-5 text-blue-800" />
              <h3 className="text-sm font-extrabold text-[#002147] uppercase tracking-wider">
                Analyst Security Audit Trail
              </h3>
            </div>
            <button
              onClick={onClose}
              className="p-1 rounded bg-slate-100 text-slate-600 hover:text-slate-900"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          <p className="text-xs text-slate-600 font-sans">
            Immutable cryptographically tagged audit log recording all analyst manual overrides, file ingestions, and parameter export operations.
          </p>
        </div>

        {/* Log Entries List */}
        <div className="flex-1 my-4 overflow-y-auto space-y-2 pr-1">
          {auditLogs.length === 0 ? (
            <p className="text-xs text-slate-500 italic text-center pt-8">No actions logged yet in this session.</p>
          ) : (
            auditLogs.map((log) => (
              <div 
                key={log.id} 
                className="bg-slate-50 p-3 rounded-lg border border-slate-200 text-xs space-y-1"
              >
                <div className="flex items-center justify-between text-[10px] text-slate-500 font-bold">
                  <span className="text-blue-900">{log.user}</span>
                  <span className="flex items-center">
                    <Clock className="w-3 h-3 mr-1 text-slate-400" />
                    {log.timestamp}
                  </span>
                </div>
                <p className="text-slate-800 leading-snug">{log.action}</p>
              </div>
            ))
          )}
        </div>

        {/* Drawer Footer Actions */}
        <div className="pt-4 border-t border-slate-200 flex items-center justify-between">
          <span className="text-[11px] text-slate-600 font-bold">
            Total Entries: <strong className="text-blue-900">{auditLogs.length}</strong>
          </span>
          <button
            onClick={handleExportLogs}
            className="px-3.5 py-1.5 rounded-lg bg-[#002147] hover:bg-[#003366] text-white text-xs font-bold flex items-center shadow-xs"
          >
            <Download className="w-3.5 h-3.5 mr-1 text-amber-400" />
            Export Audit Trail
          </button>
        </div>
      </div>
    </div>
  );
}
