#!/usr/bin/env python3
"""Fetch a paper from a URL and print extracted text to stdout.

Usage: python3 fetch_web.py <url>

Prints:
  TITLE: <best-effort title, may be empty>
  <blank line>
  <extracted body text>
"""
import sys
import re
import io
import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; paper-summarizer-skill/1.0)"
}


def fetch_arxiv_abs(url: str):
    """Special-case arxiv abstract pages: fast, structured, reliable."""
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    title_tag = soup.find("h1", class_="title")
    title = title_tag.get_text(" ", strip=True) if title_tag else ""
    title = re.sub(r"^Title:\s*", "", title).strip()

    authors_tag = soup.find("div", class_="authors")
    authors = authors_tag.get_text(" ", strip=True) if authors_tag else ""
    authors = re.sub(r"^Authors:\s*", "", authors).strip()

    abstract_tag = soup.find("blockquote", class_="abstract")
    abstract = abstract_tag.get_text(" ", strip=True) if abstract_tag else ""
    abstract = re.sub(r"^Abstract:\s*", "", abstract).strip()

    body = []
    if authors:
        body.append(f"Authors: {authors}")
    if abstract:
        body.append(f"Abstract: {abstract}")
    return title, "\n\n".join(body)


def fetch_pdf(url: str):
    import pdfplumber

    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    text_parts = []
    title = ""
    with pdfplumber.open(io.BytesIO(r.content)) as pdf:
        meta = pdf.metadata or {}
        title = (meta.get("Title") or "").strip()
        # Cap pages to keep extraction fast/bounded for very long PDFs.
        for page in pdf.pages[:40]:
            t = page.extract_text()
            if t:
                text_parts.append(t)
    return title, "\n\n".join(text_parts)


def fetch_generic(url: str):
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    ctype = r.headers.get("Content-Type", "")
    if "application/pdf" in ctype or url.lower().endswith(".pdf"):
        return fetch_pdf(url)

    soup = BeautifulSoup(r.text, "html.parser")
    title = soup.title.get_text(strip=True) if soup.title else ""

    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    # Prefer <article> or <main> if present, else fall back to body.
    main = soup.find("article") or soup.find("main") or soup.body or soup
    text = main.get_text("\n", strip=True)
    # Collapse excessive blank lines.
    text = re.sub(r"\n{3,}", "\n\n", text)
    return title, text


def main():
    if len(sys.argv) < 2:
        print("Usage: fetch_web.py <url>", file=sys.stderr)
        sys.exit(1)
    url = sys.argv[1]

    try:
        if "arxiv.org/abs/" in url:
            # 优先用 PDF：把 abs 链接自动转成 pdf 链接再抓取全文
            url = url.replace("arxiv.org/abs/", "arxiv.org/pdf/")
            title, text = fetch_pdf(url)
        elif "arxiv.org/pdf/" in url:
            title, text = fetch_pdf(url)
        else:
            title, text = fetch_generic(url)
    except Exception as e:
        print(f"TITLE:", flush=True)
        print(f"\n[fetch_web.py error] Failed to fetch or parse {url}: {e}",
            file=sys.stderr)
        sys.exit(1)

    print(f"TITLE: {title}")
    print()
    print(text)


if __name__ == "__main__":
    main()
