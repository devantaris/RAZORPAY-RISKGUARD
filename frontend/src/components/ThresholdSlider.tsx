'use client';
import { useEffect, useState } from 'react';
import { BanditDiagnostics, getMerchantThreshold, setMerchantThreshold } from '@/lib/api';

const ARMS = [-0.10, -0.05, 0.0, 0.05, 0.10];

export function ThresholdSlider({ merchantId }: { merchantId: string }) {
  const [diag, setDiag] = useState<BanditDiagnostics | null>(null);
  const [offset, setOffset] = useState(0);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState('');

  useEffect(() => {
    getMerchantThreshold(merchantId).then(d => {
      setDiag(d);
      setOffset(parseFloat(d.current_arm || '0'));
    }).catch(() => {});
  }, [merchantId]);

  const handleSave = async () => {
    setSaving(true);
    try {
      const res = await setMerchantThreshold(merchantId, offset);
      setMsg(`Saved: threshold = ${res.effective_threshold}`);
      const d = await getMerchantThreshold(merchantId);
      setDiag(d);
    } catch { setMsg('Save failed'); }
    setSaving(false);
    setTimeout(() => setMsg(''), 3000);
  };

  const effective = Math.max(0.40, Math.min(0.95, 0.80 + offset));

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-gray-700">Decline Threshold</span>
        <span className="text-2xl font-bold text-gray-900">{effective.toFixed(2)}</span>
      </div>
      <input
        type="range" min={-3} max={3} step={1}
        value={ARMS.indexOf(offset)}
        onChange={e => setOffset(ARMS[parseInt(e.target.value)] ?? 0)}
        className="w-full accent-blue-600"
      />
      <div className="flex justify-between text-xs text-gray-400">
        {ARMS.map(a => <span key={a}>{(0.80 + a).toFixed(2)}</span>)}
      </div>
      {diag && (
        <div className="grid grid-cols-3 gap-2 text-center text-xs">
          <div className="bg-gray-50 rounded p-2">
            <div className="font-semibold text-gray-700">{diag.n_samples}</div>
            <div className="text-gray-400">Samples</div>
          </div>
          <div className="bg-gray-50 rounded p-2">
            <div className="font-semibold text-gray-700">{diag.ema_reward.toFixed(3)}</div>
            <div className="text-gray-400">EMA Reward</div>
          </div>
          <div className="bg-gray-50 rounded p-2">
            <div className={`font-semibold ${diag.is_adjusted ? 'text-emerald-600' : 'text-gray-400'}`}>
              {diag.is_adjusted ? 'Active' : 'Learning'}
            </div>
            <div className="text-gray-400">Bandit</div>
          </div>
        </div>
      )}
      <div className="flex items-center gap-2">
        <button
          onClick={handleSave} disabled={saving}
          className="flex-1 bg-blue-600 text-white text-sm py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          {saving ? 'Saving...' : 'Apply Override'}
        </button>
        {msg && <span className="text-xs text-emerald-600">{msg}</span>}
      </div>
    </div>
  );
}
