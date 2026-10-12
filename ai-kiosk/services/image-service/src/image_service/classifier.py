"""ViT disease/pest classifier (CLASS-0.1.0) with a diagnosis guard.

Why a dedicated classifier (docs/05 §3): WACV 2026 HARVEST-Vision shows open
VLMs achieve only ~39–65% on fine-grained crop disease classification vs
~93% for prompted proprietary models — a domain classifier is required for
reliable disease/pest ID.

**Diagnosis guard (invariant):** a weak visual signal is never converted into
a high-confidence diagnosis merely because an image exists. If the top
probability is below `min_confidence`, or the top-2 margin is below
`min_margin`, the result is `UNCERTAIN` — the case proceeds to the
clarification/hypothesis branch instead.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable


@dataclass(frozen=True)
class Classification:
    class_name: str
    probability: float


@dataclass(frozen=True)
class GuardedClassification:
    """Classifier output after the diagnosis guard."""

    state: str  # "CLASSIFIED" | "UNCERTAIN"
    top: Classification | None = None
    runner_up: Classification | None = None
    margin: float | None = None
    all: list[Classification] = field(default_factory=list)
    reason: str | None = None


@runtime_checkable
class DiseaseClassifier(Protocol):
    def available(self) -> bool: ...

    def classify(self, image_bytes: bytes) -> list[Classification]: ...


class VitClassifier:
    """ViT-B/16 fine-tuned on the KVK dataset (ONNX in production).

    Lazy import of onnxruntime/torch so the service runs without them.
    """

    def __init__(self, model_path: str | None = None) -> None:
        self._model_path = model_path
        self._session = None  # lazy

    def available(self) -> bool:
        if not self._model_path:
            return False
        try:
            import onnxruntime  # noqa: F401

            return True
        except ImportError:
            return False

    def classify(self, image_bytes: bytes) -> list[Classification]:
        if not self.available():
            raise RuntimeError("ViT classifier not configured (model_path + onnxruntime)")
        # Production: preprocess (resize 224, normalize) → ONNX session →
        # softmax over the KVK class set → top-k. Kept as a seam here.
        raise RuntimeError("ViT inference not wired — install the KVK model bundle")


class MockClassifier:
    """Test double with canned class probabilities."""

    def __init__(self, classes: list[Classification] | None = None, available: bool = True) -> None:
        self._classes = classes or []
        self._available = available

    def available(self) -> bool:
        return self._available

    def classify(self, image_bytes: bytes) -> list[Classification]:
        return list(self._classes)


def classify_with_guard(
    image_bytes: bytes,
    classifier: DiseaseClassifier,
    min_confidence: float = 0.60,
    min_margin: float = 0.15,
) -> GuardedClassification:
    """Run the classifier and apply the diagnosis guard."""
    classes = sorted(classifier.classify(image_bytes), key=lambda c: c.probability, reverse=True)
    if not classes:
        return GuardedClassification(state="UNCERTAIN", reason="no classes returned")
    top = classes[0]
    runner_up = classes[1] if len(classes) > 1 else None
    margin = (top.probability - runner_up.probability) if runner_up else top.probability

    if top.probability < min_confidence:
        return GuardedClassification(
            state="UNCERTAIN",
            top=top,
            runner_up=runner_up,
            margin=margin,
            all=classes,
            reason=f"top probability {top.probability:.2f} < {min_confidence:.2f}",
        )
    if runner_up is not None and margin < min_margin:
        return GuardedClassification(
            state="UNCERTAIN",
            top=top,
            runner_up=runner_up,
            margin=margin,
            all=classes,
            reason=f"top-2 margin {margin:.2f} < {min_margin:.2f} (ambiguous)",
        )
    return GuardedClassification(
        state="CLASSIFIED",
        top=top,
        runner_up=runner_up,
        margin=margin,
        all=classes,
    )
