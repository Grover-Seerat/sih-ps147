import React, { useEffect, useRef, useState } from 'react';
import { Activity, Play, Pause, RefreshCw } from 'lucide-react';
import { apiFetch } from '../../api';

export default function SpectralModule({ activeSignal, onLogAction }) {
  const [fftSize, setFftSize] = useState(1024);
  const [isLive, setIsLive] = useState(false);
  const [spectrum, setSpectrum] = useState(null);
  const [spectrogram, setSpectrogram] = useState(null);
  const [error, setError] = useState('');
  const psdCanvasRef = useRef(null);
  const waterfallCanvasRef = useRef(null);

  const loadData = async () => {
    if (!activeSignal?.analysisId) return;
    setError('');
    try {
      const [psd, waterfall] = await Promise.all([
        apiFetch(`/spectrum/${activeSignal.analysisId}`),
        apiFetch(`/spectrogram/${activeSignal.analysisId}`)
      ]);
      setSpectrum(psd);
      setSpectrogram(waterfall);
      onLogAction?.('Loaded backend PSD and spectrogram data');
    } catch (e) {
      setError(e.message);
    }
  };

  useEffect(() => { loadData(); }, [activeSignal?.analysisId]);

  useEffect(() => {
    const canvas = psdCanvasRef.current;
    if (!canvas || !spectrum?.frequencies_hz?.length) return;
    const ctx = canvas.getContext('2d');
    const w = canvas.width, h = canvas.height;
    ctx.clearRect(0, 0, w, h);
    ctx.fillStyle = '#0a0f1d'; ctx.fillRect(0, 0, w, h);
    ctx.strokeStyle = 'rgba(71,85,105,.5)'; ctx.lineWidth = 1;
    for (let y = 30; y < h; y += 40) { ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(w,y); ctx.stroke(); }
    const p = spectrum.power_db;
    const min = Math.min(...p), max = Math.max(...p);
    ctx.beginPath(); ctx.strokeStyle = '#22d3ee'; ctx.lineWidth = 2;
    p.forEach((v,i) => {
      const x=i/(p.length-1)*w, y=h-((v-min)/Math.max(max-min,1))*h*0.9-5;
      if(i===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
    });
    ctx.stroke();
  }, [spectrum, fftSize]);

  useEffect(() => {
    const canvas = waterfallCanvasRef.current;
    const power = spectrogram?.power_db;
    if (!canvas || !power?.length) return;
    const rows = power.length, cols = power[0]?.length || 0;
    if (!cols) return;
    const ctx = canvas.getContext('2d');
    const img = ctx.createImageData(canvas.width, canvas.height);
    let min=Infinity,max=-Infinity;
    power.forEach(r=>r.forEach(v=>{min=Math.min(min,v);max=Math.max(max,v)}));
    for(let y=0;y<canvas.height;y++){
      const sr=Math.min(rows-1,Math.floor(y/canvas.height*rows));
      for(let x=0;x<canvas.width;x++){
        const sc=Math.min(cols-1,Math.floor(x/canvas.width*cols));
        const val=Math.max(0,Math.min(1,(power[sr][sc]-min)/Math.max(max-min,1)));
        const idx=(y*canvas.width+x)*4;
        img.data[idx]=Math.floor(20+val*235);
        img.data[idx+1]=Math.floor(30+val*180);
        img.data[idx+2]=Math.floor(60+val*190);
        img.data[idx+3]=255;
      }
    }
    ctx.putImageData(img,0,0);
  }, [spectrogram]);

  if (!activeSignal) return <Empty message="Upload and analyze a signal first to view the backend spectrum." />;

  return (
    <div className="p-6 space-y-6 font-mono">
      <div className="bg-white border border-slate-200 rounded-xl p-4 flex flex-wrap items-center justify-between gap-4 shadow-sm">
        <div>
          <h2 className="text-sm font-extrabold text-[#002147] flex items-center"><Activity className="w-5 h-5 mr-2" />BACKEND SPECTRAL ANALYSIS</h2>
          <p className="text-[11px] text-slate-600 mt-1">{activeSignal.name} · {activeSignal.modulation} · fs {activeSignal.sampleRateMHz} MHz</p>
        </div>
        <div className="flex items-center gap-3 text-xs">
          <select value={fftSize} onChange={e=>setFftSize(Number(e.target.value))} className="border rounded px-2 py-1">
            <option value={512}>512</option><option value={1024}>1024</option><option value={2048}>2048</option>
          </select>
          <button onClick={()=>setIsLive(!isLive)} className="px-3 py-1.5 rounded-lg bg-slate-100 border font-bold flex items-center">
            {isLive?<Pause className="w-3.5 h-3.5 mr-1"/>:<Play className="w-3.5 h-3.5 mr-1"/>}{isLive?'PAUSE':'LIVE'}
          </button>
          <button onClick={loadData} className="px-3 py-1.5 rounded-lg bg-[#002147] text-white font-bold flex items-center"><RefreshCw className="w-3.5 h-3.5 mr-1"/>REFRESH</button>
        </div>
      </div>
      {error && <div className="bg-red-50 border border-red-200 text-red-800 rounded-xl p-3 text-xs font-bold">{error}</div>}
      <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
        <h3 className="text-sm font-extrabold text-[#002147] mb-2">POWER SPECTRAL DENSITY — BACKEND DSP</h3>
        <div className="bg-slate-950 rounded-xl overflow-hidden"><canvas ref={psdCanvasRef} width="1000" height="300" className="w-full h-[300px]"/></div>
        {spectrum && <p className="text-[10px] text-slate-500 mt-2">Samples returned: {spectrum.frequencies_hz.length} frequency bins. Values are computed from the uploaded capture.</p>}
      </div>
      <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
        <h3 className="text-sm font-extrabold text-[#002147] mb-2">WATERFALL / SPECTROGRAM — BACKEND DSP</h3>
        <div className="bg-slate-950 rounded-xl overflow-hidden"><canvas ref={waterfallCanvasRef} width="1000" height="280" className="w-full h-[280px]"/></div>
      </div>
    </div>
  );
}
function Empty({message}) { return <div className="p-10 text-center text-sm text-slate-500">{message}</div>; }
