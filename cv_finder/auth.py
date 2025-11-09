from __future__ import annotations

import json
from typing import Any

import azure.functions as func

from .settings import is_valid_api_key


def _extract_api_key(req: func.HttpRequest) -> str | None:
    header_key = req.headers.get("x-api-key")
    if header_key:
        return header_key

    query_key = req.params.get("apiKey")
    if query_key:
        return query_key

    if req.method in {"POST", "PUT", "PATCH"}:
        try:
            payload: Any = req.get_json()
        except ValueError:
            return None
        if isinstance(payload, dict):
            body_key = payload.get("apiKey")
            if isinstance(body_key, str):
                return body_key
    return None


def authorize_request(req: func.HttpRequest) -> bool:
    return is_valid_api_key(_extract_api_key(req))


def unauthorized_response() -> func.HttpResponse:
    body = {"statusCode": 401, "statusCodeDescription": "Unauthorized"}
    return func.HttpResponse(
        json.dumps(body),
        status_code=401,
        mimetype="application/json",
    )
