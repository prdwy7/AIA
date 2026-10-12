# 07 — Security, Privacy & Compliance

> Roadmap §14. Security is designed in, not bolted on: the system handles farmer
> pseudonyms, photos (with faces), audio, and agricultural decisions that can cause
> real harm if wrong.

## 1. Threat model

**Assets (by sensitivity):**

| Asset | Location | Sensitivity | Notes |
|---|---|---|---|
| Case graph + decisions (pseudonym, crop, location, treatment history) | Central + edge | High | System of record; 5-year retention |
| Media (photos with faces, audio) | Central MinIO + edge queue | High | Faces blurred by default |
| Farmer PII (phone, if opt-in) | Central | High | Pseudonymous `farmer_ref`; purpose-limited |
| Knowledge base + rules + regulatory tables | Central (signed bundles on edge) | Medium | Versioned; re-verified per release |
| Model artifacts + fine-tuning data | Central | Medium | Signed; license-tracked |
| Learning records + provenance | Central | Medium | 5-year retention |
| Audit log | Central | Medium | 7-year; append-only |
| Device identity (mTLS certificates) | Edge + central registry | Medium | Rotated; revocable |
| Secrets / credentials | Central vault | Critical | No secrets on edge except device cert |
| Weather cache | Central + edge | Low | Re-fetchable; 90-day retention |

**Threats:**

| ID | Threat | Asset | Vector | Mitigation | Residual risk |
|---|---|---|---|---|---|
| T01 | Physical theft / tampering of kiosk | Edge data, device | Theft, physical access | LUKS full-disk encryption; tamper-resistant IP5x enclosure; no local admin; remote wipe via command channel; re-provisioning runbook | Low |
| T02 | Unauthorized access to central platform | All data | Credential theft, exposed endpoint | Keycloak OIDC + RBAC; MFA for admin/scientist; WAF; rate limiting; network segmentation | Low |
| T03 | Insider overreach (operator/admin) | Cases, KB, rules | Privileged account misuse | Least privilege; role separation (operator cannot approve); two-person rule for production promotion; 7-year audit log | Low |
| T04 | Prompt injection via farmer input | LLM output, system prompt | Malicious/accidental text | 7-layer defense (§5); red-team CI gate; deterministic rules engine cannot be overridden | Low |
| T05 | Tampered update bundle | Edge device | Supply chain, MITM | Signed bundles (minisign/cosign), SHA-256 content-addressed; edge verifies signature before activation; staged rollout; one-command rollback | Very low |
| T06 | Sync channel interception / spoofing | Case data in transit | Network attacker | mTLS device certificates; TLS 1.3; outbound-only; no inbound ports on device | Very low |
| T07 | Data breach (DB/MinIO compromise) | Farmer PII, media | Exploited vulnerability, misconfig | Encryption at rest; PII minimization; pseudonymity; DPDP 72-h breach notification; incident response (§7) | Low |
| T08 | Media privacy violation (face exposure) | Farmer images | Over-retention, over-access | Faces blurred by default; original only on request + consent; aggregate-only surveillance; physical privacy shutter | Low |
| T09 | Regulatory data staleness (PPQS updates) | Unsafe prescription | Missed gazette update | Versioned regulatory tables; re-verification before each release; quarterly audit; gazette monitoring | Low |
| T10 | LLM hallucination → incorrect advice | Farmer (agronomic harm) | Model error | RAG grounding + evidence-ID; rules gate; scientist gate; zero unapproved prescriptions; groundedness gate; red-team | Low |
| T11 | Availability attack (DDoS) | WhatsApp webhook, PWA | Volumetric attack | WAF; rate limiting; edge offline-first resilience (kiosk keeps serving) | Low |
| T12 | Supply chain (dependencies, model weights) | Platform | Malicious package, license change | Lockfiles; signed model artifacts; license tracking (Gemma ToU / Llama CL); CI vulnerability scanning | Low |
| T13 | WhatsApp / external API abuse | Billing, spam | Template misuse, API abuse | Template approval; rate limiting; billing dashboard; adapter isolates billing | Low |

## 2. Identity & access

**Keycloak RBAC (roles per roadmap §4.1.1):**

| Role (Keycloak) | Authentication | MFA | Access |
|---|---|---|---|
| farmer (pseudonymous) | Case-scoped token (no account) | — | Own case: inputs, corrections, outcomes; opt-in phone → `farmer_ref` |
| operator | Device-scoped credential | — | Device: reset session, check health, replace paper; may not approve/correct |
| scientist | OIDC | Yes (TOTP) | Review queue; approve/correct/escalate; candidate approval; dashboards |
| knowledge-owner | OIDC (scientist) | Yes (TOTP) | Approve production knowledge versions |
| rule-owner | OIDC (scientist + engineer) | Yes (TOTP) | Approve production rule versions |
| release-authority | OIDC (institutional nominee) | Yes (TOTP) | Shadow→canary→production promotion; rollback |
| admin | OIDC | Yes (TOTP) | Users, devices, configuration; no agricultural content |
| auditor | OIDC | Yes (TOTP) | Read-only; full traceability to provenance |

