import { Decision } from '@/lib/api';

const CONFIG: Record<Decision, { bg: string; text: string; label: string; dot: string }> = {
  APPROVE:  { bg: 'bg-emerald-50',  text: 'text-emerald-700', dot: 'bg-emerald-500', label: 'APPROVE'  },
  DECLINE:  { bg: 'bg-red-50',     text: 'text-red-700',     dot: 'bg-red-500',     label: 'DECLINE'  },
  STEP_UP:  { bg: 'bg-amber-50',   text: 'text-amber-700',   dot: 'bg-amber-500',   label: 'STEP UP'  },
  PEND:     { bg: 'bg-blue-50',    text: 'text-blue-700',    dot: 'bg-blue-500',    label: 'PEND'     },
};

export function DecisionBadge({ decision, size = 'md' }: { decision: Decision; size?: 'sm' | 'md' | 'lg' }) {
  const c = CONFIG[decision];
  const sz = size === 'sm' ? 'px-2 py-0.5 text-xs' : size === 'lg' ? 'px-4 py-2 text-base font-bold' : 'px-3 py-1 text-sm font-semibold';
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full ${c.bg} ${c.text} ${sz}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${c.dot}`} />
      {c.label}
    </span>
  );
}
