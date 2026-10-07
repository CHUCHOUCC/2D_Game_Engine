import httpx


class AiServiceError(Exception):
    """The AI service could not be reached or answered with an error."""


class AiServiceClient:
    """The backend's only way to talk to the separate AI service.

    It sends the shared service key so the AI service knows the call comes
    from the backend. The frontend never reaches the AI service directly.
    """

    def __init__(self, base_url: str, service_key: str, transport=None, timeout: float = 60.0):
        self._base_url = base_url.rstrip("/")
        self._service_key = service_key
        self._transport = transport
        # Generous timeout: a sleeping free-tier service needs time to wake up.
        self._timeout = timeout

    def generate(self, prompt: str) -> list:
        try:
            with httpx.Client(transport=self._transport, timeout=self._timeout) as client:
                response = client.post(
                    f"{self._base_url}/generate",
                    json={"prompt": prompt},
                    headers={"X-Service-Key": self._service_key},
                )
            response.raise_for_status()
            return response.json()["objects"]
        except (httpx.HTTPError, KeyError, ValueError) as error:
            raise AiServiceError(f"AI service call failed: {type(error).__name__}") from error
