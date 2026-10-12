"""Enumerations for the canonical case schema.

Every enum is a `str`-mixin so values serialize cleanly to JSON/SQL.
Source: roadmap §6 (data model) and §4 (state machines, rules, learning).
"""

from __future__ import annotations

from enum import StrEnum


class Channel(StrEnum):
    """Entry channel for a case (roadmap §7, §9.5.2)."""

    KIOSK = "kiosk"
    WHATSAPP = "whatsapp"
    WEB = "web"
    OPERATOR = "operator"


class Modality(StrEnum):
    """Input modality — voice/touch/text/picture are first-class (user requirement)."""

    VOICE = "voice"
    TOUCH = "touch"
    TEXT = "text"
    PICTURE = "picture"
    MIXED = "mixed"
    SYSTEM = "system"


class CaseStatus(StrEnum):
    """Case lifecycle (roadmap §4.2)."""

    OPEN = "open"
    INTERPRETING = "interpreting"
    CLARIFYING = "clarifying"
    DECIDING = "deciding"
    AWAITING_REVIEW = "awaiting_review"
    APPROVED = "approved"
    DELIVERED = "delivered"
    FOLLOWUP = "followup"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"


class NodeType(StrEnum):
    """Case-to-Solution Tree node types (roadmap §6.1)."""

    INPUT = "input"
    INTERPRETATION = "interpretation"
    CORRECTION = "correction"
    OBSERVATION = "observation"
    HYPOTHESIS = "hypothesis"
    QUESTION = "question"
    ANSWER = "answer"
    EVIDENCE = "evidence"
    CONTRADICTION = "contradiction"
    DECISION = "decision"
    INTERVENTION = "intervention"
    OUTCOME = "outcome"
    ESCALATION = "escalation"
    SCIENTIST_FEEDBACK = "scientist_feedback"
    SIMILAR_CASE_REF = "similar_case_ref"


class NodeStatus(StrEnum):
    """Append-only node status. Only `active -> superseded | rejected` transitions
    are allowed; all other UPDATEs are rejected by DB triggers (roadmap §6.1)."""

    ACTIVE = "active"
    SUPERSEDED = "superseded"
    REJECTED = "rejected"


class Intent(StrEnum):
    """Decision intent (roadmap §6.1 decision payload)."""

    INFORMATION = "information"
    DIAGNOSIS = "diagnosis"
    ADVISORY = "advisory"
    PRESCRIPTION = "prescription"


class DecisionStatus(StrEnum):
    DRAFT = "draft"
    APPROVED = "approved"
    CORRECTED = "corrected"
    REJECTED = "rejected"
    LOCKED = "locked"


class InterventionStatus(StrEnum):
    DELIVERED = "delivered"
    PENDING_APPROVAL = "pending_approval"
    BLOCKED = "blocked"


class RuleClass(StrEnum):
    """Rule classes (roadmap §6.5)."""

    REGULATORY = "regulatory"
    CROP_TARGET = "crop_target"
    FORMULATION = "formulation"
    DOSE = "dose"
    METHOD = "method"
    WEATHER_WINDOW = "weather_window"
    PHI_PPE = "phi_ppe"
    ENVIRONMENT = "environment"
    CONFIDENCE_GATE = "confidence_gate"
    CLARIFICATION_POLICY = "clarification_policy"


class RuleAction(StrEnum):
    """Deterministic rule actions (roadmap §6.5)."""

    BLOCK = "BLOCK"
    REVIEW = "REVIEW"
    CONDITION = "CONDITION"
    WARN = "WARN"
    REQUIRE_CONFIRMATION = "REQUIRE_CONFIRMATION"
    ALLOWED = "ALLOWED"


class RuleResult(StrEnum):
    """Per-rule evaluation outcome recorded on the decision node."""

    PASS = "pass"
    BLOCK = "block"
    REVIEW = "review"
    WARN = "warn"
    CONDITION = "condition"
    REQUIRE_CONFIRMATION = "require_confirmation"


