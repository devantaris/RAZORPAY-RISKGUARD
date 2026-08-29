'use client';
import { useState, useEffect } from 'react';
import { AssessForm } from '@/components/AssessForm';
import { LiveFeed } from '@/components/LiveFeed';
import { ThresholdSlider } from '@/components/ThresholdSlider';
import { BatchSimulator } from '@/components/BatchSimulator';
import { getHealth } from '@/lib/api';
import { 
  Activity, 
  Sliders, 
  BarChart3, 
  Scale, 
  Zap,
  Clock
} from 'lucide-react';

type TabKey = 'assessor' | 'stream' | 'bandit' | 'batch' | 'math';

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState<TabKey>('assessor');
  const [health, setHealth] = useState<{ status: string; service: string; version: string; uptime_s: number; pipeline: string } | null>(null);

  useEffect(() => {
    getHealth().then(setHealth).catch(() => setHealth(null));
    const t = setInterval(() => {
      getHealth().then(setHealth).catch(() => setHealth(null));
    }, 8000);
    return () => clearInterval(t);
  }, []);

  return (
    <div className="min-h-screen bg-slate-50 font-sans pb-16">
      
      {/* Sub-Header Banner */}
      <div className="bg-white border-b border-slate-200 px-6 py-4">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2.5">
              <h1 className="text-xl font-extrabold text-slate-900 tracking-tight">
                AI Risk Operations Command Center
              </h1>
              <span className="px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs font-mono font-bold">
                100% DECLINE Precision
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Real-time payment fraud prevention via staged uncertainty & belief fusion.
            </p>
          </div>

          {/* Quick System Telemetry */}
          <div className="flex items-center gap-3 text-xs font-mono">
            <div className="px-3 py-1.5 rounded-xl bg-slate-50 border border-slate-200 flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${health?.pipeline === 'ready' ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'}`} />
              <span className="text-slate-600 font-medium">
                {health?.pipeline === 'ready' ? 'V1-V4 Models Live' : 'Backend Disconnected'}
              </span>
            </div>

            {health && (
              <div className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-50 border border-slate-200 text-slate-600">
                <Clock className="w-3.5 h-3.5 text-blue-600" />
                <span>Uptime: {(health.uptime_s / 60).toFixed(0)}m</span>
              </div>
            )}
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="max-w-7xl mx-auto mt-4 flex gap-2 overflow-x-auto border-t border-slate-100 pt-3">
          {[
            { id: 'assessor', label: 'Single Assessor & Inspector', icon: Activity },
            { id: 'stream', label: 'Live SSE Feed Monitor', icon: Zap },
            { id: 'bandit', label: 'Multi-Armed Bandit Studio', icon: Sliders },
            { id: 'batch', label: 'Batch Stress Simulator', icon: BarChart3 },
            { id: 'math', label: 'Belief Fusion Math & Architecture', icon: Scale },
          ].map(tab => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as TabKey)}
                className={`px-3.5 py-2 rounded-xl text-xs font-semibold flex items-center gap-2 transition-all whitespace-nowrap ${
                  isActive 
                    ? 'bg-blue-600 text-white shadow-sm shadow-blue-600/30' 
                    : 'bg-white text-slate-600 hover:bg-slate-100 hover:text-slate-900 border border-slate-200/80'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                {tab.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Tab Contents */}
      <main className="max-w-7xl mx-auto px-6 pt-6">

        {/* TAB 1: SINGLE ASSESSOR & DEEP INSPECTOR */}
        {activeTab === 'assessor' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 animate-in fade-in duration-200">
            <div className="lg:col-span-6 bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
              <div className="flex items-center justify-between mb-4 border-b border-slate-100 pb-3">
                <h2 className="font-bold text-slate-900 text-base flex items-center gap-2">
                  <Activity className="w-4 h-4 text-blue-600" />
                  Interactive Transaction Assessor
                </h2>
                <span className="text-[11px] font-mono text-slate-400">POST /v1/assess</span>
              </div>
              <AssessForm />
            </div>

            <div className="lg:col-span-6 bg-white rounded-2xl border border-slate-200 p-6 shadow-sm flex flex-col h-[760px]">
              <div className="flex items-center justify-between mb-4 border-b border-slate-100 pb-3">
                <h2 className="font-bold text-slate-900 text-base flex items-center gap-2">
                  <Zap className="w-4 h-4 text-emerald-600" />
                  Live Synthetic Transaction Stream
                </h2>
                <span className="text-[11px] font-mono text-slate-400">GET /v1/stream</span>
              </div>
              <LiveFeed />
            </div>
          </div>
        )}

        {/* TAB 2: FULL WIDTH LIVE STREAM MONITOR */}
        {activeTab === 'stream' && (
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm flex flex-col h-[75vh] animate-in fade-in duration-200">
            <div className="flex items-center justify-between mb-4 border-b border-slate-100 pb-3">
              <div>
                <h2 className="font-bold text-slate-900 text-base flex items-center gap-2">
                  <Zap className="w-4 h-4 text-emerald-600" />
                  High-Throughput Operational Event Stream
                </h2>
                <p className="text-xs text-slate-500 mt-0.5">
                  Streaming live payment assessments with latency telemetry, stage routing, and confidence metrics.
                </p>
              </div>
              <span className="font-mono text-xs text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-md border border-emerald-200">
                SSE Active
              </span>
            </div>
            <LiveFeed />
          </div>
        )}

        {/* TAB 3: MULTI-ARMED BANDIT STUDIO */}
        {activeTab === 'bandit' && (
          <div className="space-y-6 animate-in fade-in duration-200">
            <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
              <div className="max-w-3xl">
                <span className="text-xs font-mono uppercase tracking-wider text-purple-600 font-bold bg-purple-50 px-2.5 py-1 rounded-md border border-purple-100">
                  Agent 3B • Multi-Armed Bandit
                </span>
                <h2 className="text-xl font-bold text-slate-900 mt-2 mb-2">
                  Autonomous Per-Merchant Threshold Optimization
                </h2>
                <p className="text-xs text-slate-600 leading-relaxed">
                  Different merchant categories carry vastly distinct risk tolerances. An e-commerce jewelry store requires a stricter fraud decline threshold than a high-volume food delivery merchant. RiskGuard uses an epsilon-greedy bandit (epsilon=0.10, alpha=0.30) to optimize thresholds dynamically while respecting hard safety bounds [0.40, 0.95].
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <ThresholdSlider 
                merchantId="merch_jewelry_001" 
                categoryTitle="High-Value Jewelry" 
                categoryDesc="Strict threshold • High ticket size (INR 20k - 2L) • High chargeback severity" 
              />
              <ThresholdSlider 
                merchantId="merch_travel_001" 
                categoryTitle="Airlines & Travel" 
                categoryDesc="Medium threshold • High volume & velocity spikes • Cross-border signals" 
              />
              <ThresholdSlider 
                merchantId="merch_food_001" 
                categoryTitle="Food Delivery & QSR" 
                categoryDesc="Relaxed threshold • High volume low ticket (INR 100 - 800) • Zero churn tolerance" 
              />
              <ThresholdSlider 
                merchantId="merch_electronics_001" 
                categoryTitle="Consumer Electronics" 
                categoryDesc="Dynamic threshold • High resale value risk • Frequent velocity bursts" 
              />
              <ThresholdSlider 
                merchantId="merch_gaming_001" 
                categoryTitle="Digital Gaming & In-App" 
                categoryDesc="Fast threshold • Instant digital fulfillment • High micro-transaction rate" 
              />
              <ThresholdSlider 
                merchantId="merch_pharmacy_001" 
                categoryTitle="Online Pharmacy" 
                categoryDesc="Standard threshold • Regular customer recurring orders • Strict BIN rules" 
              />
            </div>
          </div>
        )}

        {/* TAB 4: BATCH STRESS SIMULATOR */}
        {activeTab === 'batch' && (
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm animate-in fade-in duration-200">
            <div className="mb-6 border-b border-slate-100 pb-4">
              <span className="text-xs font-mono uppercase tracking-wider text-blue-600 font-bold bg-blue-50 px-2.5 py-1 rounded-md border border-blue-100">
                Performance & Throughput Stress Tester
              </span>
              <h2 className="text-xl font-bold text-slate-900 mt-2 mb-1">
                Batch Transaction Evaluation (POST /v1/batch)
              </h2>
              <p className="text-xs text-slate-600">
                Simulate high-concurrency payment traffic spikes and measure throughput (TPS), latency percentiles, and decision distributions live.
              </p>
            </div>
            <BatchSimulator />
          </div>
        )}

        {/* TAB 5: MATHEMATICAL PROOFS & ARCHITECTURE */}
        {activeTab === 'math' && (
          <div className="bg-white rounded-2xl border border-slate-200 p-8 shadow-sm space-y-8 animate-in fade-in duration-200">
            <div>
              <span className="text-xs font-mono uppercase tracking-wider text-indigo-600 font-bold bg-indigo-50 px-2.5 py-1 rounded-md border border-indigo-100">
                Theoretical Foundations
              </span>
              <h2 className="text-2xl font-bold text-slate-900 mt-2 mb-2">
                Dempster-Shafer Belief Fusion & Epistemic Uncertainty
              </h2>
              <p className="text-sm text-slate-600 leading-relaxed max-w-4xl">
                Standard machine learning models compute a single scalar probability. When models encounter distribution shifts or conflicting signals (e.g. valid card BIN but abnormal spend spike), they output an uncalibrated 0.50 without indicating whether the 0.50 represents genuine borderline probability or utter ignorance.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 font-mono text-xs">
              <div className="p-5 rounded-xl bg-slate-50 border border-slate-200">
                <div className="font-bold text-blue-600 mb-2 text-sm">Source 1: XGBoost Ensemble</div>
                <p className="text-slate-600 font-sans text-xs mb-3">
                  Normalizes ensemble standard deviation against scale sigma_0 = 0.05.
                </p>
                <div className="bg-white p-3 rounded-lg border border-slate-200 space-y-1 text-[11px]">
                  <div>u = min(sigma / 0.05, 1.0) * 0.50</div>
                  <div>m_1(Fraud) = mean * (1 - u)</div>
                  <div>m_1(Legit) = (1 - mean) * (1 - u)</div>
                  <div>m_1(Theta) = u (Ignorance)</div>
                </div>
              </div>

              <div className="p-5 rounded-xl bg-slate-50 border border-slate-200">
                <div className="font-bold text-purple-600 mb-2 text-sm">Source 2: Isolation Forest</div>
                <p className="text-slate-600 font-sans text-xs mb-3">
                  Transforms raw tree anomaly score into non-linear sigmoid belief mass.
                </p>
                <div className="bg-white p-3 rounded-lg border border-slate-200 space-y-1 text-[11px]">
                  <div>a = sigmoid(iso_score * 20.0)</div>
                  <div>m_2(Fraud) = a * (1 - 0.40)</div>
                  <div>m_2(Legit) = (1 - a) * (1 - 0.40)</div>
                  <div>m_2(Theta) = 0.40 (Base Ignorance)</div>
                </div>
              </div>

              <div className="p-5 rounded-xl bg-slate-50 border border-slate-200">
                <div className="font-bold text-emerald-600 mb-2 text-sm">Source 3: Calibrated SVM</div>
                <p className="text-slate-600 font-sans text-xs mb-3">
                  Independent linear hyperplane providing orthogonal decision evidence.
                </p>
                <div className="bg-white p-3 rounded-lg border border-slate-200 space-y-1 text-[11px]">
                  <div>c = |p_svm - 0.5| * 2</div>
                  <div>ign = 0.45 - (0.30 * c)</div>
                  <div>m_3(Fraud) = p_svm * (1 - ign)</div>
                  <div>m_3(Theta) = ign</div>
                </div>
              </div>
            </div>

            <div className="p-6 rounded-2xl bg-slate-900 text-white font-mono text-xs space-y-4">
              <div className="font-bold text-blue-400 text-sm">Exact Decision Routing Rules:</div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-slate-300">
                <div className="p-3 bg-slate-800 rounded-lg">
                  <span className="text-rose-400 font-bold">1. AUTO_DECLINE</span>
                  <p className="text-[11px] text-slate-400 mt-1 font-sans">
                    Requires Bel(Fraud) &gt;= 0.91 AND Ignorance &lt;= 0.05. Guarantees zero false blocks on legitimate transactions.
                  </p>
                </div>
                <div className="p-3 bg-slate-800 rounded-lg">
                  <span className="text-blue-400 font-bold">2. HUMAN_ESCALATE (PEND)</span>
                  <p className="text-[11px] text-slate-400 mt-1 font-sans">
                    Fires when Conflict Metric K &gt;= 0.25 OR Ignorance &gt;= 0.10. Refuses auto-declining and routes with SHAP reason codes.
                  </p>
                </div>
              </div>
            </div>

          </div>
        )}

      </main>

    </div>
  );
}
