import argparse
import json
import re
from pathlib import Path


SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md", ".docx"}


def normalize_text(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = text.replace("\ufeff", "")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    lines = [line.strip() for line in text.split("\n")]
    cleaned_lines = [line for line in lines if line]
    return "\n".join(cleaned_lines).strip()


def extract_pdf_text(file_path: Path) -> str:
    try:
        import fitz
    except Exception:
        fitz = None
    if fitz is not None:
        chunks = []
        with fitz.open(file_path) as doc:
            for page in doc:
                page_text = page.get_text("text")
                if page_text:
                    chunks.append(page_text)
        return "\n".join(chunks)
    try:
        from pypdf import PdfReader
    except Exception as exc:
        raise RuntimeError("未安装可用的 PDF 文本抽取库，请安装 PyMuPDF 或 pypdf") from exc
    reader = PdfReader(str(file_path))
    chunks = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        if page_text:
            chunks.append(page_text)
    return "\n".join(chunks)


def extract_docx_text(file_path: Path) -> str:
    try:
        from docx import Document
    except Exception as exc:
        raise RuntimeError("处理 docx 需要安装 python-docx") from exc
    document = Document(str(file_path))
    return "\n".join(paragraph.text for paragraph in document.paragraphs if paragraph.text)


def load_text(file_path: Path) -> str:
    ext = file_path.suffix.lower()
    if ext == ".pdf":
        return extract_pdf_text(file_path)
    if ext == ".docx":
        return extract_docx_text(file_path)
    if ext in {".txt", ".md"}:
        return file_path.read_text(encoding="utf-8", errors="ignore")
    raise ValueError(f"不支持的文件格式: {file_path.name}")


def process_file(file_path: Path, output_dir: Path) -> dict:
    raw = load_text(file_path)
    cleaned = normalize_text(raw)
    output_file = output_dir / f"{file_path.stem}.cleaned.txt"
    output_file.write_text(cleaned, encoding="utf-8")
    return {
        "source_file": file_path.name,
        "source_ext": file_path.suffix.lower(),
        "raw_chars": len(raw),
        "cleaned_chars": len(cleaned),
        "output_file": output_file.name,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", default="domain_docs")
    parser.add_argument("--output-dir", default="cleaned_docs")
    parser.add_argument("--report-file", default="preprocess_report.json")
    args = parser.parse_args()

    input_dir = Path(args.input_dir).resolve()
    output_dir = Path(args.output_dir).resolve()
    report_file = Path(args.report_file).resolve()

    if not input_dir.exists():
        raise FileNotFoundError(f"输入目录不存在: {input_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)
    records = []
    for file_path in sorted(input_dir.iterdir(), key=lambda p: p.name.lower()):
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        try:
            records.append(process_file(file_path, output_dir))
        except Exception as exc:
            records.append(
                {
                    "source_file": file_path.name,
                    "source_ext": file_path.suffix.lower(),
                    "error": str(exc),
                }
            )

    summary = {
        "input_dir": str(input_dir),
        "output_dir": str(output_dir),
        "total_files": len(records),
        "success_files": sum(1 for x in records if "error" not in x),
        "failed_files": sum(1 for x in records if "error" in x),
        "records": records,
    }
    report_file.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
