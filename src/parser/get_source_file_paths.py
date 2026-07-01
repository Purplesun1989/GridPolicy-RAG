from pathlib import Path
from typing import Dict, List
from src.config import (
    ISP_PDFS_DIR,
    ESOO_NEM_PDFS_DIR,
    ESOO_WEM_PDFS_DIR,
    OPERATIONS_PDFS_DIR
)

pdf_paths: Dict[str, Path] = {}
pdf_dirs: List[Path] = [
    ISP_PDFS_DIR,
    ESOO_NEM_PDFS_DIR,
    ESOO_WEM_PDFS_DIR,
    OPERATIONS_PDFS_DIR
]
def collect_all_CSV_paths() -> Dict[str, Path]:
    return 0

def collect_all_txt_paths() -> Dict[str, Path]:
    return 0

def collect_all_pdf_paths() -> Dict[str, Path]:
    """
    Recursively scan a list of PDF directories and return a doc_id -> PDF path registry.
    """
    pdf_paths: Dict[str, Path] = {}

    for dir_path in pdf_dirs:

        if not dir_path.exists():
            print(f"No Path: {dir_path}")
            continue

        if not dir_path.is_dir():
            print(f"Not valid dir: {dir_path}")
            continue

        # 使用 rglob 进行深度递归扫描
        for pdf_file in dir_path.rglob("*.pdf"):

            # 过滤临时和隐藏文件
            if pdf_file.name.startswith("~") or pdf_file.name.startswith("."):
                continue

            # 自动生成系统内唯一的 doc_id 作为键名（蛇形命名法）
            doc_key = pdf_file.stem.lower().replace("-", "_").replace(" ", "_")

            # 防止因文件名完全相同导致字典键冲突覆盖（防御策略）
            if doc_key in pdf_paths:
                doc_key = f"{pdf_file.parent.name}_{doc_key}"

            # 🌟 修复点 2：把扫描锁定到的 PDF 绝对物理路径，真正装填进我们的字典弹药库中！
            pdf_paths[doc_key] = pdf_file.resolve()


    return pdf_paths

