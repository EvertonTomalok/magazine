import asyncio
from logging import INFO, getLogger

import backoff
from requests_html import AsyncHTMLSession

from crawler_magazine.downloader import BaseDownloader

logger = getLogger()
logger.setLevel(INFO)


class AsyncDownloader(BaseDownloader):
    def __init__(self, header: dict = None, proxy: dict = None):
        super().__init__(header, proxy)
        self.asession = AsyncHTMLSession()

    def __del__(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.asession.close())

    @property
    def cookies(self):
        return self.asession.cookies

    async def get(self, url, *args, **kwargs):
        """
        Example:
            payload = {'some': 'data'}
            headers = {'content-type': 'application/json'}
            params = {'key1': 'value1', 'key2': 'value2'}
        """
        return await self.execute("get", url, *args, **kwargs)

    async def post(self, url, *args, **kwargs):
        """
        Example:
            payload = {'some': 'data'}
            headers = {'content-type': 'application/json'}
            params = {'key1': 'value1', 'key2': 'value2'}
        """
        return await self.execute("post", url, *args, **kwargs)

    @backoff.on_exception(
        backoff.expo,
        Exception,
        max_tries=3,
        max_time=30,
    )
    async def execute(
        self,
        method: str,
        url,
        headers: dict = None,
        json: dict = None,
        params: dict = None,
        cookies=None,
        payload=None,
        files=None,
        timeout: int = 60,
    ):
        if method.lower() not in ["get", "post"]:
            raise ValueError

        content = dict()
        content["headers"] = headers if headers else self.custom_header

        if payload:
            content["data"] = payload
        if json:
            content["json"] = json
        if params:
            content["params"] = params
        if cookies:
            content["cookies"] = cookies
        if files:
            content["files"] = files
        if timeout:
            content["timeout"] = timeout
        if self.proxies:
            content["proxies"] = self.proxies

        return await self.asession.request(method, url, **content)
