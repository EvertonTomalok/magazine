from abc import ABC, abstractmethod

from crawler_magazine.downloader.asynchronous import AsyncDownloader


class CrawlerInterface(ABC):
    def __init__(self, url):
        self.url = url
        self.downloader = AsyncDownloader()

    async def get_page(self, url=None):
        return await self.downloader.get(url or self.url)

    @abstractmethod
    def parse(self, html):
        """Need to be implemented"""

    @abstractmethod
    def crawl(self):
        """Need to be implemented"""
