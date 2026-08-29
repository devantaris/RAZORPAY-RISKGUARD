'use client';
import { useEffect, useState } from 'react';
import { BanditDiagnostics, getMerchantThreshold, setMerchantThreshold } from '@/lib/api';
import { Sliders, RotateCcw } from 'lucide-react';

const ARMS = [-0.10, -0.05, 0.0, 0.05, 0.10];

interface ThresholdSliderProps {
  merchantId: string;
  categoryTitle?: string;
  categoryDesc?: string;
}

export function ThresholdSlider({ 
  merchantId, 
  categoryTitle = 'Merchant Threshold',
  categoryDesc = 'Dynamic Auto-Threshold Bandit (ε=0.10, α=0.30)' 
}: ThresholdSliderProps) {
  const [diag, setDiag] = useState<BanditDiagnostics | null>(null);
  const [offset, setOffset] = useState(0);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState('');

  useEffect(() => {
    getMerchantThreshold(merchantId)
      .then(d => {
        setDiag(d);
        setOffset(parseFloat(d.current_arm || '0'));
      })
      .catch(() => {});
  }, [merchantId]);

  const handleSave = async () => {
    setSaving(true);
    try {
      const res = await setMerchantThreshold(merchantId, offset);
      setMsg(`Updated to ${res.effective_threshold.toFixed(2)}`);
      const d = await getMerchantThreshold(merchantId);
      setDiag(d);
    } catch {
      setMsg('Failed to update');
    } finally {
      setSaving(false);
      setTimeout(() => setMsg(''), 3000);
    }
  };

  const effective = Math.max(0.40, Math.min(0.95, 0.80 + offset));

  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm space-y-4 hover:border-slate-300 transition-all flex flex-col justify-between">
      
      {/* Card Header */}
      <div>
        <div className="flex items-center justify-between mb-1">
          <h3 className="font-bold text-slate-900 text-sm flex items-center gap-1.5">
            <Sliders className="w-4 h-4 text-blue-600" />
            {categoryTitle}
          </h3>
          <span className="font-mono text-[10px] text-slate-400 bg-slate-100 px-2 py-0.5 rounded">
            {merchantId}
          </span>
        </div>
        <p className="text-[11px] text-slate-500">{categoryDesc}</p>
      </div>

      {/* Threshold Display & Slider */}
      <div className="p-3.5 bg-slate-50 border border-slate-100 rounded-xl space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs font-medium text-slate-600">Effective Decline Threshold</span>
          <span className="text-xl font-mono font-bold text-slate-900 bg-white px-2.5 py-0.5 rounded-lg border border-slate-200 shadow-inner">
            {effective.toFixed(2)}
          </span>
        </div>

        <div>
          <input
            type="range"
            min={0}
            max={ARMS.length - 1}
            step={1}
            value={Math.max(0, ARMS.indexOf(offset))}
            onChange={e => setOffset(ARMS[parseInt(e.target.value)] ?? 0)}
            className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
          />
          <div className="flex justify-between text-[10px] font-mono text-slate-400 mt-1">
            <span>0.70 (Aggressive)</span>
            <span>0.80 (Base)</span>
            <span>0.90 (Conservative)</span>
          </div>
        </div>
      </div>

      {/* Diagnostics */}
      {diag ? (
        <div className="grid grid-cols-3 gap-2 text-center text-xs font-mono">
          <div className="p-2 rounded-lg bg-slate-50 border border-slate-100">
            <div className="text-[10px] text-slate-400 uppercase font-semibold">Samples</div>
            <div className="font-bold text-slate-800 mt-0.5">{diag.n_samples}</div>
          </div>

          <div className="p-2 rounded-lg bg-slate-50 border border-slate-100">
            <div className="text-[10px] text-slate-400 uppercase font-semibold">EMA Reward</div>
            <div className="font-bold text-blue-600 mt-0.5">{diag.ema_reward.toFixed(2)}</div>
          </div>

          <div className={`p-2 rounded-lg border ${
            diag.is_adjusted 
              ? 'bg-emerald-50 border-emerald-200 text-emerald-700' 
              : 'bg-amber-50 border-amber-200 text-amber-700'
          }`}>
            <div className="text-[10px] uppercase font-semibold">Bandit State</div>
            <div className="font-bold mt-0.5 text-[11px]">
              {diag.is_adjusted ? 'Tuned' : 'Warm-up'}
            </div>
          </div>
        </div>
      ) : (
        <div className="p-2 rounded-lg bg-slate-50 border border-slate-100 text-center text-[11px] text-slate-400 font-mono">
          Bandit listening for live rewards...
        </div>
      )}

      {/* Action Button */}
      <div className="flex items-center gap-2 pt-1">
        <button
          type="button"
          onClick={handleSave}
          disabled={saving}
          className="w-full bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold py-2.5 rounded-xl transition-all flex items-center justify-center gap-1.5 shadow-sm disabled:opacity-50"
        >
          {saving ? (
            <>
              <RotateCcw className="w-3.5 h-3.5 animate-spin" />
              Applying...
            </>
          ) : (
            'Apply Threshold Override'
          )}
        </button>
        {msg && <span className="text-[11px] font-mono text-emerald-600 whitespace-nowrap">{msg}</span>}
      </div>

    </div>
  );
}
