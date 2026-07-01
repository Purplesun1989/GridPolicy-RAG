import fitz
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
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
fitz.TOOLS.mupdf_display_errors(False)
fitz.TOOLS.mupdf_display_warnings(False)

def _vertical_overlap_ratio(
    y0_a: float,
    y1_a: float,
    y0_b: float,
    y1_b: float,
) -> float:
    overlap = max(0.0, min(y1_a, y1_b) - max(y0_a, y0_b))
    height = max(1.0, min(y1_a - y0_a, y1_b - y0_b))
    return overlap / height


def _get_words_in_y_band(
    page: fitz.Page,
    y0: float,
    y1: float,
    min_overlap_ratio: float = 0.25,
) -> List[Tuple]:
    """
    Return words whose vertical range overlaps the candidate bbox.
    PyMuPDF word tuple:
        (x0, y0, x1, y1, word, block_no, line_no, word_no)
    """
    words = page.get_text("words")
    matched_words = []

    for word in words:
        wx0, wy0, wx1, wy1, text, *_ = word

        overlap_ratio = _vertical_overlap_ratio(
            y0,
            y1,
            wy0,
            wy1,
        )

        if overlap_ratio >= min_overlap_ratio:
            matched_words.append(word)

    return matched_words


def _find_right_text_edge(
    page: fitz.Page,
    bbox_pdf: List[float],
    min_extension_pt: float = 80.0,
) -> Tuple[float, bool]:
    """
    If there are words in the same y-band extending far beyond detected x1,
    treat them as part of the same table row/column area.
    """
    x0, y0, x1, y1 = bbox_pdf

    words = _get_words_in_y_band(
        page=page,
        y0=y0,
        y1=y1,
    )

    if not words:
        return x1, False

    right_edge = max(float(w[2]) for w in words)

    if right_edge > x1 + min_extension_pt:
        return right_edge, True

    return x1, False


def _find_horizontal_line_edges(
    page: fitz.Page,
    bbox_pdf: List[float],
    min_line_width_pt: float = 300.0,
    y_margin_pt: float = 12.0,
) -> Optional[Tuple[float, float]]:
    """
    Find long horizontal ruling lines near the detected table bbox.

    This is useful for AEMO glossary-style tables where PyMuPDF detects
    only the left columns, while the horizontal table lines extend across
    the full table width.
    """
    x0, y0, x1, y1 = bbox_pdf

    try:
        drawings = page.get_drawings()
    except Exception:
        return None

    line_candidates = []

    for drawing in drawings:
        for item in drawing.get("items", []):
            if not item:
                continue

            # PyMuPDF line drawing item format:
            # ("l", Point(x0, y0), Point(x1, y1))
            if item[0] != "l":
                continue

            p1 = item[1]
            p2 = item[2]

            lx0, ly0 = float(p1.x), float(p1.y)
            lx1, ly1 = float(p2.x), float(p2.y)

            if abs(ly0 - ly1) > 1.5:
                continue

            line_y = ly0
            line_width = abs(lx1 - lx0)

            if line_width < min_line_width_pt:
                continue

            if y0 - y_margin_pt <= line_y <= y1 + y_margin_pt:
                line_candidates.append(
                    (
                        min(lx0, lx1),
                        max(lx0, lx1),
                        line_width,
                    )
                )

    if not line_candidates:
        return None

    best_line = max(line_candidates, key=lambda x: x[2])
    return best_line[0], best_line[1]


