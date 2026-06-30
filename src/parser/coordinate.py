# coordinate_system = pymupdf_top_left_origin
# bbox_unit = pdf_points
# render_dpi = 200
# zoom = 200 / 72

from typing import List

PDF_POINTS_PER_INCH = 72


def expand_bbox(
    bbox_pdf: List[float],
    page_width_pt: float,
    page_height_pt: float,
    left_pt: float = 8.0,
    top_pt: float = 42.0,
    right_pt: float = 8.0,
    bottom_pt: float = 25.0,
) -> List[float]:
    """
    Expand bbox while keeping it inside page boundaries.

    Coordinate system:
    - PyMuPDF top-left origin
    - unit: PDF points
    - bbox format: [x0, y0, x1, y1]
    - no y-axis flipping
    """
    x0, y0, x1, y1 = bbox_pdf

    return [
        max(0.0, x0 - left_pt),
        max(0.0, y0 - top_pt),
        min(page_width_pt, x1 + right_pt),
        min(page_height_pt, y1 + bottom_pt),
    ]


def normalize_bbox(
    bbox_pdf: List[float],
    page_width_pt: float,
    page_height_pt: float,
) -> List[float]:
    """
    Normalize bbox from PDF points to [0, 1].

    Coordinate system:
    - PyMuPDF top-left origin
    - x increases rightward
    - y increases downward
    - bbox format: [x0, y0, x1, y1]
    """
    x0, y0, x1, y1 = bbox_pdf

    return [
        x0 / page_width_pt,
        y0 / page_height_pt,
        x1 / page_width_pt,
        y1 / page_height_pt,
    ]


def pdf_bbox_to_pixel_bbox(
    bbox_pdf: List[float],
    dpi: int = 200,
) -> List[int]:
    """
    Convert PyMuPDF PDF bbox to rendered pixel bbox.

    Important:
    - Input bbox_pdf uses PyMuPDF top-left-origin coordinates.
    - Unit is PDF points.
    - No y-axis flipping is performed.
    """
    zoom = dpi / PDF_POINTS_PER_INCH
    x0, y0, x1, y1 = bbox_pdf

    return [
        int(round(x0 * zoom)),
        int(round(y0 * zoom)),
        int(round(x1 * zoom)),
        int(round(y1 * zoom)),
    ]


def clamp_bbox_to_page(
    bbox_pdf: List[float],
    page_width_pt: float,
    page_height_pt: float,
    padding_pt: float = 0.0,
) -> List[float]:
    """
    Clamp bbox to page boundary.

    Coordinate system:
    - PyMuPDF top-left origin
    - unit: PDF points
    """
    x0, y0, x1, y1 = bbox_pdf

    x0 = max(0.0, x0 - padding_pt)
    y0 = max(0.0, y0 - padding_pt)
    x1 = min(page_width_pt, x1 + padding_pt)
    y1 = min(page_height_pt, y1 + padding_pt)

    return [x0, y0, x1, y1]