**Farmer pseudonymity:**
- No name is stored. Farmer identity is a pseudonymous `farmer_ref` (opt-in phone/QR), never a name.
- No account needed at kiosk: the session is case-scoped; `farmer_ref` is optional and opt-in.
- WhatsApp: phone → `farmer_ref` → case mapping (pseudonymous).
- Case-scoped tokens for farmer endpoints; OIDC bearer for scientist/admin/auditor; device mTLS for sync.

**Access control details:**
- MFA (TOTP) enforced for all privileged roles (scientist, admin, auditor, owners, release-authority).
- Session policy: short-lived tokens; refresh rotation; idle timeout.
- All access events to the 7-year append-only audit log.
- Quarterly RBAC access review.
- Device identity: each kiosk has a TLS client certificate (mTLS) for sync; device registry in central DB; certificate lifecycle (issue, rotate, revoke).

## 3. Device & artifact security

**Edge (kiosk):**
- LUKS full-disk encryption (1 TB NVMe).
- Ubuntu 24.04 LTS, kiosk mode (auto-start, no desktop escape); dedicated non-admin OS account; ports minimized.
- No inbound ports; outbound-only mTLS to central; remote ops via the central command channel (roadmap §7.5).
- Physical: IP5x dust-resistant, tamper-resistant, serviceable, VESA mount; camera with physical privacy shutter.
- UPS 10–15 min; graceful shutdown → clean state.

**Transport:** TLS 1.3 everywhere (reverse proxy + mTLS for device sync).

**Artifacts (signed updates):**
- All production artifacts (app, models, KB bundles, rules, prompt policy, speech) are content-addressed (SHA-256) + signed (minisign/cosign).
- Edge verifies signature before activation; unsigned/invalid → reject + alert.
- Staged rollout: canary device → fleet; one-command rollback, RTO ≤ 15 min/device.

**OS hardening & patching:**
- CIS benchmark baseline; unattended security updates (central); edge updates via signed app bundles.
- Security patch ≤ 7 days from CVE publication (critical ≤ 48 h).

**Secrets & keys:**
- No secrets on edge except the device certificate + sync key (in the LUKS-protected keystore).
- Central secrets in a vault (SOPS / sealed-secrets); rotation on schedule + on personnel change.
- Device certificate lifecycle (issue, rotate, revoke) in the device registry.

## 4. DPDP Act 2023 + Rules 2025

The Digital Personal Data Protection Act 2023 and the DPDP Rules 2025 govern how
the system collects, uses, retains, and protects farmer personal data. **Full
fiduciary obligations take effect May 2027 — before the trial starts (Jul 2027) — so
the compliance program must be complete before the trial.**

**Verified timeline:**

| Milestone | Date | Impact |
|---|---|---|
| DPDP Act 2023 passed by Parliament | 11 Aug 2023 | In force |
| DPDP Rules notified (G.S.R. 846(E)) | 13 Nov 2025 | Phased compliance begins |
| Phase 1 (immediate): core fiduciary obligations | Nov 2025 | Applies to the system |
| Phase 2: consent manager framework | by Nov 2026 | Plan integration |
| Phase 3: full fiduciary obligations | **May 2027** | **Must be complete before trial** |
| DPDP tribunal / adjudication begins | Jul 2027 | Trial begins same month — fully compliant |

**Obligations & implementation:**

| Obligation | Implementation |
|---|---|
| Notice + verifiable consent at first interaction (Telugu-first) | Consent screen at kiosk session start (`consent_ack`); WhatsApp consent template; web PWA consent; recorded in the case graph |
| Purpose limitation | Data policy; purpose field on all collection; no secondary use without new consent |
| PII minimization | Pseudonymous `farmer_ref`; no name; phone opt-in; faces blurred by default |
| Retention | Roadmap §6.9 schedule; automated retention job (delete/anonymize) |
| Breach → notify DPBI within 72 h | Incident response (§7): SEV1 data breach → DPBI notification within 72 h |
| Grievance redressal within 90 days | Grievance officer (KVK); SLA 90 days; logged |
| No automatic training on farmer conversations | Learning governance; explicit consent for learning use |
| Data mapping / inventory | Data map artifact (Phase 0 data policy) |
| Consent withdrawal | Withdrawal flow (kiosk/WhatsApp/web); delete + 90 days |
| Data principal rights (access/correct/erase) | Self-service via KVK counter + portal; logged |

**Program milestones (M1 → M13):**

| Month | Milestone |
|---|---|
| M1 | DPDP program kickoff (Phase 0): appoint grievance officer, data map, consent design |
| M2 | Consent capture implemented in kiosk MVP (touch/text); sensitive-data classification (D6) |
| M3 | Consent across all channels (WhatsApp template, web PWA); retention automation v1 |
| M4 | Breach-response process + DPBI notification template; tabletop exercise |
| M5 | Media privacy controls (face-blur pipeline) verified |
| M6 | UAT consent flow with farmers (comprehension) |
| M9 | Full DPDP operational review (pre-trial gate) |
| M10 | Trial start — full fiduciary obligations in force (May 2027 deadline met) |
| M13 | Trial-exit DPDP audit; grievance log review |