class CorrectionType(StrEnum):
    """Decision-delta classification — 10 types (roadmap §4.3.2)."""

    PRODUCT_SELECTION = "PRODUCT_SELECTION"
    DOSAGE = "DOSAGE"
    FORMULATION = "FORMULATION"
    TIMING = "TIMING"
    DIAGNOSIS = "DIAGNOSIS"
    MISSING_CONTEXT = "MISSING_CONTEXT"
    OUTDATED_KNOWLEDGE = "OUTDATED_KNOWLEDGE"
    LOCAL_CONDITION = "LOCAL_CONDITION"
    EXPERT_PREFERENCE = "EXPERT_PREFERENCE"
    EXPLANATION = "EXPLANATION"


class EvidenceStatus(StrEnum):
    """How a correction/feedback is backed (roadmap §4.3.2)."""

    EVIDENCE_BACKED = "EVIDENCE_BACKED"
    LOCALLY_VALIDATED = "LOCALLY_VALIDATED"
    EXPERT_PREFERENCE = "EXPERT_PREFERENCE"


class LearningChannel(StrEnum):
    """Learning channels — case memory, knowledge, rules and training data stay
    separate (source §46)."""

    KNOWLEDGE = "knowledge"
    RULE = "rule"
    TRAINING = "training"
    CASE_MEMORY = "case_memory"
    LANGUAGE = "language"
    NONE = "none"


class DeltaApprovalStatus(StrEnum):
    PENDING = "pending"
    APPROVED_FOR_LEARNING = "approved_for_learning"
    REJECTED = "rejected"


class OutcomeResult(StrEnum):
    """Outcome classes (roadmap §6.1 outcome payload; source §43)."""

    WORKED = "worked"
    PARTIAL = "partial"
    FAILED = "failed"
    WORSENED = "worsened"
    UNKNOWN = "unknown"


class LearningStatus(StrEnum):
    """Whether a failure/outcome learning record has been captured."""

    PENDING = "pending"
    CAPTURED = "captured"
    REJECTED = "rejected"


class FailureClass(StrEnum):
    """Failure classification for failed interventions (source §43.3)."""

    WRONG_DIAGNOSIS = "wrong_diagnosis"
    WRONG_PRODUCT = "wrong_product"
    WRONG_DOSE = "wrong_dose"
    WRONG_TIMING = "wrong_timing"
    WEATHER_INTERFERENCE = "weather_interference"
    NON_COMPLIANCE = "non_compliance"
    RESISTANCE = "resistance"
    PARTIAL_EFFECT = "partial_effect"
    UNKNOWN = "unknown"


class EscalationLevel(StrEnum):
    """Escalation levels (roadmap §4.4)."""

    L1 = "L1"
    L2 = "L2"
    L3 = "L3"
    L4 = "L4"


class EscalationStatus(StrEnum):
    """Escalation workflow (roadmap §6.1)."""

    OPEN = "OPEN"
    ASSIGNED = "ASSIGNED"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED = "RESOLVED"
    LEARNING_CAPTURED = "LEARNING_CAPTURED"


class ObservationType(StrEnum):
    """Image-derived observation types (roadmap §6.1)."""

    LESION = "lesion"
    DISCOLORATION = "discoloration"
    INSECT_PRESENCE = "insect_presence"
    DISTORTION = "distortion"
    WILTING = "wilting"
    OTHER = "other"


class ObservationState(StrEnum):
    """Observation confidence states (roadmap §9.4.4)."""

    OBSERVED = "OBSERVED"
    POSSIBLE = "POSSIBLE"
    UNCERTAIN = "UNCERTAIN"
    CONTRADICTORY = "CONTRADICTORY"
    NOT_VISIBLE = "NOT_VISIBLE"


class HypothesisStatus(StrEnum):
    ACTIVE = "active"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"


class ContradictionResolution(StrEnum):
    CLARIFIED = "clarified"
    RESOLVED_BY_FARMER_ANSWER = "resolved_by_farmer_answer"
    UNRESOLVED = "unresolved"


class AsrEngine(StrEnum):
    """ASR engines (user-specified: Vaani-Whisper primary, SraVaani fast fallback)."""

    VAANI_WHISPER = "vaani-whisper"
    SRAVAANI = "sravaani"
    BHASHINI = "bhashini"


class TtsEngine(StrEnum):
    PIPER = "piper"
    BHASHINI = "bhashini"
    TEXT_ONLY = "text_only"


