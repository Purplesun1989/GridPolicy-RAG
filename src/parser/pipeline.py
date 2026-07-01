from dataclasses import asdict

from src.config import (
    MANIFEST_DIR,
    DEBUG_PAGE_DIR,
    TABLE_IMAGE_DIR,
    PDF_RENDER_DPI,
)
from src.parser.table_region_detector import detect_tables_with_pymupdf
from src.parser.table_image_exporter import export_table_candidate_images
from src.parser.visualize_table_regions import export_debug_page
from src.parser.manifest_writer import write_jsonl
from src.parser.get_source_file_paths import collect_all_pdf_paths



def run_single_page_test(page_number: int,PDF_PATH:str ,DOC_ID:str) -> None:
    """
    Single-page debug mode:
    1. Detect tables on one page.
    2. Export cropped table images.
    3. Export debug page with bbox overlay.
    4. Write manifest.
    """
    candidates = detect_tables_with_pymupdf(
        pdf_path=PDF_PATH,
        doc_id=DOC_ID,
        page_numbers=[page_number],
    )

    exported_candidates = export_table_candidate_images(
        pdf_path=PDF_PATH,
        candidates=candidates,
        output_root=TABLE_IMAGE_DIR,
        dpi=PDF_RENDER_DPI,
        padding_x_pt=6.0,
        padding_y_pt=6.0,
    )

    candidate_dicts = [asdict(c) for c in exported_candidates]

    debug_page_path = export_debug_page(
        pdf_path=PDF_PATH,
        doc_id=DOC_ID,
        page_number=page_number,
        candidates=candidate_dicts,
        output_dir=str(DEBUG_PAGE_DIR),
    )

    for candidate in exported_candidates:
        candidate.debug_page_path = debug_page_path

    manifest_path = MANIFEST_DIR / "table_candidates_single_page.jsonl"

    write_jsonl(
        records=exported_candidates,
        output_path=str(manifest_path),
    )

    print(f"Detected {len(exported_candidates)} table candidates")
    print(f"Table images saved to: {TABLE_IMAGE_DIR / DOC_ID}")
    print(f"Manifest saved to: {manifest_path}")
    print(f"Debug page saved to: {debug_page_path}")


def run_full_pdf_table_detection(
    export_debug_pages: bool ,
    PDF_PATH:str ,
    DOC_ID:str
) -> None:
    """
    Full PDF mode:
    1. Scan the whole PDF.
    2. Detect table regions on every page.
    3. Export cropped table images to data/processed/region_detection/region_images/tables.
    4. Optionally export debug pages.
    5. Write full manifest.
    """
    candidates = detect_tables_with_pymupdf(
        pdf_path=PDF_PATH,
        doc_id=DOC_ID,
        page_numbers=None,
    )

    exported_candidates = export_table_candidate_images(
        pdf_path=PDF_PATH,
        candidates=candidates,
        output_root=TABLE_IMAGE_DIR,
        dpi=PDF_RENDER_DPI,
        padding_x_pt=6.0,
        padding_y_pt=6.0,
    )

    if export_debug_pages:
        page_numbers = sorted({c.page_number for c in exported_candidates})

        for page_number in page_numbers:
            page_candidates = [
                asdict(c)
                for c in exported_candidates
                if c.page_number == page_number
            ]

            debug_page_path = export_debug_page(
                pdf_path=PDF_PATH,
                doc_id=DOC_ID,
                page_number=page_number,
                candidates=page_candidates,
                output_dir=str(DEBUG_PAGE_DIR/DOC_ID),
            )

            for candidate in exported_candidates:
                if candidate.page_number == page_number:
                    candidate.debug_page_path = debug_page_path

    manifest_path = MANIFEST_DIR / f"{DOC_ID}_table_candidates.jsonl"

    write_jsonl(
        records=exported_candidates,
        output_path=str(manifest_path),
    )

    print(f"Detected {len(exported_candidates)} table candidates")
    print(f"Table images saved to: {TABLE_IMAGE_DIR / DOC_ID}")
    print(f"Manifest saved to: {manifest_path}")

    if export_debug_pages:
        print(f"Debug pages saved to: {DEBUG_PAGE_DIR / DOC_ID}")


if __name__ == "__main__":
    # 单页测试
    # run_single_page_test(60)

    # 获取所有 PDF 路径对象的 values 集合
    pdf_paths = collect_all_pdf_paths().values()
    for path in pdf_paths:
        full_path_str = str(path)
        pdf_stem_name = path.stem
        run_full_pdf_table_detection(True, full_path_str, pdf_stem_name)