## 5. LLM safety & prompt injection

The LLM is a language/reasoning assistant, never the authority. Seven layers of defense:

| # | Layer | Control |
|---|---|---|
| 1 | Input sanitization + data/instruction separation | Farmer text is data, never instructions; delimiters; no raw regulatory data as "instructions" (rules engine only) |
| 2 | System-prompt hardening | No secrets in prompt; role constraints; refusal policy; no system-prompt leak |
| 3 | Output schema validation | Pydantic v2 before the rules pipeline; LLM output never free text to farmer for high-risk |
| 4 | Deterministic rules-engine gate | Regulatory/dose/PHI/weather — LLM cannot override |
| 5 | Scientist gate for high-risk | No unapproved prescriptions |
| 6 | Red-team suite in CI | promptfoo, 10 scenarios (roadmap §13.4), blocking; monthly production sample |
| 7 | Monitoring + logging | Injection attempts logged; anomaly detection on output drift; kill switch |

Additional controls: LLM-as-judge bias controls (judge models pinned and versioned;
≥10% weekly human audit of judge outputs); shadow mode before promotion; groundedness
gate (100% evidence-ID retention on prescriptions).

## 6. Media privacy

- **Faces blurred by default** in stored copies (policy decision; open question D2 for confirmation).
- **Original retained only** if a scientist explicitly requests it for diagnosis, **with recorded consent**.
- Retention: 1 year default; 5 years if flagged for diagnosis/learning with consent.
- Media stored in MinIO with case references; edge cache LUKS-encrypted.
- **Surveillance use is aggregate only**, mandal-level minimum granularity, no individual farmer identification in dashboards.
- Physical privacy shutter on the camera (visible control).
- WhatsApp photos: same policy on central storage.
- Audio: retained per retention schedule; used in evaluation only with consent.
- Access: media access logged; scientist access to unblurred originals requires a justification field (audit).

## 7. Incident response

**Severity levels:**

| Severity | Definition | Examples | Response | Notification |
|---|---|---|---|---|
| SEV1 (critical) | Data breach affecting farmer PII/media; unsafe prescription delivered (harm); platform-wide outage | DB compromise, face exposure, harmful advice | Immediate (24×7 during trial) | DPBI within 72 h if personal-data breach; institution same day |
| SEV2 (high) | Safety-gate bypass detected; regulatory violation; central outage > 1 h; kiosk down in service hours | Rule bypass, PPQS miss | ≤ 1 h response | Same-day resolution plan |
| SEV3 (medium) | Single kiosk degraded (printer/GPU); sync backlog > threshold; weather stale > 6 h | Printer failure, GPU OOM | ≤ 4 h in service hours | On-call log |
| SEV4 (low) | Cosmetic; single non-critical bug | UI glitch | Next business day | Log |

**Process:**
1. **Detect** — alerts (safety metrics, rule blocks, L4 escalation, on-call).
2. **Triage** — assign severity.
3. **Contain** — isolate the affected component; kill switch for the LLM if needed.
4. **Resolve** — fix per runbook ([08-operations.md](08-operations.md) §6).
5. **Post-incident review** — within 5 days.
6. **Learning capture** — escalation workflow `LEARNING_CAPTURED`; incident → learning candidate where applicable.
7. **DPBI notification** — within 72 h if a personal-data breach.

**L4 escalation = SEV1/SEV2 path:** immediate + incident process.

**Roles:** incident commander (on-call L2); comms (PO/KVK); DPDP lead for breaches.

## 8. Compliance checklist

| # | Control | Requirement | Implementation | Verified by |
|---|---|---|---|---|
| 1 | Consent capture | DPDP notice + verifiable consent | Kiosk/WhatsApp/web consent flow, recorded | Phase 2 exit + UAT |
| 2 | PII minimization | No name; pseudonymous `farmer_ref` | Schema + test | Phase 1 exit |
| 3 | Faces blurred by default | Media privacy | Blur pipeline + test | Phase 5 exit |
| 4 | Retention automation | Retention schedule | Retention job + audit | Phase 14 |
| 5 | Breach notification | DPBI within 72 h | IR process + template + drill | M4 tabletop |
| 6 | Grievance redressal | 90 days | Grievance officer + log | M1 appointment |
| 7 | MFA for privileged roles | Admin/scientist | Keycloak policy | Phase 1 |
| 8 | Device mTLS | Sync authentication | Certificate lifecycle | Phase 1 |
| 9 | Signed bundles | Artifact integrity | minisign/cosign verification test | Phase 14 |
| 10 | Audit log | 7 years, immutable | Append-only + test | Phase 1 |
| 11 | Regulatory data currency | PPQS re-verification | Pre-release check + quarterly audit | Each release |
| 12 | No auto-training | Learning governance | Promotion-gate test | Phase 11 exit |
| 13 | LLM safety | Prompt-injection defense | Red-team CI gate | Each build |
| 14 | Data map | DPDP inventory | Data policy artifact | Phase 0 |
| 15 | Access review | Quarterly RBAC review | Admin console report | Quarterly |
