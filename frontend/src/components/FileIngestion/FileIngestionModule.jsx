import React, { useState } from 'react';
import {
  UploadCloud, Sliders, Clock, Play, Sparkles, Database, Satellite,
  CheckCircle2, AlertTriangle
} from 'lucide-react';
import { uploadAndAnalyze } from '../../api';

function toFrontendSignal(analysis, originalFile, metadata) {
  const s = analysis.signals?.[0];
  if (!s) throw new Error(analysis.error || 'Backend returned no detectable signal.');

  const mod = s.modulation || {};
  return {
    id: analysis.analysis_id,
    analysisId: analysis.analysis_id,
    fileId: analysis.analysis_id,
    name: originalFile.name,
    format: analysis.file?.format || originalFile.type || 'IQ/WAV',
    sampleRateMHz: (analysis.file?.sample_rate_hz || 0) / 1e6,
    centerFreqMHz: Number(metadata.centerFreqMHz) || 0,
    bandwidthMHz: (s.bandwidth_hz?.value || 0) / 1e6,
    modulation: mod.label || 'Unknown',
    confidence: Number(((mod.confidence || 0) * 100).toFixed(1)),
    estSymbolRateBaud: s.symbol_rate_hz?.value || 0,
    snrDb: s.snr_db?.value ?? null,
    carrierOffsetHz: s.carrier_offset_hz?.value ?? null,
    fecType: 'Not analyzed by backend',
    interleaver: 'Not analyzed by backend',
    timestamp: new Date().toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' }) + ' IST',
    evidence: s.evidence || [],
    topCandidates: mod.top_candidates || [],
    demodulation: s.demodulation || null,
    dspFeatures: s.dsp_features || {},
    rawResult: analysis,
    noradId: metadata.noradId || '',
    orbitType: metadata.orbitType || ''
  };
}

