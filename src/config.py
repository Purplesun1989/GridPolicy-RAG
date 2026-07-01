from pathlib import Path


# ============================================================
# Project root
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]


# ============================================================
# Data directories
# ============================================================

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
PARSED_JSON_DIR = PROCESSED_DATA_DIR / "parsed_json"
REVIEW_SAMPLE_DIR = PROCESSED_DATA_DIR / "review_samples"

# ============================================================
# Raw data subdirectories
# ============================================================

ISP_RAW_DIR = RAW_DATA_DIR / "isp"
ISP_PDFS_DIR = ISP_RAW_DIR / "pdf"
ISP_WORKBOOKS_DIR = ISP_RAW_DIR / "workbooks"

ESOO_RAW_DIR = RAW_DATA_DIR / "esoo"

ESOO_NEM_RAW_DIR = ESOO_RAW_DIR / "nem"
ESOO_NEM_PDFS_DIR = ESOO_NEM_RAW_DIR / "pdf"
ESOO_NEM_WORKBOOKS_DIR = ESOO_NEM_RAW_DIR / "workbooks"

ESOO_WEM_RAW_DIR = ESOO_RAW_DIR / "wem"
ESOO_WEM_PDFS_DIR = ESOO_WEM_RAW_DIR / "pdf"

OPERATIONS_RAW_DIR = RAW_DATA_DIR / "operations"
OPERATIONS_PDFS_DIR = OPERATIONS_RAW_DIR / "pdf"



# ============================================================
# Registry and reports
# ============================================================

DOCUMENT_REGISTRY_PATH = PROCESSED_DATA_DIR / "document_registry.csv"
PARSING_QUALITY_REPORT_PATH = PROCESSED_DATA_DIR / "parsing_quality_report.csv"


# ============================================================
# Raw PDF targets
# ============================================================

TARGET_PDFS = {
    "isp_2026_nem_main": RAW_DATA_DIR / "isp/pdf/2026-integrated-system-plan-isp.pdf",
    "esoo_2025_nem_main": RAW_DATA_DIR / "esoo/nem/pdf/2025-electricity-statement-of-opportunities.pdf",
    "operations_power_system_security_guidelines": RAW_DATA_DIR / "operations/pdf/so_op_3715-power-system-security-guidelines.pdf",
}


# ============================================================
# Region detection & outputs
# ============================================================

REGION_DETECTION_DIR = PROCESSED_DATA_DIR / "region_detection"

MANIFEST_DIR = REGION_DETECTION_DIR / "manifests"
DEBUG_PAGE_DIR = REGION_DETECTION_DIR / "debug_pages"
REGION_LOGS_DIR = REGION_DETECTION_DIR / "logs"
REGION_PAGEOBJ_DIR = REGION_DETECTION_DIR / "page_objects"


REGION_IMAGE_DIR = REGION_DETECTION_DIR / "region_images"
TABLE_IMAGE_DIR = REGION_IMAGE_DIR / "tables"
CHART_IMAGE_DIR = REGION_IMAGE_DIR / "charts"
FIGURE_IMAGE_DIR = REGION_IMAGE_DIR / "figures"


# ============================================================
# PDF rendering / coordinate settings
# ============================================================

PDF_RENDER_DPI = 200
PDF_POINTS_PER_INCH = 72
PDF_RENDER_ZOOM = PDF_RENDER_DPI / PDF_POINTS_PER_INCH

COORDINATE_SYSTEM = "pymupdf_top_left_origin"
BBOX_UNIT = "pdf_points"
BBOX_FORMAT = "[x0, y0, x1, y1]"


# ============================================================
# Optional backward-compatible aliases
# ============================================================
# Keep these only if older files still import DEFAULT_RENDER_DPI
# or DEFAULT_RENDER_ZOOM.

DEFAULT_RENDER_DPI = PDF_RENDER_DPI
DEFAULT_RENDER_ZOOM = PDF_RENDER_ZOOM