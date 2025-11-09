from __future__ import annotations

import json
from typing import Any

import azure.functions as func

from cv_finder.auth import authorize_request, unauthorized_response
from cv_finder.crawler import CrawlError, crawl_for_document
from cv_finder.document_processing import (
    pdf_to_markdown,
    pdf_to_plain_text,
    word_to_markdown,
    word_to_plain_text,
)

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


@app.function_name(name="findCVOnHomepage")
@app.route(route="findCVOnHomepage", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def find_cv_on_homepage(req: func.HttpRequest) -> func.HttpResponse:
    if not authorize_request(req):
        return unauthorized_response()

    url = req.params.get("url")
    if not url:
        body = {"statusCode": 400, "statusCodeDescription": "Bad Request", "message": "url parameter is required"}
        return func.HttpResponse(json.dumps(body), status_code=400, mimetype="application/json")

    try:
        result = crawl_for_document(url)
    except CrawlError as exc:
        body = {"statusCode": 400, "statusCodeDescription": "Bad Request", "message": str(exc)}
        return func.HttpResponse(json.dumps(body), status_code=400, mimetype="application/json")

    if not result:
        body = {"statusCode": 404, "statusCodeDescription": "Not Found"}
        return func.HttpResponse(json.dumps(body), status_code=404, mimetype="application/json")

    body = {
        "documentName": result.document_name,
        "documentLink": result.document_link,
        "documentType": result.document_type,
        "documentContent": result.document_content,
        "statusCode": 200,
        "statusCodeDescription": "OK",
    }
    return func.HttpResponse(json.dumps(body), status_code=200, mimetype="application/json")


@app.function_name(name="wordToPlainText")
@app.route(route="wordToPlainText", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def word_to_plain_text_handler(req: func.HttpRequest) -> func.HttpResponse:
    if not authorize_request(req):
        return unauthorized_response()

    payload = _safe_json(req)
    document_content = _extract_document_content(payload)
    if document_content is None:
        body = {"statusCode": 400, "statusCodeDescription": "Bad Request", "message": "documentContent must be provided"}
        return func.HttpResponse(json.dumps(body), status_code=400, mimetype="application/json")

    try:
        text_output = word_to_plain_text(document_content)
    except ValueError as exc:
        body = {"statusCode": 400, "statusCodeDescription": "Bad Request", "message": str(exc)}
        return func.HttpResponse(json.dumps(body), status_code=400, mimetype="application/json")

    body = {
        "documentText": text_output,
        "statusCode": 200,
        "statusCodeDescription": "OK",
    }
    return func.HttpResponse(json.dumps(body), status_code=200, mimetype="application/json")


@app.function_name(name="wordToMarkdown")
@app.route(route="wordToMarkdown", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def word_to_markdown_handler(req: func.HttpRequest) -> func.HttpResponse:
    if not authorize_request(req):
        return unauthorized_response()

    payload = _safe_json(req)
    document_content = _extract_document_content(payload)
    if document_content is None:
        body = {"statusCode": 400, "statusCodeDescription": "Bad Request", "message": "documentContent must be provided"}
        return func.HttpResponse(json.dumps(body), status_code=400, mimetype="application/json")

    try:
        markdown_output = word_to_markdown(document_content)
    except ValueError as exc:
        body = {"statusCode": 400, "statusCodeDescription": "Bad Request", "message": str(exc)}
        return func.HttpResponse(json.dumps(body), status_code=400, mimetype="application/json")

    body = {
        "documentMarkdown": markdown_output,
        "statusCode": 200,
        "statusCodeDescription": "OK",
    }
    return func.HttpResponse(json.dumps(body), status_code=200, mimetype="application/json")


@app.function_name(name="pdfToPlainText")
@app.route(route="pdfToPlainText", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def pdf_to_plain_text_handler(req: func.HttpRequest) -> func.HttpResponse:
    if not authorize_request(req):
        return unauthorized_response()

    payload = _safe_json(req)
    document_content = _extract_document_content(payload)
    if document_content is None:
        body = {"statusCode": 400, "statusCodeDescription": "Bad Request", "message": "documentContent must be provided"}
        return func.HttpResponse(json.dumps(body), status_code=400, mimetype="application/json")

    try:
        text_output = pdf_to_plain_text(document_content)
    except ValueError as exc:
        body = {"statusCode": 400, "statusCodeDescription": "Bad Request", "message": str(exc)}
        return func.HttpResponse(json.dumps(body), status_code=400, mimetype="application/json")

    body = {
        "documentText": text_output,
        "statusCode": 200,
        "statusCodeDescription": "OK",
    }
    return func.HttpResponse(json.dumps(body), status_code=200, mimetype="application/json")


@app.function_name(name="pdfToMarkdown")
@app.route(route="pdfToMarkdown", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def pdf_to_markdown_handler(req: func.HttpRequest) -> func.HttpResponse:
    if not authorize_request(req):
        return unauthorized_response()

    payload = _safe_json(req)
    document_content = _extract_document_content(payload)
    if document_content is None:
        body = {"statusCode": 400, "statusCodeDescription": "Bad Request", "message": "documentContent must be provided"}
        return func.HttpResponse(json.dumps(body), status_code=400, mimetype="application/json")

    try:
        markdown_output = pdf_to_markdown(document_content)
    except ValueError as exc:
        body = {"statusCode": 400, "statusCodeDescription": "Bad Request", "message": str(exc)}
        return func.HttpResponse(json.dumps(body), status_code=400, mimetype="application/json")

    body = {
        "documentMarkdown": markdown_output,
        "statusCode": 200,
        "statusCodeDescription": "OK",
    }
    return func.HttpResponse(json.dumps(body), status_code=200, mimetype="application/json")


def _safe_json(req: func.HttpRequest) -> dict[str, Any]:
    try:
        payload = req.get_json()
    except ValueError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _extract_document_content(payload: dict[str, Any]) -> str | None:
    value = payload.get("documentContent")
    return value if isinstance(value, str) and value else None
