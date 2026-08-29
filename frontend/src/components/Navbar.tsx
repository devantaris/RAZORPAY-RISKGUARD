import Link from 'next/link';
import { ShieldCheck } from 'lucide-react';

export function Navbar() {
  return (
    <nav className="bg-[#02042b] border-b border-slate-800 px-6 py-4 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <Link href="/" className="flex items-center gap-3 group">
          <div className="w-8 h-8 bg-[#2d68f8] rounded-lg flex items-center justify-center transition-transform group-hover:scale-105">
            <ShieldCheck className="w-5 h-5 text-white" />
          </div>
          <span className="font-bold text-white text-lg tracking-tight">Razorpay RiskGuard</span>
        </Link>
        <div className="flex gap-8 items-center">
          <Link href="/dashboard" className="text-sm font-medium text-slate-300 hover:text-white transition-colors">Risk Dashboard</Link>
          <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer" className="text-sm font-medium text-slate-300 hover:text-white transition-colors">API Reference</a>
          <Link href="https://github.com/devantaris/RAZORPAY-RISKGUARD" target="_blank" className="text-sm font-medium text-slate-300 hover:text-white transition-colors">GitHub Repo</Link>
        </div>
      </div>
    </nav>
  );
}
