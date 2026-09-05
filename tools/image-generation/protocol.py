"""Provider-agnostic illustration contract.

No network calls live here. Adapters may be added later under providers/.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol


@dataclass
class OutputRequirements:
    aspect_ratio: str = "3:2"
    text_safe_region: str = "lower third or as directed"
    resolution: str = "unspecified"
    image_format: str = "png"


@dataclass
class IllustrationRequest:
    spread: int
    book_number: int
    character_reference_images: list[Path] = field(default_factory=list)
    art_style_reference: Path | None = None
    previous_spread_reference: Path | None = None
    location_reference: Path | None = None
    continuity_state: dict[str, Any] = field(default_factory=dict)
    art_direction: dict[str, Any] = field(default_factory=dict)
    negative_constraints: list[str] = field(default_factory=list)
    output_requirements: OutputRequirements = field(default_factory=OutputRequirements)


@dataclass
class IllustrationResult:
    path: Path
    provider: str
    version: int
    request_digest: str = ""
    notes: str = ""


@dataclass
class VisualQAResult:
    result: str
    reasons: list[str]
    regenerate: bool


class ImageProvider(Protocol):
    name: str

    def generate_illustration(self, request: IllustrationRequest) -> IllustrationResult:
        ...

    def edit_illustration(
        self,
        request: IllustrationRequest,
        source_image: Path,
        edit_instructions: str,
    ) -> IllustrationResult:
        ...

    def evaluate_illustration(
        self,
        image: Path,
        request: IllustrationRequest,
        references: list[Path],
    ) -> VisualQAResult:
        ...


class UnconfiguredProvider:
    """Default provider. Refuses to invent a vendor."""

    name = "unconfigured"

    def generate_illustration(self, request: IllustrationRequest) -> IllustrationResult:
        raise RuntimeError(
            "No image provider is configured. Art direction can proceed; "
            "generation cannot. See tools/image-generation/README.md."
        )

    def edit_illustration(
        self,
        request: IllustrationRequest,
        source_image: Path,
        edit_instructions: str,
    ) -> IllustrationResult:
        raise RuntimeError("No image provider is configured.")

    def evaluate_illustration(
        self,
        image: Path,
        request: IllustrationRequest,
        references: list[Path],
    ) -> VisualQAResult:
        raise RuntimeError(
            "Model-side evaluateIllustration is not configured. "
            "Use the Visual QA agent instead."
        )


def get_provider() -> ImageProvider:
    return UnconfiguredProvider()
