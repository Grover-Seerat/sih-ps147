import React from 'react';
import { 
  Globe, 
  Share2, 
  ExternalLink, 
  ShieldCheck, 
  QrCode,
  ArrowUp
} from 'lucide-react';
import AshokStambh from './Shared/AshokStambh';

export default function Footer() {
  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <footer className="w-full bg-[#050914] text-slate-300 font-sans border-t-4 border-amber-500 mt-auto">
      
      {/* 1. Top Government Initiatives Bar (Directly modelled after image) */}
      <div className="bg-[#090e1c] py-6 border-b border-slate-800 px-6">
        <div className="max-w-[1700px] mx-auto flex flex-wrap items-center justify-between gap-6">
          
          <div className="flex flex-wrap items-center gap-6 justify-center md:justify-start w-full">
            <div className="px-4 py-2 rounded-lg bg-slate-900 border border-slate-700 text-xs font-mono font-bold text-slate-200">
              RIGHT TO INFORMATION
            </div>
            <div className="px-4 py-2 rounded-lg bg-[#002147] border border-blue-600 text-xs font-mono font-bold text-white">
              CPGRAMS
            </div>
            <div className="px-4 py-2 rounded-lg bg-slate-900 border border-slate-700 text-xs font-mono font-bold text-amber-400">
              data.gov.in
            </div>
            <div className="px-4 py-2 rounded-lg bg-slate-900 border border-slate-700 text-xs font-mono font-bold text-slate-200">
              PM INDIA
            </div>
            <div className="px-4 py-2 rounded-lg bg-gradient-to-r from-blue-700 to-indigo-800 text-xs font-mono font-bold text-white shadow-md">
              Digital India
            </div>
            <div className="px-4 py-2 rounded-lg bg-slate-900 border border-slate-700 text-xs font-mono font-bold text-emerald-400">
              myGov
            </div>
            <div className="px-4 py-2 rounded-lg bg-slate-900 border border-slate-700 text-xs font-mono font-bold text-cyan-300">
              UMANG
            </div>
          </div>
        </div>
      </div>

      {/* 2. Middle Multi-Column Grid Links (Exact replica of india.gov.in footer in image) */}
      <div className="max-w-[1700px] mx-auto px-6 py-10 text-xs font-sans">
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-8">
          
          {/* Column 1: Category */}
          <div className="space-y-3">
            <h4 className="text-sm font-extrabold text-white uppercase tracking-wider border-b border-slate-800 pb-2">
              Category
            </h4>
            <ul className="space-y-2 text-slate-400 font-medium">
              <li><a href="#" className="hover:text-amber-400 transition-colors">Space Telemetry & Satellite</a></li>
              <li><a href="#" className="hover:text-amber-400 transition-colors">Defence & Foreign Affairs</a></li>
              <li><a href="#" className="hover:text-amber-400 transition-colors">Science, IT & Communications</a></li>
              <li><a href="#" className="hover:text-amber-400 transition-colors">Governance & Planning</a></li>
              <li><a href="#" className="hover:text-amber-400 transition-colors">Infrastructure & Industries</a></li>
            </ul>
          </div>

          {/* Column 2: Directory */}
          <div className="space-y-3">
            <h4 className="text-sm font-extrabold text-white uppercase tracking-wider border-b border-slate-800 pb-2">
              Directory
            </h4>
            <ul className="space-y-2 text-slate-400 font-medium">
              <li><a href="#" className="hover:text-amber-400 transition-colors">Satellite Constellations</a></li>
              <li><a href="#" className="hover:text-amber-400 transition-colors">NORAD Transponders</a></li>
              <li><a href="#" className="hover:text-amber-400 transition-colors">Ground Tracking Stations</a></li>
              <li><a href="#" className="hover:text-amber-400 transition-colors">Web Directory</a></li>
              <li><a href="#" className="hover:text-amber-400 transition-colors">Public Helplines</a></li>
            </ul>
          </div>

          {/* Column 3: My-Government */}
          <div className="space-y-3">
            <h4 className="text-sm font-extrabold text-white uppercase tracking-wider border-b border-slate-800 pb-2">
              My-Government
            </h4>
            <ul className="space-y-2 text-slate-400 font-medium">
              <li><a href="#" className="hover:text-amber-400 transition-colors">Acts & Satellite Rules</a></li>
              <li><a href="#" className="hover:text-amber-400 transition-colors">National Space Schemes</a></li>
              <li><a href="#" className="hover:text-amber-400 transition-colors">Constitution of India</a></li>
              <li><a href="#" className="hover:text-amber-400 transition-colors">Documents & Data Policy</a></li>
            </ul>
          </div>

          {/* Column 4: About Us */}
          <div className="space-y-3">
            <h4 className="text-sm font-extrabold text-white uppercase tracking-wider border-b border-slate-800 pb-2">
              About Us
            </h4>
            <ul className="space-y-2 text-slate-400 font-medium">
              <li><a href="#" className="hover:text-amber-400 transition-colors">Contact Space Cell</a></li>
              <li><a href="#" className="hover:text-amber-400 transition-colors">Feedback & Inquiries</a></li>
              <li><a href="#" className="hover:text-amber-400 transition-colors">FAQs</a></li>
              <li><a href="#" className="hover:text-amber-400 hover:underline">Help & Guidance</a></li>
              <li><a href="#" className="hover:text-amber-400 transition-colors">Site Map</a></li>
            </ul>
          </div>

          {/* Column 5: Spotlights */}
          <div className="space-y-3">
            <h4 className="text-sm font-extrabold text-white uppercase tracking-wider border-b border-slate-800 pb-2">
              Spotlights
            </h4>
            <ul className="space-y-2 text-slate-400 font-medium">
              <li><a href="#" className="hover:text-amber-400 transition-colors">Visitor Summary</a></li>
              <li><a href="#" className="hover:text-amber-400 transition-colors">Disclaimer</a></li>
              <li><a href="#" className="hover:text-amber-400 transition-colors">Website Policy</a></li>
              <li><a href="#" className="hover:text-amber-400 transition-colors">App Privacy Policy</a></li>
              <li><a href="#" className="hover:text-amber-400 transition-colors">Content Sources</a></li>
            </ul>
          </div>

          {/* Column 6: Mobile QR Code & Social */}
          <div className="space-y-3">
            <h4 className="text-sm font-extrabold text-white uppercase tracking-wider border-b border-slate-800 pb-2">
              View on Mobile
            </h4>
            <div className="bg-white p-3 rounded-xl inline-block shadow-md">
              <QrCode className="w-20 h-20 text-slate-900" />
            </div>
            <div className="pt-2">
              <span className="text-[11px] font-bold text-slate-400 block mb-1">Follow Us:</span>
              <div className="flex space-x-2">
                <span className="w-7 h-7 rounded-full bg-slate-800 hover:bg-blue-600 text-white flex items-center justify-center font-bold cursor-pointer transition-colors">f</span>
                <span className="w-7 h-7 rounded-full bg-slate-800 hover:bg-slate-700 text-white flex items-center justify-center font-bold cursor-pointer transition-colors">X</span>
              </div>
            </div>
          </div>

        </div>
      </div>

      {/* 3. Bottom Disclaimer & Attribution Bar */}
      <div className="bg-[#02050c] border-t border-slate-800/80 px-6 py-6 text-xs text-slate-400 font-sans">
        <div className="max-w-[1700px] mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-4">
            <div className="text-amber-400">
              <AshokStambh className="w-6 h-8" />
            </div>
            <p className="text-[11px] leading-relaxed text-slate-400 max-w-4xl">
              Space Telemetry Portal is developed under the Digital India Programme to provide citizens and authorized analysts with secure access to satellite signal intelligence. Content Owned & Maintained by <strong className="text-slate-200">National Technical Research Organisation (NTRO)</strong>, Government of India.
            </p>
          </div>

          <button 
            onClick={scrollToTop}
            className="p-3 rounded-full bg-indigo-600 hover:bg-indigo-700 text-white shadow-lg transition-all flex-shrink-0"
            title="Back to Top"
          >
            <ArrowUp className="w-4 h-4" />
          </button>
        </div>
      </div>
    </footer>
  );
}