def resolve_export_bbox_from_page(
    page: fitz.Page,
    bbox_detected_pdf: List[float],
    page_width_pt: float,
    page_height_pt: float,
) -> Tuple[List[float], Dict[str, Any]]:
    """
    Build bbox_export_pdf from bbox_detected_pdf.

    This replaces simple fixed padding with page-aware expansion:

    1. Apply normal padding.
    2. Expand right boundary using same-y-band text.
    3. Expand table width using long horizontal lines.
    4. Clamp to page boundary.

    Important:
    - bbox_detected_pdf remains unchanged.
    - bbox_export_pdf is the corrected crop box for image export.
    """
    left_pt = 8.0
    top_pt = 42.0
    right_pt = 8.0
    bottom_pt = 25.0

    x0, y0, x1, y1 = bbox_detected_pdf

    bbox_export_pdf = expand_bbox(
        bbox_pdf=bbox_detected_pdf,
        page_width_pt=page_width_pt,
        page_height_pt=page_height_pt,
        left_pt=left_pt,
        top_pt=top_pt,
        right_pt=right_pt,
        bottom_pt=bottom_pt,
    )

    expansion_steps = [
        {
            "method": "fixed_padding",
            "left_pt": left_pt,
            "top_pt": top_pt,
            "right_pt": right_pt,
            "bottom_pt": bottom_pt,
            "reason": "include_table_caption_units_and_notes",
        }
    ]

    export_x0, export_y0, export_x1, export_y1 = bbox_export_pdf

    # 1. Expand right edge using words in the same y-band.
    text_right_edge, expanded_by_text = _find_right_text_edge(
        page=page,
        bbox_pdf=bbox_detected_pdf,
        min_extension_pt=80.0,
    )

    if expanded_by_text:
        old_x1 = export_x1
        export_x1 = max(export_x1, text_right_edge + 8.0)

        expansion_steps.append(
            {
                "method": "right_text_edge",
                "old_x1": old_x1,
                "new_x1": export_x1,
                "text_right_edge": text_right_edge,
                "reason": "same_y_band_text_extends_beyond_detected_bbox",
            }
        )

    # 2. Expand x0 / x1 using long horizontal table lines.
    line_edges = _find_horizontal_line_edges(
        page=page,
        bbox_pdf=bbox_detected_pdf,
        min_line_width_pt=300.0,
        y_margin_pt=12.0,
    )

    if line_edges is not None:
        line_x0, line_x1 = line_edges

        old_x0 = export_x0
        old_x1 = export_x1

        export_x0 = min(export_x0, line_x0 - 4.0)
        export_x1 = max(export_x1, line_x1 + 4.0)

        expansion_steps.append(
            {
                "method": "horizontal_line_edges",
                "old_x0": old_x0,
                "old_x1": old_x1,
                "new_x0": export_x0,
                "new_x1": export_x1,
                "line_x0": line_x0,
                "line_x1": line_x1,
                "reason": "long_horizontal_table_line_detected_near_bbox",
            }
        )

    # 3. Clamp to page boundary.
    export_x0 = max(0.0, min(export_x0, page_width_pt))
    export_y0 = max(0.0, min(export_y0, page_height_pt))
    export_x1 = max(0.0, min(export_x1, page_width_pt))
    export_y1 = max(0.0, min(export_y1, page_height_pt))

    bbox_export_pdf = [
        export_x0,
        export_y0,
        export_x1,
        export_y1,
    ]

    bbox_expansion = {
        "source": "bbox_detected_pdf",
        "strategy": "fixed_padding_plus_page_aware_right_expansion",
        "steps": expansion_steps,
    }

    return bbox_export_pdf, bbox_expansion


def detect_tables_with_pymupdf(
    pdf_path: str,
    doc_id: str,
    page_numbers: Optional[List[int]] = None,
) -> List[TableCandidate]:
    """
    Detect table-like regions using PyMuPDF find_tables().

    Coordinate contract:
    - bbox_detected_pdf uses PyMuPDF top-left-origin coordinate system.
    - bbox_export_pdf is page-aware corrected bbox for image export.
    - Unit is PDF points.
    - bbox format is [x0, y0, x1, y1].
    """
    pdf_path = Path(pdf_path)

    candidates: List[TableCandidate] = []

    with fitz.open(pdf_path) as doc:
        if page_numbers is None:
            target_page_indices = range(len(doc))
        else:
            target_page_indices = [p - 1 for p in page_numbers]

        for page_index in target_page_indices:
            page = doc[page_index]
            page_number = page_index + 1

            page_width_pt = float(page.rect.width)
            page_height_pt = float(page.rect.height)
            page_rotation = int(page.rotation)

            try:
                table_finder = page.find_tables()
                tables = getattr(table_finder, "tables", [])
            except Exception as e:
                print(f"[WARN] find_tables failed on page {page_number}: {e}")
                continue

            for table_idx, table in enumerate(tables, start=1):
                candidate_id = f"{doc_id}_p{page_number:03d}_t{table_idx:03d}"

                # 1. Raw detector bbox.
                bbox_detected_pdf = list(table.bbox)

                bbox_detected_norm = normalize_bbox(
                    bbox_pdf=bbox_detected_pdf,
                    page_width_pt=page_width_pt,
                    page_height_pt=page_height_pt,
                )

                # 2. Page-aware export bbox.
                bbox_export_pdf, bbox_expansion = resolve_export_bbox_from_page(
                    page=page,
                    bbox_detected_pdf=bbox_detected_pdf,
                    page_width_pt=page_width_pt,
                    page_height_pt=page_height_pt,
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

                    bbox_expansion=bbox_expansion,

                    render_dpi=DEFAULT_RENDER_DPI,
                    render_zoom=DEFAULT_RENDER_ZOOM,
                    bbox_export_px_on_full_page=bbox_export_px,

                    detection_methods=[
                        "pymupdf_find_tables",
                        "page_aware_export_bbox_resolution",
                    ],
                    table_score=0.50,
                    complexity_score=0.00,
                    needs_review=True,
                    reason=[
                        "detected_by_pymupdf_find_tables",
                        "bbox_export_resolved_by_page_text_and_lines",
                    ],
                )

                candidates.append(candidate)


    return candidates