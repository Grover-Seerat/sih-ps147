import React, { useEffect, useRef, useState } from 'react';
import { Radio, RefreshCw, Eye } from 'lucide-react';
import { apiFetch } from '../../api';

export default function DemodulationModule({ activeSignal, onLogAction }) {
  const [points, setPoints] = useState(null);
  const [error, setError] = useState('');
  const canvasRef = useRef(null);

  useEffect(() => {
    if (!activeSignal?.analysisId) return;
    apiFetch(`/constellation/${activeSignal.analysisId}`)
      .then(data => { setPoints(data.normalized_iq || data.raw_iq); setError(''); })
      .catch(e => setError(e.message));
  }, [activeSignal?.analysisId]);

  useEffect(() => {
    const canvas=canvasRef.current;
    if(!canvas || !points?.i?.length) return;
    const ctx=canvas.getContext('2d'), w=canvas.width,h=canvas.height;
    ctx.clearRect(0,0,w,h); ctx.fillStyle='#0a0f1d'; ctx.fillRect(0,0,w,h);
    ctx.strokeStyle='rgba(71,85,105,.7)'; ctx.beginPath();
    ctx.moveTo(w/2,0);ctx.lineTo(w/2,h);ctx.moveTo(0,h/2);ctx.lineTo(w,h/2);ctx.stroke();
    const lim=1.5;
    ctx.fillStyle='#22d3ee';
    const n=Math.min(points.i.length,3000);
    for(let k=0;k<n;k++){
      const x=w/2+(Math.max(-lim,Math.min(lim,points.i[k]))/lim)*(w*.42);
      const y=h/2-(Math.max(-lim,Math.min(lim,points.q[k]))/lim)*(h*.42);
      ctx.fillRect(x-1.5,y-1.5,3,3);
    }
  }, [points]);

  if(!activeSignal) return <div className="p-10 text-center text-slate-500">Upload and analyze a signal first.</div>;
  const demod=activeSignal.demodulation;
  const result=demod?.result;
  return (
    <div className="p-6 space-y-6 font-mono">
      <div className="bg-white border border-slate-200 rounded-xl p-4 flex justify-between items-center shadow-sm">
        <div>
          <h2 className="text-sm font-extrabold text-[#002147] flex items-center"><Radio className="w-5 h-5 mr-2"/>DEMODULATION & CONSTELLATION ANALYSIS</h2>
          <p className="text-[11px] text-slate-600 mt-1">{activeSignal.name} · Backend classified as <strong>{activeSignal.modulation}</strong></p>
        </div>
        <button onClick={()=>apiFetch(`/constellation/${activeSignal.analysisId}`).then(d=>setPoints(d.normalized_iq||d.raw_iq)).catch(e=>setError(e.message))}
          className="px-3 py-1.5 rounded-lg bg-[#002147] text-white text-xs font-bold flex items-center"><RefreshCw className="w-3.5 h-3.5 mr-1"/>REFRESH</button>
      </div>
      {error && <div className="bg-red-50 border border-red-200 text-red-800 rounded-xl p-3 text-xs font-bold">{error}</div>}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-7 bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
          <h3 className="text-sm font-extrabold text-[#002147] mb-3">I/Q CONSTELLATION — ACTUAL UPLOADED SAMPLES</h3>
          <div className="bg-slate-950 rounded-xl p-3"><canvas ref={canvasRef} width="600" height="600" className="w-full max-h-[520px] object-contain"/></div>
        </div>
        <div className="lg:col-span-5 bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4">
          <h3 className="text-sm font-extrabold text-[#002147] flex items-center"><Eye className="w-4 h-4 mr-2"/>BACKEND DEMODULATION RESULT</h3>
          <Metric label="Modulation" value={activeSignal.modulation}/>
          <Metric label="Demodulator status" value={demod?.status || 'Unavailable'}/>
          <Metric label="Carrier offset" value={`${activeSignal.carrierOffsetHz ?? 'N/A'} Hz`}/>
          <Metric label="Samples per symbol" value={result?.samples_per_symbol ?? 'N/A'}/>
          <Metric label="Recovered bits" value={result?.num_bits ?? (result?.bits?.length ?? 0)}/>
          {result?.audio && <Metric label="Recovered audio samples" value={result.audio.length}/>}
          <div className="p-3 rounded-lg bg-slate-50 border text-[11px] text-slate-600">
            The constellation and demodulation values shown here come from the FastAPI backend; no synthetic frontend constellation is used.
          </div>
        </div>
      </div>
    </div>
  );
}
function Metric({label,value}){return <div className="flex justify-between border-b border-slate-100 pb-2 text-xs"><span className="font-bold text-slate-600">{label}</span><span className="font-extrabold text-blue-900">{String(value)}</span></div>}
