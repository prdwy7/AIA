**AI-ENABLED AGRICULTURAL ADVISORY KIOSK**

**CONTINUOUS LEARNING & EXPERT FEEDBACK ARCHITECTURE — v2.0**

Scientist-supervised trials • Context-aware correction capture • Controlled learning • Offline-first • Telugu voice

*Detailed technical design based on the supplied KVK Banavasi proposal and the subsequent requirement that scientist corrections become structured learning signals.*

| Document scopeNo pricing is included. This document defines the problem, target architecture, scientist trial workflow, automatic context capture, learning pipeline, safety controls, technology stack, data model, APIs, validation and scale-up. |
| :---- |

The supplied proposal describes an AI-enabled voice-assisted information and pesticide-prescription printable kiosk for KVK Banavasi. It explicitly covers voice assistance, crop/pest/dose recommendations, scientist validation, printed prescriptions, weather integration, offline operation and pest surveillance. fileciteturn0file0L12-L18

# **1\. Executive Summary**

The platform should be implemented as a governed agricultural decision-support system, not as a free-form chatbot. The AI interprets farmer language, retrieves evidence and explains decisions. Deterministic rules control regulatory, agronomic and safety constraints. A scientist remains the final authority during the supervised trial.

| Core new requirementWhen a scientist corrects an AI recommendation, the scientist should only need to provide the changed output fields. The application automatically captures the complete background state that produced the original recommendation, the original AI output, the scientist correction, evidence, rules, weather, model and knowledge versions, and turns that record into a controlled learning signal. |
| :---- |

The correction must not immediately modify the production model. Instead, the system classifies the correction and routes it to knowledge learning, rule learning, training-data generation or simple case memory. New artifacts are validated and approved before release.

FARMER CASE  
    ↓  
AI DECISION  
    ↓  
SCIENTIST CORRECTION  
    ↓  
FULL CONTEXT SNAPSHOT \+ DECISION DELTA  
    ↓  
CORRECTION CLASSIFICATION  
    ↓  
Knowledge candidate / Rule candidate / Training example  
    ↓  
Validation \+ regression \+ scientist approval  
    ↓  
Versioned production release

# **2\. Requirements from the Supplied Proposal**

The proposal identifies diverse literacy, language and technology exposure and the need for timely crop protection, weather, diagnostics and pesticide-use guidance. fileciteturn0file0L86-L95

| Requirement | Original proposal direction | v1 design |
| :---- | :---- | :---- |
| Voice | Telugu/English verbal questions and audio answers | Telugu-first ASR/TTS, confidence handling and confirmation of critical entities. fileciteturn0file0L103-L110 |
| Scientific recommendations | Crop/pest/dose-specific recommendations validated by KVK | Hybrid retrieval \+ deterministic rules \+ scientist workflow. |
| Prescription | Diagnosis, pesticide/dose, method, interval, PHI, PPE and safety | Structured prescription object, then print/QR. fileciteturn0file0L121-L129 |
| Weather | Local weather to determine spray timing | Weather snapshot \+ explicit spray-window rules. fileciteturn0file0L226-L228 |
| Offline | Offline operation with periodic cloud updates | Local AI/knowledge/rules \+ encrypted sync queue. fileciteturn0file0L235-L250 |
| Surveillance | Log crop, pest and location | Structured events and privacy-aware analytics. fileciteturn0file0L239-L241 |
| Expert validation | Field trials and expert reviews | Three-month supervised correction loop. fileciteturn0file0L394-L401 |
| Pilot refinement | Farmer feedback, scientist validation and tuning | Formal learning sandbox and versioned releases. fileciteturn0file0L447-L465 |

# **3\. Problem Definition**

| ID | Problem | Required solution |
| :---- | :---- | :---- |
| P1 | Farmer input is ambiguous or incomplete | Structured case builder and clarification questions |
| P2 | LLM can generate plausible but incorrect recommendations | LLM cannot be final prescription authority |
| P3 | A scientist correction may be small but its context is large | Automatic full-context snapshot |
| P4 | Agricultural guidance changes | Versioned knowledge with effective dates |
| P5 | Regulatory restrictions cannot safely live only in model weights | Deterministic regulatory/policy layer |
| P6 | Weather affects application suitability | Weather-aware rule engine |
| P7 | Expert preference is not necessarily universal truth | Correction classification and evidence status |
| P8 | Immediate self-training can destabilize production | Learning sandbox and approval gate |
| P9 | Rural connectivity can be intermittent | Local-first execution and synchronization |
| P10 | Future kiosks need one consistent architecture | Canonical schemas and version registry |

## **3.1 Output classes**

| Class | Example | Control |
| :---- | :---- | :---- |
| Information | Explain a pest lifecycle | Grounded evidence |
| Diagnosis support | Possible pest/disease candidates | Evidence \+ confidence \+ clarification |
| Advisory | Management options | Knowledge \+ rules |
| Prescription | Specific product/formulation/dose/timing | Full safety pipeline \+ approval |

# **4\. Target Architecture**

                         FARMER  
                           │  
            ┌──────────────┼──────────────┐  
            ▼              ▼              ▼  
          VOICE          TOUCH          IMAGE\*  
            └──────────────┼──────────────┘  
                           ▼  
                  EXPERIENCE LAYER  
                           ▼  
              SPEECH / NORMALIZATION  
                           ▼  
                     CASE BUILDER  
                           ▼  
          ┌────────────────┼────────────────┐  
          ▼                ▼                ▼  
      KNOWLEDGE         WEATHER          HISTORY  
       RETRIEVAL         CONTEXT          (minimal)  
          └────────────────┼────────────────┘  
                           ▼  
                 DETERMINISTIC RULES  
                           ▼  
                      LOCAL LLM  
                           ▼  
                 SAFETY / CONFIDENCE  
                           ▼  
                    SCIENTIST GATE  
                           ▼  
                 APPROVED RESPONSE  
                           ▼  
              VOICE \+ SCREEN \+ PRINT  
                           ▼  
                       QR / ID  
                           ▼  
                    EVENT / AUDIT  
                           ▼  
                CONTINUOUS LEARNING  
                           ▼  
              VALIDATION SANDBOX  
                           ▼  
                  APPROVED RELEASE  
                           ▼  
                 EDGE SYNCHRONIZATION

\* Optional future computer-vision module.

## **4.1 Core principle**

| LLM is not the authorityLLM \= language and reasoning assistant. Knowledge base \= evidence. Rules engine \= safety gate. Scientist \= authority. Prescription service \= controlled output. Learning engine \= controlled improvement. |
| :---- |

# **5\. Recommended Technology Stack**

| Layer | Recommended v1 | Why |
| :---- | :---- | :---- |
| Kiosk UI | Flutter or controlled PWA | Touch-first kiosk experience |
| Backend | Python \+ FastAPI \+ Pydantic | Strong fit for AI/data workflows and typed APIs |
| Database | PostgreSQL | Transactional system of record |
| Vector retrieval | pgvector | Vector search inside PostgreSQL |
| Local LLM | Ollama or llama.cpp | Local/offline inference |
| Speech | BHASHINI \+ AI4Bharat/local model evaluation | Indian-language support and offline path |
| Rules | Python policy package | Deterministic and testable |
| Weather | IMD/approved source integration | Official Indian weather ecosystem |
| Identity | Keycloak/OIDC | Scientist/admin authentication and authorization |
| Messaging | MQTT at edge; Kafka later if scale requires | Rural device messaging \+ future event streaming |
| Observability | OpenTelemetry | Traces, metrics and logs |
| Packaging | Docker/Podman | Repeatable deployment |
| Analytics | PostgreSQL \+ dashboard layer | Enough for pilot and early district scale |

pgvector supports exact and approximate nearest-neighbor search within PostgreSQL, including HNSW and IVFFlat, making a PostgreSQL-first hybrid retrieval architecture practical. citeturn0search1turn0search3

OpenTelemetry is a vendor-neutral observability framework for telemetry such as traces, metrics and logs. citeturn0search0turn0search4

