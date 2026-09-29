import React, { useState } from 'react';
import { Shield, Lock, User, Key, CheckCircle, AlertCircle, RefreshCw, LogIn } from 'lucide-react';

export default function LoginModal({ onLogin }) {
  const [email, setEmail] = useState('analyst@ntro.gov.in');
  const [password, setPassword] = useState('ntro@sigint2026');
  const [securityPin, setSecurityPin] = useState('7809');
  const [captchaInput, setCaptchaInput] = useState('');
  const [captchaCode, setCaptchaCode] = useState('9A7K');
  const [errorMsg, setErrorMsg] = useState('');

  const refreshCaptcha = () => {
    const chars = '23456789ABCDEFGHJKLMNPQRSTUVWXYZ';
    let code = '';
    for (let i = 0; i < 4; i++) {
      code += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    setCaptchaCode(code);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!email || !password) {
      setErrorMsg('Please enter valid email and password.');
      return;
    }
    if (captchaInput.toUpperCase() !== captchaCode.toUpperCase()) {
      setErrorMsg('Invalid Captcha security code. Please try again.');
      refreshCaptcha();
      return;
    }

    // Success login
    onLogin({
      email,
      name: email.split('@')[0].toUpperCase(),
      role: 'Analyst (Level-3)',
      badgeId: `NTRO-SEC-${securityPin}`
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/80 backdrop-blur-sm p-4 font-sans">
      <div className="w-full max-w-lg bg-white rounded-2xl shadow-2xl border border-slate-300 overflow-hidden animate-fadeIn">
        
        {/* Top Tricolor Banner */}
        <div className="h-2 w-full bg-tri-color-bar" />

        {/* Modal Header */}
        <div className="bg-[#002147] text-white p-6 text-center relative">
          <div className="flex justify-center mb-2">
            <img 
              src="/ntro-logo.png" 
              alt="NTRO Logo" 
              className="w-16 h-16 object-contain rounded-full bg-white p-1 border-2 border-amber-400 shadow-lg" 
            />
          </div>
          <h2 className="text-xl font-extrabold tracking-wide uppercase">
            National Technical Research Organisation
          </h2>
          <p className="text-xs text-amber-300 font-mono font-bold mt-1">
            राष्ट्रीय तकनीकी अनुसंधान संगठन • SIGINT Analyst Portal
          </p>
          <span className="inline-block mt-2 px-3 py-0.5 rounded-full bg-amber-500/20 text-amber-300 text-[11px] font-mono border border-amber-400/40">
            RESTRICTED // GOI AUTHORIZED PERSONNEL ONLY
          </span>
        </div>

        {/* Login Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          
          {/* Quick Demo Credentials Info Box */}
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-3.5 text-xs text-blue-900 space-y-1">
            <div className="font-extrabold flex items-center text-blue-950 text-sm">
              <Shield className="w-4 h-4 mr-1.5 text-blue-700" />
              Demo Credentials (Pre-filled):
            </div>
            <div className="grid grid-cols-2 gap-2 pt-1 font-mono">
              <div>Email: <strong className="text-slate-900">analyst@ntro.gov.in</strong></div>
              <div>Password: <strong className="text-slate-900">ntro@sigint2026</strong></div>
              <div>Security PIN: <strong className="text-slate-900">7809</strong></div>
              <div>Captcha: Type code shown below</div>
            </div>
          </div>

          {errorMsg && (
            <div className="bg-red-50 border border-red-300 text-red-800 p-3 rounded-lg text-xs font-bold flex items-center">
              <AlertCircle className="w-4 h-4 mr-2 text-red-600 flex-shrink-0" />
              {errorMsg}
            </div>
          )}

          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
              Analyst Official Email / ID
            </label>
            <div className="relative">
              <User className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full pl-9 pr-3 py-2 bg-slate-50 border border-slate-300 rounded-lg text-sm text-slate-900 font-medium focus:border-blue-600 outline-none"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
              Security Password
            </label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full pl-9 pr-3 py-2 bg-slate-50 border border-slate-300 rounded-lg text-sm text-slate-900 font-medium focus:border-blue-600 outline-none"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                Security PIN
              </label>
              <div className="relative">
                <Key className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                <input
                  type="text"
                  value={securityPin}
                  onChange={(e) => setSecurityPin(e.target.value)}
                  className="w-full pl-9 pr-3 py-2 bg-slate-50 border border-slate-300 rounded-lg text-sm text-slate-900 font-mono font-bold focus:border-blue-600 outline-none"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                Enter Captcha
              </label>
              <div className="flex items-center space-x-2">
                <input
                  type="text"
                  value={captchaInput}
                  onChange={(e) => setCaptchaInput(e.target.value)}
                  placeholder={captchaCode}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-lg text-sm font-mono font-bold text-slate-900 focus:border-blue-600 outline-none uppercase"
                  required
                />
                <div className="bg-amber-100 border border-amber-300 font-mono font-extrabold text-amber-900 text-base px-3 py-1.5 rounded-lg select-none tracking-widest flex items-center">
                  {captchaCode}
                  <button type="button" onClick={refreshCaptcha} className="ml-2 text-amber-700 hover:text-amber-900">
                    <RefreshCw className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>
          </div>

          <button
            type="submit"
            className="w-full py-3 px-4 bg-[#002147] hover:bg-[#003366] text-white font-bold text-sm rounded-xl shadow-md transition-all flex items-center justify-center uppercase tracking-wider"
          >
            <LogIn className="w-4 h-4 mr-2 text-amber-400" />
            Authenticate & Access SIGINT Suite
          </button>
        </form>

        {/* Modal Footer */}
        <div className="bg-slate-100 px-6 py-3 text-center text-[11px] text-slate-500 font-mono border-t border-slate-200">
          Government of India • National Technical Research Organisation
        </div>
      </div>
    </div>
  );
}
