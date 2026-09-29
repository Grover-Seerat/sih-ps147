import React, { useEffect, useState } from 'react';
import { Sliders, AlertTriangle, Play } from 'lucide-react';

export default function ParameterModule({ activeSignal, setActiveSignal, onLogAction }) {
  const [overrides,setOverrides]=useState({});
  useEffect(()=>{ if(activeSignal) setOverrides({modulation:activeSignal.modulation,symbolRateBaud:activeSignal.estSymbolRateBaud||'',fecType:activeSignal.fecType||'Not analyzed',interleaver:activeSignal.interleaver||'Not analyzed'}); },[activeSignal?.id]);

  if(!activeSignal) return <div className="p-10 text-center text-slate-500">Upload and analyze a signal first.</div>;

  const cards=[
    ['SAMPLING FREQUENCY (fs)',`${activeSignal.sampleRateMHz} MHz`,'From WAV header or supplied raw-IQ sample rate','Backend reader'],
    ['OCCUPIED BANDWIDTH',`${activeSignal.bandwidthMHz?.toFixed(4) ?? 'N/A'} MHz`,'99% power bandwidth estimate','DSP estimated'],
    ['MODULATION',activeSignal.modulation,`ML + DSP fusion · ${activeSignal.confidence}% confidence`,'ML + DSP fusion'],
    ['SIGNAL-TO-NOISE RATIO',`${activeSignal.snrDb ?? 'N/A'} dB`,'Computed from uploaded samples','DSP estimated'],
    ['SYMBOL RATE',activeSignal.estSymbolRateBaud?`${(activeSignal.estSymbolRateBaud/1e6).toFixed(3)} MBaud`:'N/A',activeSignal.estSymbolRateBaud?`${activeSignal.estSymbolRateBaud.toLocaleString()} symbols/sec`:'Not available','DSP estimated'],
    ['CARRIER OFFSET',`${activeSignal.carrierOffsetHz ?? 'N/A'} Hz`,'Estimated after modulation classification','DSP estimated']
  ];
  const apply=()=>{const updated={...activeSignal,modulation:overrides.modulation,estSymbolRateBaud:Number(overrides.symbolRateBaud)||activeSignal.estSymbolRateBaud,fecType:overrides.fecType,interleaver:overrides.interleaver,isOverridden:true};setActiveSignal(updated);onLogAction?.(`Analyst override applied: ${updated.modulation}`)};

  return <div className="p-6 space-y-6 font-mono">
    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm"><h2 className="text-lg font-extrabold text-[#002147] flex items-center"><Sliders className="w-5 h-5 mr-2"/>SIGNAL PARAMETER CLASSIFICATION DASHBOARD</h2><p className="text-xs text-slate-600 mt-1">Values below are derived from the selected backend analysis. No default signal is injected.</p></div>
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
      {cards.map(([title,value,sub,status])=><div key={title} className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm"><div className="flex justify-between text-[11px] font-extrabold text-slate-500"><span>{title}</span><span className="bg-slate-100 px-2 py-0.5 rounded">{status}</span></div><div className="text-2xl font-black text-blue-900 mt-3">{value}</div><div className="text-xs text-slate-600 mt-1">{sub}</div></div>)}
    </div>
    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4">
      <h3 className="text-sm font-extrabold text-[#002147] flex items-center"><AlertTriangle className="w-4 h-4 mr-2 text-amber-600"/>Analyst Manual Override</h3>
      <p className="text-[11px] text-slate-500">Override is a hypothesis for downstream UI/demodulation; it does not change the trained model.</p>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
        <select value={overrides.modulation||''} onChange={e=>setOverrides({...overrides,modulation:e.target.value})} className="border rounded p-2"><option value="">Select modulation</option>{['BPSK','QPSK','8PSK','16QAM','FSK','GFSK','AM','FM'].map(x=><option key={x}>{x}</option>)}</select>
        <input type="number" value={overrides.symbolRateBaud||''} onChange={e=>setOverrides({...overrides,symbolRateBaud:e.target.value})} placeholder="Symbol rate (baud)" className="border rounded p-2"/>
        <input value={overrides.fecType||''} onChange={e=>setOverrides({...overrides,fecType:e.target.value})} placeholder="FEC (optional)" className="border rounded p-2"/>
      </div>
      <button disabled={!overrides.modulation} onClick={apply} className="px-4 py-2 rounded-lg bg-amber-600 text-white text-xs font-bold flex items-center"><Play className="w-3.5 h-3.5 mr-1"/>APPLY HYPOTHESIS</button>
    </div>
  </div>
}
