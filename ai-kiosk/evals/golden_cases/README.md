# golden_cases — scripted end-to-end cases (docs/08 §1, pyramid #3)

≥ **50 scripted cases** across crops × modalities × risk tiers. Run on **every
build and every release**; each case asserts the expected decision, risk tier,
and any blocking rule. DVC-versioned; consented + pseudonymous (no PII, phone →
`farmer_ref`, faces blurred).

## Case format (one JSON per case)

```json
{
  "id": "GC-001",
  "crop": "cotton",
  "stage": "flowering",
  "input": {
    "modality": "voice",            // voice | touch | text | picture
    "confidence": 0.92,
    "content": { "text_te": "ఆకులు విల్ట్ అవుతున్నాయి", "text_en": "leaves are wilting" }
  },
  "weather": { "status": "fresh" },  // fresh | stale
  "expected": {
    "decision": "advisory",
    "risk_tier": "ADVISORY",
    "blocked": false,
    "requires_confirmation": false
  },
  "assertions": [
    "decision == advisory",
    "risk_tier == ADVISORY",
    "every high-risk output carries evidence IDs"
  ]
}
```

## Coverage matrix (target)

| Axis | Values |
|---|---|
| Crops | cotton, paddy, groundnut, maize, arhar, castor, millets, chilli (8) |
| Modalities | voice, touch, text, picture (+ mixed within a case) |
| Risk tiers | INFORMATION, DIAGNOSIS, ADVISORY, PRESCRIPTION |
| Edge | online / offline (`--network none`), stale weather, printer failure, sync gap |

## Acceptance

- Every supported crop has representative **positive and negative** cases.
- Every intervention rule has allowed and blocked cases (property test: **no
  blocked intervention can reach printable state**).
- Every `blocked=true` case must not reach a printable prescription.
- Run gate wires this corpus into CI (`ci/workflows/eval-gate.yml`).
