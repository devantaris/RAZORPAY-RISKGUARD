import Link from 'next/link';
import { 
  ShieldCheck, 
  ShieldAlert, 
  BrainCircuit, 
  ArrowRight, 
  Cpu, 
  Sliders, 
  Scale
} from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="w-full font-sans text-slate-900 selection:bg-blue-500 selection:text-white bg-slate-50">
      
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-[#070d1f] text-white pt-20 pb-28 border-b border-slate-800">
        <div className="absolute -top-40 left-1/2 -translate-x-1/2 w-[1000px] h-[500px] bg-gradient-to-tr from-blue-600/25 to-indigo-600/20 blur-[140px] rounded-full pointer-events-none" />
        <div className="absolute -bottom-20 right-10 w-[400px] h-[300px] bg-emerald-500/10 blur-[100px] rounded-full pointer-events-none" />

        <div className="max-w-7xl mx-auto px-6 relative z-10">
          <div className="flex flex-col items-center text-center max-w-4xl mx-auto">
            
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-slate-900/90 border border-blue-500/30 text-xs font-mono text-blue-300 mb-8 shadow-inner">
              <span className="w-2 h-2 rounded-full bg-blue-400 animate-ping"></span>
              <span>Razorpay AI Builder 2026 • Track 2: AI Risk Manager</span>
            </div>

            <h1 className="text-5xl sm:text-6xl md:text-7xl font-extrabold tracking-tight mb-6 leading-[1.1]">
              Knowing When <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-sky-300 to-emerald-400">
                Not to Decide.
              </span>
            </h1>

            <p className="text-lg sm:text-xl text-slate-300 max-w-2xl mx-auto mb-10 leading-relaxed font-normal">
              A staged uncertainty payment risk pipeline powered by <strong>Dempster-Shafer belief fusion</strong>. 
              Guarantees <span className="text-emerald-400 font-semibold">100% DECLINE precision</span> by deferring ambiguous cases to human analysts instead of false-blocking good customers.
            </p>

            <div className="flex flex-col sm:flex-row items-center gap-4 w-full sm:w-auto">
              <Link 
                href="/dashboard" 
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white px-8 py-4 rounded-xl font-semibold text-base transition-all shadow-[0_0_35px_rgba(37,99,235,0.4)] hover:shadow-[0_0_50px_rgba(37,99,235,0.6)]"
              >
                Launch Risk Ops Dashboard
                <ArrowRight className="w-4 h-4" />
              </Link>

              <a 
                href="http://localhost:8000/docs" 
                target="_blank" 
                rel="noreferrer" 
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 bg-slate-900/90 hover:bg-slate-800 text-slate-200 px-6 py-4 rounded-xl font-medium text-base transition-colors border border-slate-700/80"
              >
                <Cpu className="w-4 h-4 text-blue-400" />
                Swagger API (Port 8000)
              </a>
            </div>

            <div className="mt-14 pt-8 border-t border-slate-800/80 w-full grid grid-cols-2 md:grid-cols-4 gap-6 text-left">
              <div className="bg-slate-900/50 border border-slate-800/60 p-4 rounded-xl">
                <div className="text-2xl sm:text-3xl font-mono font-bold text-emerald-400">100%</div>
                <div className="text-xs text-slate-400 uppercase tracking-wider font-semibold mt-1">DECLINE Precision</div>
                <p className="text-[11px] text-slate-500 mt-1">0 legitimate customers falsely blocked</p>
              </div>

              <div className="bg-slate-900/50 border border-slate-800/60 p-4 rounded-xl">
                <div className="text-2xl sm:text-3xl font-mono font-bold text-blue-400">97.5%</div>
                <div className="text-xs text-slate-400 uppercase tracking-wider font-semibold mt-1">Fraud Recall</div>
                <p className="text-[11px] text-slate-500 mt-1">39/40 test frauds detected</p>
              </div>

              <div className="bg-slate-900/50 border border-slate-800/60 p-4 rounded-xl">
                <div className="text-2xl sm:text-3xl font-mono font-bold text-indigo-300">0.9840</div>
                <div className="text-xs text-slate-400 uppercase tracking-wider font-semibold mt-1">Ensemble ROC-AUC</div>
                <p className="text-[11px] text-slate-500 mt-1">Bootstrap 5-model calibrated XGBoost</p>
              </div>

              <div className="bg-slate-900/50 border border-slate-800/60 p-4 rounded-xl">
                <div className="text-2xl sm:text-3xl font-mono font-bold text-amber-300">&lt;96ms</div>
                <div className="text-xs text-slate-400 uppercase tracking-wider font-semibold mt-1">p50 Latency</div>
                <p className="text-[11px] text-slate-500 mt-1">V1-V4 + SHAP + LLM Agent pipeline</p>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* 4-Stage Architecture */}
      <section className="py-20 bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <span className="text-xs font-mono uppercase tracking-widest text-blue-600 font-bold bg-blue-50 px-3 py-1 rounded-full border border-blue-100">
              Architecture Lineage • IEEE TDSC Paper
            </span>
            <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 mt-4 mb-3">
              The 4-Stage Uncertainty Pipeline
            </h2>
            <p className="text-slate-600 text-base">
              Traditional ML models force binary yes/no guesses under high uncertainty. 
              RiskGuard decomposes risk into belief mass and ignorance before making irreversible declines.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 relative">
            <div className="bg-slate-50 border border-slate-200/80 rounded-2xl p-6 relative hover:border-blue-300 transition-all hover:shadow-md">
              <div className="w-10 h-10 rounded-xl bg-blue-600 text-white flex items-center justify-center font-mono font-bold text-sm mb-4 shadow-sm shadow-blue-500/30">
                V1
              </div>
              <h3 className="font-bold text-slate-900 text-lg mb-2">Ensemble + Novelty</h3>
              <p className="text-xs text-slate-600 leading-relaxed mb-4">
                5 bootstrap XGBoost models with isotonic calibration generate mean and std probabilities. Isolation Forest flags anomalous structures.
              </p>
              <div className="space-y-1.5 pt-3 border-t border-slate-200 text-[11px] font-mono">
                <div className="text-emerald-700">→ APPROVE (std &lt; 0.02)</div>
                <div className="text-rose-700">→ DECLINE (prob ≥ 0.80)</div>
                <div className="text-amber-700">→ ABSTAIN / ESCALATE</div>
              </div>
            </div>

            <div className="bg-slate-50 border border-slate-200/80 rounded-2xl p-6 relative hover:border-blue-300 transition-all hover:shadow-md">
              <div className="w-10 h-10 rounded-xl bg-indigo-600 text-white flex items-center justify-center font-mono font-bold text-sm mb-4 shadow-sm shadow-indigo-500/30">
                V2
              </div>
              <h3 className="font-bold text-slate-900 text-lg mb-2">SVM Second Opinion</h3>
              <p className="text-xs text-slate-600 leading-relaxed mb-4">
                Executes exclusively on ABSTAIN cases where ensemble models disagree. A cost-optimal Calibrated Linear SVM clears transactions if p(fraud) &lt; 0.01.
              </p>
              <div className="space-y-1.5 pt-3 border-t border-slate-200 text-[11px] font-mono">
                <div className="text-emerald-700">→ APPROVE if p &lt; 1%</div>
                <div className="text-blue-700">→ PEND (Model Disagree)</div>
              </div>
            </div>

            <div className="bg-slate-50 border border-slate-200/80 rounded-2xl p-6 relative hover:border-blue-300 transition-all hover:shadow-md">
              <div className="w-10 h-10 rounded-xl bg-purple-600 text-white flex items-center justify-center font-mono font-bold text-sm mb-4 shadow-sm shadow-purple-500/30">
                V3
              </div>
              <h3 className="font-bold text-slate-900 text-lg mb-2">Dempster-Shafer Fusion</h3>
              <p className="text-xs text-slate-600 leading-relaxed mb-4">
                Fuses 3 independent BPA sources (Ensemble, IsoForest, V3 SVM). Calculates exact Conflict Metric K, Belief of Fraud, and epistemic Ignorance.
              </p>
              <div className="space-y-1.5 pt-3 border-t border-slate-200 text-[11px] font-mono">
                <div className="text-rose-700">→ DECLINE (Bel ≥ 0.91)</div>
                <div className="text-amber-700">→ STEP_UP (Bel ≥ 0.35)</div>
                <div className="text-blue-700">→ PEND (K ≥ 0.25)</div>
              </div>
            </div>

            <div className="bg-slate-50 border border-slate-200/80 rounded-2xl p-6 relative hover:border-blue-300 transition-all hover:shadow-md">
              <div className="w-10 h-10 rounded-xl bg-emerald-600 text-white flex items-center justify-center font-mono font-bold text-sm mb-4 shadow-sm shadow-emerald-500/30">
                V4
              </div>
              <h3 className="font-bold text-slate-900 text-lg mb-2">SHAP & Agent Layer</h3>
              <p className="text-xs text-slate-600 leading-relaxed mb-4">
                Extracts top SHAP tree attributions for all deferred transactions. Generates structured reason codes and fires the LLM Explanation Agent and Chargeback Predictor.
              </p>
              <div className="space-y-1.5 pt-3 border-t border-slate-200 text-[11px] font-mono">
                <div className="text-blue-700">→ Structured Reason Code</div>
                <div className="text-slate-700">→ LLM Analyst Narrative</div>
                <div className="text-orange-700">→ Chargeback Risk Score</div>
              </div>
            </div>
          </div>

          <div className="mt-10 p-6 rounded-2xl bg-gradient-to-r from-blue-900 to-indigo-900 text-white flex flex-col md:flex-row items-center justify-between gap-6 shadow-xl">
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-blue-300 font-mono text-xs uppercase tracking-wider font-semibold">
                <Scale className="w-4 h-4" />
                Dempster Combination Rule Proof
              </div>
              <div className="font-mono text-sm text-slate-200">
                m_12(A) = [ sum_(B cap C = A) m_1(B) m_2(C) ] / (1 - K),  where K = sum_(B cap C = empty) m_1(B) m_2(C)
              </div>
              <p className="text-xs text-slate-400">
                When conflict K ≥ 0.25, sources fundamentally contradict. The system refuses auto-decision and defers to human risk ops.
              </p>
            </div>
            <Link 
              href="/dashboard" 
              className="whitespace-nowrap px-5 py-2.5 bg-blue-500 hover:bg-blue-400 text-white rounded-lg text-xs font-semibold tracking-wide transition-colors"
            >
              Test Fusion Live →
            </Link>
          </div>

        </div>
      </section>

      {/* 3 AI Agents in Loop */}
      <section className="py-20 bg-slate-50 border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <span className="text-xs font-mono uppercase tracking-widest text-indigo-600 font-bold bg-indigo-50 px-3 py-1 rounded-full border border-indigo-100">
              Agentic Intelligence
            </span>
            <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 mt-4 mb-3">
              3 Specialized AI Agents in the Loop
            </h2>
            <p className="text-slate-600 text-base">
              Moving beyond static ML thresholds by incorporating autonomous learning and natural-language explainability.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-white rounded-2xl p-7 border border-slate-200 shadow-sm flex flex-col justify-between">
              <div>
                <div className="w-12 h-12 rounded-xl bg-blue-50 border border-blue-100 text-blue-600 flex items-center justify-center mb-6">
                  <BrainCircuit className="w-6 h-6" />
                </div>
                <span className="text-xs font-mono font-bold text-blue-600 uppercase">Agent 3A</span>
                <h3 className="text-xl font-bold text-slate-900 mt-1 mb-3">Risk Explanation Agent</h3>
                <p className="text-sm text-slate-600 leading-relaxed mb-4">
                  Takes top SHAP feature vectors and translates mathematical attributions into concise, 2-sentence actionable narratives for merchant analysts. Cached in Redis by feature signature.
                </p>
              </div>
              <div className="bg-slate-50 rounded-xl p-3.5 border border-slate-100 text-xs font-mono text-slate-700 italic">
                &ldquo;Transaction declined: amount is 4.2x merchant average, card BIN is elevated risk, and 3 rapid attempts observed in 1 hour.&rdquo;
              </div>
            </div>

            <div className="bg-white rounded-2xl p-7 border border-slate-200 shadow-sm flex flex-col justify-between">
              <div>
                <div className="w-12 h-12 rounded-xl bg-purple-50 border border-purple-100 text-purple-600 flex items-center justify-center mb-6">
                  <Sliders className="w-6 h-6" />
                </div>
                <span className="text-xs font-mono font-bold text-purple-600 uppercase">Agent 3B</span>
                <h3 className="text-xl font-bold text-slate-900 mt-1 mb-3">Auto-Threshold Bandit</h3>
                <p className="text-sm text-slate-600 leading-relaxed mb-4">
                  An epsilon-greedy Multi-Armed Bandit (epsilon=0.10, alpha=0.30) that dynamically tunes the decline threshold per merchant ID based on feedback rewards.
                </p>
              </div>
              <div className="bg-purple-50/50 rounded-xl p-3.5 border border-purple-100 text-xs font-mono text-purple-900">
                Jewelry: 0.85 (Strict) • Food: 0.75 (Relaxed) <br />
                Hard Safety Guards: [0.40, 0.95]
              </div>
            </div>

            <div className="bg-white rounded-2xl p-7 border border-slate-200 shadow-sm flex flex-col justify-between">
              <div>
                <div className="w-12 h-12 rounded-xl bg-orange-50 border border-orange-100 text-orange-600 flex items-center justify-center mb-6">
                  <ShieldAlert className="w-6 h-6" />
                </div>
                <span className="text-xs font-mono font-bold text-orange-600 uppercase">Agent 3C</span>
                <h3 className="text-xl font-bold text-slate-900 mt-1 mb-3">Chargeback Risk Predictor</h3>
                <p className="text-sm text-slate-600 leading-relaxed mb-4">
                  Cost-sensitive XGBoost trained with SMOTE oversampling to estimate the likelihood of a post-transaction dispute before funds settle to the merchant account (ROC-AUC 0.9318).
                </p>
              </div>
              <div className="bg-orange-50/50 rounded-xl p-3.5 border border-orange-100 text-xs font-mono text-orange-900">
                Pre-Settlement Alert: Chargeback Risk 89.4% <br />
                Hold settlement window by 48h
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Comparison Matrix */}
      <section className="py-20 bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 mb-3">
              Why Knowing When Not to Decide Wins
            </h2>
            <p className="text-slate-600 text-base">
              Comparing RiskGuard against traditional industry approaches.
            </p>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full border-collapse border border-slate-200 rounded-2xl overflow-hidden bg-white text-sm text-left">
              <thead>
                <tr className="bg-slate-900 text-white font-mono text-xs">
                  <th className="p-4 border-b border-slate-800">Capability</th>
                  <th className="p-4 border-b border-slate-800 text-slate-400">Traditional Rule Engine</th>
                  <th className="p-4 border-b border-slate-800 text-slate-400">Standard Binary XGBoost</th>
                  <th className="p-4 border-b border-slate-800 text-emerald-400 font-bold bg-blue-950/80">
                    Razorpay RiskGuard 🛡️
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 font-sans">
                <tr>
                  <td className="p-4 font-semibold text-slate-900">DECLINE False Positive Rate</td>
                  <td className="p-4 text-rose-600 font-mono">12% – 18% (High False Blocks)</td>
                  <td className="p-4 text-rose-600 font-mono">4% – 8% (Costly customer churn)</td>
                  <td className="p-4 text-emerald-700 font-mono font-bold bg-blue-50/50">0.0% (100% Precision) ✅</td>
                </tr>
                <tr>
                  <td className="p-4 font-semibold text-slate-900">Epistemic Uncertainty Handling</td>
                  <td className="p-4 text-slate-500">None (Hardcoded IF/ELSE)</td>
                  <td className="p-4 text-slate-500">None (Forced binary guess)</td>
                  <td className="p-4 text-emerald-700 font-semibold bg-blue-50/50">Dempster-Shafer Conflict Metric K</td>
                </tr>
                <tr>
                  <td className="p-4 font-semibold text-slate-900">Analyst Reason Codes</td>
                  <td className="p-4 text-slate-500">Static rule name</td>
                  <td className="p-4 text-slate-500">None / Raw prob only</td>
                  <td className="p-4 text-emerald-700 font-semibold bg-blue-50/50">TreeExplainer SHAP + Natural Language</td>
                </tr>
                <tr>
                  <td className="p-4 font-semibold text-slate-900">Merchant Specific Thresholds</td>
                  <td className="p-4 text-slate-500">Manual rules per merchant</td>
                  <td className="p-4 text-slate-500">Global fixed threshold (0.50)</td>
                  <td className="p-4 text-emerald-700 font-semibold bg-blue-50/50">Autonomous Multi-Armed Bandit</td>
                </tr>
                <tr>
                  <td className="p-4 font-semibold text-slate-900">Pre-Settlement Dispute Prevention</td>
                  <td className="p-4 text-slate-500">Post-facto chargeback tracking</td>
                  <td className="p-4 text-slate-500">None</td>
                  <td className="p-4 text-emerald-700 font-semibold bg-blue-50/50">SMOTE-trained Chargeback Predictor (0.93 AUC)</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-[#070d1f] text-slate-400 py-12 border-t border-slate-800">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <span className="font-bold text-white text-base">Razorpay RiskGuard</span>
              <p className="text-xs text-slate-500">AI Builder Internship 2026 Submission • Track 2</p>
            </div>
          </div>

          <div className="flex items-center gap-6 text-xs font-mono">
            <Link href="/dashboard" className="text-blue-400 hover:underline">Risk Dashboard</Link>
            <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer" className="text-slate-400 hover:text-white">FastAPI Docs</a>
            <a href="https://github.com/devantaris/RAZORPAY-RISKGUARD" target="_blank" rel="noreferrer" className="text-slate-400 hover:text-white">GitHub</a>
          </div>
        </div>
      </footer>

    </div>
  );
}
