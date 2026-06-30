from dataclasses import asdict

from src.config import MANIFEST_DIR, DEBUG_PAGE_DIR
from src.parser.table_region_detector import detect_tables_with_pymupdf
from src.parser.visualize_table_regions import export_debug_page
from src.parser.manifest_writer import write_jsonl


def run_single_page_test(page_number: int) -> None:
    doc_id = "isp_2026_nem_main"
    pdf_path = "data/raw/isp/pdf/2026-integrated-system-plan-isp.pdf"
    page_numbers = [page_number]

    candidates = detect_tables_with_pymupdf(
        pdf_path=pdf_path,
        doc_id=doc_id,
        page_numbers=page_numbers,
    )

    # 1. 先把 TableCandidate 转成 dict，给 debug page 使用
    candidate_dicts = [asdict(c) for c in candidates]

    debug_page_path = export_debug_page(
        pdf_path=pdf_path,
        doc_id=doc_id,
        page_number=page_number,
        candidates=candidate_dicts,
        output_dir=str(DEBUG_PAGE_DIR),
    )

    # 2. 把 debug_page_path 写回每个 TableCandidate
    for candidate in candidates:
        candidate.debug_page_path = debug_page_path


    manifest_path = MANIFEST_DIR / "table_candidates.jsonl"
    write_jsonl(
        records=candidates,
        output_path=str(manifest_path),
    )

    export_debug_page(
        pdf_path=pdf_path,
        doc_id=doc_id,
        page_number=page_number,
        candidates=candidates,
        output_dir=str(DEBUG_PAGE_DIR),
    )

    print(f"Detected {len(candidates)} table candidates")
    print(f"Manifest saved to: {manifest_path}")
    print(f"Debug page saved to: {DEBUG_PAGE_DIR / doc_id}")


if __name__ == "__main__":
    run_single_page_test(60)