import type {
  CallSummary,
  CoachingQueueRow,
  ComplianceQueueRow,
  DisagreementRow,
  EvidenceResponse,
  ScoreResult,
} from '../types'

const BASE = '/api'

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`)
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail ?? `HTTP ${res.status}`)
  }
  return res.json()
}

async function post<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: body !== undefined ? { 'Content-Type': 'application/json' } : {},
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })
  if (!res.ok) {
    const b = await res.json().catch(() => ({}))
    throw new Error(b.detail ?? `HTTP ${res.status}`)
  }
  return res.json()
}

export const api = {
  calls: {
    list: () => get<CallSummary[]>('/calls'),
    get: (id: string) => get<ScoreResult>(`/calls/${id}`),
    evidence: (id: string, dimension: string) =>
      get<EvidenceResponse>(`/calls/${id}/evidence/${dimension}`),
    getNote: (id: string) => get<{ call_id: string; text: string }>(`/calls/${id}/note`),
    saveNote: (id: string, text: string) =>
      post<{ call_id: string; text: string }>(`/calls/${id}/note`, { text }),
    override: (
      id: string,
      payload: {
        dimension: string
        ai_score: number | null
        manager_score: number | null
        comment: string
      }
    ) => post<DisagreementRow>(`/calls/${id}/override`, payload),
  },
  queue: {
    coaching: () => get<CoachingQueueRow[]>('/queue/coaching'),
    markCoached: (id: string) =>
      post<{ call_id: string; status: string }>(`/queue/coaching/${id}/complete`),
    compliance: () => get<ComplianceQueueRow[]>('/queue/compliance'),
    markReviewed: (id: string, comment: string) =>
      post<{ call_id: string; status: string }>(`/queue/compliance/${id}/review`, { comment }),
  },
  disagreements: {
    list: () => get<DisagreementRow[]>('/disagreements'),
    exportUrl: () => `${BASE}/disagreements/export`,
  },
}
