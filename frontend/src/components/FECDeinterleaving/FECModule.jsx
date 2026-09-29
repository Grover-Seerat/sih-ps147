import React from 'react';
import { ShieldCheck, Info } from 'lucide-react';

export default function FECModule({ activeSignal }) {
  if(!activeSignal) return <div className="p-10 text-center text-slate-500">Upload and analyze a signal first.</div>;
  return <div className="p-6 space-y-6 font-mono">
    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
      <h2 className="text-lg font-extrabold text-[#002147] flex items-center"><ShieldCheck className="w-5 h-5 mr-2"/>FEC & DE-INTERLEAVING</h2>
      <p className="text-xs text-slate-600 mt-1">Backend currently analyzes modulation/DSP/demodulation. FEC decoding is not implemented, so no simulated BER or corrected-bit values are displayed.</p>
    </div>
    <div className="bg-blue-50 border border-blue-200 rounded-xl p-6 text-sm text-blue-900">
      <div className="flex items-start"><Info className="w-5 h-5 mr-2 mt-0.5"/><div>
        <strong>Analysis status</strong>
        <p className="mt-2">Selected signal: {activeSignal.name}</p>
        <p>Detected modulation: {activeSignal.modulation}</p>
        <p>FEC: {activeSignal.fecType}</p>
        <p className="mt-2">To keep the application evidence-based, the frontend no longer shows hard-coded FEC lock, BER, corrected-error counts, or fabricated before/after bitstreams.</p>
      </div></div>
    </div>
  </div>;
}
