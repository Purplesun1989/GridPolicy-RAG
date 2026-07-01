# src/parser/table_image_exporter.py

from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Any, Optional

import fitz  # PyMuPDF

from src.parser.table_candidate_schema import TableCandidate


def _clamp_bbox_to_page(
    bbox: List[float],
    page_width_pt: float,
    page_height_pt: float,
) -> List[float]:
    """
    Clamp bbox to PDF page boundary.

    bbox format:
        [x0, y0, x1, y1]

    coordinate system:
        PyMuPDF top-left origin

    unit:
        PDF points
    """
    x0, y0, x1, y1 = bbox

    x0 = max(0.0, min(float(x0), page_width_pt))
    y0 = max(0.0, min(float(y0), page_height_pt))
    x1 = max(0.0, min(float(x1), page_width_pt))
    y1 = max(0.0, min(float(y1), page_height_pt))

    if x1 <= x0 or y1 <= y0:
        raise ValueError(f"Invalid bbox after clamping: {[x0, y0, x1, y1]}")

    return [x0, y0, x1, y1]


def _expand_bbox(
    bbox: List[float],
    page_width_pt: float,
    page_height_pt: float,
    padding_x_pt: float = 6.0,
    padding_y_pt: float = 6.0,
) -> tuple[List[float], Dict[str, Any]]:
    """
    Expand detected bbox into export bbox.

    This is useful because table detectors often produce tight boxes,
    while screenshots need a small margin around the table.
    """
    x0, y0, x1, y1 = bbox

    expanded = [
        x0 - padding_x_pt,
        y0 - padding_y_pt,
        x1 + padding_x_pt,
        y1 + padding_y_pt,
    ]

    clamped = _clamp_bbox_to_page(
        expanded,
        page_width_pt=page_width_pt,
        page_height_pt=page_height_pt,
    )

    expansion_info = {
        "source": "bbox_detected_pdf",
        "padding_x_pt": padding_x_pt,
        "padding_y_pt": padding_y_pt,
        "before": bbox,
        "after": clamped,
        "clamped_to_page": clamped != expanded,
    }

    return clamped, expansion_info


def _normalize_bbox(
    bbox: List[float],
    page_width_pt: float,
    page_height_pt: float,
) -> List[float]:
    """
    Convert PDF-point bbox into normalized bbox.

    Output format:
        [x0_norm, y0_norm, x1_norm, y1_norm]
    """
    x0, y0, x1, y1 = bbox

    return [
        x0 / page_width_pt,
        y0 / page_height_pt,
        x1 / page_width_pt,
        y1 / page_height_pt,
    ]


def _get_page_dimensions(
    page: fitz.Page,
    candidate: TableCandidate,
) -> tuple[float, float]:
    """
    Prefer dimensions stored in candidate.
    Fall back to PyMuPDF page.rect if missing.
    """
    page_width_pt = getattr(candidate, "page_width_pt", 0.0) or page.rect.width
    page_height_pt = getattr(candidate, "page_height_pt", 0.0) or page.rect.height

    return float(page_width_pt), float(page_height_pt)


def _resolve_export_bbox(
    *,
    page: fitz.Page,
    candidate: TableCandidate,
    padding_x_pt: float,
    padding_y_pt: float,
) -> List[float]:
    """
    Decide which bbox should be used for image export.

    Priority:
    1. Use candidate.bbox_export_pdf if already available.
    2. Otherwise expand candidate.bbox_detected_pdf.
    3. Save the final result back into candidate.bbox_export_pdf.
    """
    page_width_pt, page_height_pt = _get_page_dimensions(page, candidate)

    if candidate.bbox_export_pdf:
        export_bbox = _clamp_bbox_to_page(
            candidate.bbox_export_pdf,
            page_width_pt=page_width_pt,
            page_height_pt=page_height_pt,
        )

        candidate.bbox_export_pdf = export_bbox
        candidate.bbox_export_norm = _normalize_bbox(
            export_bbox,
            page_width_pt=page_width_pt,
            page_height_pt=page_height_pt,
        )

        if not candidate.bbox_expansion:
            candidate.bbox_expansion = {
                "source": "bbox_export_pdf",
                "note": "bbox_export_pdf already existed; exporter used it directly",
            }

        return export_bbox

    if not candidate.bbox_detected_pdf:
        raise ValueError(
            f"Candidate {candidate.candidate_id} has neither "
            f"bbox_export_pdf nor bbox_detected_pdf."
        )

    detected_bbox = _clamp_bbox_to_page(
        candidate.bbox_detected_pdf,
        page_width_pt=page_width_pt,
        page_height_pt=page_height_pt,
    )

    candidate.bbox_detected_pdf = detected_bbox
    candidate.bbox_detected_norm = _normalize_bbox(
        detected_bbox,
        page_width_pt=page_width_pt,
        page_height_pt=page_height_pt,
    )

    export_bbox, expansion_info = _expand_bbox(
        detected_bbox,
        page_width_pt=page_width_pt,
        page_height_pt=page_height_pt,
        padding_x_pt=padding_x_pt,
        padding_y_pt=padding_y_pt,
    )

    candidate.bbox_export_pdf = export_bbox
    candidate.bbox_export_norm = _normalize_bbox(
        export_bbox,
        page_width_pt=page_width_pt,
        page_height_pt=page_height_pt,
    )
    candidate.bbox_expansion = expansion_info

    return export_bbox


