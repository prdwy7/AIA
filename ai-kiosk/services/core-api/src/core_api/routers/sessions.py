"""Session endpoints (docs/04 §1)."""

from __future__ import annotations

from canonical_schema import CreateSessionRequest, CreateSessionResponse
from fastapi import APIRouter, Request

router = APIRouter(prefix="/v1", tags=["sessions"])


@router.post("/session", response_model=CreateSessionResponse, status_code=201)
def create_session(request: Request, body: CreateSessionRequest) -> CreateSessionResponse:
    """Create a kiosk session. Consent is mandatory (DPDP)."""
    store = request.app.state.store
    session_id, case = store.create_session(
        channel=body.channel,
        kiosk_id=body.kiosk_id,
        language=body.language,
        consent_ack=body.consent_ack,
    )
    return CreateSessionResponse(
        session_id=session_id,
        case_id=case.case_id,
        short_code=case.short_code,
    )
