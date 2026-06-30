import fitz
from pathlib import Path
from typing import List, Optional

from src.config import (
    COORDINATE_SYSTEM,
    BBOX_UNIT,
    BBOX_FORMAT,
    DEFAULT_RENDER_DPI,
    DEFAULT_RENDER_ZOOM,
)

from src.parser.coordinate import (
    normalize_bbox,
    pdf_bbox_to_pixel_bbox,
    expand_bbox,
)

from src.parser.table_candidate_schema import TableCandidate


def detect_tables_with_pymupdf(
    pdf_path: str,
    doc_id: str,
    page_numbers: Optional[List[int]] = None,
) -> List[TableCandidate]:
    """
    Detect table-like regions using PyMuPDF find_tables().

    Coordinate contract:
    - bbox_detected_pdf uses PyMuPDF top-left-origin coordinate system.
    - bbox_export_pdf is expanded from bbox_detected_pdf for image export.
    - Unit is PDF points.
    - bbox format is [x0, y0, x1, y1].
    """
    pdf_path = Path(pdf_path)
    doc = fitz.open(pdf_path)

    candidates: List[TableCandidate] = []

    if page_numbers is None:
        target_page_indices = range(len(doc))
    else:
        target_page_indices = [p - 1 for p in page_numbers]

    for page_index in target_page_indices:
        page = doc[page_index]
        page_number = page_index + 1

        page_width_pt = page.rect.width
        page_height_pt = page.rect.height
        page_rotation = page.rotation

        try:
            table_finder = page.find_tables()
            tables = getattr(table_finder, "tables", [])
        except Exception as e:
            print(f"[WARN] find_tables failed on page {page_number}: {e}")
            continue

        for table_idx, table in enumerate(tables, start=1):
            candidate_id = f"{doc_id}_p{page_number:03d}_t{table_idx:03d}"

            # 1. 原始检测框：只记录 detector 看到的表格主体
            bbox_detected_pdf = list(table.bbox)

            bbox_detected_norm = normalize_bbox(
                bbox_pdf=bbox_detected_pdf,
                page_width_pt=page_width_pt,
                page_height_pt=page_height_pt,
            )

            # 2. 导出框：向外扩展，用于截图，尽量包含 caption / units / notes
            bbox_export_pdf = expand_bbox(
                bbox_pdf=bbox_detected_pdf,
                page_width_pt=page_width_pt,
                page_height_pt=page_height_pt,
                left_pt=8.0,
                top_pt=42.0,
                right_pt=8.0,
                bottom_pt=25.0,
            )

            bbox_export_norm = normalize_bbox(
                bbox_pdf=bbox_export_pdf,
                page_width_pt=page_width_pt,
                page_height_pt=page_height_pt,
            )

            bbox_export_px = pdf_bbox_to_pixel_bbox(
                bbox_pdf=bbox_export_pdf,
                dpi=DEFAULT_RENDER_DPI,
            )

            candidate = TableCandidate(
                candidate_id=candidate_id,
                doc_id=doc_id,
                source_pdf=str(pdf_path),

                page_number=page_number,
                page_index=page_index,

                coordinate_system=COORDINATE_SYSTEM,
                bbox_unit=BBOX_UNIT,
                bbox_format=BBOX_FORMAT,

                page_width_pt=page_width_pt,
                page_height_pt=page_height_pt,
                page_rotation=page_rotation,

                bbox_detected_pdf=bbox_detected_pdf,
                bbox_detected_norm=bbox_detected_norm,

                bbox_export_pdf=bbox_export_pdf,
                bbox_export_norm=bbox_export_norm,

                bbox_expansion={
                    "left_pt": 8.0,
                    "top_pt": 42.0,
                    "right_pt": 8.0,
                    "bottom_pt": 25.0,
                    "reason": "include_table_caption_and_notes",
                },

                render_dpi=DEFAULT_RENDER_DPI,
                render_zoom=DEFAULT_RENDER_ZOOM,
                bbox_export_px_on_full_page=bbox_export_px,

                detection_methods=["pymupdf_find_tables"],
                table_score=0.50,
                complexity_score=0.00,
                needs_review=True,
                reason=["detected_by_pymupdf_find_tables"],
            )

            candidates.append(candidate)

    doc.close()
    return candidates