Keycloak exposes OpenID Connect endpoints for application authentication and authorization. citeturn0search6

# **6\. Three-Month Scientist-Supervised Trial**

The supplied proposal already includes pilot testing, farmer feedback, scientist validation and technical refinement. fileciteturn0file0L342-L346

| Stage | Operating mode | Learning objective |
| :---- | :---- | :---- |
| Pre-trial | All knowledge/rules/model versions frozen for baseline | Create benchmark cases and safety tests |
| Month 1 | Scientist reviews every prescription and uncertain case | Capture broad correction dataset |
| Month 2 | Continue full oversight; analyze recurring correction patterns | Create candidate knowledge/rule changes |
| Month 3 | Confidence-based routing only if institution approves | Validate whether corrections are decreasing and identify remaining failure modes |
| Post-trial | Governed production | Continue monitoring and periodic expert review |

| ImportantThree months is a trial duration, not an automatic authorization for unsupervised prescriptions. Any reduction in oversight should be based on measured performance and institutional approval. |
| :---- |

# **7\. Scientist Correction UX**

The scientist should correct only what is wrong. The application should automatically attach everything else.

AI RECOMMENDATION  
┌──────────────────────────────────────┐  
│ Crop: Cotton                          │  
│ Stage: Flowering                      │  
│ Problem: \[identified problem\]         │  
│ Product: A                            │  
│ Dose: 2 ml/L                          │  
└──────────────────────────────────────┘

\[ APPROVE \] \[ CORRECT \] \[ ESCALATE \]

If CORRECT:  
  Product: \[optional\]  
  Dose:    \[optional\]  
  Method:  \[optional\]  
  Timing:  \[optional\]  
  Note:    \[optional\]

APPLICATION AUTOMATICALLY ATTACHES:  
crop \+ stage \+ symptoms \+ location  
weather \+ soil \+ previous treatment  
retrieved evidence \+ rules fired  
model \+ knowledge \+ rule versions  
original output \+ confidence  
scientist output \+ timestamp

                  ↓  
            LEARNING RECORD

| Scientist action | System behavior |
| :---- | :---- |
| Approve | Store positive expert-validation example |
| Change chemical | Preserve all other fields and create product-selection delta |
| Change dosage | Preserve context and create dosage delta |
| Change chemical \+ dose | Create one multi-field decision delta |
| Reject | Mark AI output invalid while preserving original evidence |
| Escalate | Create human-review case; no automatic learning release |
| Add note | Store qualitative evidence; do not automatically turn it into a rule |

# **8\. Automatic Context Snapshot**

Every reviewed decision should be reproducible. The scientist should not need to remember or re-enter the background information.

| Category | Captured information |
| :---- | :---- |
| Case | case\_id, session\_id, kiosk\_id, timestamp |
| Language | language, transcript, ASR confidence |
| Farmer input | original query and normalized query |
| Crop | crop, variety, stage |
| Problem | symptoms, candidate diagnosis, severity |
| Location | state, district, mandal, village, coordinates if permitted |
| Weather | temperature, humidity, rainfall, wind, forecast timestamp/source |
| Soil | soil-test values if available |
| Previous management | previous interventions and response if known |
| Knowledge | source IDs, versions, retrieval scores |
| Rules | rules evaluated, passed, blocked |
| AI | model ID/version, structured output, confidence |
| Scientist | correction, reason, approval |
| Output | final prescription, print ID, QR ID |
| Audit | timestamps, edits, synchronization state |

# **9\. Decision Delta Model**

The fundamental learning object is the difference between what the AI decided and what the scientist decided under the same contextual state.

FULL CONTEXT  
     │  
     ├──────────► AI DECISION  
     │  
     └──────────► SCIENTIST DECISION  
                       │  
AI DECISION ───────────┤  
                       ▼  
                 DECISION DELTA  
                       │  
             changed field(s)  
             old value(s)  
             new value(s)  
             reason  
             evidence  
             correction type  
             approval status

| Correction type | Meaning | Possible learning target |
| :---- | :---- | :---- |
| PRODUCT\_SELECTION | AI selected wrong product | Knowledge/rule \+ training example |
| DOSAGE | Dose changed | Dose rule \+ training example |
| FORMULATION | Formulation changed | Product/formulation rule |
| TIMING | Application timing changed | Weather/stage rule |
| DIAGNOSIS | Problem identification changed | Diagnostic knowledge/model data |
| MISSING\_CONTEXT | Critical information was absent | Clarification policy |
| OUTDATED\_KNOWLEDGE | Source changed | Knowledge version |
| LOCAL\_CONDITION | Locally validated exception | Region-specific candidate rule |
| EXPERT\_PREFERENCE | Scientist preference without authoritative evidence | Preference record only |
| EXPLANATION | Decision correct but explanation poor | Language-model evaluation data |

# **10\. Continuous Learning Architecture**

PRODUCTION CASE  
      ↓  
SCIENTIST FEEDBACK  
      ↓  
FEEDBACK INGESTION  
      ↓  
CORRECTION CLASSIFIER  
      │  
      ├── Knowledge candidate  
      ├── Rule candidate  
      ├── Training example  
      └── Case memory  
      ↓  
LEARNING SANDBOX  
      │  
      ├── Data quality checks  
      ├── Regression tests  
      ├── Safety tests  
      ├── Counterexample tests  
      └── Holdout evaluation  
      ↓  
SCIENTIST / AUTHORIZED REVIEW  
      │  
   ┌──┴──┐  
   ▼     ▼  
REJECT  APPROVE  
          ↓  
   VERSIONED ARTIFACT  
          ↓  
   SHADOW / CANARY  
          ↓  
      PRODUCTION

| No uncontrolled self-modificationA scientist correction is a learning signal, not an instruction to rewrite production model weights immediately. |
| :---- |

# **11\. Three Learning Channels**

## **11.1 Knowledge learning**

Correction  
   ↓  
Source/evidence verification  
   ↓  
Knowledge candidate  
   ↓  
Expert approval  
   ↓  
KB version N+1  
   ↓  
Re-index / re-embed  
   ↓  
Edge synchronization

## **11.2 Rule learning**

Repeated validated corrections  
   ↓  
Pattern discovery  
   ↓  
Candidate rule  
   ↓  
Counterexample search  
   ↓  
Scientist review  
   ↓  
Rule version N+1  
   ↓  
Regression suite  
   ↓  
Production

## **11.3 Model learning**

Approved feedback records  
   ↓  
Dataset curation  
   ↓  
Label validation  
   ↓  
Train / validation / test  
   ↓  
Candidate model  
   ↓  
Safety \+ regression evaluation  
   ↓  
Expert evaluation  
   ↓  
Shadow mode  
   ↓  
Canary  
   ↓  
Production

# **12\. Canonical Data Model**

## **12.1 Case object**

Case  
 ├─ case\_id  
 ├─ session\_id  
 ├─ kiosk\_id  
 ├─ timestamp  
 ├─ language  
 ├─ farmer\_ref (optional)  
 ├─ location  
 ├─ crop  
 ├─ variety  
 ├─ stage  
 ├─ symptoms\[\]  
 ├─ severity  
 ├─ weather\_snapshot  
 ├─ soil\_snapshot  
 ├─ previous\_interventions\[\]  
 └─ media\_refs\[\]

## **12.2 Decision object**

Decision  
 ├─ decision\_id  
 ├─ case\_id  
 ├─ intent  
 ├─ diagnoses\[\]  
 ├─ selected\_diagnosis  
 ├─ interventions\[\]  
 ├─ dose  
 ├─ formulation  
 ├─ method  
 ├─ timing  
 ├─ PHI  
 ├─ PPE  
 ├─ warnings\[\]  
 ├─ evidence\_refs\[\]  
 ├─ rules\_evaluated\[\]  
 ├─ confidence  
 ├─ model\_version  
 ├─ knowledge\_version  
 └─ rule\_version

## **12.3 Correction object**

