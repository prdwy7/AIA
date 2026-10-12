"""Case endpoints (docs/04 §1)."""

from __future__ import annotations

from canonical_schema import CreateCaseRequest, CreateCaseResponse, GetTreeResponse
from fastapi import APIRouter, Request

router = APIRouter(prefix="/v1/cases", tags=["cases"])


@router.post("", response_model=CreateCaseResponse, status_code=201)
def create_case(request: Request, body: CreateCaseRequest) -> CreateCaseResponse:
    """Create a case (channel, location, language, farmer_ref?)."""
    store = request.app.state.store
    case = store.create_case(
        channel=body.channel,
        kiosk_id=body.kiosk_id,
        language=body.language,
        farmer_ref=body.farmer_ref,
        consent_ref=None if body.consent_ack else "missing",
        location=body.location,
    )
    return CreateCaseResponse(
        case_id=case.case_id,
        short_code=case.short_code,
        qr_payload=case.qr_payload,
    )


@router.get("/{case_id}/tree", response_model=GetTreeResponse)
def get_tree(request: Request, case_id: str) -> GetTreeResponse:
    """Retrieve the full Case-to-Solution Tree (append-only)."""
    store = request.app.state.store
    nodes = store.get_tree(case_id)
    return GetTreeResponse(
        nodes=[n.model_dump(mode="json") for n in nodes],
        state=store.case_state(case_id),
    )
