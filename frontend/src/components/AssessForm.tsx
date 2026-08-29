'use client';
import { useState } from 'react';
import { AssessRequest, AssessResponse, assessTransaction } from '@/lib/api';
import { DecisionBadge } from './DecisionBadge';
import { ShapWaterfall } from './ShapWaterfall';

const PRESETS: Record<string, Partial<AssessRequest>> = {
  'High-Risk': { transaction_id: 'txn_demo_hr', merchant_id: 'merch_jewelry_001', amount: 98000, currency: 'INR', card_bin: '438935', payment_method: 'CARD', device_id: 'dev_new_001' },
  'Low-Risk':  { transaction_id: 'txn_demo_lr', merchant_id: 'merch_food_001',    amount: 349,   currency: 'INR', payment_method: 'UPI' },
  'Step-Up':   { transaction_id: 'txn_demo_su', merchant_id: 'merch_travel_001',  amount: 38000, currency: 'INR', card_bin: '400066', payment_method: 'CARD' },
};

export function AssessForm() {
  const [form, setForm] = useState<Partial<AssessRequest>>(PRESETS['High-Risk']);
  const [result, setResult] = useState<AssessResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const set = (k: keyof AssessRequest, v: string | number) => setForm(f => ({ ...f, [k]: v }));

  const submit = async () => {
    setLoading(true); setError(''); setResult(null);
    try {
      const res = await assessTransaction(form as AssessRequest);
      setResult(res);
    } catch (e: unknown) { setError(e instanceof Error ? e.message : 'Request failed'); }
    setLoading(false);
  };

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        {Object.keys(PRESETS).map(p => (
          <button key={p} onClick={() => setForm(PRESETS[p])}
            className="px-3 py-1.5 text-xs bg-gray-100 hover:bg-gray-200 rounded-full transition-colors">
            {p}
          </button>
        ))}
      </div>
      <div className="grid grid-cols-2 gap-3">
        {([
          ['transaction_id', 'Transaction ID'], ['merchant_id', 'Merchant ID'],
          ['amount', 'Amount (INR)'], ['card_bin', 'Card BIN'],
          ['payment_method', 'Payment Method'], ['device_id', 'Device ID'],
        ] as [keyof AssessRequest, string][]).map(([k, label]) => (
          <div key={k}>
            <label className="block text-xs text-gray-500 mb-1">{label}</label>
            <input
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={(form[k] as string | number | undefined) ?? ''}
              onChange={e => set(k, k === 'amount' ? parseFloat(e.target.value) || 0 : e.target.value)}
            />
          </div>
        ))}
      </div>
      <button onClick={submit} disabled={loading}
        className="w-full bg-blue-600 text-white py-2.5 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 transition-colors">
        {loading ? 'Assessing...' : 'POST /v1/assess'}
      </button>
      {error && <p className="text-red-500 text-sm">{error}</p>}
      {result && (
        <div className="border border-gray-200 rounded-xl p-4 space-y-4 bg-gray-50">
          <div className="flex items-center justify-between">
            <DecisionBadge decision={result.decision} size="lg" />
            <div className="text-right">
              <div className="text-xs text-gray-400">Stage: <b>{result.stage_reached}</b></div>
              <div className="text-xs text-gray-400">Latency: <b>{result.inference_ms?.toFixed(1)}ms</b></div>
              {result.risk_report.chargeback_risk !== null && (
                <div className="text-xs text-orange-600">Chargeback Risk: <b>{((result.risk_report.chargeback_risk ?? 0) * 100).toFixed(1)}%</b></div>
              )}
            </div>
          </div>
          <div className="text-sm text-gray-700 bg-white border border-gray-100 rounded-lg p-3">
            {result.risk_report.explanation}
          </div>
          {result.risk_report.shap_top_features?.length > 0 && (
            <div>
              <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">SHAP Feature Attributions</h4>
              <ShapWaterfall features={result.risk_report.shap_top_features} />
            </div>
          )}
          {result.risk_report.pend_reason_code && (
            <div className="text-xs font-mono text-blue-600 bg-blue-50 rounded px-2 py-1">{result.risk_report.pend_reason_code}</div>
          )}
        </div>
      )}
    </div>
  );
}
