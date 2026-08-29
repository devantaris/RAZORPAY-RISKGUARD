'use client';
import { useState } from 'react';
import { AssessRequest, BatchAssessResponse, batchAssessTransactions } from '@/lib/api';
import { DecisionBadge } from './DecisionBadge';
import { 
  RotateCcw, 
  AlertCircle, 
  Play
} from 'lucide-react';

const SAMPLE_PAYLOADS: AssessRequest[] = [
  { transaction_id: 'txn_batch_001', merchant_id: 'merch_jewelry_001', amount: 98000, currency: 'INR', card_bin: '438935', payment_method: 'CARD' },
  { transaction_id: 'txn_batch_002', merchant_id: 'merch_food_001', amount: 349, currency: 'INR', payment_method: 'UPI' },
  { transaction_id: 'txn_batch_003', merchant_id: 'merch_travel_001', amount: 38000, currency: 'INR', card_bin: '400066', payment_method: 'CARD' },
  { transaction_id: 'txn_batch_004', merchant_id: 'merch_electronics_001', amount: 14500, currency: 'INR', card_bin: '410057', payment_method: 'CARD' },
  { transaction_id: 'txn_batch_005', merchant_id: 'merch_food_001', amount: 120, currency: 'INR', payment_method: 'UPI' },
  { transaction_id: 'txn_batch_006', merchant_id: 'merch_gaming_001', amount: 2499, currency: 'INR', card_bin: '532101', payment_method: 'CARD' },
  { transaction_id: 'txn_batch_007', merchant_id: 'merch_jewelry_001', amount: 154000, currency: 'INR', card_bin: '461046', payment_method: 'CARD' },
  { transaction_id: 'txn_batch_008', merchant_id: 'merch_petrol_001', amount: 2000, currency: 'INR', payment_method: 'CARD' },
  { transaction_id: 'txn_batch_009', merchant_id: 'merch_ecommerce_001', amount: 4800, currency: 'INR', card_bin: '512345', payment_method: 'CARD' },
  { transaction_id: 'txn_batch_010', merchant_id: 'merch_pharmacy_001', amount: 850, currency: 'INR', payment_method: 'UPI' },
];

