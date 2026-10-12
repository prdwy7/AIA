/**
 * Scientist Portal (S21) — skeleton.
 *
 * The scientist's workbench: review queue (prescriptions + uncertain cases),
 * minimal-field correction UX (approve/correct/escalate — only wrong fields
 * editable), multimodal feedback, candidate approval, escalation queue with
 * SLA, dashboards.
 *
 * Full module context: docs/02-modules.md §S21.
 * Invariants: MFA (TOTP) required; context snapshot is read-only; the
 * scientist changes ONLY the wrong fields — the original AI decision is
 * never overwritten.
 */
import { useEffect, useState } from 'react'

const API_BASE = '/v1'

interface ReviewItem {
  id: string
  case_id: string
  status: string
  created_at: string
}

export default function App() {
  const [items, setItems] = useState<ReviewItem[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // TODO: Keycloak OIDC login (MFA/TOTP required) before any data call.
    fetch(`${API_BASE}/review/queue`)
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then((d: { items: ReviewItem[] }) => setItems(d.items))
      .catch((e: Error) => setError(e.message))
  }, [])

  return (
    <main style={{ fontFamily: 'system-ui', margin: '2rem auto', maxWidth: 900 }}>
      <h1>AI Kiosk — Scientist Portal</h1>
      <p>
        Skeleton (S21). Review queue: approve / correct / escalate — the scientist
        changes <strong>only the wrong fields</strong>; the original AI decision is
        never overwritten. Every correction carries an evidence status
        (EVIDENCE_BACKED / LOCALLY_VALIDATED / EXPERT_PREFERENCE).
      </p>
      {error && <p style={{ color: 'crimson' }}>review-service unreachable: {error}</p>}
      <ul>
        {items.map((i) => (
          <li key={i.id}>
            {i.id} — case {i.case_id} ({i.status})
          </li>
        ))}
      </ul>
    </main>
  )
}
