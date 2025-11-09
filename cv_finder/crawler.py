from __future__ import annotations

import base64
import mimetypes
import re
from collections import deque
from dataclasses import dataclass
from typing import Iterable
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

USER_AGENT = "CVFinderBot/1.0"
MAX_DEPTH = 3
DOCUMENT_EXTENSIONS = {".pdf", ".doc", ".docx", ".rtf"}
DOCUMENT_MIME_PREFIXES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/rtf",
}
CV_TOKENS = {"cv", "resume", "resumes", "vita", "vitae"}
CV_PHRASES = ("curriculum vitae",)


@dataclass(slots=True)
class DocumentResult:
    document_name: str
    document_link: str
    document_type: str
    document_content: str


class CrawlError(Exception):
    pass


def _request_url(url: str) -> requests.Response | None:
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": USER_AGENT})
        if response.status_code == 200:
            return response
    except requests.RequestException:
        return None
    return None


def _looks_like_document(url: str, content_type: str | None) -> bool:
    if content_type and content_type.split(";")[0].lower() in DOCUMENT_MIME_PREFIXES:
        return True
    path = urlparse(url).path.lower()
    return any(path.endswith(ext) for ext in DOCUMENT_EXTENSIONS)


def _score_html_candidate(url: str, text: str, anchor_text: str | None, title: str | None) -> int:
    score = 0
    if _has_cv_keyword(url):
        score += 3
    if _has_cv_keyword(text):
        score += 2
    if anchor_text and _has_cv_keyword(anchor_text):
        score += 3
    if title and _has_cv_keyword(title):
        score += 3
    return score


def _encode_payload(content: bytes) -> str:
    return base64.b64encode(content).decode("ascii")


def _normalise_name(url: str) -> str:
    path = urlparse(url).path
    if not path or path.endswith("/"):
        path = path.rstrip("/")
    name = path.split("/")[-1] or "index"
    return name


def crawl_for_document(start_url: str) -> DocumentResult | None:
    if not start_url.lower().startswith("http"):
        raise CrawlError("URL must include http or https scheme")

    parsed_root = urlparse(start_url)
    allowed_netloc = parsed_root.netloc
    visited: set[str] = set()
    queue: deque[tuple[str, int, str | None]] = deque([(start_url, 0, None)])
    best_html: tuple[int, int, DocumentResult] | None = None

    while queue:
        current_url, depth, source_hint = queue.popleft()
        if current_url in visited:
            continue
        visited.add(current_url)

        response = _request_url(current_url)
        if not response:
            continue

        content_type = response.headers.get("Content-Type", "").split(";")[0].lower()

        if _looks_like_document(current_url, content_type):
            filename = _normalise_name(current_url)
            disposition = response.headers.get("Content-Disposition", "")
            if _has_cv_keyword(filename, current_url, source_hint, disposition):
                return DocumentResult(
                    document_name=filename,
                    document_link=current_url,
                    document_type=content_type or mimetypes.guess_type(current_url)[0] or "application/octet-stream",
                    document_content=_encode_payload(response.content),
                )
            continue

        if content_type.startswith("text/html"):
            html_text = response.text
            soup = BeautifulSoup(html_text, "html.parser")
            title = soup.title.string.strip() if soup.title and soup.title.string else _normalise_name(current_url)
            score = _score_html_candidate(current_url, html_text, source_hint, title)
            candidate = DocumentResult(
                document_name=title,
                document_link=current_url,
                document_type="text/html",
                document_content=_encode_payload(html_text.encode("utf-8")),
            )
            if best_html is None or score > best_html[0] or (score == best_html[0] and depth < best_html[1]):
                best_html = (score, depth, candidate)

            if depth < MAX_DEPTH:
                links = _extract_links(current_url, soup)
                for link, link_text in links:
                    parsed_link = urlparse(link)
                    if parsed_link.scheme in {"http", "https"} and parsed_link.netloc == allowed_netloc:
                        queue.append((link, depth + 1, link_text or source_hint))

    if best_html and best_html[0] > 0:
        return best_html[2]
    return None


def _extract_links(base_url: str, soup: BeautifulSoup) -> Iterable[tuple[str, str | None]]:
    anchors = soup.find_all("a", href=True)
    for anchor in anchors:
        href = anchor.get("href")
        if not href or href.startswith("mailto:"):
            continue
        cleaned = href.strip()
        if cleaned.startswith("#"):
            continue
        if cleaned.startswith("javascript:"):
            continue
        absolute = urljoin(base_url, cleaned)
        link_text = anchor.get_text(strip=True) or None
        yield absolute, link_text


def _has_cv_keyword(*parts: str | None) -> bool:
    for part in parts:
        if not part:
            continue
        normalised = re.sub(r"[^a-z0-9]+", " ", part.lower())
        if any(phrase in normalised for phrase in CV_PHRASES):
            return True
        tokens = normalised.split()
        if any(token in CV_TOKENS for token in tokens):
            return True
    return False