Correction  
 ├─ correction\_id  
 ├─ decision\_id  
 ├─ scientist\_id  
 ├─ timestamp  
 ├─ changed\_fields\[\]  
 ├─ original\_values  
 ├─ corrected\_values  
 ├─ correction\_type  
 ├─ reason  
 ├─ evidence\_refs\[\]  
 ├─ approval\_status  
 ├─ learning\_channel  
 └─ released\_version

# **13\. Example Learning Record**

Illustrative schema only. Actual pesticide/product/dose values must come from authorized agricultural sources.

{  
  "case\_id": "CASE-00018372",  
  "context": {  
    "crop": "cotton",  
    "stage": "flowering",  
    "problem": "P001",  
    "location": "Kurnool",  
    "weather\_snapshot": "WX-9912"  
  },  
  "ai\_decision": {  
    "product": "CHEM-A",  
    "dose": "2 ml/L"  
  },  
  "scientist\_correction": {  
    "product": "CHEM-B",  
    "dose": "1.5 ml/L"  
  },  
  "correction": {  
    "type": "PRODUCT\_AND\_DOSAGE",  
    "reason": "validated local recommendation"  
  },  
  "versions": {  
    "model": "MODEL-0.9.1",  
    "knowledge": "KB-1.7.3",  
    "rules": "RULE-1.4.2"  
  },  
  "status": "APPROVED\_FOR\_LEARNING"  
}

Never overwrite the original AI decision. The original and corrected states are both required for learning and auditability.

# **14\. RAG and Evidence Pipeline**

A simple vector search over PDFs is not sufficient for prescription decisions. Structured filters should be applied before semantic retrieval.

FARMER QUESTION  
      ↓  
Intent \+ entity extraction  
      ↓  
Structured filters  
 crop / stage / geography / validity  
      ↓  
Hybrid retrieval  
 ├─ SQL/exact  
 ├─ keyword  
 └─ vector  
      ↓  
Evidence ranking  
 authority \+ freshness \+ relevance  
      ↓  
Rules engine  
      ↓  
LLM explanation  
      ↓  
Source IDs retained

pgvector supports vector similarity search directly in PostgreSQL and offers exact and approximate nearest-neighbor approaches. citeturn0search1

# **15\. Regulatory and Safety Layer**

PPQS publishes official lists of pesticides banned, refused registration or restricted in use. The cited PPQS publication is updated 31 March 2024\. citeturn0search104

PROPOSED INTERVENTION  
       ↓  
REGULATORY CHECK  
 ├─ prohibited → BLOCK  
 ├─ restricted → REVIEW / CONDITIONS  
 └─ permitted → continue  
       ↓  
CROP / TARGET CHECK  
       ↓  
FORMULATION CHECK  
       ↓  
DOSE CHECK  
       ↓  
APPLICATION METHOD  
       ↓  
WEATHER WINDOW  
       ↓  
PHI / PPE / ENVIRONMENT  
       ↓  
CONFIDENCE  
       ↓  
SCIENTIST GATE

The current official regulatory dataset must be treated as a controlled, versioned dependency. Model memory must never be the regulatory source of truth.

# **16\. Telugu Voice Pipeline**

The source proposal explicitly targets Telugu voice interaction. fileciteturn0file0L103-L110

FARMER SPEECH  
      ↓  
Voice activity / noise processing  
      ↓  
Telugu ASR  
      ↓  
Transcript \+ confidence  
      ↓  
Agricultural vocabulary normalization  
      ↓  
Entity extraction  
      ↓  
Confirm critical terms when uncertain  
      ↓  
Case object  
      ↓  
AI \+ rules  
      ↓  
Telugu response  
      ↓  
TTS  
      ↓  
Speaker

BHASHINI and AI4Bharat are relevant technologies to benchmark for Indian-language speech. Final selection should be based on measured Kurnool agricultural vocabulary accuracy, latency, offline capability and licensing/operational constraints.

# **17\. Weather Integration**

The proposal calls for rainfall, temperature, humidity and windspeed to support spray timing and unsafe-condition warnings. fileciteturn0file0L226-L228

APPROVED WEATHER SOURCE  
      ↓  
Validate timestamp \+ location  
      ↓  
Normalize units  
      ↓  
Local cache  
      ↓  
Weather rules  
      ↓  
GREEN / CAUTION / BLOCKED / UNKNOWN  
      ↓  
Advisory context

The application should show when weather information is stale or unavailable. It should not silently infer current conditions from old data.

# **18\. Offline-First Operation**

LOCAL KIOSK  
 ├─ UI  
 ├─ ASR/TTS  
 ├─ Local LLM  
 ├─ Knowledge cache  
 ├─ Rule engine  
 ├─ Local DB  
 ├─ Printer  
 ├─ Event queue  
 └─ Sync agent  
        │  
        │ encrypted sync  
        ▼  
CENTRAL PLATFORM  
 ├─ Knowledge publishing  
 ├─ Scientist portal  
 ├─ Model registry  
 ├─ Weather ingestion  
 ├─ Analytics  
 └─ Device management

| Function | Offline behavior |
| :---- | :---- |
| Approved information | Available from cached knowledge |
| Basic AI explanation | Available through local model |
| Rules | Available locally |
| Printing | Available |
| Live weather | Unavailable/stale and explicitly marked |
| New knowledge | Queued until synchronization |
| Scientist review | Queued or blocked according to policy |
| Analytics | Queued locally and uploaded later |

# **19\. Learning Governance**

| Artifact | AI may propose? | AI may publish? | Approval |
| :---- | :---- | :---- | :---- |
| Training example | Yes | No | Quality/learning policy |
| Knowledge candidate | Yes | No | Authorized agricultural expert |
| Rule candidate | Yes | No | Authorized scientist |
| Model candidate | Yes | No | Technical \+ agricultural review |
| Production knowledge | No | No | Knowledge owner |
| Production rule | No | No | Rule owner |
| Production model | No | No | Release authority |
| Prescription | Draft only | No | Scientist / institutional policy |

## **19.1 Expert preference vs expert correction**

The system must distinguish an evidence-backed correction from a personal preference. For example, a scientist may prefer one product based on local experience. That should not automatically become a universal rule. A correction should become a production knowledge/rule change only when its authority and evidence status meet the defined governance criteria.

# **20\. Pattern Discovery**

After enough validated corrections accumulate, the platform can search for recurring decision deltas.

VALIDATED CORRECTIONS  
      ↓  
Group by crop / stage / problem / region / season  
      ↓  
Compare AI vs scientist choices  
      ↓  
Frequency \+ consistency analysis  
      ↓  
Counterexample search  
      ↓  
Candidate pattern  
      ↓  
Scientist review  
      ↓  
Rule / knowledge candidate

Example candidate pattern:

IF crop \= X  
AND stage \= Y  
AND problem \= Z  
AND region \= R  
AND validated conditions \= C

THEN prioritize intervention B

STATUS \= CANDIDATE  
NOT PRODUCTION

# **21\. Model Training Strategy**

Do not begin by fine-tuning the model. First stabilize the structured knowledge, rules and expert feedback system.

| Step | Activity |
| :---- | :---- |
| 1 | Collect approved cases and corrections |
| 2 | Clean transcripts and remove duplicates |
| 3 | Classify correction types |
| 4 | Preserve complete context |
| 5 | Create time/geography-aware train/validation/test splits |
| 6 | Benchmark current production model |
| 7 | Train candidate model only for error classes appropriate for model learning |
| 8 | Run safety and regression tests |
| 9 | Run expert evaluation |
| 10 | Shadow-test candidate model |
| 11 | Canary deployment |
| 12 | Version and release |
| 13 | Retain previous production version for rollback |

## **21.1 Shadow mode**

A candidate model receives live cases but its answer is hidden from farmers. Its output is compared against the production model and scientist decisions. This provides a safer test of whether learning actually improves performance.

# **22\. MLOps / KnowledgeOps**

SOURCE DATA  
   ↓  
VERSION CONTROL  
   ↓  
VALIDATION  
   ↓  
DATASET BUILD  
   ↓  
MODEL / RULE / KB CANDIDATE  
   ↓  
AUTOMATED TESTS  
   ↓  
SAFETY TESTS  
   ↓  
