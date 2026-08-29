'use client';
import { ShapFeature } from '@/lib/api';

const LABELS: Record<string, string> = {
  amount_log: 'Amount (log)',
  amount_vs_merchant_avg: 'Amount vs Avg',
  velocity_1h_count: 'Velocity 1h count',
  velocity_1h_amount_log: 'Velocity 1h spend',
  velocity_24h_count: 'Velocity 24h count',
  velocity_24h_amount_log: 'Velocity 24h spend',
  bin_risk_score: 'Card BIN Risk',
  device_seen_before: 'Device Known',
  is_odd_hour: 'Odd Hour (1-5am)',
  hour_sin: 'Time of Day',
  hour_cos: 'Time of Day',
  payment_method_upi: 'UPI Payment',
  payment_method_card: 'Card Payment',
  payment_method_wallet: 'Wallet Payment',
};

export function ShapWaterfall({ features }: { features: ShapFeature[] }) {
  if (!features.length) return <p className="text-sm text-gray-400 italic">No SHAP features available.</p>;
  const maxImpact = Math.max(...features.map(f => f.impact));
  return (
    <div className="space-y-2">
      {features.map((f, i) => {
        const isFraud = f.direction === 'elevates_fraud';
        const pct = Math.round((f.impact / maxImpact) * 100);
        return (
          <div key={i} className="flex items-center gap-3">
            <span className="w-40 text-xs text-gray-600 truncate text-right">{LABELS[f.feature] || f.feature}</span>
            <div className="flex-1 bg-gray-100 rounded-full h-3 overflow-hidden">
              <div
                className={`h-3 rounded-full transition-all duration-500 ${isFraud ? 'bg-red-400' : 'bg-emerald-400'}`}
                style={{ width: `${pct}%` }}
              />
            </div>
            <span className={`text-xs font-mono w-14 text-right ${isFraud ? 'text-red-600' : 'text-emerald-600'}`}>
              {isFraud ? '+' : '-'}{f.impact.toFixed(3)}
            </span>
          </div>
        );
      })}
    </div>
  );
}
