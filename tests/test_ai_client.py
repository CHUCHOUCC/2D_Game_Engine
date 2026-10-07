import json

import httpx
import pytest

from app.ai_client import AiServiceClient, AiServiceError


def client_with(handler):
    return AiServiceClient("https://ai.example.com/", "s3cret", transport=httpx.MockTransport(handler))


def test_generate_sends_the_prompt_and_the_service_key():
    seen = {}

    def handler(request):
        seen["url"] = str(request.url)
        seen["key"] = request.headers["x-service-key"]
        seen["body"] = json.loads(request.content)
        return httpx.Response(200, json={"objects": [{"id": "a", "kind": "box", "x": 1, "y": 2}]})

    objects = client_with(handler).generate("a box")

    assert objects == [{"id": "a", "kind": "box", "x": 1, "y": 2}]
    assert seen["url"] == "https://ai.example.com/generate"
    assert seen["key"] == "s3cret"
    assert seen["body"] == {"prompt": "a box"}


def test_error_status_becomes_ai_service_error():
    with pytest.raises(AiServiceError):
        client_with(lambda request: httpx.Response(502)).generate("x")


def test_unexpected_reply_becomes_ai_service_error():
    with pytest.raises(AiServiceError):
        client_with(lambda request: httpx.Response(200, json={"nope": 1})).generate("x")


def test_network_failure_becomes_ai_service_error():
    def handler(request):
        raise httpx.ConnectError("unreachable")

    with pytest.raises(AiServiceError):
        client_with(handler).generate("x")
