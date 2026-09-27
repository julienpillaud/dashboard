import httpx2
from tactill import AsyncTactillClient


class TactillClientFactory:
    def __init__(self, http_client: httpx2.AsyncClient) -> None:
        self._http_client = http_client
        self._clients: dict[str, AsyncTactillClient] = {}

    async def get(self, api_key: str) -> AsyncTactillClient:
        client = self._clients.get(api_key)
        if client is None:
            client = await AsyncTactillClient.create(api_key, self._http_client)
            self._clients[api_key] = client
        return client