class PrescriptionStatus(StrEnum):
    DRAFT = "draft"
    APPROVED = "approved"
    LOCKED = "locked"
    PRINTED = "printed"
    VOID = "void"


class CandidateStatus(StrEnum):
    """Learning candidate lifecycle (roadmap §6.6)."""

    DRAFT = "draft"
    IN_VALIDATION = "in_validation"
    EXPERT_REVIEW = "expert_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    RELEASED = "released"


class ArtifactClass(StrEnum):
    """Versioned artifact classes (version tuple, roadmap §4.5)."""

    MODEL = "model"
    KNOWLEDGE = "knowledge"
    RULES = "rules"
    PROMPT_POLICY = "prompt_policy"
    SPEECH = "speech"
    SCHEMA = "schema"


class ArtifactStatus(StrEnum):
    """Artifact deployment status (roadmap §4.5)."""

    CANDIDATE = "candidate"
    SHADOW = "shadow"
    CANARY = "canary"
    PRODUCTION = "production"
    RETIRED = "retired"


class KEntryType(StrEnum):
    """KB entry types (roadmap §6.4)."""

    PEST = "pest"
    DISEASE = "disease"
    CROP_PRACTICE = "crop_practice"
    PRODUCT = "product"
    REGULATION = "regulation"
    WEATHER_RULE = "weather_rule"
    GENERAL = "general"


class KEntryStatus(StrEnum):
    ACTIVE = "active"
    RETIRED = "retired"


class SourceType(StrEnum):
    """Evidence source types (roadmap §4.6.1)."""

    LAW = "law"
    INSTITUTIONAL = "institutional"
    KVC_SA = "kvc_sa"
    WEATHER = "weather"
    RESEARCH = "research"
    LOCAL_VALIDATED = "local_validated"
    SECONDARY = "secondary"


class DeviceStatus(StrEnum):
    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"
    DECOMMISSIONED = "decommissioned"


class SyncEventType(StrEnum):
    """Sync event types (roadmap §6.7)."""

    INPUT = "input"
    INTERPRETATION = "interpretation"
    CORRECTION = "correction"
    DECISION = "decision"
    OUTCOME = "outcome"
    ESCALATION = "escalation"
    TELEMETRY = "telemetry"
    PRINT_JOB = "print_job"


class AckStatus(StrEnum):
    PENDING = "pending"
    ACKED = "acked"
    FAILED = "failed"


class RegulatoryStatus(StrEnum):
    """PPQS/CIB&RC product status (roadmap §6.5 regulatory_products)."""

    BANNED = "banned"
    REFUSED = "refused"
    RESTRICTED = "restricted"
    PERMITTED = "permitted"


class WeatherStatus(StrEnum):
    """Weather snapshot freshness (roadmap §9.3)."""

    FRESH = "FRESH"
    STALE = "STALE"
    UNKNOWN = "UNKNOWN"


class SprayWindow(StrEnum):
    """Spray window derived from weather (STALE weather -> UNKNOWN, roadmap §9.3)."""

    OPEN = "OPEN"
    CLOSED = "CLOSED"
    UNKNOWN = "UNKNOWN"


class CreatedByKind(StrEnum):
    """Who created a node (roadmap §6.1)."""

    FARMER = "farmer"
    SYSTEM = "system"
    SCIENTIST = "scientist"
    OPERATOR = "operator"


class ScientistAction(StrEnum):
    """Scientist feedback actions (roadmap §6.1)."""

    APPROVE = "approve"
    CORRECT = "correct"
    REJECT = "reject"
    ESCALATE = "escalate"


class RetrievalMethod(StrEnum):
    SQL = "sql"
    KEYWORD = "keyword"
    VECTOR = "vector"
    HYBRID = "hybrid"


class Environment(StrEnum):
    EDGE = "edge"
    CENTRAL = "central"


class MediaKind(StrEnum):
    AUDIO = "audio"
    IMAGE = "image"
    DOCUMENT = "document"


class FaceBlurStatus(StrEnum):
    """Face-blur state on stored media (roadmap §14.6)."""

    BLURRED = "blurred"
    ORIGINAL_ON_REQUEST = "original_on_request"
    NOT_APPLICABLE = "not_applicable"


class Language(StrEnum):
    TE = "te"
    EN = "en"
    TE_EN = "te-en"
