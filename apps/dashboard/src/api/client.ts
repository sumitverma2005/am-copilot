import type { CallSummary, EvidenceResponse, ScoreResult } from '../types'

const BASE = '/api'

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`)
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail ?? `HTTP ${res.status}`)
  }
  return res.json()
}

export const api = {
  calls: {
    list: () => get<CallSummary[]>('/calls'),
    get: (id: string) => get<ScoreResult>(`/calls/${id}`),
    evidence: (id: string, dimension: string) =>
      get<EvidenceResponse>(`/calls/${id}/evidence/${dimension}`),
  },
}
