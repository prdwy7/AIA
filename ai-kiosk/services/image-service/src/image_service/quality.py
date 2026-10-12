"""Deterministic image quality checks (roadmap §9.4.4).

Checks (no ML — fast, explainable, testable):
- size: minimum width/height (usable detail),
- brightness: mean luminance in a sane band (too dark / blown out),
- sharpness: variance of the Laplacian (blur detection).

Each failure produces a **concrete retry instruction** shown to the farmer
(Telugu-first), so a bad photo never dead-ends the case.
"""

from __future__ import annotations

import io
import statistics
from dataclasses import dataclass, field

from PIL import Image, ImageFilter

# Defaults tuned for phone cameras at 1–2 m from the plant.
MIN_WIDTH = 320
MIN_HEIGHT = 240
MIN_BRIGHTNESS = 30  # 0..255
MAX_BRIGHTNESS = 225
MIN_SHARPNESS = 100.0  # variance of Laplacian (standard blur-detection threshold)


@dataclass(frozen=True)
class QualityResult:
    usable: bool
    reasons: list[str] = field(default_factory=list)
    retry_instruction: str | None = None  # bilingual, concrete
    metrics: dict[str, float] = field(default_factory=dict)


def _laplacian_variance(img: Image.Image) -> float:
    """Variance of the Laplacian — the standard blur metric."""
    gray = img.convert("L")
    lap = gray.filter(
        ImageFilter.Kernel((3, 3), [0, -1, 0, -1, 4, -1, 0, -1, 0], scale=1, offset=128)
    )
    pixels = list(lap.get_flattened_data())
    if len(pixels) < 2:
        return 0.0
    return statistics.pvariance(pixels)


def _mean_brightness(img: Image.Image) -> float:
    gray = img.convert("L")
    # Sample a grid to keep this fast on large images.
    w, h = gray.size
    step_x = max(1, w // 64)
    step_y = max(1, h // 64)
    samples = [gray.getpixel((x, y)) for x in range(0, w, step_x) for y in range(0, h, step_y)]
    return sum(samples) / len(samples) if samples else 0.0


def check_image_quality(
    image_bytes: bytes,
    min_width: int = MIN_WIDTH,
    min_height: int = MIN_HEIGHT,
    min_brightness: float = MIN_BRIGHTNESS,
    max_brightness: float = MAX_BRIGHTNESS,
    min_sharpness: float = MIN_SHARPNESS,
) -> QualityResult:
    """Run all deterministic checks. Returns a usable flag + retry guidance."""
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img.load()
    except Exception:
        return QualityResult(
            usable=False,
            reasons=["unreadable_image"],
            retry_instruction=(
                "ఫోటో సరిగ్గా తీసేది లేదు. మళ్ళీ తీసి పంపండి. "
                "(Photo could not be read. Please retake and resend.)"
            ),
        )

    width, height = img.size
    brightness = _mean_brightness(img)
    sharpness = _laplacian_variance(img)
    metrics = {
        "width": float(width),
        "height": float(height),
        "brightness": brightness,
        "sharpness": sharpness,
    }

    reasons: list[str] = []
    instructions: list[str] = []
    if width < min_width or height < min_height:
        reasons.append("too_small")
        instructions.append(
            "మొక్క దగ్గరకు వెళ్ళి, పూర్తిగా కనిపించేలా ఫోటో తీయండి "
            "(Move closer so the plant fills the frame)"
        )
    if brightness < min_brightness:
        reasons.append("too_dark")
        instructions.append("వెలుగులో ఉంచి ఫోటో తీయండి (Take the photo in good light)")
    elif brightness > max_brightness:
        reasons.append("overexposed")
        instructions.append(
            "సూర్యుడి నేరుగా వెలుగులో కాకుండా ఫోటో తీయండి "
            "(Avoid direct sunlight / overexposure)"
        )
    if sharpness < min_sharpness:
        reasons.append("blurry")
        instructions.append(
            "కెమెరా స్థిరంగా పట్టుకుని, పత్రం క్లారిగా కనిపించేలా తీయండి "
            "(Hold the camera steady so the leaf is in focus)"
        )

    if reasons:
        return QualityResult(
            usable=False,
            reasons=reasons,
            retry_instruction=" · ".join(instructions),
            metrics=metrics,
        )
    return QualityResult(usable=True, metrics=metrics)
