"""Input endpoints — all four modalities (docs/04 §1)."""

from __future__ import annotations

from canonical_schema import AddInputRequest, AddInputResponse, AsrResult, Modality
from fastapi import APIRouter, Request

router = APIRouter(prefix="/v1/cases/{case_id}", tags=["inputs"])


@router.post("/inputs", response_model=AddInputResponse, status_code=201)
def add_input(
    request: Request, case_id: str, body: AddInputRequest
) -> AddInputResponse:
    """Add a typed input (voice | touch | text | picture).

    Voice inputs require `asr_result` (schema-enforced). Touch inputs carry
    confidence 1.0. Mixed modalities within one case are always allowed.
    """
    store = request.app.state.store
    asr = AsrResult.model_validate(body.asr_result) if body.asr_result else None
    node = store.add_input(
        case_id=case_id,
        modality=body.modality,
        payload=body.payload,
        media_ref=body.media_ref,
        asr=asr,
    )
    quality = None
    if body.modality == Modality.PICTURE and node.payload.quality is not None:
        quality = node.payload.quality.model_dump()
    return AddInputResponse(
        input_node_id=node.node_id,
        quality=quality,
        next_state=store.case_state(case_id),
    )
