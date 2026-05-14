/* Types mirror the ScoreResult Pydantic model in services/scoring-engine/scoring_engine/models.py */

export interface EvaluationRow {
  call_id: string
  agent_id: string
  call_timestamp: string
  duration_seconds: number
  scenario_type: string | null
  rubric_version: string
  prompt_version: string
  model_id: string
  overall_score: number
  compliance_override_triggered: boolean
  confidence_overall: number
  manager_summary: string
  status: string
  scored_at: string
}

export interface DimensionScoreRow {
  dimension: string
  raw_score: number | null
  weighted_score: number | null
  weight: number
  confidence: number | null
  ai_rationale: string
  coaching_note: string | null
  is_na: boolean
}

export interface EvidenceAnchorRow {
  dimension: string
  turn_number: number
  timestamp_seconds: number
  speaker: string
  text_snippet: string
  relevance_rank: number
}

export interface ComplianceFlagRow {
  flag_code: string
  matched_phrase: string
  turn_number: number
  timestamp_seconds: number
  severity: string
  reviewed: boolean
}

export interface ScoreResult {
  evaluation: EvaluationRow
  dimension_scores: DimensionScoreRow[]
  evidence_anchors: EvidenceAnchorRow[]
  compliance_flags: ComplianceFlagRow[]
}

/* Summary row returned by GET /calls */
export interface CallSummary {
  call_id: string
  agent_id: string
  call_timestamp: string
  duration_seconds: number
  scenario_type: string | null
  overall_score: number
  compliance_override_triggered: boolean
  status: string
  worst_dimension: string | null
  has_compliance_flags: boolean
}

/* Evidence endpoint response */
export interface EvidenceResponse {
  call_id: string
  dimension: string
  anchors: EvidenceAnchorRow[]
  dim_score: DimensionScoreRow | null
}

export const DIMENSION_LABELS: Record<string, string> = {
  empathy_rapport: 'Empathy & Rapport',
  insurance_verification: 'Insurance Verification',
  clinical_screening: 'Clinical Screening',
  urgency_triage: 'Urgency Triage',
  family_caller_handling: 'Family Caller Handling',
  objection_handling: 'Objection Handling',
  next_step_clarity: 'Next-Step Clarity',
  compliance_language: 'Compliance Language',
}
