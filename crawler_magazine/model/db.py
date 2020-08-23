from bson import ObjectId
from pymongo import DESCENDING, MongoClient

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

    def insert_update_product(self, data):
        self.products.update_one(
            {
                "sku": data.get("sku")
            },
            {
                "$set": data
            }
        )
        return f"Added/updated sku {data.get('sku')}"

    def count_product_by_brand(self, marca: str):
        # The same result could be retrieved using `count_documents`
        #   self.products.count_documents({"marca": "MONDIAL"})
        # I think that's a best way to count documents.

        if product_aggregate := list(
            self.products.aggregate(
                [
                    {
                        "$match": {
                            "marca": f"{marca}"
                        }
                    },
                    {
                        "$group": {
                            "_id": "$marca",
                            "count": {
                                "$sum": 1
                            }
                        }
                    }
                ]
            )
        ):
            return product_aggregate[0]
        return {"_id": f"{marca}", "count": 0}

    def count_available_rupture_products(self):
        if available_rupture := self.products.aggregate(
            [
                {
                    "$group": {
                        "_id": "$estoque",
                        "count": {
                            "$sum": 1
                        }
                    }
                }
            ]
        ):
            return {
                ("disponiveis" if item["_id"] == "S" else "ruptura"): item["count"]
                for item in available_rupture
            }
        return {"disponiveis": 0, "ruptura": 0}

    def find_ean(self, ean: str):
        return self.products.find_one({"ean": ean})

    def find_sku(self, sku: str):
        return self.products.find_one({"sku": sku})