EXPERT REVIEW  
   ↓  
REGISTRY  
   ↓  
SHADOW  
   ↓  
CANARY  
   ↓  
PRODUCTION  
   ↓  
MONITOR  
   ↓  
ROLLBACK / REVISE

## **22.1 Version tuple**

SYSTEM\_VERSION \=  
    MODEL\_VERSION  
  \+ KNOWLEDGE\_VERSION  
  \+ RULE\_VERSION  
  \+ PROMPT\_POLICY\_VERSION  
  \+ SPEECH\_VERSION  
  \+ DATA\_SCHEMA\_VERSION

Every prescription should record the version tuple that produced it.

# **23\. API Contract**

| Endpoint | Purpose |
| :---- | :---- |
| POST /v1/session | Create kiosk session |
| POST /v1/speech/transcribe | Speech recognition |
| POST /v1/intent/parse | Typed intent extraction |
| POST /v1/cases | Create/update case |
| POST /v1/retrieval/search | Hybrid evidence retrieval |
| POST /v1/rules/evaluate | Deterministic validation |
| POST /v1/advisory/draft | Grounded advisory draft |
| POST /v1/review | Approve/correct/escalate |
| POST /v1/corrections | Persist decision delta |
| POST /v1/prescriptions | Create locked prescription |
| GET /v1/prescriptions/{id} | Verify prescription |
| POST /v1/print | Print approved artifact |
| POST /v1/sync/push | Upload queued events |
| GET /v1/sync/manifest | Get current versions |
| POST /v1/learning/candidates | Create candidate learning artifact |
| GET /v1/learning/candidates | Scientist review queue |
| POST /v1/releases | Approve release |
| GET /v1/device/health | Device health |

Use typed request/response schemas. LLM output must be schema-validated before entering the rules or prescription pipeline.

# **24\. Security and Privacy**

* Run the kiosk under a dedicated non-administrative account.  
* Disable unnecessary services, ports and external interfaces.  
* Encrypt sensitive local data.  
* Use TLS for synchronization.  
* Use device identity/certificates where appropriate.  
* Use role-based access for scientist, operator, administrator and auditor.  
* Keep security logs separate from farmer analytics.  
* Use signed application, model and knowledge updates.  
* Maintain backup and recovery procedures.  
* Minimize personally identifiable information.  
* Do not automatically use farmer conversations for model training.

Keycloak supports OpenID Connect-based authentication and authorization. citeturn0search6

The Digital Personal Data Protection Act, 2023 should be considered when defining data collection, notice/consent, purpose, retention and access controls; final compliance should be reviewed by the implementing institution.

# **25\. Observability**

| Metric | Purpose |
| :---- | :---- |
| ASR confidence | Speech quality |
| Entity correction rate | Vocabulary problems |
| Retrieval recall | Knowledge retrieval gaps |
| Scientist correction rate | AI decision quality |
| Correction type distribution | Failure-mode analysis |
| Rule-block count | Safety/regulatory monitoring |
| Escalation rate | Uncertainty monitoring |
| Prescription latency | Service performance |
| Print success | Hardware/service reliability |
| Sync backlog | Offline health |
| Knowledge age | Staleness detection |
| Model drift | Long-term performance |
| Candidate rule count | Learning pipeline workload |

OpenTelemetry provides a common instrumentation layer for traces, metrics and logs. citeturn0search0

# **26\. Testing Framework**

## **26.1 Functional**

* Every supported crop has representative positive and negative cases.  
* Every intervention rule has allowed and blocked cases.  
* Critical numeric fields are tested independently of the LLM.  
* Offline operation is tested with network disabled.  
* Printer failures do not duplicate prescriptions.  
* Synchronization is idempotent.  
* Rollback restores the previous production version.

## **26.2 AI evaluation**

| Metric | Definition |
| :---- | :---- |
| ASR entity accuracy | Correct crop/pest/product/location recognition |
| Intent accuracy | Correct request classification |
| Retrieval recall | Authoritative evidence retrieved |
| Groundedness | Generated claims supported by evidence |
| Correction rate | Scientist changes per reviewed case |
| Correction severity | Distribution of low/high-risk corrections |
| Rule compliance | No model output bypasses blocking rules |
| Clarification quality | Critical missing data requested |
| Telugu comprehension | Target-user understanding |
| Latency | Question-to-answer and question-to-print |

## **26.3 Red-team scenarios**

* Ask for a prohibited/restricted product.  
* Use an ambiguous local product name.  
* Provide an incorrect crop stage.  
* Ask the AI to ignore scientist rules.  
* Create conflicting evidence sources.  
* Return stale weather.  
* Disconnect network during approval/printing.  
* Restart during synchronization.  
* Attempt prompt injection through farmer text.  
* Provide a scientist correction that conflicts with authoritative guidance.

# **27\. Knowledge Governance**

AUTHORITATIVE SOURCE  
       ↓  
INGESTION  
       ↓  
NORMALIZATION  
       ↓  
EXPERT REVIEW  
       ↓  
TEST CASES  
       ↓  
VERSION  
       ↓  
PUBLISH  
       ↓  
EDGE BUNDLE  
       ↓  
MONITOR  
       ↓  
RETIRE / REPLACE

1. Applicable law and official regulatory notices.  
2. Current official institutional recommendations.  
3. KVK/ICAR/SAU-approved technical material.  
4. Official weather/agromet information.  
5. Peer-reviewed or institutional research.  
6. Locally observed information validated by authorized experts.  
7. Secondary sources only after explicit review.

The source proposal explicitly calls for collaboration with agricultural universities, research institutions and government bodies and for expert review and field validation. fileciteturn0file0L394-L401

# **28\. Kiosk Hardware and Edge Services**

| Subsystem | Recommended design |
| :---- | :---- |
| Compute | Industrial mini-PC/edge computer sized for local AI |
| Display | Large, bright touchscreen |
| Microphone | Directional microphone array |
| Speaker | High-clarity speaker |
| Printer | Thermal printer with error status |
| Connectivity | Ethernet \+ Wi-Fi \+ cellular fallback |
| Power | UPS with graceful shutdown |
| Enclosure | Dust/tamper-resistant and serviceable |
| Camera | Optional future module |
| Maintenance | Secured service access |

kiosk-ui  
  │  
  ├── speech-service  
  ├── llm-service  
  ├── knowledge-service  
  ├── rules-service  
  ├── prescription-service  
  ├── printer-service  
  ├── sync-agent  
  └── device-agent  
        │  
     local database  
        │  
     local telemetry

# **29\. End-to-End Data Pipeline**

FARMER  
  ↓  
Voice / Touch / Image  
  ↓  
ASR \+ Input Normalizer  
  ↓  
Intent \+ Entity Parser  
  ↓  
CASE OBJECT  
  ↓  
Hybrid Retrieval  
  ├─ Structured records  
  ├─ Approved documents  
  └─ Semantic evidence  
  ↓  
Context Enrichment  
  ├─ Weather  
  ├─ Crop calendar  
  ├─ Location  
  └─ Season  
  ↓  
Deterministic Rules  
  ↓  
Local LLM  
  ↓  
Safety / Confidence  
  ↓  
Scientist Approval when required  
  ↓  
LOCKED OUTPUT  
  ↓  
Voice \+ Screen \+ Print \+ QR  
  ↓  
AUDIT EVENT  
  ↓  
Scientist Correction  
  ↓  
Decision Delta  
  ↓  
Learning Candidate  
  ↓  
Validation Sandbox  
  ↓  
Expert Approval  
  ↓  
Versioned Release  
  ↓  
Edge Sync

# **30\. Analytics and Pest Surveillance**

The proposal expects structured crop-pest-location information to support pest incidence trends, hotspot identification and early warning. fileciteturn0file0L310-L317

| Dashboard | Indicators |
| :---- | :---- |
| Service operations | queries/day, response time, print success, escalation |
| Crop intelligence | crop/stage distribution |
| Pest surveillance | incidence by geography/time |
| AI quality | correction rate and correction types |
| Safety | blocked interventions and regulatory conflicts |
| Knowledge | unanswered questions and stale records |
| Language | ASR confidence and corrected entities |
| Learning | accepted corrections, candidate rules, model versions |
| Device | uptime, errors, temperature, sync backlog |

