from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional


@dataclass
class TableCandidate:
    """
    Table candidate schema.

    Coordinate contract:
    - All PDF bboxes use PyMuPDF coordinate system.
    - Origin is top-left.
    - x increases rightward.
    - y increases downward.
    - Unit is PDF points.
    - bbox format is [x0, y0, x1, y1].
    - No y-axis flipping is allowed.

    bbox_detected_pdf:
        Raw bbox returned by detector, e.g. PyMuPDF find_tables().

    bbox_export_pdf:
        Expanded bbox used for cropping table images and sending to APIs.
        This should include table caption, body, and possible notes.
    """

    candidate_id: str
    doc_id: str
    source_pdf: str

    page_number: int
    page_index: int

    coordinate_system: Literal["pymupdf_top_left_origin"] = "pymupdf_top_left_origin"
    bbox_unit: Literal["pdf_points"] = "pdf_points"
    bbox_format: Literal["[x0, y0, x1, y1]"] = "[x0, y0, x1, y1]"

    # Page metadata
    page_width_pt: float = 0.0
    page_height_pt: float = 0.0
    page_rotation: int = 0

    # Detector raw bbox
    bbox_detected_pdf: List[float] = field(default_factory=list)
    bbox_detected_norm: List[float] = field(default_factory=list)

    # Final export bbox
    bbox_export_pdf: List[float] = field(default_factory=list)
    bbox_export_norm: List[float] = field(default_factory=list)

    # How bbox_detected_pdf was expanded into bbox_export_pdf
    bbox_expansion: Dict[str, object] = field(default_factory=dict)

    # Rendering metadata
    render_dpi: int = 200
    render_zoom: float = 200 / 72
    bbox_export_px_on_full_page: List[int] = field(default_factory=list)

    # Exported files
    image_path: Optional[str] = None
    debug_page_path: Optional[str] = None
    table_image_width_px: Optional[int] = None
    table_image_height_px: Optional[int] = None

    # Detection metadata
    detection_methods: List[str] = field(default_factory=list)
    table_score: float = 0.0
    complexity_score: float = 0.0
    needs_review: bool = True
    reason: List[str] = field(default_factory=list)

    # Optional caption metadata
    nearby_caption: Optional[str] = None
    nearby_caption_confidence: Optional[float] = None