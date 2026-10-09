import json

import httpx
import jwt
import pytest

from app.ai_client import AiServiceClient, AiServiceError

KEY = "s3cret-shared-service-key-32-characters"


def client_with(handler):
    return AiServiceClient("https://ai.example.com/", KEY, transport=httpx.MockTransport(handler))


def bearer(request):
    return request.headers["authorization"].removeprefix("Bearer ")


def test_generate_sends_the_prompt_and_a_signed_service_token():
    seen = {}

    def handler(request):
        seen["url"] = str(request.url)
        seen["token"] = bearer(request)
        seen["body"] = json.loads(request.content)
        return httpx.Response(200, json={"objects": [{"id": "a", "kind": "box", "x": 1, "y": 2}]})

    objects = client_with(handler).generate("a box")

    assert objects == [{"id": "a", "kind": "box", "x": 1, "y": 2}]
    assert seen["url"] == "https://ai.example.com/generate"
    assert seen["body"] == {"prompt": "a box", "scene": []}
    claims = jwt.decode(seen["token"], KEY, algorithms=["HS256"], audience="ai-service")
    assert claims["iss"] == "2d-engine-backend"
    assert claims["exp"] - claims["iat"] == 60


def test_the_raw_key_is_never_sent():
    def handler(request):
        assert KEY not in str(request.headers)
        return httpx.Response(200, json={"objects": []})

    client_with(handler).generate("x")


def test_obstacles_sends_model_scene_and_count():
    seen = {}

    def handler(request):
        seen["path"] = request.url.path
        seen["body"] = json.loads(request.content)
        return httpx.Response(200, json={"objects": [], "difficulty": 0.7})

    reply = client_with(handler).obstacles({"w": 1}, [], 4)
    assert reply["difficulty"] == 0.7
    assert seen == {"path": "/obstacles", "body": {"model": {"w": 1}, "scene": [], "count": 4}}


def test_learn_returns_the_updated_model():
    def handler(request):
        return httpx.Response(200, json={"model": {"runs": 1}, "reward": 0.2, "difficulty": 0.55})

    assert client_with(handler).learn({}, {"outcome": "won"})["model"] == {"runs": 1}


def test_learn_without_a_model_is_an_error():
    with pytest.raises(AiServiceError):
        client_with(lambda request: httpx.Response(200, json={"reward": 1})).learn({}, {})


def test_error_status_becomes_ai_service_error():
    with pytest.raises(AiServiceError):
        client_with(lambda request: httpx.Response(502)).generate("x")


def test_unexpected_reply_becomes_ai_service_error():
    with pytest.raises(AiServiceError):
        client_with(lambda request: httpx.Response(200, json={"nope": 1})).generate("x")
    with pytest.raises(AiServiceError):
        client_with(lambda request: httpx.Response(200, json=[1, 2])).generate("x")


def test_network_failure_becomes_ai_service_error():
    def handler(request):
        raise httpx.ConnectError("unreachable")

    with pytest.raises(AiServiceError):
        client_with(handler).generate("x")
