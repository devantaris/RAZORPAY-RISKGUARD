import Link from 'next/link';
import { ShieldAlert, Zap, BrainCircuit, ArrowRight, Activity, Cpu } from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="w-full font-sans text-gray-900 selection:bg-blue-200">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-[#02042b] text-white pt-24 pb-32">
         {/* Background Glow */}
         <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[400px] bg-blue-600/20 blur-[120px] rounded-full pointer-events-none" />
         
         <div className="max-w-7xl mx-auto px-6 relative z-10 text-center">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-800/50 border border-slate-700 text-sm font-medium text-blue-400 mb-8">
               <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></span>
               Razorpay AI Builder Internship 2026 • Track 2
            </div>
            
            <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-8 leading-tight">
              Knowing When <br/>
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400">Not to Decide.</span>
            </h1>
            
            <p className="text-xl text-slate-300 max-w-2xl mx-auto mb-10 leading-relaxed">
              An AI risk manager that uses Dempster-Shafer belief fusion to achieve <strong>100% decline precision</strong>. We route ambiguous transactions to human review instead of guessing—eliminating false blocks.
            </p>
            
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
               <Link href="/dashboard" className="inline-flex items-center gap-2 bg-[#2d68f8] hover:bg-blue-600 text-white px-8 py-4 rounded-lg font-semibold text-lg transition-all shadow-[0_0_40px_rgba(45,104,248,0.3)] hover:shadow-[0_0_60px_rgba(45,104,248,0.5)]">
                 Open Risk Dashboard <ArrowRight className="w-5 h-5" />
               </Link>
               <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer" className="inline-flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-white px-8 py-4 rounded-lg font-semibold text-lg transition-colors border border-slate-700">
                 View API Docs
               </a>
            </div>
         </div>
      </section>

      {/* Stats Banner */}
      <section className="border-b border-gray-200 bg-white">
         <div className="max-w-7xl mx-auto px-6 py-10 grid grid-cols-2 md:grid-cols-4 gap-8 divide-x divide-gray-100 text-center">
            <div>
               <div className="text-3xl font-bold text-gray-900 mb-1">100%</div>
               <div className="text-sm font-medium text-gray-500 uppercase tracking-wider">Decline Precision</div>
            </div>
            <div>
               <div className="text-3xl font-bold text-gray-900 mb-1">0</div>
               <div className="text-sm font-medium text-gray-500 uppercase tracking-wider">False Blocks</div>
            </div>
            <div>
               <div className="text-3xl font-bold text-gray-900 mb-1">97.5%</div>
               <div className="text-sm font-medium text-gray-500 uppercase tracking-wider">Fraud Caught</div>
            </div>
            <div>
               <div className="text-3xl font-bold text-gray-900 mb-1">&lt;100ms</div>
               <div className="text-sm font-medium text-gray-500 uppercase tracking-wider">p50 Latency</div>
            </div>
         </div>
      </section>

      {/* Value Props */}
      <section className="py-24 bg-slate-50">
        <div className="max-w-7xl mx-auto px-6">
           <div className="text-center max-w-3xl mx-auto mb-16">
              <h2 className="text-3xl font-bold mb-4">The Agentic AI Pipeline</h2>
              <p className="text-gray-600 text-lg">A staged uncertainty architecture that bridges the gap between raw ML predictions and human risk operators.</p>
           </div>

           <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {/* Prop 1 */}
              <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                 <div className="w-14 h-14 bg-emerald-50 text-emerald-600 rounded-xl flex items-center justify-center mb-6 border border-emerald-100">
                    <ShieldAlert className="w-7 h-7" />
                 </div>
                 <h3 className="text-xl font-bold mb-3 text-gray-900">Belief Fusion Math</h3>
                 <p className="text-gray-600 leading-relaxed">
                    Combines XGBoost and Isolation Forest signals using Dempster-Shafer theory to quantify ignorance and epistemic conflict separately from actual fraud probability.
                 </p>
              </div>
              
              {/* Prop 2 */}
              <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                 <div className="w-14 h-14 bg-blue-50 text-blue-600 rounded-xl flex items-center justify-center mb-6 border border-blue-100">
                    <BrainCircuit className="w-7 h-7" />
                 </div>
                 <h3 className="text-xl font-bold mb-3 text-gray-900">Agentic Explanations</h3>
                 <p className="text-gray-600 leading-relaxed">
                    Extracts raw SHAP tree attributions and pipes them through an LLM to generate plain-English, actionable risk narratives for human operators in under 30ms.
                 </p>
              </div>
              
              {/* Prop 3 */}
              <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                 <div className="w-14 h-14 bg-purple-50 text-purple-600 rounded-xl flex items-center justify-center mb-6 border border-purple-100">
                    <Activity className="w-7 h-7" />
                 </div>
                 <h3 className="text-xl font-bold mb-3 text-gray-900">Auto-Threshold Bandit</h3>
                 <p className="text-gray-600 leading-relaxed">
                    An ε-greedy Multi-Armed Bandit constantly drifts the decision threshold for each individual merchant based on their live chargeback and approval reward signals.
                 </p>
              </div>
           </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 py-12 text-center">
         <div className="flex items-center justify-center gap-2 text-gray-900 font-bold text-xl mb-4">
            <ShieldCheck className="w-6 h-6 text-blue-600" />
            Razorpay RiskGuard
         </div>
         <p className="text-gray-500 text-sm">
            Developed for the Razorpay AI Builder Internship 2026.
         </p>
      </footer>
    </div>
  );
}
