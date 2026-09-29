import React, { useMemo, useState } from 'react';
import { Binary, Search, Plus, Info } from 'lucide-react';

function bitsToHex(bits) {
  if (!bits?.length) return [];
  const rows=[];
  for(let i=0;i<bits.length;i+=64){
    const chunk=bits.slice(i,i+64).join('');
    const padded=chunk.padEnd(64,'0');
    const hex=padded.match(/.{1,8}/g).map(b=>parseInt(b,2).toString(16).padStart(2,'0').toUpperCase()).join(' ');
    rows.push({offset:`0x${(i/8).toString(16).padStart(4,'0')}`,hex, bits:chunk});
  }
  return rows.slice(0,32);
}

export default function BitstreamModule({ activeSignal, onLogAction }) {
  const [searchTerm,setSearchTerm]=useState('');
  const [customPatterns,setCustomPatterns]=useState([]);
  const [newPattern,setNewPattern]=useState('');
  const result=activeSignal?.demodulation?.result;
  const bits=result?.bits || [];
  const rows=useMemo(()=>bitsToHex(bits),[bits]);

  if(!activeSignal) return <div className="p-10 text-center text-slate-500">Upload and analyze a signal first.</div>;

  const filtered=rows.filter(r=>!searchTerm || r.hex.includes(searchTerm.replace(/^0x/i,'').toUpperCase()) || r.bits.includes(searchTerm.replace(/\s/g,'')));

  const addPattern=()=>{
    const p=newPattern.trim().toUpperCase();
    if(p&&!customPatterns.includes(p)){setCustomPatterns([...customPatterns,p]);onLogAction?.(`Added analyst preamble pattern: 0x${p}`);}
    setNewPattern('');
  };

  return (
    <div className="p-6 space-y-6 font-mono">
      <div className="bg-white border border-slate-200 rounded-xl p-5 flex flex-wrap items-center justify-between gap-4 shadow-sm">
        <div><h2 className="text-lg font-extrabold text-[#002147] flex items-center"><Binary className="w-5 h-5 mr-2"/>BITSTREAM INSPECTOR</h2>
        <p className="text-xs text-slate-600 mt-1">Derived from the backend demodulator — no hard-coded payload is displayed.</p></div>
        <div className="flex gap-2"><div className="relative"><Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400"/><input value={searchTerm} onChange={e=>setSearchTerm(e.target.value)} placeholder="Search HEX / bits" className="border rounded-lg pl-9 pr-3 py-2 text-xs w-48"/></div>
        <input value={newPattern} onChange={e=>setNewPattern(e.target.value)} placeholder="Add HEX pattern" className="border rounded-lg px-3 py-2 text-xs w-36"/>
        <button onClick={addPattern} className="px-3 py-2 rounded-lg bg-[#002147] text-white text-xs font-bold"><Plus className="w-3.5 h-3.5 inline mr-1"/>ADD</button></div>
      </div>
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
        <div className="flex justify-between border-b pb-3"><h3 className="text-sm font-extrabold text-[#002147]">RECOVERED BITSTREAM / HEX VIEW</h3><span className="text-xs text-slate-500">{bits.length} bits</span></div>
        {!bits.length ? <div className="py-12 text-center text-xs text-slate-500">The selected backend demodulator did not return a bitstream.</div> :
        <div className="mt-4 space-y-2 max-h-[500px] overflow-y-auto">{filtered.map((r,i)=><div key={i} className="flex gap-4 items-center text-xs"><span className="text-slate-500 w-16">{r.offset}</span><span className="bg-slate-50 border rounded px-3 py-2 tracking-widest text-blue-900">{r.hex}</span><span className="text-slate-500">{r.bits}</span></div>)}</div>}
      </div>
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 text-xs text-blue-900 flex items-start"><Info className="w-4 h-4 mr-2 mt-0.5"/><div><strong>Preamble correlation:</strong> the current FastAPI backend does not expose a correlation endpoint, so no fabricated correlation score is shown. Analyst patterns saved above are local UI state only.</div></div>
    </div>
  );
}
