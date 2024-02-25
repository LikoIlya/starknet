from typing import Optional, Union, Dict, Any, List

from aiohttp import ClientSession
from loguru import logger
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.http_client import RpcHttpClient, HttpMethod


class ProxyRPCClient(RpcHttpClient):
    def __init__(self, node_url: str, session: Optional[ClientSession] = None, proxy: str = None):
        super().__init__(node_url, session)
        self.proxy_url = proxy

    async def _make_request(
            self,
            session: ClientSession,
            address: str,
            http_method: HttpMethod,
            params: dict,
            payload: dict,
    ) -> dict:
        try:
            if self.proxy_url:
                logger.warning(f"Proxying via: {self.proxy_url}")
            async with session.request(
                    method=http_method.value,
                    url=address,
                    params=params,
                    json=payload,
                    proxy=self.proxy_url,
                    # ssl=False
            ) as request:
                await self.handle_request_error(request)
                return await request.json(content_type=None)
        except: raise


class ProxyFullNodeClient(FullNodeClient):
    def __init__(
            self,
            node_url: str,
            session: Optional[ClientSession] = None,
            proxy: str = None
    ):
        super().__init__(node_url, session)
        self._client = ProxyRPCClient(node_url, session, proxy)
