import json

from crawler_magazine.crawlers import CrawlerInterface


class IteratorPageCrawler(CrawlerInterface):
    def __init__(self, url, max_iteration=100):
        super().__init__(url)
        self.max_iteration = max_iteration

    def parse(self, html, json_=None):
        if not json_:
            json_ = self._get_data_json(html)
        return self._find_product_urls(json_)

    async def crawl(self):
        return await self._iterate_and_find_partial_products()

    @staticmethod
    def _get_last_page(json_) -> int:
        if last_page := json_.get(
            "props", {}
        ).get(
            "initialState", {}
        ).get(
            "pagination", {}
        ).get("lastPage"):
            return last_page
        return 1

    @staticmethod
    def _get_data_json(request_html):
        if data := request_html.html.xpath("//script[contains(text(), '__NEXT_DATA__')]"):
            data = data[0].text.replace("__NEXT_DATA__ = ", "")
            data = data.split(";__NEXT_LOADED_PAGES__=[];")[0]
            return json.loads(data)
        return {}

    @staticmethod
    def _find_product_urls(json_) -> list:
        return [
            item.get("url")
            for item in json_.get(
                "props", {}
            ).get(
                "initialState", {}
            ).get(
                "products", {}
            ).get("navigationShowcase", [])
        ]

    async def _iterate_and_find_partial_products(self, index: int = 1, partial_products=None):
        if not partial_products:
            partial_products = []

        page = await self.get_page(
            self.url.format(index)
        )

        json_ = self._get_data_json(page)
        last_page = self._get_last_page(json_)

        partial_products.extend(
            self.parse(page, json_)
        )

        return (
            set(partial_products)
            if (index == last_page or index == self.max_iteration)
            else await self._iterate_and_find_partial_products(
                index + 1, partial_products
            )
        )


if __name__ == '__main__':
    import asyncio
    from pprint import pprint
    page_crawler = IteratorPageCrawler(
        "https://www.magazineluiza.com.br/aquecedor-eletrico/"
        "ar-e-ventilacao/s/ar/arae/brand---mondial?page={}"
    )
    loop = asyncio.get_event_loop()
    URLS = loop.run_until_complete(page_crawler.crawl())
    pprint(URLS)