Anomaly detection should create a review signal, not an autonomous declaration of an outbreak or an autonomous pesticide response.

# **31\. Scale-Up Architecture**

LEVEL 1: SINGLE KIOSK  
        ↓  
LEVEL 2: KVK / MULTI-KIOSK  
        ↓  
LEVEL 3: RSK / RBK / FPO / MANDAL  
        ↓  
LEVEL 4: DISTRICT  
        ↓  
LEVEL 5: STATE

COMMON CONTRACT:  
case schema  
knowledge version  
rule version  
model version  
device identity  
sync protocol  
audit trail

The source proposal anticipates expansion to villages, FPO headquarters, cluster-level RBKs and mandal-level extension centers. fileciteturn0file0L359-L369

# **32\. Implementation Roadmap**

| Phase | Deliverable | Exit criterion |
| :---- | :---- | :---- |
| 0 Governance | Authority, safety, data and source policy | Approved governance specification |
| 1 Data model | Case/decision/correction/prescription schemas | Complete workflow representable structurally |
| 2 Knowledge | Versioned agricultural knowledge base | Source traceability |
| 3 Rules | Agronomic/regulatory/weather rules | Unsafe cases blocked |
| 4 Kiosk MVP | Touch \+ print \+ basic voice | Information workflow works end-to-end |
| 5 AI/RAG | Local LLM \+ hybrid retrieval | Grounded structured answers |
| 6 Scientist portal | Approve/correct/escalate | Correction takes minimal input |
| 7 Learning engine | Context \+ delta \+ candidate generation | Every correction reproducible |
| 8 Offline | Local execution \+ sync | Core service works without network |
| 9 Three-month trial | Controlled supervised operation | Validated dataset and metrics |
| 10 MLOps | Sandbox \+ regression \+ registry | New versions safely testable |
| 11 Scale | Device/knowledge/analytics management | Repeatable multi-kiosk deployment |

# **33\. Trial Acceptance Criteria**

| Area | Acceptance test |
| :---- | :---- |
| Voice | Critical crop/product/stage terms are confirmed when uncertain |
| Grounding | Prescription drafts retain evidence IDs |
| Rules | Blocked interventions cannot reach printable state |
| Correction UX | Scientist changes only the fields that are wrong |
| Context capture | Original input, AI output, evidence, rules and versions stored |
| Learning | Correction is classified and routed |
| Safety | Candidate model cannot publish directly |
| Offline | Cached information and printing work without network |
| Recovery | Interrupted sync resumes without duplication |
| Audit | Prescription traces to model/KB/rule versions |
| Rollback | Previous production version can be restored |

# **34\. Research References**

* **BHASHINI:** https://bhashini.gov.in/ — Indian-language language services  
* **AI4Bharat:** https://ai4bharat.iitm.ac.in/ — Indian-language AI and speech research  
* **IMD:** https://api.imd.gov.in/public/api\_reference.html — Official weather API reference  
* **ICAR:** https://www.icar.gov.in/ — Agricultural research and extension ecosystem  
* **PPQS:** https://ppqs.gov.in/sites/default/files/list\_of\_pesticides\_which\_are\_banned\_refused\_registration\_and\_restricted\_in\_use\_0.pdf — Official pesticide restriction publication cited above  
* **Ollama:** https://ollama.com/ — Local model runtime  
* **pgvector:** https://github.com/pgvector/pgvector — PostgreSQL vector search  
* **OpenTelemetry:** https://opentelemetry.io/docs/ — Observability framework  
* **Keycloak:** https://www.keycloak.org/ — Identity and access management  
* **MeitY:** https://www.meity.gov.in/ — Digital personal-data protection resources

Technology availability, APIs, licenses and regulatory data can change. Re-check official sources immediately before production implementation.



# **36. v2 — MULTIMODAL CASE-TO-SOLUTION TREE**

## **36.1 Core architectural change**

The v1 architecture already establishes a structured case, evidence retrieval, deterministic rules, scientist review, correction deltas and controlled learning. v2 extends this into a **Case-to-Solution Tree (CST)**.

The system must not assume that the first interpretation of a farmer's message is correct. Every interaction creates or updates a case graph containing:

```text
FARMER INPUT
   │
   ├── text
   ├── voice
   ├── photo / video
   └── mixed input
          │
          ▼
INPUT INTERPRETATION
   │
   ├── transcript
   ├── entities
   ├── visual observations
   ├── stated problem
   └── missing / uncertain information
          │
          ▼
CROSS-CORRECTION
   │
   ├── "Did you mean this?"
   ├── entity confirmation
   ├── image interpretation confirmation
   └── farmer correction
          │
          ▼
CASE TREE
   │
   ├── Hypothesis A
   ├── Hypothesis B
   ├── Hypothesis C
   │
   ├── supporting evidence
   ├── contradictory evidence
   ├── missing evidence
   └── confidence / uncertainty
          │
          ▼
VERIFICATION QUESTIONS
          │
          ▼
EVIDENCE + RULES + SIMILAR CASES
          │
          ▼
CANDIDATE SOLUTIONS
          │
          ▼
SAFETY / REGULATORY / AGRONOMIC CHECKS
          │
          ▼
CONFIRMATION GATE
          │
          ▼
ACTION / ADVISORY / PRESCRIPTION
          │
          ▼
OUTCOME FOLLOW-UP
   │
   ├── worked
   ├── partially worked
   ├── did not work
   ├── worsened
   └── unknown
          │
          ├──────────────► CLOSE CASE
          │
          └──────────────► ESCALATE / NEW BRANCH
```

The tree is persistent. A correction must update the interpretation branch without deleting the original input or the original AI interpretation.

## **36.2 Why a tree instead of a single answer**

Agricultural cases are often ambiguous. A farmer may describe a symptom using a local term, an ASR system may mishear a crop or pest name, and an image may support several possible diagnoses.

Therefore the system should maintain:

- the original farmer statement;
- the system's first interpretation;
- corrected farmer interpretation;
- image-derived observations;
- competing hypotheses;
- evidence supporting each hypothesis;
- evidence against each hypothesis;
- questions asked;
- answers received;
- actions taken;
- expected outcome;
- actual outcome;
- scientist interventions;
- escalation history.

This creates a reproducible path from **input → evidence → decision → outcome**, rather than storing only the final answer.

---

# **37. INPUT CORRECTION AND CROSS-VERIFICATION**

## **37.1 AI must be able to say "I may have understood this incorrectly"**

The normalization layer must produce both a normalized interpretation and an uncertainty record.

Example:

```text
Farmer voice:
"నా పత్తిలో ఆకులు ముడుచుకుంటున్నాయి"

System interpretation:
Crop = cotton
Symptom = leaf curling
Confidence = 0.86

Potential ambiguity:
Could refer to:
  A. leaf curling
  B. leaf distortion
  C. damage associated with a sucking pest

System:
"I understood that the cotton leaves are curling.
Is that correct?"
```

The system must not silently replace the farmer's words with the normalized interpretation.

## **37.2 Cross-correction object**

```text
InterpretationCorrection
 ├─ correction_id
 ├─ case_id
 ├─ input_id
 ├─ original_transcript
 ├─ original_entities
 ├─ original_interpretation
 ├─ corrected_interpretation
 ├─ corrected_by
 │    ├─ farmer
 │    ├─ scientist
 │    └─ system-confirmed
 ├─ correction_reason
 ├─ confidence_before
 ├─ confidence_after
 ├─ evidence_refs[]
 └─ timestamp
```

The original interpretation remains immutable.

## **37.3 Contradiction detector**

Every new piece of information should be checked against the existing case tree.

Examples:

```text
Existing:
Crop = cotton

New:
Farmer says "this is chilli"

→ CONTRADICTION
→ Ask clarification
→ Do not continue to prescription

Existing:
Problem = fungal disease

New:
Photo evidence suggests insect feeding

→ CONFLICTING EVIDENCE
→ Create competing hypotheses
→ Ask targeted verification questions
```

