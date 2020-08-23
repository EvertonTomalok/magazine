from pymongo import MongoClient

from crawler_magazine.model.settings import MONGODB_SETTINGS


class Database:
    __client = None
    __database = None

    def __init__(self):
        self.__setup()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__teardown()

    def __del__(self):
        self.__teardown()

    def __setup(self):
        if not self.__client:
            self.__client = MongoClient(MONGODB_SETTINGS["url"])
        self.__database = self.__client["magazine"]
        self.products = self.__database.products
        self.err_col = self.__database.err_col

    def __teardown(self):
        if self.__client:
            try:
                self.__client.close()
            except TypeError:
                pass

    def insert_update_product(self, data) -> str:
        self.products.update_one({"sku": data.get("sku")}, {"$set": data}, upsert=True)
        return f"Added/updated sku {data.get('sku')}"

    def count_product_by_brand(self, marca: str) -> dict:
        # The same result could be retrieved using `count_documents`
        #   self.products.count_documents({"marca": "MONDIAL"})
        # I think that's a best way to count documents.

        if product_aggregate := list(
            self.products.aggregate(
                [
                    {"$match": {"marca": f"{marca}"}},
                    {"$group": {"_id": "$marca", "count": {"$sum": 1}}},
                ]
            )
        ):
            return product_aggregate[0]
        return {"_id": f"{marca}", "count": 0}

    def count_available_rupture_products(self) -> dict:
        if available_rupture := self.products.aggregate(
            [{"$group": {"_id": "$estoque", "count": {"$sum": 1}}}]
        ):
            return {
                ("disponiveis" if item["_id"] == "S" else "ruptura"): item["count"]
                for item in available_rupture
            }
        return {"disponiveis": 0, "ruptura": 0}

    def find_ean(self, ean: str) -> list:
        return list(self.products.find({"ean": ean}, {"_id": 0}))

    def find_sku(self, sku: str) -> dict:
        return self.products.find_one({"sku": sku}, {"_id": 0})

    def _ensure_indexes(self):
        """
        Create indexes if it not exists
        """
        self.products.create_index([("ean", 1)], name="ean_index", background=True)
        self.products.create_index(
            [("sku", 1)], name="sku_index", background=True, unique=True
        )
        self.products.create_index([("marca", 1)], name="marca_index", background=True)
        self.products.create_index(
            [("estoque", 1)], name="estoque_index", background=True
        )
