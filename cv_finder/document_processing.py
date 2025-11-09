from __future__ import annotations

import base64
import binascii
from io import BytesIO
from typing import Iterable, List

from docx import Document
from docx.document import Document as DocumentType
from docx.table import Table
from docx.text.paragraph import Paragraph


def decode_base64_document(encoded: str) -> bytes:
    try:
        return base64.b64decode(encoded)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("documentContent is not valid base64 data") from exc


def _load_docx(encoded: str) -> DocumentType:
    raw_bytes = decode_base64_document(encoded)
    try:
        return Document(BytesIO(raw_bytes))
    except Exception as exc:  # python-docx raises several internal errors
        raise ValueError("Unable to parse Word document") from exc


def word_to_plain_text(encoded: str) -> str:
    doc = _load_docx(encoded)
    lines: List[str] = []
    for block in _iterate_blocks(doc):
        if isinstance(block, Paragraph):
            text = block.text.strip()
            if text:
                lines.append(text)
        elif isinstance(block, Table):
            lines.extend(_table_to_plain(block))
    return "\n".join(lines).strip()


def word_to_markdown(encoded: str) -> str:
    doc = _load_docx(encoded)
    lines: List[str] = []
    for block in _iterate_blocks(doc):
        if isinstance(block, Paragraph):
            markdown_line = _paragraph_to_markdown(block)
            if markdown_line:
                lines.append(markdown_line)
        elif isinstance(block, Table):
            lines.extend(_table_to_markdown(block))
    return "\n".join(lines).strip()


def _iterate_blocks(parent) -> Iterable[Paragraph | Table]:
    if isinstance(parent, DocumentType):
        parent_elm = parent.element.body
    else:
        parent_elm = parent._element  # type: ignore[attr-defined]

    for child in parent_elm.iterchildren():
        if child.tag.endswith("}p"):
            yield Paragraph(child, parent)
        elif child.tag.endswith("}tbl"):
            yield Table(child, parent)


def _paragraph_to_markdown(paragraph: Paragraph) -> str:
    text = paragraph.text.strip()
    if not text:
        return ""

    style_name = paragraph.style.name if paragraph.style else ""
    level_prefix = ""
    if style_name.startswith("Heading"):
        level = _parse_heading_level(style_name)
        level_prefix = "#" * max(1, level)
        return f"{level_prefix} {text}".strip()

    if _has_numbering(paragraph):
        return f"- {text}"

    return text


def _parse_heading_level(style_name: str) -> int:
    for token in style_name.split():
        if token.isdigit():
            return int(token)
    return 1


def _has_numbering(paragraph: Paragraph) -> bool:
    p_pr = paragraph._p.pPr if paragraph._p is not None else None
    if p_pr is not None and getattr(p_pr, "numPr", None) is not None:
        return True
    text = paragraph.text.lstrip()
    if text.startswith(('-', '*')):
        return True
    if len(text) > 2 and text[1] == '.' and text[0].isdigit():
        return True
    return False


def _table_to_plain(table: Table) -> List[str]:
    rows = []
    for row in table.rows:
        cells = [cell.text.strip() for cell in row.cells]
        rows.append("\t".join(cells))
    return rows


def _table_to_markdown(table: Table) -> List[str]:
    markdown_lines: List[str] = []
    if not table.rows:
        return markdown_lines

    header_cells = [cell.text.strip() or " " for cell in table.rows[0].cells]
    header = " | ".join(header_cells)
    separator = " | ".join("---" for _ in header_cells)
    markdown_lines.extend([f"| {header} |", f"| {separator} |"])

    for row in table.rows[1:]:
        cells = [cell.text.strip() or " " for cell in row.cells]
        markdown_lines.append(f"| {' | '.join(cells)} |")

    return markdown_lines
