#!/usr/bin/env python3
"""Extract text from a local paper file (.pdf, .docx, .txt, .md).

Usage: python3 extract_local.py <file_path>

Prints:
  TITLE: <best-effort title, may be empty>
  <blank line>
  <extracted body text>
"""
import sys
import os


def extract_pdf(path: str):
    import pdfplumber

    title = ""
    parts = []
    with pdfplumber.open(path) as pdf:
        meta = pdf.metadata or {}
        title = (meta.get("Title") or "").strip()
        for page in pdf.pages[:40]:
            t = page.extract_text()
            if t:
                parts.append(t)
    return title, "\n\n".join(parts)


def extract_docx(path: str):
    import docx

    d = docx.Document(path)
    paras = [p.text for p in d.paragraphs if p.text.strip()]
    title = paras[0] if paras else ""
    return title, "\n\n".join(paras)


def extract_text_file(path: str):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    first_line = content.strip().splitlines()[0] if content.strip() else ""
    title = first_line.lstrip("# ").strip()
    return title, content


def main():
    if len(sys.argv) < 2:
        print("Usage: extract_local.py <file_path>", file=sys.stderr)
        sys.exit(1)
    path = sys.argv[1]
    if not os.path.exists(path):
        print(f"[extract_local.py error] File not found: {path}", file=sys.stderr)
        sys.exit(1)

    ext = os.path.splitext(path)[1].lower()
    try:
        if ext == ".pdf":
            title, text = extract_pdf(path)
        elif ext == ".docx":
            title, text = extract_docx(path)
        elif ext in (".txt", ".md"):
            title, text = extract_text_file(path)
        else:
            print(f"[extract_local.py error] Unsupported file type: {ext}",
                  file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"[extract_local.py error] Failed to extract {path}: {e}",
              file=sys.stderr)
        sys.exit(1)

    print(f"TITLE: {title}")
    print()
    print(text)


if __name__ == "__main__":
    main()
