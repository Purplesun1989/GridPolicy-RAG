from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

PARSED_JSON_DIR = PROCESSED_DATA_DIR / "parsed_json"
TABLE_OUTPUT_DIR = PROCESSED_DATA_DIR / "tables"
REVIEW_SAMPLE_DIR = PROCESSED_DATA_DIR / "review_samples"

DOCUMENT_REGISTRY_PATH = PROCESSED_DATA_DIR / "document_registry.csv"
PARSING_QUALITY_REPORT_PATH = PROCESSED_DATA_DIR / "parsing_quality_report.csv"

TARGET_PDFS = {
    "isp_2026_nem_main": RAW_DATA_DIR / "isp/pdf/2026-integrated-system-plan-isp.pdf",
    "esoo_2025_nem_main": RAW_DATA_DIR / "esoo/nem/pdf/2025-electricity-statement-of-opportunities.pdf",
    "operations_power_system_security_guidelines": RAW_DATA_DIR / "operations/pdf/so_op_3715-power-system-security-guidelines.pdf",
}



REGION_DETECTION_DIR = PROCESSED_DATA_DIR / "region_detection"
MANIFEST_DIR = REGION_DETECTION_DIR / "manifests"
DEBUG_PAGE_DIR = REGION_DETECTION_DIR / "debug_pages"
TABLE_IMAGE_DIR = REGION_DETECTION_DIR / "table_images"
REGION_LOGS_DIR = REGION_DETECTION_DIR / "logs"
REGION_PAGEOBJ_DIR = REGION_DETECTION_DIR / "page_objects"

DEFAULT_RENDER_DPI = 200
PDF_POINTS_PER_INCH = 72
DEFAULT_RENDER_ZOOM = DEFAULT_RENDER_DPI / PDF_POINTS_PER_INCH
COORDINATE_SYSTEM = "pymupdf_top_left_origin"
BBOX_UNIT = "pdf_points"
BBOX_FORMAT = "[x0, y0, x1, y1]"