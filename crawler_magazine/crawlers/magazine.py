import asyncio

from crawler_magazine.crawlers.product import ProductDetail, IteratorPageCrawler


class MagazineCrawler:
    def __init__(self, start_url: str):
        if "www.magazineluiza.com.br" not in start_url:
            raise ValueError(
                "Only Magazine Luiza site is accept."
            )
        if "?page={}" not in start_url:
            start_url += "?page={}"

        self.start_url = start_url

    def crawl(self):
        loop = asyncio.get_event_loop()
        partial_products = loop.run_until_complete(
            IteratorPageCrawler(self.start_url).crawl()
        )
        print(partial_products)
        detail_product_crawler = asyncio.gather(
            *(ProductDetail(item.get("url")).crawl() for item in partial_products)
        )
        all_details = loop.run_until_complete(detail_product_crawler)
        print(all_details)
        print(len(all_details))


if __name__ == '__main__':
    MagazineCrawler(
        "https://www.magazineluiza.com.br/aquecedor-eletrico/"
        "ar-e-ventilacao/s/ar/arae/brand---mondial?page={}"
    ).crawl()
