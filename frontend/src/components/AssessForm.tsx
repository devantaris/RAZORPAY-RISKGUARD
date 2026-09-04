'use client';
import { useState } from 'react';
import { AssessRequest, AssessResponse, assessTransaction } from '@/lib/api';
import { DecisionBadge } from './DecisionBadge';
import { ShapWaterfall } from './ShapWaterfall';
import { 
  Send, 
  Sparkles, 
  AlertCircle, 
  Clock, 
  RotateCcw, 
  Layers
} from 'lucide-react';

const PRESETS: Record<string, { label: string; desc: string; data: Partial<AssessRequest> }> = {
  'High-Risk': {
    label: '₹98k Jewelry (High Risk)',
    desc: 'High-value jewelry + high-risk BIN 438935 + odd hour',
    data: {
      transaction_id: 'txn_jewelry_fraud_001',
      merchant_id: 'merch_jewelry_001',
      amount: 98000,
      currency: 'INR',
      card_bin: '438935',
      payment_method: 'CARD',
      device_id: 'dev_unknown_mac_99',
      customer_id: 'cust_fraud_sim_01',
    },
  },
  'Low-Risk': {
    label: '₹349 Food (UPI Legit)',
    desc: 'Food delivery via UPI, familiar device & merchant avg',
    data: {
      transaction_id: 'txn_food_upi_002',
      merchant_id: 'merch_food_001',
      amount: 349,
      currency: 'INR',
      payment_method: 'UPI',
      device_id: 'dev_known_iphone_14',
      customer_id: 'cust_swiggy_regular',
    },
  },
  'Uncertain-Travel': {
    label: '₹45k Travel (PEND Review)',
    desc: 'Flight ticket with model disagreement & high uncertainty',
    data: {
      transaction_id: 'txn_travel_pend_003',
      merchant_id: 'merch_travel_001',
      amount: 45000,
      currency: 'INR',
      card_bin: '521234',
      payment_method: 'CARD',
      device_id: 'dev_tablet_new_02',
      customer_id: 'cust_travel_guest',
    },
  },
  'Step-Up-Auth': {
    label: '₹32k Electronics (Step-Up)',
    desc: 'Medium-high risk electronics purchase triggering OTP / 3DS challenge',
    data: {
      transaction_id: 'txn_elec_stepup_004',
      merchant_id: 'merch_electronics_001',
      amount: 32000,
      currency: 'INR',
      card_bin: '438935',
      payment_method: 'CARD',
      device_id: 'dev_laptop_unseen',
      customer_id: 'cust_croma_buyer',
    },
  },
};

