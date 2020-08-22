import json
from logging import getLogger, INFO

from crawler_magazine.crawlers import CrawlerInterface
from crawler_magazine.model.product import PartialProduct
from crawler_magazine.model.utils import validate_and_parse_model, validate_model
from crawler_magazine.utils.strings import normalize_text

from pprint import pprint

logger = getLogger()
logger.setLevel(INFO)


class IteratorPageCrawler(CrawlerInterface):
    def __init__(self, url, max_iteration=100):
        super().__init__(url)
        self.max_iteration = max_iteration

    def parse(self, html, json_=None, product_page_info=None):
        if not json_:
            json_ = self._get_data_json(html)
        return self._find_products(json_, product_page_info)

    async def crawl(self):
        return await self._iterate_and_find_partial_products()

    async def _iterate_and_find_partial_products(
            self,
            index: int = 1,
            partial_products=None
    ) -> list:
        if not partial_products:
            partial_products = []

        page = await self.get_page(
            self.url.format(index)
        )

        product_page_info = self.get_product_market_info(page)

        json_ = self._get_data_json(page)
        last_page = self._get_last_page(json_)

        partial_products.extend(
            self.parse(page, json_, product_page_info)
        )

        return (
            partial_products
            if (index == last_page or index == self.max_iteration)
            else await self._iterate_and_find_partial_products(
                index + 1, partial_products
            )
        )

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
    def _find_products(json_, product_page_info) -> list:
        products = []
        for product_info in json_.get(
                "props", {}
            ).get(
                "initialState", {}
            ).get(
                "products", {}
            ).get(
                "navigationShowcase", []
        ):
            installment = (
                product_info["installment"]
                if product_info.get("installment")
                else {}
            )
            product = {
                "url": product_info.get("url"),
                "image_url": product_info.get("imageUrl"),
                "preco_por": installment.get("totalValue"),
                "parcelas": installment.get("quantity"),
                "valor_parcela": installment.get("value"),
                "marca": normalize_text(product_info.get("brand", "")),
                "taxa_de_juros": normalize_text(installment.get("description", "")),
                "estoque": "S" if installment else "N",
            }
            product.update(product_page_info)
            try:
                products.append(
                    validate_and_parse_model(product, PartialProduct)
                )
            except Exception as err:
                logger.error(
                    "Something went wrong trying to crawl a product - "
                    f"{type(err)} - {err}"
                )

        return products

    @staticmethod
    def get_product_market_info(page_html) -> dict:
        default_return = {
            "department": None,
            "category": None,
            "sub_category": None,
        }

        if group := page_html.html.xpath("//nav[@aria-label='Breadcrumb']/ol/li/a"):
            if len(group) == 4:
                return {
                    "department": normalize_text(group[1].text),
                    "category": normalize_text(group[2].text),
                    "sub_category": normalize_text(group[3].text),
                }
            return default_return
        return default_return


if __name__ == '__main__':
    import asyncio
    page_crawler = IteratorPageCrawler(
        "https://www.magazineluiza.com.br/aquecedor-eletrico/"
        "ar-e-ventilacao/s/ar/arae/brand---mondial?page={}"
    )
    loop = asyncio.get_event_loop()
    URLS = loop.run_until_complete(page_crawler.crawl())
    pprint(URLS)
    print(len(URLS))