The system should prefer **clarification over forced certainty**.

---

# **38. IMAGE-FIRST AND MULTIMODAL CASE BUILDING**

## **38.1 Photo is evidence, not automatic diagnosis**

When a farmer sends a photo, the system should first evaluate:

1. Is the image readable?
2. Is the crop/plant visible?
3. Is the affected area visible?
4. Is the image too dark, blurred or distant?
5. Is the symptom localized or widespread?
6. Is more than one plant/leaf/fruit visible?
7. Are there contextual clues?
8. Is a second image required?

Only after image quality and relevance checks should visual analysis contribute to the case tree.

## **38.2 Image workflow**

```text
PHOTO
 ↓
QUALITY CHECK
 ├─ usable
 └─ unusable → request another photo
 ↓
VISUAL OBSERVATIONS
 ├─ lesion
 ├─ discoloration
 ├─ insect-like presence
 ├─ distortion
 ├─ wilting
 └─ other structured observations
 ↓
CANDIDATE HYPOTHESES
 ↓
COMPARE WITH TEXT / VOICE
 ↓
CONFLICT?
 ├─ yes → clarification branch
 └─ no → evidence accumulation
 ↓
RETRIEVAL + RULES
 ↓
ADVISORY / ESCALATION
```

## **38.3 Multiple photos**

The case should support a media set rather than a single image:

```text
media_refs[]
 ├─ whole plant
 ├─ affected leaf
 ├─ stem
 ├─ fruit / flower
 ├─ pest close-up
 └─ field-level context
```

The system should be able to explicitly request the missing view.

Example:

> "Please send one close photo of the affected leaf and one photo showing the whole plant."

## **38.4 Image uncertainty**

The model must never convert a weak visual signal into a high-confidence diagnosis merely because an image exists.

Image output should use structured states such as:

- OBSERVED
- POSSIBLE
- UNCERTAIN
- CONTRADICTORY
- NOT_VISIBLE

---

# **39. WHATSAPP, KIOSK, WEB AND FUTURE CHANNELS**

The channel must not determine the intelligence of the system.

All channels should be adapters into the same canonical case service:

```text
                 ┌── KIOSK
                 ├── WHATSAPP
                 ├── WEB
                 ├── MOBILE
                 ├── CALL-CENTRE / OPERATOR
                 └── FUTURE CHANNEL
                        │
                        ▼
                 CHANNEL ADAPTER
                        │
                        ▼
                CANONICAL CASE API
                        │
                        ▼
              CASE-TO-SOLUTION TREE
```

## **39.1 WhatsApp**

A WhatsApp case may contain:

```text
Text message
Voice note
Photo
Multiple photos
Follow-up text
Scientist reply
Outcome report
```

All messages should map to one `case_id`.

A farmer can therefore start with:

```text
Voice note
  ↓
case created
  ↓
system asks clarification
  ↓
farmer sends photo
  ↓
same case updated
  ↓
system asks another question
  ↓
solution confirmed
```

The farmer must not have to repeat the complete problem every time.

## **39.2 Case continuity**

Use a durable case identifier:

```text
CASE-2026-00018372
```

Expose a simple QR / short code where appropriate so that:

- kiosk → WhatsApp can continue the case;
- WhatsApp → scientist can continue the case;
- printed output → follow-up can reopen the case;
- field worker → scientist can retrieve the complete history.

---

# **40. FIRST-MESSAGE SOLUTION VERIFICATION**

A critical v2 rule:

> **An apparently obvious solution is still a hypothesis until the required verification gates are satisfied.**

If the first message appears to contain enough information, the system should not automatically skip verification.

### Low-risk information

The system may answer directly when the request is informational and the evidence is unambiguous.

### Diagnosis support

The system should perform at least a minimal cross-check:

```text
Initial hypothesis
 ↓
Known symptom match
 ↓
Alternative hypothesis check
 ↓
One or more targeted questions
 ↓
Confirm / revise
```

### High-risk intervention / prescription

The system should require:

```text
Case completeness
+
Evidence support
+
Contradiction check
+
Regulatory check
+
Agronomic rule check
+
Weather check where relevant
+
Similar-case / historical evidence check where available
+
Required scientist approval
```

The "similar case" mechanism must not blindly copy a previous solution. It is evidence for comparison, and differences in crop, stage, geography, season, symptoms and prior treatment must be visible.

---

# **41. SIMILAR-CASE REASONING**

Introduce a `CaseSimilarityService`.

```text
CURRENT CASE
    ↓
retrieve similar validated cases
    ↓
compare:
  crop
  variety
  stage
  geography
  season
  symptom pattern
  image observations
  weather
  previous intervention
  outcome
    ↓
similarity + differences
    ↓
supporting / conflicting evidence
```

The system should store not only successful cases but also failed cases.

A failed case is valuable because it can prevent the same recommendation from being repeated under similar conditions.

---

# **42. SCIENTIST MULTIMODAL FEEDBACK**

Scientists should be able to provide feedback through:

- text;
- voice;
- image;
- annotated image;
- structured correction;
- approval;
- rejection;
- escalation.

Example:

```text
SCIENTIST VOICE:
"The diagnosis is not correct. This looks more like X under these field
conditions. Use the attached image as the reference."

        ↓

Scientist ASR
        ↓
Structured correction
        ↓
Reference image attached
        ↓
Automatic context snapshot
        ↓
Decision delta
        ↓
Evidence / authority classification
        ↓
Learning candidate
```

The scientist should not need to manually fill the complete context.

The system automatically attaches:

- farmer input;
- transcript;
- image(s);
- normalized entities;
- case tree;
- hypotheses;
- retrieved sources;
- rules;
- weather;
- model versions;
- original AI decision;
- previous corrections;
- outcome history.

This extends the existing v1 principle that the scientist should correct only what is wrong while the application captures the background automatically. fileciteturn0file0L169-L210

---

# **43. OUTCOME-BASED LEARNING AND FAILED-SOLUTION ESCALATION**

A major v2 addition is a **closed-loop outcome layer**.

The system must not treat "advice delivered" as "problem solved".

```text
ADVICE / PRESCRIPTION
        ↓
EXPECTED OBSERVATION
        ↓
FOLLOW-UP DATE / WINDOW
        ↓
FARMER RESPONSE
 ├─ worked
 ├─ partly worked
 ├─ no improvement
 ├─ worsened
 └─ cannot determine
        ↓
OUTCOME VALIDATION
        ↓
CASE UPDATE
        ↓
LEARNING / ESCALATION
```

## **43.1 Follow-up**

The system should generate an expected follow-up point based on the approved advisory protocol, not on an arbitrary fixed interval.

Channels:

- WhatsApp message;
- kiosk return visit;
- SMS where supported;
- extension worker;
- scientist portal.

## **43.2 Failed solution protocol**

If the farmer reports that the intervention did not work:

```text
FAILURE REPORTED
      ↓
STOP AUTOMATIC REPETITION
      ↓
REASSESS CASE
      ↓
REQUEST NEW EVIDENCE
 ├─ new photo
 ├─ new symptom description
 ├─ treatment details
 ├─ timing
 └─ environmental conditions
      ↓
COMPARE ORIGINAL VS CURRENT CASE
      ↓
CHECK ALTERNATIVE HYPOTHESES
      ↓
ESCALATE IF:
 ├─ high-risk case
 ├─ worsening condition
 ├─ repeated failure
 ├─ contradictory evidence
 ├─ uncertain diagnosis
 ├─ safety concern
 └─ no validated alternative
```

The system should never respond to failure by automatically recommending another intervention simply because the first intervention failed.

## **43.3 Failure learning record**

```text
Outcome
 ├─ outcome_id
 ├─ case_id
 ├─ intervention_id
 ├─ expected_result
 ├─ observed_result
 ├─ farmer_report
 ├─ supporting_media[]
 ├─ timing
 ├─ environmental_context
 ├─ verified_by
 ├─ failure_class
 ├─ escalation_id
 └─ learning_status
```

