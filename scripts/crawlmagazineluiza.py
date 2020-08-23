from crawler_magazine.crawlers.magazine import MagazineCrawler
from time import perf_counter


if __name__ == '__main__':
    start = perf_counter()
    MagazineCrawler(
        "https://www.magazineluiza.com.br/aquecedor-eletrico/"
        "ar-e-ventilacao/s/ar/arae/brand---mondial"
    ).crawl()

    print(
        f"Crawling took {perf_counter() - start} seconds."
    )
