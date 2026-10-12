"""In-memory case store with append-only semantics (dev/test).

The production system of record is PostgreSQL (db/migrations/0002) with
trigger-enforced append-only `case_nodes`. This store mirrors the same
invariants in-process so the API is testable without a database:

- cases are immutable once created (frozen Pydantic models);
- nodes are append-only — the only legal mutation is a status transition
  (`active -> superseded | rejected`) via `CaseNode.transition_status()`;
- voice inputs require an ASR result (enforced by `InputPayload`).
"""

from __future__ import annotations

import secrets
from datetime import UTC, datetime

from canonical_schema import (
    AsrResult,
    Case,
    CaseNode,
    CaseStatus,
    Channel,
    InputPayload,
    Language,
    Modality,
    NodeStatus,
    NodeType,
    VersionTuple,
    new_ulid,
)

_CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


class CaseNotFound(KeyError):
    """Raised when a case_id does not exist."""


class ConsentRequired(ValueError):
    """Raised when a session/case is created without consent (DPDP)."""


def _short_code(prefix: str = "BNV") -> str:
    """Human-readable case code, e.g. "BNV-4F7K2"."""
    return f"{prefix}-" + "".join(secrets.choice(_CROCKFORD) for _ in range(5))


def _now() -> datetime:
    return datetime.now(UTC)


class InMemoryCaseStore:
    """Append-only case graph store (single-process)."""

    def __init__(self, version_tuple: VersionTuple) -> None:
        self._version_tuple = version_tuple
        self._cases: dict[str, Case] = {}
        self._nodes: dict[str, list[CaseNode]] = {}
        self._sessions: dict[str, str] = {}  # session_id -> case_id

    # -- sessions ----------------------------------------------------------

    def create_session(
        self,
        channel: Channel,
        kiosk_id: str | None,
        language: Language,
        consent_ack: bool,
    ) -> tuple[str, Case]:
        """Create a session + its case. Returns (session_id, case)."""
        if not consent_ack:
            raise ConsentRequired("consent_ack is required (DPDP Act 2023)")
        case = self.create_case(
            channel=channel,
            kiosk_id=kiosk_id,
            language=language,
            consent_ref=new_ulid(),
        )
        session_id = new_ulid()
        self._sessions[session_id] = case.case_id
        return session_id, case

    def case_for_session(self, session_id: str) -> Case:
        case_id = self._sessions.get(session_id)
        if case_id is None:
            raise CaseNotFound(session_id)
        return self.get_case(case_id)

    # -- cases -------------------------------------------------------------

    def create_case(
        self,
        channel: Channel,
        kiosk_id: str | None = None,
        language: Language = Language.TE,
        farmer_ref: str | None = None,
        consent_ref: str | None = None,
        location: dict | None = None,
    ) -> Case:
        case = Case(
            short_code=_short_code(),
            qr_payload=f"ai-kiosk://case/{new_ulid()}",
            channel=channel,
            kiosk_id=kiosk_id,
            language=language,
            farmer_ref=farmer_ref,
            consent_ref=consent_ref,
            location=location,
            version_tuple=self._version_tuple,
            created_at=_now(),
        )
        self._cases[case.case_id] = case
        self._nodes[case.case_id] = []
        return case

    def get_case(self, case_id: str) -> Case:
        try:
            return self._cases[case_id]
        except KeyError:
            raise CaseNotFound(case_id) from None

    # -- inputs (append-only) ----------------------------------------------

    def add_input(
        self,
        case_id: str,
        modality: Modality,
        payload: str | None = None,
        media_ref: str | None = None,
        asr: AsrResult | None = None,
        created_by: str = "farmer",
    ) -> CaseNode:
        """Append an immutable Input node. Voice requires `asr`."""
        case = self.get_case(case_id)  # raises CaseNotFound
        if modality == Modality.VOICE and asr is None:
            raise ValueError("voice input requires an asr result")
        node_payload = InputPayload(
            modality=modality,
            raw_ref=media_ref if modality in (Modality.VOICE, Modality.PICTURE) else payload,
            asr=asr,
        )
        node = CaseNode(
            case_id=case_id,
            node_type=NodeType.INPUT,
            payload=node_payload,
            created_at=_now(),
            created_by=created_by,
            source_channel=case.channel,
            source_modality=modality,
            confidence=1.0 if modality == Modality.TOUCH else None,
        )
        self._nodes[case_id].append(node)
        return node

    # -- tree --------------------------------------------------------------

    def get_tree(self, case_id: str) -> list[CaseNode]:
        self.get_case(case_id)  # raises CaseNotFound
        return list(self._nodes[case_id])

    def transition_node_status(
        self, case_id: str, node_id: str, new_status: NodeStatus
    ) -> CaseNode:
        """The only legal node mutation: active -> superseded | rejected."""
        nodes = self._nodes.get(case_id, [])
        for i, node in enumerate(nodes):
            if node.node_id == node_id:
                updated = node.transition_status(new_status)
                nodes[i] = updated
                return updated
        raise CaseNotFound(node_id)

    # -- state -------------------------------------------------------------

    def case_state(self, case_id: str) -> CaseStatus:
        return self.get_case(case_id).status