---

# **44. ESCALATION ENGINE**

Introduce an explicit `EscalationEngine`.

### Escalation levels

```text
LEVEL 0
Normal automated information

LEVEL 1
Clarification required

LEVEL 2
Scientist review required

LEVEL 3
Urgent human intervention / field visit according to institutional policy

LEVEL 4
Safety / regulatory incident
```

Escalation should be triggered by evidence and policy, not merely by low LLM confidence.

Examples:

- repeated contradictory farmer information;
- image cannot distinguish important alternatives;
- treatment failed;
- disease/pest severity increasing;
- suspected regulatory issue;
- unusual or novel symptom;
- possible harmful recommendation;
- scientist disagreement;
- missing critical information.

Every escalation receives an ID and status:

```text
OPEN → ASSIGNED → INVESTIGATING → RESOLVED → LEARNING_CAPTURED
```

---

# **45. CASE GRAPH DATA MODEL**

Extend the v1 `Case` object into a graph-oriented structure:

```text
Case
 ├─ case_id
 ├─ channel
 ├─ farmer_ref
 ├─ inputs[]
 │    ├─ text
 │    ├─ audio
 │    ├─ image
 │    └─ metadata
 ├─ interpretations[]
 ├─ corrections[]
 ├─ observations[]
 ├─ hypotheses[]
 ├─ questions[]
 ├─ answers[]
 ├─ evidence[]
 ├─ contradictions[]
 ├─ decisions[]
 ├─ interventions[]
 ├─ outcomes[]
 ├─ escalations[]
 ├─ scientist_feedback[]
 ├─ similar_cases[]
 └─ version_history[]
```

Each node should have:

```text
node_id
parent_node_id
created_at
created_by
source
confidence
evidence_refs[]
status
```

This allows the system to answer:

> "Why did the system reach this recommendation?"

and:

> "What changed after the farmer corrected the AI?"

and:

> "Why was this case escalated?"

---

# **46. KNOWLEDGE BASE VS CASE MEMORY VS MODEL TRAINING**

The v1 design correctly separates learning channels. v2 should make the distinction even stronger.

| Artifact | Purpose | Automatically generated? | Production automatically changed? |
|---|---|---:|---:|
| Case memory | Remember what happened in a case | Yes | N/A |
| Outcome record | Capture whether advice worked | Yes | No |
| Training example | Teach a future model | Candidate | No |
| Knowledge candidate | Proposed evidence update | Candidate | No |
| Rule candidate | Proposed deterministic rule | Candidate | No |
| Similar-case index | Retrieve comparable validated cases | Yes | Controlled index update |
| Production KB | Authoritative knowledge | No | No |
| Production rules | Safety/agronomic constraints | No | No |
| Production model | Language/reasoning capability | Candidate | No |

**Important:** "save all corrected data" should mean **save it all with provenance**, not "put every correction directly into model weights."

The v1 document already establishes this controlled-learning principle: corrections become learning signals, while production changes require validation and approval. fileciteturn0file0L14-L37

---

# **47. NEW LEARNING LOOP: INPUT → DECISION → OUTCOME**

The complete v2 learning loop is:

```text
INPUT
  ↓
INTERPRETATION
  ↓
FARMER CORRECTION
  ↓
CASE TREE
  ↓
EVIDENCE
  ↓
DECISION
  ↓
SCIENTIST VALIDATION
  ↓
ACTION
  ↓
OUTCOME
  ↓
SUCCESS / FAILURE / UNCERTAIN
  ↓
REASSESSMENT
  ↓
SCIENTIST FEEDBACK
  ↓
LEARNING CANDIDATE
  ↓
VALIDATION
  ↓
RELEASE
  ↓
MONITOR
```

This is stronger than training only on scientist corrections because it captures **real-world outcome evidence**.

---

# **48. FEEDBACK PROVENANCE**

Every learning signal should answer:

```text
Who provided it?
What did they observe?
When?
Through which channel?
What evidence did they provide?
What did the AI originally say?
What was corrected?
Was it independently verified?
Did the farmer outcome support the correction?
Was it approved for learning?
Which production version used it?
```

This makes the knowledge base auditable.

---

# **49. HUMAN HANDOFF DESIGN**

The farmer should never experience escalation as a dead end.

Instead:

```text
AI:
"I need an agricultural expert to review this case."

CASE ID:
CASE-2026-00018372

STATUS:
Scientist review requested

WHAT THE FARMER CAN DO:
• Send another photo
• Send a voice explanation
• Wait for expert response
• Visit the nearest supported center
```

The scientist receives a compact case packet:

```text
CASE SUMMARY
 ├─ farmer statement
 ├─ media
 ├─ interpretation
 ├─ contradictions
 ├─ hypotheses
 ├─ evidence
 ├─ previous treatments
 ├─ weather
 ├─ AI recommendation
 └─ reason for escalation
```

---

# **50. ADDITIONAL IMPROVEMENTS RECOMMENDED**

## **50.1 Evidence ledger**

Maintain a machine-readable evidence ledger:

```text
CLAIM → SOURCE → VERSION → DATE → AUTHORITY → CONFIDENCE
```

Every high-impact recommendation should be traceable to its evidence.

## **50.2 Reason-for-question engine**

Questions should be generated because they resolve a decision branch.

Bad:

> "Can you provide more information?"

Better:

> "Are the insects visible on the underside of the leaf?"

The UI can show:

```text
Question purpose:
Distinguishes hypothesis A from hypothesis B.
```

## **50.3 Active information gathering**

The system should choose the next question that is expected to reduce uncertainty the most, subject to farmer effort and safety constraints.

```text
Possible questions
       ↓
Estimate information value
       ↓
Choose smallest useful question
       ↓
Update case tree
```

## **50.4 Do-not-repeat memory**

The system should remember within the case:

- questions already answered;
- images already received;
- treatments already attempted;
- failed interventions;
- corrections already made.

This avoids frustrating repeated questioning.

## **50.5 Farmer-friendly explanation**

Do not expose internal probabilities as the main interface.

Instead:

```text
What I understood
What I am checking
Why I am asking
What you should do now
When to check again
When to contact an expert
```

## **50.6 Local terminology dictionary**

Build a governed agricultural lexicon:

```text
local farmer term
      ↓
possible normalized terms
      ↓
crop/geography context
      ↓
confirmation
      ↓
validated mapping
```

Farmer vocabulary corrections should become language-learning candidates, not silently overwrite standard terminology.

## **50.7 Outcome quality dashboard**

Add:

- first-contact resolution rate;
- clarification rate;
- scientist correction rate;
- failed-advice rate;
- repeat-failure rate;
- escalation rate;
- time-to-expert-response;
- outcome verification rate;
- unresolved case rate;
- channel-wise performance;
- crop-wise performance;
- geography-wise performance;
- image-quality failure rate;
- ASR correction rate.

These are operational/quality indicators, not automatic claims about agronomic effectiveness.

---

# **51. REVISED END-TO-END ARCHITECTURE**

```text
                 KIOSK
                   │
WHATSAPP ──────────┤
                   ├── WEB / MOBILE
                   │
                   └── OPERATOR
                         │
                         ▼
                 CHANNEL ADAPTERS
                         │
                         ▼
                 INPUT ORCHESTRATOR
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
       TEXT/ASR       IMAGE AI       METADATA
          └──────────────┼──────────────┘
                         ▼
                 NORMALIZATION
                         │
                         ▼
                 CROSS-CORRECTION
                         │
                         ▼
             CASE-TO-SOLUTION TREE
                         │
        ┌────────────────┼─────────────────┐
        ▼                ▼                 ▼
   HYPOTHESES         QUESTIONS       CONTRADICTIONS
        │                │                 │
        └────────────────┼─────────────────┘
                         ▼
              EVIDENCE / SIMILAR CASES
                         │
                         ▼
                RULES + SAFETY
                         │
                         ▼
                    AI DRAFT
                         │
                         ▼
                 CONFIRMATION GATE
                         │
               ┌─────────┴─────────┐
               ▼                   ▼
           SAFE/APPROVED        REVIEW
               │                   │
               ▼                   ▼
             ACTION            SCIENTIST
               │                   │
               └─────────┬─────────┘
                         ▼
                    FOLLOW-UP
                         │
                         ▼
                      OUTCOME
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
            WORKED     FAILED    UNCERTAIN
              │          │          │
              ▼          └────┬─────┘
             CLOSE            ▼
                         REASSESS
                            │
                            ▼
                         ESCALATE
                            │
                            ▼
                    EXPERT FEEDBACK
                            │
                            ▼
                    LEARNING SANDBOX
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
          KNOWLEDGE       RULES       TRAINING DATA
              └─────────────┼─────────────┘
                            ▼
                     VALIDATION
                            │
                            ▼
                     VERSIONED RELEASE
                            │
                            ▼
                         EDGE SYNC
```

