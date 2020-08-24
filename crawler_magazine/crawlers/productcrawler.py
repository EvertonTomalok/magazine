import json
import re
from logging import INFO, getLogger

import nest_asyncio

from crawler_magazine.crawlers import CrawlerInterface
from crawler_magazine.model.db import Database
from crawler_magazine.model.product import DetailProduct, PartialProduct, Product
from crawler_magazine.model.utils import validate_and_parse_model
from crawler_magazine.utils.strings import normalize_text

nest_asyncio.apply()

logger = getLogger()
logger.setLevel(INFO)


class IteratorPageCrawler(CrawlerInterface):
    def __init__(self, url, max_iteration=100):
        super().__init__(url)
        self.max_iteration = max_iteration

    def parse(self, html, json_=None, product_page_info=None):
        """
        It receives the  urrent page html json_ that has all information about products
        in the page, and the informations about actual section in page, like
        `ar e ventilação > aquecedor > aquecedor elétrico`, and return all products
        found in this page
        :param html: HTML
        :param json_: JSON { props, ... }
        :param product_page_info: JSON { departmento, categoria, subcategoria }
        :return: LIST [ PartialProduct ]
        """
        if not json_:
            json_ = self._get_data_json(html)
        return self._find_products(json_, product_page_info)

    async def crawl(self):
        return await self._iterate_and_find_partial_products()

    async def _iterate_and_find_partial_products(
        self, index: int = 1, partial_products: list = None
    ) -> list:
        """
        Iterate from all the pages and crawl information about
        products, and return a list containing it
        :param index: int
        :param partial_products: list
        :return: list [ PartialProduct ]
        """
        if not partial_products:
            partial_products = []

        page = await self.get_page(self.url.format(index))

        product_page_info = self.get_product_market_info(page)

        json_ = self._get_data_json(page)
        last_page = self._get_last_page(json_)

        partial_products.extend(self.parse(page, json_, product_page_info))

        return (
            partial_products
            if (index == last_page or index == self.max_iteration)
            else await self._iterate_and_find_partial_products(
                index + 1, partial_products
            )
        )

    @staticmethod
    def _get_last_page(json_) -> int:
        """
        Found the total pages to iterate
        :param json_: DICT
        :return: int
        """
        return (
            json_.get("props", {})
            .get("initialState", {})
            .get("pagination", {})
            .get("lastPage", 1)
        )

    @staticmethod
    def _get_data_json(request_html) -> dict:
        """
        Retrieves json who has all product info in the page and parse it
        :param request_html: Current Page
        :return: dict
        """
        if data := request_html.html.xpath(
            "//script[contains(text(), '__NEXT_DATA__')]"
        ):
            data = data[0].text.replace("__NEXT_DATA__ = ", "")
            data = data.split(";__NEXT_LOADED_PAGES__=[];")[0]
            return json.loads(data)
        return {}

    @staticmethod
    def _find_products(json_: dict, product_page_info: dict) -> list:
        """
        It receives the json_ that has all information about products in the page,
        and the informations about actual section in page, like
        `ar e ventilação > aquecedor > aquecedor elétrico`
        :param json_: JSON { props, ... }
        :param product_page_info: JSON { departmento, categoria, subcategoria }
        :return: LIST [ PartialProduct ]
        """
        products = []
        for product_info in (
            json_.get("props", {})
            .get("initialState", {})
            .get("products", {})
            .get("navigationShowcase", [])
        ):

            installment = (
                product_info["installment"] if product_info.get("installment") else {}
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
                products.append(validate_and_parse_model(product, PartialProduct))
            except Exception as err:
                logger.error(
                    "Something went wrong trying to crawl a product - "
                    f"{type(err)} - {err}"
                )

        return products

    @staticmethod
    def get_product_market_info(page_html) -> dict:
        """
        It crawl the category, department, and sub_category from page
        :param page_html: Current page HTML
        :return: dict
        """
        default_return = {
            "departmento": None,
            "categoria": None,
            "sub_categoria": None,
        }

        if group := page_html.html.xpath("//nav[@aria-label='Breadcrumb']/ol/li/a"):
            if len(group) == 4:
                return {
                    "departmento": normalize_text(group[1].text),
                    "categoria": normalize_text(group[2].text),
                    "sub_categoria": normalize_text(group[3].text),
                }
            return default_return
        return default_return


class ProductCrawler(CrawlerInterface):
    def __init__(self, url, data: dict = None):
        """
        This Class will crawl a page, based in the url received.
        If some data was passed in data argument, it'll be joined
        with the content crawled later.
        :param url: str
        :param data: dict
        """
        super().__init__(url)
        self.data = data

    def parse(self, html, *args):
        return self._extract_all_product_info(html)

    async def crawl(self):
        product_page = await self.get_page(self.url)

        # Retrieving DetailedProductInfo
        product_parsed = self.parse(product_page)
        try:
            product = validate_and_parse_model(product_parsed, DetailProduct)

            # joining PartialProductInfo with DetailedProductInfo
            if self.data:
                product.update(self.data)

            # Including data in MongoDB
            product = validate_and_parse_model(product, Product)
            with Database() as db:
                inserted_id = db.insert_update_product(product)
                print(inserted_id)
            return product
        except Exception as err:
            logger.error(
                "Something went wrong trying to crawl a product - "
                f"{type(err)} - {err}"
            )
            return {}

    def _extract_all_product_info(self, page_html) -> dict:
        """
        Crawl detail information in the current product page
        :param page_html: HTML
        :return: dict
        """
        if json_element := page_html.html.xpath(
            "//script[contains(text(), 'digitalData = ')]", first=True
        ):
            return {
                "produto": self._extract_product_name(page_html),
                "ean": self._extract_ean(json_element.html),
                "sku": self._extract_sku(json_element.html),
                "atributos": self._extract_attributes(json_element.html),
            }
        return {}

    @staticmethod
    def _extract_product_name(req_html) -> str:
        if element := req_html.html.xpath(
            "//h1[@class='header-product__title']", first=True
        ):
            return normalize_text(element.text)
        return ""

    @staticmethod
    def _extract_ean(element_html) -> str:
        ean_pattern = r'variantions.{0,100}"ean":"(.{10,25})",'
        ean_list = re.findall(ean_pattern, element_html)

        if ean_list:
            return ean_list[0]
        return "NOT FOUND"

    @staticmethod
    def _extract_sku(element_html) -> str:
        sku_pattern = r"'id': '(.*)', // parent id"
        sku_list = re.findall(sku_pattern, element_html)
        if sku_list:
            return sku_list[0]
        return "NOT FOUND"

    @staticmethod
    def _extract_attributes(element_html) -> dict:
        attr_type_pattern = r'"attributesTypes": (\[.*\]),'
        attr_value_pattern = r'attributesValues": (\[.*\]),'
        html = element_html.replace("'", '"')

        types = re.findall(attr_type_pattern, html)
        attrs = re.findall(attr_value_pattern, html)

        if types and attrs:
            types = eval(types[0])
            attrs = eval(attrs[0])
            return dict(zip(types, attrs))
        return {}
