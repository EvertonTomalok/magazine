import asyncio

from crawler_magazine.crawlers.productcrawler import IteratorPageCrawler, ProductCrawler


class MagazineCrawler:
    def __init__(self, start_url: str):
        if "www.magazineluiza.com.br" not in start_url:
            raise ValueError("Only Magazine Luiza site is accept.")
        if "?page={}" not in start_url:
            start_url += "?page={}"

        self.start_url = start_url

    def crawl(self):
        """
        Get all products iterating in the pages, and run async to crawl each
        product found and save it on MongoDB
        """
        loop = asyncio.get_event_loop()

        # Iterates on pages and get all products info
        partial_products = loop.run_until_complete(
            IteratorPageCrawler(self.start_url).crawl()
        )

        # Crawl each product, join information, and save it
        detail_product_crawler = asyncio.gather(
            *(
                ProductCrawler(url=item.get("url"), data=item).crawl()
                for item in partial_products
            )
        )
        loop.run_until_complete(detail_product_crawler)
