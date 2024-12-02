

from .basesdk import BaseSDK
from .httpclient import AsyncHttpClient, HttpClient
from .sdkconfiguration import SDKConfiguration
from .utils.logger import Logger, get_default_logger
from .utils.retries import RetryConfig
from defendai_wozway import models, utils
from defendai_wozway._hooks import SDKHooks
from defendai_wozway.activities import Activities
from defendai_wozway.api_keys import APIKeys
from defendai_wozway.applications import Applications
from defendai_wozway.connections import Connections
from defendai_wozway.incidents import Incidents
from defendai_wozway.policies import Policies
from defendai_wozway.types import OptionalNullable, UNSET
from defendai_wozway.users import Users
import httpx
from typing import Any, Callable, Dict, Optional, Union


class Wozway(BaseSDK):
    r"""DefendAi API docs: API documentation for the defendai backend system"""

    activities: Activities
    api_keys: APIKeys
    applications: Applications
    connections: Connections
    incidents: Incidents
    policies: Policies
    users: Users

    def __init__(
        self,
        bearer_auth: Optional[Union[Optional[str], Callable[[], Optional[str]]]] = None,
        server_idx: Optional[int] = None,
        server_url: Optional[str] = None,
        url_params: Optional[Dict[str, str]] = None,
        client: Optional[HttpClient] = None,
        async_client: Optional[AsyncHttpClient] = None,
        retry_config: OptionalNullable[RetryConfig] = UNSET,
        timeout_ms: Optional[int] = None,
        debug_logger: Optional[Logger] = None,
    ) -> None:
        r"""Instantiates the SDK configuring it with the provided parameters.

        :param bearer_auth: The bearer_auth required for authentication
        :param server_idx: The index of the server to use for all methods
        :param server_url: The server URL to use for all methods
        :param url_params: Parameters to optionally template the server URL with
        :param client: The HTTP client to use for all synchronous methods
        :param async_client: The Async HTTP client to use for all asynchronous methods
        :param retry_config: The retry configuration to use for all supported methods
        :param timeout_ms: Optional request timeout applied to each operation in milliseconds
        """
        if client is None:
            client = httpx.Client()

        assert issubclass(
            type(client), HttpClient
        ), "The provided client must implement the HttpClient protocol."

        if async_client is None:
            async_client = httpx.AsyncClient()

        if debug_logger is None:
            debug_logger = get_default_logger()

        assert issubclass(
            type(async_client), AsyncHttpClient
        ), "The provided async_client must implement the AsyncHttpClient protocol."

        security: Any = None
        if callable(bearer_auth):
            security = lambda: models.Security(bearer_auth=bearer_auth())  # pylint: disable=unnecessary-lambda-assignment
        else:
            security = models.Security(bearer_auth=bearer_auth)

        if server_url is not None:
            if url_params is not None:
                server_url = utils.template_url(server_url, url_params)

        BaseSDK.__init__(
            self,
            SDKConfiguration(
                client=client,
                async_client=async_client,
                security=security,
                server_url=server_url,
                server_idx=server_idx,
                retry_config=retry_config,
                timeout_ms=timeout_ms,
                debug_logger=debug_logger,
            ),
        )

        hooks = SDKHooks()

        current_server_url, *_ = self.sdk_configuration.get_server_details()
        server_url, self.sdk_configuration.client = hooks.sdk_init(
            current_server_url, self.sdk_configuration.client
        )
        if current_server_url != server_url:
            self.sdk_configuration.server_url = server_url

        # pylint: disable=protected-access
        self.sdk_configuration.__dict__["_hooks"] = hooks

        self._init_sdks()

    def _init_sdks(self):
        self.activities = Activities(self.sdk_configuration)
        self.api_keys = APIKeys(self.sdk_configuration)
        self.applications = Applications(self.sdk_configuration)
        self.connections = Connections(self.sdk_configuration)
        self.incidents = Incidents(self.sdk_configuration)
        self.policies = Policies(self.sdk_configuration)
        self.users = Users(self.sdk_configuration)

    def __enter__(self):
        return self

    async def __aenter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.sdk_configuration.client is not None:
            self.sdk_configuration.client.close()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.sdk_configuration.async_client is not None:
            await self.sdk_configuration.async_client.aclose()
