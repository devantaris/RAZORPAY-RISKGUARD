// Types matching backend Pydantic schemas exactly
export type Decision = 'APPROVE' | 'DECLINE' | 'STEP_UP' | 'PEND';

export interface ShapFeature {
  feature: string;
  impact: number;
  direction: 'elevates_fraud' | 'suppresses_fraud';
}

export interface RiskReport {
  explanation: string;
  shap_top_features: ShapFeature[];
  merchant_threshold: number;
  chargeback_risk: number | null;
  uncertainty_type: string | null;
  pend_reason_code: string | null;
  ds_metrics: {
    bel_F: number;
    bel_L: number;
    pl_F: number;
    pl_L: number;
    ignorance: number;
    conflict_K: number;
  } | null;
}

export interface AssessResponse {
  transaction_id: string;
  decision: Decision;
  confidence: number;
  stage_reached: string;
  risk_report: RiskReport;
  inference_ms: number;
}

export interface AssessRequest {
  transaction_id: string;
  merchant_id: string;
  amount: number;
  currency: string;
  card_bin?: string;
  payment_method: string;
  device_id?: string;
  customer_id?: string;
}

export interface BanditDiagnostics {
  merchant_id: string;
  effective_threshold: number;
  n_samples: number;
  current_arm: string;
  ema_reward: number;
  is_adjusted: boolean;
  arm_summary: Record<string, { count: number; avg_reward: number }>;
}

export interface BatchAssessRequest {
  transactions: AssessRequest[];
}

export interface BatchAssessResponse {
  results: AssessResponse[];
  total_ms: number;
  throughput_tps: number;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export async function assessTransaction(req: AssessRequest): Promise<AssessResponse> {
  const res = await fetch(`${API_BASE}/v1/assess`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function batchAssessTransactions(transactions: AssessRequest[]): Promise<BatchAssessResponse> {
  const res = await fetch(`${API_BASE}/v1/batch`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ transactions }),
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function getHealth(): Promise<{ status: string; service: string; version: string; uptime_s: number; pipeline: string }> {
  const res = await fetch(`${API_BASE}/v1/health`);
  if (!res.ok) throw new Error(`Health check error: ${res.status}`);
  return res.json();
}

export async function getMerchantThreshold(merchantId: string): Promise<BanditDiagnostics> {
  const res = await fetch(`${API_BASE}/v1/merchants/${merchantId}/threshold`);
  if (!res.ok) throw new Error(`Merchant threshold error: ${res.status}`);
  return res.json();
}

export async function setMerchantThreshold(merchantId: string, offset: number): Promise<{ effective_threshold: number; message: string }> {
  const res = await fetch(`${API_BASE}/v1/merchants/${merchantId}/threshold`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ offset }),
  });
  if (!res.ok) throw new Error(`Set threshold error: ${res.status}`);
  return res.json();
}

export function streamTransactions(onEvent: (data: AssessResponse) => void): () => void {
  const evtSource = new EventSource(`${API_BASE}/v1/stream`);
  evtSource.onmessage = (e) => {
    try { onEvent(JSON.parse(e.data)); } catch {}
  };
  return () => evtSource.close();
}
