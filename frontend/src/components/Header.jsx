import React, { useState } from 'react';
import { Search, FileText, UserCheck, ShieldAlert } from 'lucide-react';
import AshokStambh from './Shared/AshokStambh';

export default function Header({ 
  activeSignal, 
  onSearchSignal,
  onOpenAuditLog
}) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All Categories');

  const handleSearch = (e) => {
    e.preventDefault();
    if (onSearchSignal) {
      onSearchSignal(searchQuery, selectedCategory);
    }
  };

  return (
    <header className="w-full bg-white border-b border-slate-200/80 shadow-xs relative z-30 font-sans">
      
      {/* 1. Official Government of India Tri-Color Top Ribbon */}
      <div className="h-1.5 w-full bg-tri-color-bar" />

      {/* 2. Main Clean & Smooth Header (Inspired by SIH / Ministry of Education Header) */}
      <div className="max-w-[1750px] mx-auto px-6 py-4 flex flex-col lg:flex-row items-center justify-between gap-4">
        
        {/* Left: Official Emblems + Title Stack */}
        <div className="flex items-center space-x-5 flex-shrink-0">
          
          {/* Ashok Stambh Emblem */}
          <div className="flex items-center justify-center">
            <AshokStambh className="h-16 w-auto" />
          </div>

          <div className="h-12 w-[1px] bg-slate-300 hidden sm:block" />

          {/* NTRO Transparent Logo */}
          <img 
            src="/ntro-logo.png" 
            alt="National Technical Research Organisation Transparent Logo" 
            className="h-20 w-auto object-contain hover:scale-105 transition-all drop-shadow-sm"
          />

          {/* Title Hierarchy */}
          <div className="flex flex-col">
            <h1 className="text-3xl md:text-4xl font-black tracking-tight text-[#002147] font-sans leading-none">
              sigint.ntro.gov.in
            </h1>
            
            {/* Hindi Title */}
            <p className="text-sm font-extrabold text-slate-800 tracking-wide mt-1">
              राष्ट्रीय अंतरिक्ष सिग्नल खुफिया पोर्टल
            </p>
            
            {/* English Title Directly Under Hindi Title */}
            <p className="text-xs font-bold text-amber-700 tracking-wide uppercase mt-0.5">
              National Portal of Space Telemetry
            </p>
          </div>
        </div>

        {/* Center: Wide Clean Search Box */}
        <div className="w-full lg:max-w-xl flex-1 px-2">
          <form onSubmit={handleSearch} className="flex items-center bg-slate-100/90 hover:bg-slate-100 border border-slate-300 rounded-xl p-1 shadow-2xs transition-all">
            <div className="flex-1 flex items-center px-3">
              <Search className="w-4 h-4 text-slate-400 mr-2 flex-shrink-0" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search Satellite Downlinks, NORAD Transponders, Preambles..."
                className="w-full py-2 bg-transparent text-slate-900 font-medium text-xs md:text-sm outline-none placeholder-slate-400 font-sans"
              />
            </div>

            <div className="hidden sm:block border-l border-slate-300 px-3">
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="py-1 bg-transparent text-slate-700 font-bold text-xs outline-none cursor-pointer"
              >
                <option value="All Categories">All Categories</option>
                <option value="GEO Satellites">GEO Satellites (35,786 km)</option>
                <option value="LEO Satellites">LEO Satellites (550 km)</option>
                <option value="NavIC Telemetry">NavIC Ranging</option>
              </select>
            </div>

            {/* Vibrant Red Search Button */}
            <button
              type="submit"
              className="px-6 py-2.5 bg-[#e11d48] hover:bg-red-700 text-white font-extrabold text-xs md:text-sm rounded-lg transition-all shadow-xs uppercase tracking-wider flex-shrink-0"
            >
              Search
            </button>
          </form>
        </div>

        {/* Right: Clean Modern Action Buttons (Inspired by SIH Login / MIC Alumni pills) */}
        <div className="flex items-center space-x-3 flex-shrink-0">
          
          <button
            onClick={onOpenAuditLog}
            className="px-4 py-2 rounded-full border border-slate-300 text-slate-700 hover:bg-slate-100 font-bold text-xs transition-all flex items-center shadow-2xs"
          >
            <FileText className="w-3.5 h-3.5 mr-1.5 text-amber-600" />
            Audit Logs
          </button>

          <div className="flex items-center px-4 py-2 rounded-full bg-[#002147] text-white font-bold text-xs shadow-xs space-x-2">
            <ShieldAlert className="w-3.5 h-3.5 text-amber-300" />
            <span>NTRO SIGINT Portal</span>
          </div>

          <div className="text-xl leading-none px-1">
            🇮🇳
          </div>
        </div>
      </div>
    </header>
  );
}