---

# **52. REVISED API ADDITIONS**

Add to the v1 API:

| Endpoint | Purpose |
|---|---|
| `POST /v1/cases/{id}/inputs` | Add text/audio/image input |
| `POST /v1/cases/{id}/interpretations` | Store system interpretation |
| `POST /v1/cases/{id}/corrections` | Farmer/scientist correction |
| `POST /v1/cases/{id}/questions` | Generate/store targeted question |
| `POST /v1/cases/{id}/answers` | Store answer and update tree |
| `GET /v1/cases/{id}/tree` | Retrieve case-to-solution tree |
| `POST /v1/cases/{id}/similar-cases` | Retrieve comparable validated cases |
| `POST /v1/cases/{id}/outcomes` | Record intervention outcome |
| `POST /v1/cases/{id}/escalate` | Create escalation |
| `GET /v1/escalations` | Scientist escalation queue |
| `POST /v1/scientist/feedback` | Voice/text/image/structured feedback |
| `POST /v1/media/analyze` | Image/media evidence extraction |
| `POST /v1/followups` | Schedule outcome follow-up |
| `GET /v1/learning/provenance/{id}` | Trace learning signal to source case |

The existing v1 review, correction, learning and release APIs remain and should be extended rather than duplicated. fileciteturn0file0L718-L741

---

# **53. REVISED IMPLEMENTATION ROADMAP**

| Phase | New/expanded deliverable | Exit criterion |
|---|---|---|
| 0 | Governance, safety, escalation policy | Approved governance |
| 1 | Canonical multimodal case schema | Text/voice/image represented identically |
| 2 | Channel adapters | Kiosk + web + WhatsApp enter same case service |
| 3 | Case-to-Solution Tree | Every case has hypotheses/evidence/questions/decisions |
| 4 | Cross-correction | Farmer can correct transcript/entity/visual interpretation |
| 5 | Image evidence pipeline | Quality checks + structured observations |
| 6 | Verification engine | First-message solutions still pass required checks |
| 7 | Similar-case service | Validated cases retrieved with differences visible |
| 8 | Scientist multimodal feedback | Voice/text/image feedback creates structured deltas |
| 9 | Outcome/follow-up engine | Advice can be marked worked/failed/uncertain |
| 10 | Escalation engine | Failed/uncertain/high-risk cases reach humans |
| 11 | Learning sandbox | Corrections + outcomes become governed candidates |
| 12 | Offline media synchronization | Images/audio queue and sync safely |
| 13 | Three-month supervised trial | Baseline + outcome dataset established |
| 14 | MLOps / KnowledgeOps | Candidates testable, versioned and rollbackable |
| 15 | Multi-channel scale | Same intelligence across kiosk/WhatsApp/web |

---

# **54. REVISED ACCEPTANCE CRITERIA**

### Input understanding

- Farmer can correct a transcript or normalized interpretation.
- Original input and corrected interpretation are both retained.
- Images can create structured observations without forcing a diagnosis.
- Multiple images can belong to one case.
- Voice, text and image can be mixed within the same case.

### Reasoning

- The system maintains multiple hypotheses where evidence is ambiguous.
- Contradictory evidence creates a clarification branch.
- Questions have a decision purpose.
- An apparently obvious first-message solution still passes required verification.

### Safety

- High-risk outputs cannot bypass required review.
- Failed interventions do not automatically trigger another intervention.
- Safety/regulatory contradictions create an escalation.
- Production rules remain deterministic and governed.

### Scientist workflow

- Scientist can approve/correct/escalate.
- Scientist can use voice, text and image feedback.
- Context is automatically attached.
- Corrections are classified into appropriate learning channels.

### Outcome loop

- Every applicable intervention can have a follow-up.
- Outcome can be worked/partial/failed/worsened/unknown.
- Failed cases trigger reassessment and, where required, escalation.
- Failed cases are retained as negative evidence for future similarity checks.

### Learning

- Every correction and outcome has provenance.
- Case memory, knowledge, rules and training data remain separate.
- No automatic production model retraining occurs.
- Candidate changes pass validation, expert approval and versioning.

### Channels

- Kiosk, WhatsApp and online channels use the same case schema.
- A case can move between channels without losing context.
- Offline media is queued and synchronized safely.

---

# **55. FINAL v2 DESIGN PRINCIPLE**

The system should evolve from:

```text
QUESTION → ANSWER
```

to:

```text
INPUT
→ UNDERSTAND
→ CROSS-CHECK
→ BUILD HYPOTHESES
→ ASK THE MOST USEFUL QUESTION
→ COLLECT EVIDENCE
→ COMPARE SIMILAR VALIDATED CASES
→ APPLY RULES
→ VERIFY
→ SOLVE
→ FOLLOW UP
→ MEASURE OUTCOME
→ ESCALATE IF NEEDED
→ LEARN FROM CORRECTIONS AND OUTCOMES
→ VALIDATE
→ IMPROVE THE SYSTEM
```

The most important design principle is:

> **The system should not merely learn what scientists corrected. It should learn from the entire lifecycle of a case: what the farmer meant, what the system misunderstood, what evidence was available, what was decided, what the scientist corrected, what was tried, what happened afterward, and why the case succeeded, failed or required escalation.**

This preserves the v1 principle of controlled learning while adding the missing **closed-loop, multimodal, outcome-aware intelligence layer**. The original architecture already provides the foundation for context snapshots, decision deltas, controlled learning and scientist governance; v2 turns those mechanisms into a unified case lifecycle. fileciteturn0file0L212-L304



# **35\. Final Recommendation**

| Reference architectureFarmer → Telugu voice/touch → structured case → hybrid evidence retrieval → deterministic agricultural/regulatory/weather rules → local LLM explanation → safety/confidence gate → scientist approval → locked prescription → print/QR → audit → expert correction → automatic context snapshot \+ decision delta → knowledge/rule/model candidate → validation sandbox → scientist approval → versioned release → controlled edge synchronization. |
| :---- |

## **The central design decision**

The application should learn from scientists, but it should not blindly rewrite itself. The scientist supplies the correction. The application supplies the context automatically. The learning engine determines whether the correction belongs in knowledge, rules, training data or case memory. Validation determines whether that learning is safe enough to become a new production version.

## **Why this is stronger than simple retraining**

* Every correction remains traceable to the exact agricultural context.  
* Repeated expert corrections can become explicit, auditable rules.  
* Authoritative knowledge can be updated without retraining the LLM.  
* Model training can focus on genuine reasoning/language errors.  
* One-off expert preferences do not automatically become universal rules.  
* Every production change can be tested and rolled back.  
* The same feedback loop can improve voice understanding, retrieval, diagnosis support, explanation and prescription routing.

| Bottom lineThe three-month trial is not merely a test of the kiosk. It becomes a controlled expert-learning program that builds a high-quality, context-rich agricultural intelligence dataset while keeping scientists in control of production changes. |
| :---- |

No pricing or financial estimates are included in this v1 document.

Prepared: September 2026

**v2.0 enhancement:** Multimodal Case-to-Solution Tree • Cross-correction • Image evidence • WhatsApp/web/kiosk continuity • Outcome tracking • Failed-solution escalation • Multimodal scientist feedback