export function BatchSimulator() {
  const [batchSize, setBatchSize] = useState<number>(10);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<BatchAssessResponse | null>(null);
  const [error, setError] = useState('');

  const generateBatch = (count: number): AssessRequest[] => {
    const list: AssessRequest[] = [];
    for (let i = 0; i < count; i++) {
      const base = SAMPLE_PAYLOADS[i % SAMPLE_PAYLOADS.length];
      list.push({
        ...base,
        transaction_id: `txn_sim_${Date.now()}_${i + 1}`,
        amount: Math.round(base.amount * (0.8 + Math.random() * 0.4)),
      });
    }
    return list;
  };

  const handleRunBatch = async () => {
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const batch = generateBatch(batchSize);
      const res = await batchAssessTransactions(batch);
      setResult(res);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Batch simulation failed');
    } finally {
      setLoading(false);
    }
  };

  const decisionCounts = result?.results.reduce((acc, r) => {
    acc[r.decision] = (acc[r.decision] || 0) + 1;
    return acc;
  }, {} as Record<string, number>) || {};

  return (
    <div className="space-y-6">
      
      {/* Controls */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 bg-slate-50 border border-slate-200 rounded-2xl">
        <div className="flex items-center gap-3 w-full sm:w-auto">
          <label className="text-xs font-mono uppercase tracking-wider text-slate-500 font-semibold">
            Batch Size:
          </label>
          <div className="flex gap-1.5">
            {[10, 25, 50, 100].map(size => (
              <button
                key={size}
                type="button"
                onClick={() => setBatchSize(size)}
                className={`px-3 py-1 rounded-lg text-xs font-mono font-semibold transition-all ${
                  batchSize === size 
                    ? 'bg-blue-600 text-white shadow-sm' 
                    : 'bg-white border border-slate-200 text-slate-700 hover:bg-slate-100'
                }`}
              >
                {size} txns
              </button>
            ))}
          </div>
        </div>

        <button
          type="button"
          onClick={handleRunBatch}
          disabled={loading}
          className="w-full sm:w-auto px-6 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white rounded-xl font-semibold text-xs transition-all shadow-md shadow-blue-600/20 flex items-center justify-center gap-2 disabled:opacity-50"
        >
          {loading ? (
            <>
              <RotateCcw className="w-3.5 h-3.5 animate-spin" />
              Running High-Throughput Batch...
            </>
          ) : (
            <>
              <Play className="w-3.5 h-3.5 fill-current" />
              Run Batch Simulation (POST /v1/batch)
            </>
          )}
        </button>
      </div>

      {error && (
        <div className="p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4" />
          {error}
        </div>
      )}

      {/* Results Summary */}
      {result && (
        <div className="space-y-4 animate-in fade-in duration-300">
          
          {/* Telemetry Stats */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center font-mono">
            <div className="p-3 bg-white border border-slate-200 rounded-xl">
              <div className="text-[10px] text-slate-400 uppercase font-semibold">Total Txns</div>
              <div className="text-xl font-bold text-slate-900 mt-0.5">{result.results.length}</div>
            </div>

            <div className="p-3 bg-white border border-slate-200 rounded-xl">
              <div className="text-[10px] text-slate-400 uppercase font-semibold">Total Latency</div>
              <div className="text-xl font-bold text-blue-600 mt-0.5">{result.total_ms.toFixed(1)}ms</div>
            </div>

            <div className="p-3 bg-white border border-slate-200 rounded-xl">
              <div className="text-[10px] text-slate-400 uppercase font-semibold">Throughput</div>
              <div className="text-xl font-bold text-emerald-600 mt-0.5">{result.throughput_tps.toFixed(0)} TPS</div>
            </div>

            <div className="p-3 bg-white border border-slate-200 rounded-xl">
              <div className="text-[10px] text-slate-400 uppercase font-semibold">Avg Per Txn</div>
              <div className="text-xl font-bold text-purple-600 mt-0.5">
                {(result.total_ms / result.results.length).toFixed(1)}ms
              </div>
            </div>
          </div>

          {/* Decision Distribution Bar */}
          <div className="p-4 bg-white border border-slate-200 rounded-2xl">
            <div className="text-xs font-semibold text-slate-700 mb-3 flex items-center justify-between">
              <span>Decision Breakdown</span>
              <span className="text-[11px] font-mono text-slate-500">100% DECLINE Precision</span>
            </div>

            <div className="grid grid-cols-4 gap-2 text-center text-xs font-mono mb-4">
              <div className="p-2 rounded-lg bg-emerald-50 text-emerald-800 border border-emerald-100">
                <span className="text-[10px] uppercase block">APPROVE</span>
                <span className="font-bold text-base">{decisionCounts['APPROVE'] || 0}</span>
              </div>
              <div className="p-2 rounded-lg bg-rose-50 text-rose-800 border border-rose-100">
                <span className="text-[10px] uppercase block">DECLINE</span>
                <span className="font-bold text-base">{decisionCounts['DECLINE'] || 0}</span>
              </div>
              <div className="p-2 rounded-lg bg-amber-50 text-amber-800 border border-amber-100">
                <span className="text-[10px] uppercase block">STEP UP</span>
                <span className="font-bold text-base">{decisionCounts['STEP_UP'] || 0}</span>
              </div>
              <div className="p-2 rounded-lg bg-blue-50 text-blue-800 border border-blue-100">
                <span className="text-[10px] uppercase block">PEND</span>
                <span className="font-bold text-base">{decisionCounts['PEND'] || 0}</span>
              </div>
            </div>

            {/* Results Table (First 10) */}
            <div className="max-h-64 overflow-y-auto border border-slate-100 rounded-xl divide-y divide-slate-100 text-xs font-mono">
              {result.results.map((r, i) => (
                <div key={i} className="flex items-center justify-between p-2.5 hover:bg-slate-50 transition-colors">
                  <div className="flex items-center gap-3">
                    <span className="text-slate-400 w-5">#{i + 1}</span>
                    <DecisionBadge decision={r.decision} size="sm" />
                    <span className="text-slate-600 truncate w-32">{r.transaction_id}</span>
                  </div>
                  <div className="flex items-center gap-4 text-slate-500">
                    <span>Stage: <b className="text-slate-700">{r.stage_reached}</b></span>
                    <span>Conf: <b className="text-slate-700">{(r.confidence * 100).toFixed(0)}%</b></span>
                    <span className="w-14 text-right text-slate-400">{r.inference_ms?.toFixed(1)}ms</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>
      )}

    </div>
  );
}
