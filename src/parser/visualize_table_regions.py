from pathlib import Path
from typing import Any, List

import fitz
from PIL import Image, ImageDraw

from src.config import DEFAULT_RENDER_DPI
from src.parser.coordinate import pdf_bbox_to_pixel_bbox


def _get_field(candidate: Any, field_name: str, default=None):
    """
    Read a field from either:
    - TableCandidate dataclass object: candidate.field_name
    - dict object: candidate["field_name"]

    This makes export_debug_page compatible with both:
    - List[TableCandidate]
    - List[dict]
    """
    if isinstance(candidate, dict):
        return candidate.get(field_name, default)

    return getattr(candidate, field_name, default)


def export_debug_page(
    pdf_path: str,
    doc_id: str,
    page_number: int,
    candidates: List[Any],
    output_dir: str,
    dpi: int = DEFAULT_RENDER_DPI,
) -> str:
    """
    Export a full-page debug image with detected and export bboxes.

    Coordinate contract:
    - bbox_detected_pdf and bbox_export_pdf use PyMuPDF coordinates.
    - Origin is top-left.
    - Unit is PDF points.
    - bbox format is [x0, y0, x1, y1].
    - No y-axis flipping is performed.

    Visual convention:
    - Gray thin box: bbox_detected_pdf, raw detector bbox.
    - Red thick box: bbox_export_pdf, final crop/export bbox.
    """

    output_dir = Path(output_dir) / doc_id
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{doc_id}_p{page_number:03d}_debug.png"

    # 1. Render full PDF page
    doc = fitz.open(pdf_path)
    page = doc[page_number - 1]

    zoom = dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)

    pix = page.get_pixmap(matrix=matrix, alpha=False)
    pix.save(str(output_path))

    doc.close()

    # 2. Draw candidate boxes
    img = Image.open(output_path)
    draw = ImageDraw.Draw(img)

    page_candidates = [
        c for c in candidates
        if _get_field(c, "page_number") == page_number
    ]

    for c in page_candidates:
        candidate_id = _get_field(c, "candidate_id", "unknown")
        table_score = _get_field(c, "table_score", 0.0)

        bbox_detected_pdf = _get_field(c, "bbox_detected_pdf")
        bbox_export_pdf = _get_field(c, "bbox_export_pdf")

        # 2.1 Raw detected bbox: gray thin box
        if bbox_detected_pdf:
            x0, y0, x1, y1 = pdf_bbox_to_pixel_bbox(
                bbox_pdf=bbox_detected_pdf,
                dpi=dpi,
            )

            draw.rectangle(
                [x0, y0, x1, y1],
                outline="gray",
                width=2,
            )

        # 2.2 Final export bbox: red thick box
        if bbox_export_pdf:
            x0, y0, x1, y1 = pdf_bbox_to_pixel_bbox(
                bbox_pdf=bbox_export_pdf,
                dpi=dpi,
            )

            draw.rectangle(
                [x0, y0, x1, y1],
                outline="red",
                width=4,
            )

            label = f"{candidate_id} | score={table_score:.2f}"

            draw.text(
                (x0, max(0, y0 - 18)),
                label,
                fill="red",
            )

    img.save(output_path)

    return str(output_path)