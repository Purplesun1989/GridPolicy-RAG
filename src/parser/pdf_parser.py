import fitz  # PyMuPDF
import json
import logging
from pathlib import Path
import sys

project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.config import TARGET_PDFS, PARSED_JSON_DIR

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)


def parse_pdf_to_json(pdf_path: Path, doc_id: str, output_json_path: Path):
    """
    使用 PyMuPDF 将指定的 PDF 文件解析为包含 page + block 级元数据的统一 JSON。
    """
    if not pdf_path.exists():
        logging.error(f"Can't find : {pdf_path}")
        return False

    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        logging.error(f"Open failed: {str(e)}")
        return False

    # 构造符合任务书 Schema 要求的顶层骨架数据
    parsed_data = {
        "doc_id": doc_id,
        "file_path": str(pdf_path.relative_to(project_root) if pdf_path.is_relative_to(project_root) else pdf_path),
        "parser": "pymupdf",
        "schema_version": "0.1",
        "num_pages": len(doc),
        "pages": []
    }

    # 循环按页提取
    for page_idx, page in enumerate(doc):
        page_number = page_idx + 1

        # 提取当前页的所有完整文本（用于快速全局预览）
        full_text = page.get_text("text")

        page_dict = {
            "page_number": page_number,
            "text": full_text,
            "blocks": []
        }

        # 使用 "blocks" 模式提取，该模式返回一个元组列表
        # 每个 block 元组的结构为: (x0, y0, x1, y1, "文本内容", block_no, block_type)
        raw_blocks = page.get_text("blocks")

        for reading_idx, block in enumerate(raw_blocks):
            x0, y0, x1, y1, block_text, block_no, block_type_id = block

            # 清洗文本：去除首尾多余空格
            clean_text = block_text.strip()
            if not clean_text:
                continue  # 忽略完全空白的块

            # 区分文本块和图像块 (block_type_id = 0 是文本，1 是图像)
            block_type = "text" if block_type_id == 0 else "image"

            # 组装像素级元数据 block
            block_data = {
                "block_id": f"{doc_id}_p{page_number}_b{reading_idx + 1}",
                "type": block_type,
                "text": clean_text,
                "bbox": [round(x0, 2), round(y0, 2), round(x1, 2), round(y1, 2)],
                "reading_order": reading_idx + 1,
                "section_hint": None  # 基准阶段先留空，后续 Chunking 阶段由算法根据字体/样式动态识别
            }
            page_dict["blocks"].append(block_data)

        parsed_data["pages"].append(page_dict)

    # 确保输出的目录存在
    output_json_path.parent.mkdir(parents=True, exist_ok=True)

    # 导出为规范的 JSON 文件
    try:
        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(parsed_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logging.error(f"JSON export failure: {str(e)}")
        return False


if __name__ == "__main__":

    success_count = 0

    # 动态扫描在 src/config.py 中定义好的黄金测试三角文件
    for doc_id, pdf_path in TARGET_PDFS.items():
        # 统一输出路径格式：PARSED_JSON_DIR / {doc_id}.json
        output_json_name = f"{doc_id}.json"
        output_json_path = PARSED_JSON_DIR / output_json_name

        # 执行物理剥离
        is_ok = parse_pdf_to_json(pdf_path, doc_id, output_json_path)
        if is_ok:
            success_count += 1
