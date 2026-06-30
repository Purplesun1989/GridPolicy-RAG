import csv
from pathlib import Path
import hashlib
import fitz
import os



def create_document_registry():
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)

    registry_path = output_dir / "document_registry.csv"

    headers =  [
    "doc_id",
    "domain",
    "subdomain",
    "file_path",
    "file_name",
    "file_hash",
    "file_size_mb",
    "title",
    "publication_year",
    "source_type",
    "document_type",
    "region",
    "num_pages",
    "has_tables",
    "has_workbook",
    "parse_status",
    "notes"
]

    # 录入 3 份代表性极强的高价值 AEMO 文档
    initial_docs = [
        {
            "doc_id": "isp_2026_main",
            "domain": "isp",
            "subdomain": "nem",
            "file_path": "data/raw/isp/pdf/2026-integrated-system-plan-isp.pdf",
            "file_name": "2026-integrated-system-plan-isp.pdf",
            "file_hash": "unknown",
            "file_size_mb":"unknown",
            "title": "2026 Integrated System Plan",
            "publication_year": 2026,
            "source_type": "pdf",
            "document_type": "planning_report",
            "region": "NEM",
            "num_pages": "unknown",  # 将在解析时自动更新
            "has_tables": "yes",
            "has_workbook": "yes",
            "parse_status": "pending",
            "notes": "main ISP report"
        },
        {
            "doc_id": "esoo_2025_main",
            "domain": "esoo",
            "subdomain": "nem",
            "file_path": "data/raw/esoo/nem/pdf/2025-electricity-statement-of-opportunities.pdf",
            "file_name": "2025-electricity-statement-of-opportunities.pdf",
            "file_hash": "unknown",
            "file_size_mb": "unknown",
            "title": "2025 Electricity Statement of Opportunities",
            "publication_year": 2025,
            "source_type": "pdf",
            "document_type": "planning_report",
            "region": "NEM",
            "num_pages": "unknown",
            "has_tables": "yes",
            "has_workbook": "yes",
            "parse_status": "pending",
            "notes": "esoo main report for eastern states"
        },
        {
            "doc_id": "security_guidelines_3715",
            "domain": "operations",
            "subdomain": "nem",
            "file_path": "data/raw/operations/pdf/so_op_3715-power-system-security-guidelines.pdf",
            "file_name": "so_op_3715-power-system-security-guidelines.pdf",
            "file_hash": "unknown",
            "file_size_mb": "unknown",
            "title": "Power System Security Guidelines SO_OP_3715",
            "publication_year": 2026,  # 假设当前最新
            "source_type": "pdf",
            "document_type": "operational_procedure",
            "region": "NEM",
            "num_pages": "unknown",
            "has_tables": "yes",
            "has_workbook": "no",
            "parse_status": "pending",
            "notes": "regulatory logic and constraints"
        }
    ]

    with open(registry_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for doc in initial_docs:
            file_path = doc["file_path"]
            doc["file_hash"] = get_file_hash(file_path)
            doc["file_size_mb"] = get_file_size_mb(file_path)
            doc["num_pages"] = get_num_pages(file_path)
            writer.writerow(doc)



def get_file_size_mb(file_path: str) -> float:
    path = Path(file_path)
    size_bytes = path.stat().st_size
    return round(size_bytes / (1024 * 1024), 2)


def get_file_hash(file_path: str) -> str:
    path = Path(file_path)
    sha256 = hashlib.sha256()

    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def get_num_pages(file_path: str) -> int:
    doc = fitz.open(file_path)
    return len(doc)

if __name__ == "__main__":

    print("Current working directory:", os.getcwd())
    create_document_registry()