export default function FileIngestionModule({
  activeSignal, setActiveSignal, historyList = [], onSignalAnalyzed, onLogAction
}) {
  const [dragActive, setDragActive] = useState(false);
  const [metadata, setMetadata] = useState({
    noradId: '',
    orbitType: '',
    sampleRateMHz: '',
    centerFreqMHz: '',
    sampleFormat: 'Auto-detected from file'
  });
  const [status, setStatus] = useState({ type: 'idle', message: '' });
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const processFileIngestion = async (file) => {
    const ext = file.name.toLowerCase().split('.').pop();
    if (!['iq', 'wav'].includes(ext)) {
      setStatus({ type: 'error', message: 'Only .IQ and .WAV files are supported by the backend.' });
      return;
    }

    const sr = ext === 'iq' ? Number(metadata.sampleRateMHz) * 1e6 : null;
    if (ext === 'iq' && (!sr || sr <= 0)) {
      setStatus({ type: 'error', message: 'Raw .IQ files have no header. Enter the sample rate before analysis.' });
      return;
    }

    setIsAnalyzing(true);
    setStatus({ type: 'working', message: 'Uploading file and running backend DSP + ML analysis…' });
    onLogAction?.(`Uploading ${file.name} to RF analysis backend`);

    try {
      const { analysis } = await uploadAndAnalyze(file, sr, false);
      const signal = toFrontendSignal(analysis, file, metadata);
      setMetadata(prev => ({
        ...prev,
        sampleRateMHz: signal.sampleRateMHz || prev.sampleRateMHz,
        sampleFormat: signal.format
      }));
      onSignalAnalyzed?.(signal);
      setStatus({
        type: 'success',
        message: `Analysis complete: ${signal.modulation} (${signal.confidence}% confidence)`
      });
      onLogAction?.(`Backend analyzed ${file.name}: ${signal.modulation}, SNR ${signal.snrDb ?? 'N/A'} dB`);
    } catch (error) {
      setStatus({ type: 'error', message: error.message || 'Backend analysis failed.' });
      onLogAction?.(`Backend analysis failed for ${file.name}: ${error.message}`);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragActive(false);
    if (e.dataTransfer.files?.[0]) processFileIngestion(e.dataTransfer.files[0]);
  };

  const loadSignalFromHistory = (signal) => {
    apiFetch(`/result/${signal.analysisId}`)
    setMetadata({
      noradId: signal.noradId || '',
      orbitType: signal.orbitType || '',
      sampleRateMHz: signal.sampleRateMHz || '',
      centerFreqMHz: signal.centerFreqMHz || '',
      sampleFormat: signal.format || 'Backend detected'
    });
    onLogAction?.(`Loaded analyzed session: ${signal.name}`);
  };

  return (
    <div className="p-8 max-w-[1600px] mx-auto space-y-8 font-sans">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <div className="lg:col-span-7 space-y-8">
          <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
            <div className="flex items-center justify-between mb-4 border-b border-slate-100 pb-4">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-xl bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600">
                  <Satellite className="w-5 h-5" />
                </div>
                <div>
                  <h2 className="text-lg font-black text-slate-900">RF Signal Ingestion & Analysis</h2>
                  <p className="text-xs text-slate-500 mt-0.5">Upload a real .IQ or .WAV capture. No frontend sample signal is loaded.</p>
                </div>
              </div>
              <span className="text-xs font-mono font-bold px-3 py-1 rounded-full bg-slate-100 text-slate-700">.IQ / .WAV</span>
            </div>

            <div
              onDragEnter={(e) => { e.preventDefault(); setDragActive(true); }}
              onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
              onDragLeave={() => setDragActive(false)}
              onDrop={handleDrop}
              className={`border-2 border-dashed rounded-2xl p-10 text-center transition-all relative overflow-hidden ${
                dragActive ? 'border-indigo-500 bg-indigo-50' : 'border-slate-200 hover:border-indigo-400 bg-slate-50/50'
              }`}
            >
              <input type="file" onChange={(e) => e.target.files?.[0] && processFileIngestion(e.target.files[0])}
                accept=".iq,.wav" disabled={isAnalyzing}
                className="absolute inset-0 opacity-0 cursor-pointer w-full h-full z-10" />
              <UploadCloud className="w-12 h-12 mx-auto text-indigo-600 mb-3" />
              <p className="text-base font-extrabold text-slate-800">
                {isAnalyzing ? 'Analyzing with backend…' : 'Drag & Drop RF Capture Here'}
              </p>
              <p className="text-xs text-slate-500 mt-1">The backend performs the actual DSP and Random Forest classification.</p>
            </div>

            {status.message && (
              <div className={`mt-4 p-3 rounded-xl border text-xs font-bold flex items-center ${
                status.type === 'error' ? 'bg-red-50 border-red-200 text-red-800' :
                status.type === 'success' ? 'bg-emerald-50 border-emerald-200 text-emerald-800' :
                'bg-blue-50 border-blue-200 text-blue-800'
              }`}>
                {status.type === 'success' ? <CheckCircle2 className="w-4 h-4 mr-2" /> :
                 status.type === 'error' ? <AlertTriangle className="w-4 h-4 mr-2" /> :
                 <Sparkles className="w-4 h-4 mr-2" />}
                {status.message}
              </div>
            )}
          </div>

          <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-5">
            <div className="border-b border-slate-100 pb-4">
              <h3 className="text-base font-extrabold text-slate-900 flex items-center">
                <Sliders className="w-5 h-5 mr-2 text-amber-500" /> Capture Metadata
              </h3>
              <p className="text-[11px] text-slate-500 mt-1">Only information not carried by raw IQ is entered here. It does not override ML results.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-5 text-xs">
              <div>
                <label className="block text-slate-600 font-bold mb-1.5">Selected File</label>
                <input readOnly value={activeSignal?.name || 'No file selected'}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 text-slate-800 font-bold" />
              </div>
              <div>
                <label className="block text-slate-600 font-bold mb-1.5">Sample Rate (MHz) — required for .IQ</label>
                <input type="number" step="0.001" value={metadata.sampleRateMHz}
                  onChange={e => setMetadata({...metadata, sampleRateMHz: e.target.value})}
                  placeholder="e.g. 2.0"
                  className="w-full bg-white border border-slate-200 rounded-xl p-2.5 text-slate-800" />
              </div>
              <div>
                <label className="block text-slate-600 font-bold mb-1.5">Center Frequency (MHz)</label>
                <input type="number" step="0.001" value={metadata.centerFreqMHz}
                  onChange={e => setMetadata({...metadata, centerFreqMHz: e.target.value})}
                  placeholder="Optional display metadata"
                  className="w-full bg-white border border-slate-200 rounded-xl p-2.5 text-slate-800" />
              </div>
              <div>
                <label className="block text-slate-600 font-bold mb-1.5">Satellite / Target ID</label>
                <input value={metadata.noradId} onChange={e => setMetadata({...metadata, noradId: e.target.value})}
                  placeholder="Optional"
                  className="w-full bg-white border border-slate-200 rounded-xl p-2.5 text-slate-800" />
              </div>
              <div>
                <label className="block text-slate-600 font-bold mb-1.5">Orbital Regime</label>
                <input value={metadata.orbitType} onChange={e => setMetadata({...metadata, orbitType: e.target.value})}
                  placeholder="Optional"
                  className="w-full bg-white border border-slate-200 rounded-xl p-2.5 text-slate-800" />
              </div>
              <div>
                <label className="block text-slate-600 font-bold mb-1.5">Detected Format</label>
                <input readOnly value={activeSignal?.format || metadata.sampleFormat}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 text-slate-700" />
              </div>
            </div>
          </div>
        </div>

        <div className="lg:col-span-5">
          <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-5">
            <div className="flex items-center justify-between border-b border-slate-100 pb-4">
              <h3 className="text-base font-extrabold text-slate-900 flex items-center">
                <Database className="w-5 h-5 mr-2 text-indigo-600" /> Analyzed Sessions
              </h3>
              <span className="text-xs font-mono font-bold text-slate-500">{historyList.length} Tracks</span>
            </div>

            {historyList.length === 0 ? (
              <div className="p-8 text-center border border-dashed border-slate-200 rounded-xl text-xs text-slate-500">
                No analyzed sessions yet.<br />Upload a capture to populate this list.
              </div>
            ) : (
              <div className="space-y-4 max-h-[620px] overflow-y-auto">
                {historyList.map(sig => (
                  <div key={sig.id} onClick={() => loadSignalFromHistory(sig)}
                    className={`p-4 rounded-2xl border cursor-pointer transition-all ${
                      activeSignal?.id === sig.id ? 'bg-indigo-50 border-indigo-300' : 'bg-slate-50 border-slate-200 hover:border-indigo-300'
                    }`}>
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-extrabold text-slate-900 text-sm truncate max-w-[230px]">{sig.name}</span>
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">{sig.modulation}</span>
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-xs text-slate-600 font-mono">
                      <div>Sample rate: <strong>{sig.sampleRateMHz?.toFixed?.(3) || sig.sampleRateMHz} MHz</strong></div>
                      <div>Bandwidth: <strong>{sig.bandwidthMHz?.toFixed?.(3) || 0} MHz</strong></div>
                      <div>SNR: <strong>{sig.snrDb ?? 'N/A'} dB</strong></div>
                      <div>Confidence: <strong>{sig.confidence}%</strong></div>
                    </div>
                    <div className="mt-3 pt-2 border-t border-slate-200 text-[11px] text-slate-500 flex items-center">
                      <Clock className="w-3 h-3 mr-1" /> {sig.timestamp}
                      <span className="ml-auto text-indigo-600 font-bold"><Play className="w-3 h-3 inline mr-1" />Load Session</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
