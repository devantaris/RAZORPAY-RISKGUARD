'use client';
import { useEffect, useRef, useState } from 'react';
import { DecisionBadge } from './DecisionBadge';
import type { AssessResponse } from '@/lib/api';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export function LiveFeed() {
  const [events, setEvents] = useState<AssessResponse[]>([]);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState('');
  const listRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const evtSource = new EventSource(`${API_BASE}/v1/stream`);
    evtSource.onopen = () => { setConnected(true); setError(''); };
    evtSource.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data) as AssessResponse;
        setEvents(prev => [data, ...prev].slice(0, 50));
      } catch { /* ignore malformed */ }
    };
    evtSource.onerror = () => { setConnected(false); setError('Backend offline — start backend and refresh'); };
    return () => { evtSource.close(); setConnected(false); };
  }, []);

  useEffect(() => {
    listRef.current?.scrollTo({ top: 0, behavior: 'smooth' });
  }, [events.length]);

  const counts = events.reduce((acc, e) => { acc[e.decision] = (acc[e.decision] || 0) + 1; return acc; }, {} as Record<string, number>);

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center gap-2 mb-3">
        <span className={`w-2 h-2 rounded-full ${connected ? 'bg-emerald-500 animate-pulse' : 'bg-red-400'}`} />
        <span className={`text-xs ${connected ? 'text-gray-500' : 'text-red-500'}`}>
          {connected ? 'Live stream connected' : error || 'Connecting to backend...'}
        </span>
        <div className="ml-auto flex gap-3 text-xs">
          {Object.entries(counts).map(([d, n]) => (
            <span key={d} className="text-gray-600">{d}: <b>{n}</b></span>
          ))}
        </div>
      </div>
      <div ref={listRef} className="flex-1 overflow-y-auto space-y-1.5 pr-1">
        {events.map((e, i) => (
          <div key={i} className="flex items-center gap-3 px-3 py-2 bg-white border border-gray-100 rounded-lg text-sm hover:border-gray-300 transition-colors">
            <DecisionBadge decision={e.decision} size="sm" />
            <span className="font-mono text-xs text-gray-500 w-32 truncate">{e.transaction_id}</span>
            <span className="text-gray-700">{e.risk_report?.explanation?.substring(0, 60)}...</span>
            <span className="ml-auto text-xs text-gray-400 font-mono">{e.inference_ms?.toFixed(0)}ms</span>
          </div>
        ))}
        {!events.length && (
          <div className="text-center py-12 text-gray-400 text-sm">Waiting for transactions...</div>
        )}
      </div>
    </div>
  );
}