export function AssessForm() {
  const [activePreset, setActivePreset] = useState<string>('High-Risk');
  const [form, setForm] = useState<Partial<AssessRequest>>(PRESETS['High-Risk'].data);
  const [result, setResult] = useState<AssessResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSelectPreset = (key: string) => {
    setActivePreset(key);
    setForm(PRESETS[key].data);
    setResult(null);
    setError('');
  };

  const setField = (k: keyof AssessRequest, v: string | number) => {
    setForm(prev => ({ ...prev, [k]: v }));
  };

  const handleSubmit = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const res = await assessTransaction(form as AssessRequest);
      setResult(res);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Transaction assessment failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      
      {/* Presets Header */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <label className="text-xs font-mono uppercase tracking-wider text-slate-500 font-semibold flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-blue-500" />
            1-Click Scenario Presets
          </label>
        </div>
        <div className="grid grid-cols-2 gap-2">
          {Object.entries(PRESETS).map(([key, p]) => (
            <button
              key={key}
              type="button"
              onClick={() => handleSelectPreset(key)}
              className={`p-2.5 rounded-xl text-left border transition-all text-xs ${
                activePreset === key 
                  ? 'bg-blue-50/80 border-blue-400 text-blue-900 shadow-sm' 
                  : 'bg-white border-slate-200 text-slate-700 hover:border-slate-300 hover:bg-slate-50'
              }`}
            >
              <div className="font-semibold truncate">{p.label}</div>
              <div className="text-[11px] text-slate-500 truncate mt-0.5">{p.desc}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Form Fields */}
      <form onSubmit={handleSubmit} className="space-y-3">
        <div className="grid grid-cols-2 gap-3">
          {([
            ['transaction_id', 'Transaction ID', 'text', 'e.g. txn_001'],
            ['merchant_id', 'Merchant ID', 'text', 'e.g. merch_jewelry_001'],
            ['amount', 'Amount (INR)', 'number', 'e.g. 45000'],
            ['card_bin', 'Card BIN (6 digits)', 'text', 'e.g. 438935'],
            ['payment_method', 'Payment Method', 'text', 'CARD / UPI / WALLET'],
            ['device_id', 'Device Fingerprint', 'text', 'e.g. dev_mac_01'],
          ] as [keyof AssessRequest, string, string, string][]).map(([k, label, type, placeholder]) => (
            <div key={k}>
              <label className="block text-[11px] font-medium text-slate-600 mb-1">
                {label}
              </label>
              <input
                type={type}
                placeholder={placeholder}
                className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-xs font-mono text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all"
                value={(form[k] as string | number | undefined) ?? ''}
                onChange={e => setField(k, type === 'number' ? parseFloat(e.target.value) || 0 : e.target.value)}
              />
            </div>
          ))}
        </div>

        {/* Submit button */}
        <button
          type="submit"
          disabled={loading}
          className="w-full mt-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white py-3 rounded-xl font-semibold text-sm transition-all shadow-md shadow-blue-600/25 flex items-center justify-center gap-2 disabled:opacity-60"
        >
          {loading ? (
            <>
              <RotateCcw className="w-4 h-4 animate-spin" />
              Evaluating 4-Stage Uncertainty Pipeline...
            </>
          ) : (
            <>
              <Send className="w-4 h-4" />
              Run Assessment (POST /v1/assess)
            </>
          )}
        </button>
      </form>

      {/* Error Message */}
      {error && (
        <div className="p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-start gap-2.5">
          <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
          <div>
            <span className="font-semibold">Assessment Error: </span>
            {error}
            <div className="mt-1 text-[11px] text-rose-600">Ensure the backend is running on port 8000 (`start-backend.bat`).</div>
          </div>
        </div>
      )}

      {/* Result Deep Inspection Card */}
      {result && (
        <div className="border border-slate-200 rounded-2xl p-5 space-y-4 bg-white shadow-sm transition-all animate-in fade-in duration-300">
          
          {/* Header row: Decision + Telemetry */}
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div>
              <div className="text-[10px] uppercase font-mono tracking-wider text-slate-400 font-semibold mb-1">
                Pipeline Outcome
              </div>
              <DecisionBadge decision={result.decision} size="lg" />
            </div>

            <div className="text-right space-y-1">
              <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-100 font-mono text-xs text-slate-700 font-semibold">
                <Layers className="w-3.5 h-3.5 text-blue-600" />
                Stage: {result.stage_reached}
              </div>
              <div className="flex items-center justify-end gap-1 text-[11px] font-mono text-slate-500">
                <Clock className="w-3 h-3" />
                {result.inference_ms?.toFixed(1)}ms latency
              </div>
            </div>
          </div>

          {/* Key Metrics Strip */}
          <div className="grid grid-cols-3 gap-2 text-center text-xs font-mono">
            <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-100">
              <div className="text-[10px] text-slate-400 uppercase font-semibold">P(Fraud)</div>
              <div className="font-bold text-slate-800 mt-0.5">{(result.confidence * 100).toFixed(1)}%</div>
            </div>
            
            <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-100">
              <div className="text-[10px] text-slate-400 uppercase font-semibold">Decline Thresh</div>
              <div className="font-bold text-slate-800 mt-0.5">{result.risk_report.merchant_threshold?.toFixed(2)}</div>
            </div>

            <div className={`p-2.5 rounded-xl border ${
              result.risk_report.chargeback_risk && result.risk_report.chargeback_risk > 0.5 
                ? 'bg-rose-50 border-rose-200 text-rose-700' 
                : 'bg-slate-50 border-slate-100 text-slate-800'
            }`}>
              <div className="text-[10px] text-slate-400 uppercase font-semibold">Chargeback Risk</div>
              <div className="font-bold mt-0.5">
                {result.risk_report.chargeback_risk !== null 
                  ? `${(result.risk_report.chargeback_risk * 100).toFixed(1)}%`
                  : 'Low (<1%)'}
              </div>
            </div>
          </div>

          {/* DS Belief Fusion Metrics (when V3 is reached) */}
          {result.risk_report.ds_metrics && (
            <div>
              <div className="text-[11px] font-semibold text-slate-700 mb-2 flex items-center gap-1.5">
                <Layers className="w-3.5 h-3.5 text-purple-600" />
                Dempster-Shafer Belief Fusion Metrics
              </div>
              <div className="grid grid-cols-4 gap-2 text-center text-xs font-mono">
                <div className={`p-2.5 rounded-xl border ${
                  result.risk_report.ds_metrics.bel_F >= 0.91
                    ? 'bg-rose-50 border-rose-200'
                    : result.risk_report.ds_metrics.bel_F >= 0.35
                    ? 'bg-amber-50 border-amber-200'
                    : 'bg-slate-50 border-slate-100'
                }`}>
                  <div className="text-[10px] text-slate-400 uppercase font-semibold">Bel(Fraud)</div>
                  <div className="font-bold text-slate-800 mt-0.5">{(result.risk_report.ds_metrics.bel_F * 100).toFixed(1)}%</div>
                </div>
                <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-100">
                  <div className="text-[10px] text-slate-400 uppercase font-semibold">Bel(Legit)</div>
                  <div className="font-bold text-emerald-700 mt-0.5">{(result.risk_report.ds_metrics.bel_L * 100).toFixed(1)}%</div>
                </div>
                <div className={`p-2.5 rounded-xl border ${
                  result.risk_report.ds_metrics.ignorance >= 0.10
                    ? 'bg-amber-50 border-amber-200'
                    : 'bg-slate-50 border-slate-100'
                }`}>
                  <div className="text-[10px] text-slate-400 uppercase font-semibold">Ignorance</div>
                  <div className="font-bold text-slate-800 mt-0.5">{(result.risk_report.ds_metrics.ignorance * 100).toFixed(1)}%</div>
                </div>
                <div className={`p-2.5 rounded-xl border ${
                  result.risk_report.ds_metrics.conflict_K >= 0.25
                    ? 'bg-rose-50 border-rose-200'
                    : 'bg-slate-50 border-slate-100'
                }`}>
                  <div className="text-[10px] text-slate-400 uppercase font-semibold">Conflict K</div>
                  <div className="font-bold text-slate-800 mt-0.5">{result.risk_report.ds_metrics.conflict_K.toFixed(3)}</div>
                </div>
              </div>
            </div>
          )}

          {/* Agent Narrative Explanation */}
          <div>
            <div className="text-[11px] font-semibold text-slate-700 mb-1.5 flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-blue-600" />
              Agent Explanation Narrative (Analyst View)
            </div>
            <div className="p-3.5 rounded-xl bg-blue-50/50 border border-blue-100 text-xs text-slate-700 leading-relaxed font-sans">
              {result.risk_report.explanation}
            </div>
          </div>

          {/* SHAP Attributions */}
          {result.risk_report.shap_top_features?.length > 0 && (
            <div>
              <div className="text-[11px] font-semibold text-slate-700 mb-2 flex items-center justify-between">
                <span>Top SHAP Feature Attributions</span>
                <span className="text-[10px] font-mono text-slate-400">TreeExplainer</span>
              </div>
              <ShapWaterfall features={result.risk_report.shap_top_features} />
            </div>
          )}

          {/* Reason Code (for PEND) */}
          {result.risk_report.pend_reason_code && (
            <div className="pt-2 border-t border-slate-100">
              <div className="text-[10px] font-mono text-slate-400 uppercase mb-1">Generated Reason Code</div>
              <div className="p-2 rounded-lg bg-slate-900 text-blue-300 font-mono text-xs break-all">
                {result.risk_report.pend_reason_code}
              </div>
            </div>
          )}

        </div>
      )}

    </div>
  );
}