def export_table_candidate_image(
    *,
    pdf_doc: fitz.Document,
    candidate: TableCandidate,
    output_root: Path,
    dpi: int = 200,
    padding_x_pt: float = 6.0,
    padding_y_pt: float = 6.0,
) -> TableCandidate:
    """
    Export one TableCandidate as a cropped table image.

    The function mutates and returns the same TableCandidate object:
        - fills bbox_export_pdf
        - fills bbox_export_norm
        - fills bbox_expansion
        - fills image_path if the dataclass has that field
    """
    page_index = int(candidate.page_index)
    page_number = int(candidate.page_number)

    page = pdf_doc.load_page(page_index)

    export_bbox = _resolve_export_bbox(
        page=page,
        candidate=candidate,
        padding_x_pt=padding_x_pt,
        padding_y_pt=padding_y_pt,
    )

    clip = fitz.Rect(*export_bbox)
    matrix = fitz.Matrix(dpi / 72.0, dpi / 72.0)

    pix = page.get_pixmap(
        matrix=matrix,
        clip=clip,
        alpha=False,
    )

    doc_id = candidate.doc_id
    candidate_id = candidate.candidate_id

    doc_output_dir = output_root / doc_id
    doc_output_dir.mkdir(parents=True, exist_ok=True)

    image_filename = f"{candidate_id}.png"
    image_path = doc_output_dir / image_filename

    pix.save(str(image_path))

    if hasattr(candidate, "image_path"):
        candidate.image_path = str(image_path)

    if hasattr(candidate, "dpi"):
        candidate.dpi = dpi

    if hasattr(candidate, "image_width_px"):
        candidate.image_width_px = pix.width

    if hasattr(candidate, "image_height_px"):
        candidate.image_height_px = pix.height

    if hasattr(candidate, "export_status"):
        candidate.export_status = "exported"

    return candidate


def export_table_candidate_images(
    *,
    pdf_path: Path | str,
    candidates: List[TableCandidate],
    output_root: Path | str = Path("data/region_images/tables"),
    dpi: int = 200,
    padding_x_pt: float = 6.0,
    padding_y_pt: float = 6.0,
    skip_failed: bool = True,
) -> List[TableCandidate]:
    """
    Export table images for a list of TableCandidate objects.

    This is the main function that pipeline.py should call.
    """
    pdf_path = Path(pdf_path)
    output_root = Path(output_root)

    output_root.mkdir(parents=True, exist_ok=True)

    exported: List[TableCandidate] = []

    with fitz.open(pdf_path) as pdf_doc:
        for candidate in candidates:
            try:
                exported_candidate = export_table_candidate_image(
                    pdf_doc=pdf_doc,
                    candidate=candidate,
                    output_root=output_root,
                    dpi=dpi,
                    padding_x_pt=padding_x_pt,
                    padding_y_pt=padding_y_pt,
                )
                exported.append(exported_candidate)

            except Exception as e:
                if hasattr(candidate, "export_status"):
                    candidate.export_status = "failed"

                if hasattr(candidate, "reject_reason"):
                    candidate.reject_reason = f"image_export_failed: {e}"

                if skip_failed:
                    print(
                        f"[WARN] Failed to export candidate "
                        f"{getattr(candidate, 'candidate_id', '<unknown>')}: {e}"
                    )
                    continue

                raise

    return exported