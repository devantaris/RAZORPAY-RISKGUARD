'use client';
import Link from 'next/link';
import { useState, useEffect } from 'react';
import { ShieldCheck, Activity, Terminal, Code2, ExternalLink } from 'lucide-react';
import { getHealth } from '@/lib/api';

export function Navbar() {
  const [online, setOnline] = useState<boolean | null>(null);

  useEffect(() => {
    getHealth()
      .then(h => setOnline(h.status === 'ok' && h.pipeline === 'ready'))
      .catch(() => setOnline(false));
    const timer = setInterval(() => {
      getHealth()
        .then(h => setOnline(h.status === 'ok' && h.pipeline === 'ready'))
        .catch(() => setOnline(false));
    }, 10000);
    return () => clearInterval(timer);
  }, []);

  return (
    <nav className="bg-[#0b1329]/95 backdrop-blur-md border-b border-slate-800/80 px-6 py-3.5 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <Link href="/" className="flex items-center gap-3 group">
          <div className="w-9 h-9 bg-gradient-to-tr from-blue-600 to-indigo-500 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/20 group-hover:scale-105 transition-transform">
            <ShieldCheck className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-white text-base tracking-tight">Razorpay RiskGuard</span>
              <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-400 border border-blue-500/30">
                Track 2
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-mono">Dempster-Shafer Staged Uncertainty</p>
          </div>
        </Link>

        <div className="flex items-center gap-6">
          <div className="hidden sm:flex items-center gap-2 px-3 py-1 rounded-full bg-slate-900/80 border border-slate-800 text-xs font-mono">
            <span className={`w-2 h-2 rounded-full ${online === true ? 'bg-emerald-400 animate-pulse' : online === false ? 'bg-rose-500' : 'bg-amber-400 animate-pulse'}`} />
            <span className="text-slate-300">
              {online === true ? 'Pipeline Online (V1-V4)' : online === false ? 'Backend Offline' : 'Connecting...'}
            </span>
          </div>

          <div className="flex items-center gap-4 text-sm">
            <Link 
              href="/dashboard" 
              className="px-3.5 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-medium transition-all shadow-md shadow-blue-600/30 flex items-center gap-1.5"
            >
              <Activity className="w-4 h-4" />
              Risk Dashboard
            </Link>
            <a 
              href="http://localhost:8000/docs" 
              target="_blank" 
              rel="noreferrer" 
              className="hidden md:flex items-center gap-1 text-slate-300 hover:text-white transition-colors text-xs font-medium"
            >
              <Terminal className="w-3.5 h-3.5" />
              API Docs
              <ExternalLink className="w-3 h-3 text-slate-500" />
            </a>
            <a 
              href="https://github.com/devantaris/RAZORPAY-RISKGUARD" 
              target="_blank" 
              rel="noreferrer" 
              className="flex items-center gap-1.5 text-slate-300 hover:text-white transition-colors text-xs font-medium bg-slate-800/80 hover:bg-slate-800 px-3 py-1.5 rounded-lg border border-slate-700"
            >
              <Code2 className="w-3.5 h-3.5 text-blue-400" />
              GitHub
            </a>
          </div>
        </div>
      </div>
    </nav>
  );
}
